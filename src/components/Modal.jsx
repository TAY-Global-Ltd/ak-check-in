import React, { useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import "./Modal.css";
import {
  greetingsArray,
  emojies,
  checkedInPhrases,
} from "../constants/constants";
import { getRandomElement } from "../utils/modalCopies";
import { useCheckInContext } from "../context/CheckInContext";

// TODO ~~~~~~ make overlay transparant, add green box shadow to Modal, improve lightMode ? conditional css, improve getRandomElement function, test current title with Teenage Kickboxing ot Muay Thai ( ledies only ) maybe add max-width to the container

const Modal = () => {
  const { message, lightMode } = useCheckInContext();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [newMessage, setNewMessage] = useState(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (message && message !== newMessage) {
      setNewMessage(message);
    }
  }, [message]);

  useEffect(() => {
    if (newMessage) {
      setIsModalVisible(true);

      const timeoutId = setTimeout(() => {
        setIsModalVisible(false);
        queryClient.invalidateQueries(["CheckInData"]);
      }, 3000);

      return () => clearTimeout(timeoutId);
    }
  }, [newMessage, queryClient]);

  const greeting = getRandomElement(greetingsArray);
  const emoji = getRandomElement(emojies);
  const summary = getRandomElement(checkedInPhrases);

  return (
    <div
      className={`modal-overlay ${isModalVisible ? "visible" : ""} ${
        lightMode ? "light-bg-primary" : "dark-bg-primary"
      }`}
    >
      <div
        className={`modal-content ${
          lightMode ? "light-bg-secondary" : "dark-bg-secondary"
        } ${lightMode ? "light-box-shadow" : "dark-box-shadow"}`}
      >
        <h1>{greeting}</h1>
        {newMessage && (
          <>
            <p>{newMessage.reward}</p>
            <h1 className="student-name">{newMessage.name}</h1>
          </>
        )}
        <h2>
          {summary} {emoji}
        </h2>
      </div>
    </div>
  );
};

export default Modal;
