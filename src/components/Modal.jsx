import React, { useState, useEffect } from "react";
import { greetingsArray, emojies, checkedInPhrases } from "../constants/constants";
import { getRandomElement } from "../utils/modalCopies";

import "./Modal.css";

const greeting = getRandomElement(greetingsArray);
const emoji = getRandomElement(emojies);
const summary = getRandomElement(checkedInPhrases);

const Modal = () => {
  const [isModalVisible, setIsModalVisible] = useState(true);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setIsModalVisible(false);
    }, 2000);

    return () => clearTimeout(timeoutId);
  }, []);

  return (
    <div className={`modal-overlay ${isModalVisible ? "visible" : ""}`}>
      <div className="modal-content">
        <h1>{greeting}</h1>
        <h1>Jack Sparrow</h1>
        <h1>{summary} {emoji}</h1>
      </div>
    </div>
  );
};

export default Modal;
