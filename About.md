## About

If you have tested applications that use Graph Query Language(GQL), you would have realised that none of the current day web proxies have the capability to understand and hence effectively test such requests. As a tester you would want to simplify the format so you can focus on more meaningful issues, injections,etc.

The 'GQLParser' is an extension for Burp Suite meant to do just that. It helps the tester to detect, parse & format edit/tamper the GraphQL(GQL) requests clearly and efficiently thereby saving test time.

All this is done without affecting the subsequent query structure and hence efficient tampering becomes way easier. The parser also provides a structured view for tester to see the data models being queried and attributes belonging to respective fragments. It also formats the response data to show a preview of the objects and contained attributes, clearly.

This also works via Repeater if you want to tamper/play with the request, you simply need to right-click and send to the repeater tab. The GQLParser is enabled and ready to use in the Repeater.

Refer to the README for instructions on manual installation and Usage.
