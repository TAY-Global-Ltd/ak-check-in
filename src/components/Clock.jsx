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

  const formattedTime = currentTime.toLocaleTimeString();

  return (
    <div
      className={`logo-container ${
        lightMode
          ? "light-bg-primary light-box-shadow"
          : "dark-bg-primary dark-box-shadow"
      }`}
    >
      <img src={logo} className="logo" alt="ak-logo" />
      <strong>{formattedTime}</strong>
    </div>
  );
};

export default Clock;
