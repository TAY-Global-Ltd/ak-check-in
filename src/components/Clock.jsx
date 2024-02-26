import React, { useState, useEffect } from "react";
import { useCheckInContext } from "../context/CheckInContext";
import "../App.css";

const Clock = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { lightMode, checkInData } = useCheckInContext();

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const formattedDate = new Intl.DateTimeFormat("en-GB", {
    timeZone: checkInData?.settings.timezone,
    dateStyle: "medium",
  }).format(currentTime);
  const formattedTime = new Intl.DateTimeFormat("en-GB", {
    timeZone: checkInData?.settings.timezone,
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
      <img src={checkInData?.settings.icon} className="logo" alt="ak-logo" />
      <h4 style={{ margin: "0" }}>
        {formattedTime}
        <br />
        {formattedDate}
      </h4>
    </div>
  );
};

export default Clock;
