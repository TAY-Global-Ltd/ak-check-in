import React, { useState, useEffect } from "react";
import { useCheckInContext } from "../context/CheckInContext";
import "../App.css";

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
        lightMode ? "light-bg-primary" : "dark-bg-primary"
      } ${
        lightMode ? "light-box-shadow" : "dark-box-shadow"
      }`}
    >
      <img src="logo192.png" className="logo" alt="ak-logo" />
      <strong>{formattedTime}</strong>
    </div>
  );
};

export default Clock;
