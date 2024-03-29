import React, { useState, useEffect } from "react";
import CryptoJS from "crypto-js";

import { useQueryClient } from "@tanstack/react-query";

import { useCheckInContext } from "../../context/CheckInContext";
import { encryptKey, key } from "../../utils/encrypt";
import "./KeyInputModal.css";

const KeyInputModal = ({ isOpen, onClose }) => {
  const [keyToken, setKeyToken] = useState("");
  const [error, setError] = useState("");
  const { lightMode } = useCheckInContext();
  const queryClient = useQueryClient();
  const [masked, setMasked] = useState(true);

  const authToken = localStorage.getItem("authorization_token");
  const hasAuthToken = localStorage.getItem("authorization_token") !== null;

  useEffect(() => {
    if (hasAuthToken) {
      const bytes = CryptoJS.AES.decrypt(authToken, key, {
        mode: CryptoJS.mode.ECB,
      });
      // Convert the decrypted bytes to a UTF-8 string
      const decryptedToken = bytes.toString(CryptoJS.enc.Utf8);
      setKeyToken(decryptedToken);
    }
  }, [hasAuthToken, authToken]);

  const toggleMask = () => {
    setMasked(!masked);
  };

  const handleChange = (e) => {
    setKeyToken(e.target.value);
  };

  const handleSave = async () => {
    if (keyToken.length < 3) {
      setError("Please enter minimum 3 characters!");
      return;
    }

    const encryptedToken = encryptKey(keyToken);
    localStorage.setItem("authorization_token", encryptedToken);
    queryClient.invalidateQueries("");
    onClose();
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
        <div className="input-wrapper">
          <input
            type={masked ? "password" : "text"}
            value={keyToken}
            onChange={handleChange}
            id="passwordInput"
            className={`key-input ${
              lightMode ? "light-bg-primary" : "dark-bg-primary"
            }`}
          />
          <span onClick={toggleMask} className="toggle-mask">
            {masked ? "show" : "hide"}
          </span>
        </div>
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
