import React, { useState } from "react";

import { useCheckInContext } from "../../context/CheckInContext";
import { hashString } from "../../utils/hash";
import "./KeyInputModal.css";

const KeyInputModal = ({ isOpen, onClose }) => {
  const [key, setKey] = useState("");
  const [error, setError] = useState("");
  const { lightMode } = useCheckInContext();

  const handleChange = (e) => {
    setKey(e.target.value);
  };

  const handleSave = async () => {
    if (key.length < 3) {
      setError("Please enter minimum 3 characters!");
      return;
    }

    try {
      const hashedName = await hashString(key);
      localStorage.setItem("encryption_key", hashedName);
      onClose();
    } catch (error) {
      console.error("Error hashing the key:", error);
      setError("Error hashing the key");
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className={`modal-overlay ${isOpen ? "visible" : ""} ${
        lightMode ? "overlay-light-bg-primary" : "overlay-dark-bg-primary"
      }`}
    >
      <div
        className={`modal-content ${
          lightMode ? "light-bg-secondary" : "dark-bg-secondary"
        }`}
        style={{ position: "relative", maxHeight: "30vh" }}
      >
        <span className="close" onClick={onClose}>
          &times;
        </span>
        <h1 className="key-title">
          Enter <span style={{ color: "var(--main-color" }}>Unique</span> Key
        </h1>
        <input
          type="text"
          value={key}
          onChange={handleChange}
          className={`key-input ${
            lightMode ? "light-bg-primary" : "dark-bg-primary"
          }`}
        />
        <button
          onClick={handleSave}
          className={`key-button ${
            lightMode ? "light-bg-primary" : "dark-bg-primary"
          }`}
        >
          Save
        </button>
        {error && <p style={{ color: "var(--main-color)" }}>{error}</p>}
      </div>
    </div>
  );
};

export default KeyInputModal;
