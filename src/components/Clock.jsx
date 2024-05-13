import React, { useState, useEffect } from "react";
import { useCheckInContext } from "../context/CheckInContext";
import logo from "../assets/diesel_ak_logo_tran.png";
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
    timeZone: checkInData?.settings?.timezone,
    dateStyle: "medium",
  }).format(currentTime);
  const formattedTime = new Intl.DateTimeFormat("en-GB", {
    timeZone: checkInData?.settings?.timezone,
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(currentTime);

  const timeParts = formattedTime.split(":");

  return (
    <div
      className={`logo-container ${
        lightMode
          ? "light-bg-primary light-box-shadow"
          : "dark-bg-primary dark-box-shadow"
      }`}
    >
      <img src={logo} className="logo" alt="diesel AK logo" />
      <h4 style={{ margin: "0" }}>
        <span>{timeParts[0]}:</span>
        <span>{timeParts[1]}:</span>
        <span style={{ color: "var(--main-color)" }}>{timeParts[2]}</span>{" "}
        <br />
        {formattedDate}
      </h4>
    </div>
  );
};

export default Clock;
