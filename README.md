Graph Query Parser & Editor
##A repository for Graph Query Extension for Burp Suite

If you have tested applications that use Graph Query Language(GQL), you would have realised that none of the current day web proxies have the capability to understand and hence effectively test such requests. As a tester you would want to simplify the format so you can focus on more meaningful issues, injections,etc.

The 'GQLParser' is an extension for Burp Suite meant to do just that. It helps the tester to:
  Detect
  Parse & Format
  Edit/Tamper

the GraphQL(GQL) requests clearly and efficiently thereby saving test time.

All this is done without affecting the subsequent query structure and hence efficient tampering becomes way easier. The parser also provides a structured view for tester to see the data models being queried, attributes belonging to fragments and formats the response data as well, to show a preview of the objects returned clearly.

This also works via Repeater if you want to tamper/play with the request, you simply need to right-click and send to the repeater tab. The GQLParser is enabled and ready to use in the Repeater.


Requirements:
You will need the below to get started:
  The latest version of Burp(Tested for Burp 1.7.37 and above)
  A Jython standalone Jar file (To be added to Extender > Options > Python Environment)
