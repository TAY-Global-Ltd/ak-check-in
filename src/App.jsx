import "./App.css";
import UsersTable from "./components/UsersTable";
import Timer from "./components/Timer";
import { useEffect } from "react";
import PubNub from 'pubnub';

const currentClass = "BJJ";

const App = () => {

  useEffect(() => {

    const subscribeToUpdates = async (channel, subscribeKey, uuid) => {
      const pubnub = new PubNub({
        subscribeKey: subscribeKey,
        uuid: uuid
      });

      pubnub.addListener({
        message: function (event) {
          console.log("~~~ event", event.message);
        },
        presence: function (presenceEvent) {
          console.log('~~~ Presence Event:', presenceEvent);
        },
      });

      pubnub.subscribe({
        channels: [channel],
        withPresence: true,
      });
    }

    const initApp = async () => {
      const res = await fetch('http://127.0.0.1:8765/initial_state');
      const initialState = await res.json();
      const subInfo = initialState.subscription_info
      subscribeToUpdates(subInfo.channel, subInfo.subscribe_key, subInfo.user_id)
      document.title = "AK Attendance";
    }

    initApp();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src="ak-logo.png" className="logo" alt="logo" />
        <h3>🤼‍♂️ {currentClass}</h3>
      </header>
      <UsersTable />
      <footer className="footer">
        <Timer />
      </footer>
    </div>
  );
};

export default App;
