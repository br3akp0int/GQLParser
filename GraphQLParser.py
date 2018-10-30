from burp import IBurpExtender
from burp import IMessageEditorTabFactory
from burp import IMessageEditorTab
from burp import IScannerInsertionPointProvider
from burp import IScannerInsertionPoint
from burp import IParameter
import json
import queryProcess


class BurpExtender(IBurpExtender, IScannerInsertionPointProvider, IMessageEditorTabFactory):
    ##
    #Main Class for Burp Extenders
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("GraphQLParser")
        callbacks.issueAlert("GQL Parser Started")
        print "Graph Query(GQL) Parser Started!"

        #Registering Graph Query Tab
        callbacks.registerMessageEditorTabFactory(self)

        #Registering IScannerInsertionPointProvider class Object
        callbacks.registerScannerInsertionPointProvider(self)

        return

    # Define function to fetch Insertion Points
    def getInsertionPoints(self, baseRequestResponse):
    # get the parameter for insertion
        dataParameter = self._helpers.getRequestParameter(baseRequestResponse.getRequest(), "data")
        if (dataParameter is None):
            return None
        else:
            # ad one insertion point at a time
            return [InsertionPoint(self._helpers, baseRequestResponse.getRequest(), dataParameter.getValue())]

    def createNewInstance(self, controller, editable):
        return listGQLParameters(self, controller, editable)


class listGQLParameters(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self._extender = extender
        self._helpers = extender._helpers
        self._editable = editable
        self._txtInput = extender._callbacks.createTextEditor()
        self._txtInput.setEditable(editable)
        #Define Query Indicators To Identify a GQL
        self._GQLIndicator = [
            '[{"operationName"',
            '{"operationName":',
            '[{"query":"query ',
            '{"query":"mutation',
            '{"query":"',
            '{"data":',
            '[{"data":']
        self._variable = 'variables": {'

        return

    #define Message Editor Properties for GQL Editor

    def getTabCaption(self):
        return "GraphQLParser"

    def getUiComponent(self):
        return self._txtInput.getComponent()

    def isEnabled(self, content, isRequest):
        isgql = False
        if isRequest:
            rBody = self._helpers.analyzeRequest(content)

        else:
            rBody = self._helpers.analyzeResponse(content)

        message = content[rBody.getBodyOffset():].tostring()
        for indicator in self._GQLIndicator:
            if message.startswith(indicator):
                isgql = True


        if len(message) > 2 and isgql:
            #print "Starting GQL parsing and gql Indicator found: %s"%message[:17]
            return True
        else:

            var_pos = message.find(self._variable)
            if len(message) > 2 and var_pos > 0:
                #print "GQL Indicator found: %s" % message[var_pos:var_pos+17]
                return True

        return False


    def setMessage(self, content, isRequest):
        if content is None:
            #Display Nothing for NoContent
            self._txtInput.setText(None)
            self._txtInput.setEditable(False)
        else:
            if isRequest:
                rBody = self._helpers.analyzeRequest(content)
            else:
                rBody = self._helpers.analyzeResponse(content)

            message = content[rBody.getBodyOffset():].tostring()

            try:
                limit = min(
                    message.index('{') if '{' in message else len(message),
                    message.index('[') if '[' in message else len(message)
                )
            except ValueError:
                print "Sorry, this doesnt look like a Graph Query!"
                print ValueError
                return

            garbage = message[:limit]
            clean = message[limit:]

            try:
                gql_msg = garbage.strip() + '\n' + json.dumps(json.loads(clean), indent=4)
                #gql_msg = re.sub(r'\\n', '\n', gql_msg)


            except Exception:
                print("Problem parsing the setMessage")
                print(Exception)
                gql_msg = garbage + clean

            self._txtInput.setText(gql_msg)
            self._txtInput.setEditable(self._editable)


        self._currentMessage = content
        return

    def getMessage(self):
        if self._txtInput.isTextModified():
            try:
                #self._manual = True
                data = self._txtInput.getText()

            except Exception:
                print "Problem Getting the Message After Modification"
                print Exception

            # Update Request After Modification
            r = self._helpers.analyzeRequest(self._currentMessage)

            #return self._helpers.buildHttpMessage(r.getHeaders(), self._helpers.stringToBytes(data))
            return self._helpers.buildHttpMessage(r.getHeaders(), data)


    def isModified(self):
        return self._txtInput.isTextModified()

    def getSeletedData(self):
        return self._txtInput.getSelectedText()


class InsertionPoint(IScannerInsertionPoint):

    def __init__(self, helpers, baseRequest, dataParameter):
        self._helpers = helpers
        self._baseRequest = baseRequest
        self.final_positions = []
        dataParameter = helpers.bytesToString(dataParameter)
        ##Implement Query Process to get Insertion Points
        request = queryProcess(dataParameter)
        request.findInsertionPoints()
        self.final_positions = request.findFinalPositions()

        #Loop through to Create prefix and suffix for insertion Points
        for ins_point in self.final_positions:
            start = ins_point[0]
            end = ins_point[1]
            self._insertionPointPrefix = dataParameter[:start]
            if (end == -1):
                end = dataParameter.length()
            self._baseValue = dataParameter[start:end]
            self._insertionPointSuffix = dataParameter[end:]

        return

    def getInsertionPointName(self):
        return self._baseValue

    def buildRequest(self, payload):
        input(self._insertionPointPrefix + self._helpers.bytesToString(payload) + self._insertionPointSuffix)

        return self._helpers.updateParameter(self._baseRequest, self._helpers.buildParameter("data"), input, IParameter.PARAM_BODY)

    def getPayloadOffsets(self, payload):
        return None

    def getInsertionPointType(self):
        return INS_EXTENSION_PROVIDED