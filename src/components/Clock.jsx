import '../App.css'
import React, { useState, useEffect } from "react";

const Clock = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const formattedTime = currentTime.toLocaleTimeString();

  return (
    <div className="logo-container">
      <img src="logo192.png" className="logo" alt="ak-logo" />
      <strong>{formattedTime}</strong>
    </div>
  );
};

export default Clock;
