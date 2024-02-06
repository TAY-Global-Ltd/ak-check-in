import React, { useState, useEffect } from "react";
import "./Modal.css";
import {
  greetingsArray,
  emojies,
  checkedInPhrases,
} from "../constants/constants";
import { getRandomElement } from "../utils/modalCopies";
import { useCheckInContext } from "../context/CheckInContext";

const greeting = getRandomElement(greetingsArray);
const emoji = getRandomElement(emojies);
const summary = getRandomElement(checkedInPhrases);

const Modal = () => {
  const { message } = useCheckInContext();
  const [isModalVisible, setIsModalVisible] = useState(false);

  console.log("~~~ message", message);

  useEffect(() => {
    if (message) {
      setIsModalVisible(true);

      const timeoutId = setTimeout(() => {
        setIsModalVisible(false);
      }, 3000);

      return () => clearTimeout(timeoutId);
    }
  }, [message]);

  return (
    <div className={`modal-overlay ${isModalVisible ? "visible" : ""}`}>
      <div className="modal-content">
        <h1>{greeting}</h1>
        <p>{message?.reward}</p>
        <h1>{message?.name}</h1>
        <h1>
          {summary} {emoji}
        </h1>
      </div>
    </div>
  );
};

export default Modal;
