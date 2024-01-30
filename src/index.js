import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import PubNub from 'pubnub';
// import { PubNubProvider, usePubNub } from 'pubnub-react';

const pubnub = new PubNub({
  publishKey: process.env.PUB_NUB_PUBLISH_KEY,
  subscribeKey: process.env.PUB_NUB_SUBSCRIBE_KEY,
  uuid: "myFirstUser",
});

pubnub.subscribe({
  channels: ["ak-check-in"],
  withPresence: true,
});

pubnub.addListener({
  message: function (event) {
    console.log("~~~ event", event.message);
  },
  presence: function (presenceEvent) {
    console.log('~~~ Presence Event:', presenceEvent);
  },
});


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
