import React, { useState, useEffect } from "react";
import { useCheckInContext } from "../context/CheckInContext";
import "../App.css";
import logo from "../assets/logo192.png";

const Clock = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { lightMode } = useCheckInContext();

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  // TODO update timeZone and locale once get these from server
  // console.log('~~~ checkInData', checkInData.settings.timeZone)

  const formattedDate = new Intl.DateTimeFormat("en-GB", {
    timeZone: "GMT",
    dateStyle: "medium",
  }).format(currentTime);
  const formattedTime = new Intl.DateTimeFormat("en-GB", {
    timeZone: "GMT",
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(currentTime); 

  return (
    <div
      className={`logo-container ${
        lightMode
          ? "light-bg-primary light-box-shadow"
          : "dark-bg-primary dark-box-shadow"
      }`}
    >
      <img src={logo} className="logo" alt="ak-logo" />
      <h4 style={{ margin: "0" }}>
        {formattedTime}
        <br />
        {formattedDate}
      </h4>
    </div>
  );
};

export default Clock;
