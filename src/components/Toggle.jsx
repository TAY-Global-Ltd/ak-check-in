import React from "react";
import { useCheckInContext } from "../context/CheckInContext";
import "./Toggle.css";

const Toggle = () => {
  const { toggleTheme } = useCheckInContext();

  return (
    <div className="toggle-wrapper">
      <label className="switch">
        <input type="checkbox" onChange={toggleTheme} />
        <span className="slider round"></span>
      </label>
    </div>
  );
};

export default Toggle;
