import UsersTable from "./UsersTable";
import NextClass from "./NextClass";
import Clock from "./Clock";
import Modal from "./Modal";
import CurrentClass from "./CurrentClass";
import { useCheckInContext } from "../context/CheckInContext";
import lightBackground from "../assets/ak-light-bg.png";
import darkBackground from "../assets/ak-background.png";
import "../global.css";

const CheckInPage = () => {
  const { lightMode } = useCheckInContext();
  const backgroundImage = lightMode ? lightBackground : darkBackground;

  return (
    <div
      className={`App ${lightMode ? "light-font" : "dark-font"}`}
      style={{
        backgroundImage: `url(${backgroundImage})`,
      }}
    >
      <header
        className={`App-header ${
          lightMode ? "light-bg-secondary" : "dark-bg-secondary"
        }`}
      >
        <NextClass />
        <CurrentClass />
        <div className="clock-wrapper">
          <Clock />
        </div>
      </header>
      <main>
        <Modal />
        <UsersTable />
      </main>
    </div>
  );
};

export default CheckInPage;
