# ak-check-in

A system used for a gym to display who has checked in.

AK stands for [Artillery Kai](https://www.artillerykai.co.uk), the first gym that will be using this app.

This app is mainly a UI. It does require talking a server which is outside the scope of this repository.
However there is a mock server and an example AWS Lambda function for reference.



## Installing packages

Run:

```
npm install
```

## Staring the webapp

You'll need to set the envrionment variable ``REACT_APP_CHECKIN_API_SERVER_URL`` which points to the API server. 
If it is not set, it'll be defaulted to the mock server. You can either put that in ``.env`` or explictly export it.

```
export REACT_APP_CHECKIN_API_SERVER_URL=https://my.api.server.com/v1/
```

If you are using the mock server please see ``tests/mock_messages/README.md``

Now start the react dev server

```
npm start
```

The app should automatically pop up on your browswer. If not see the print to see the URL available for browser to open the app.

## Building

Use the below to build the app into the ``build`` directory.

```
npm run build
```

## Deployment

There are some example deployment script. But most likely you will be using your own.

See ``deploy.py``
