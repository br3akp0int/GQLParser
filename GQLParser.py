from burp import IBurpExtender
from burp import IMessageEditorTabFactory
from burp import IMessageEditorTab
import json



class BurpExtender(IBurpExtender, IMessageEditorTabFactory):
    ##
    #Main Class for Burp Extenders
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("GQLParser")
        callbacks.issueAlert("GQL Parser Started")
        print "Graph Query(GQL) Parser Started!"

        #Registering Graph Query Tab
        callbacks.registerMessageEditorTabFactory(self)

        return

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
        return "GQLParser"

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
            return True
        else:

            var_pos = message.find(self._variable)
            if len(message) > 2 and var_pos > 0:
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

                data = self._txtInput.getText()

            except Exception:
                print "Problem Getting the Message After Modification"
                print Exception

            # Update Request After Modification
            r = self._helpers.analyzeRequest(self._currentMessage)

            return self._helpers.buildHttpMessage(r.getHeaders(), data)

    def isModified(self):
        return self._txtInput.isTextModified()

    def getSeletedData(self):
        return self._txtInput.getSelectedText()
