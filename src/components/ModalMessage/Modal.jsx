import React, { useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import "./Modal.css";
import { useCheckInContext } from "../../context/CheckInContext";
import { checkStudentsStatus } from "../../utils/studentSorting";

const Modal = () => {
  const { message, lightMode, students } = useCheckInContext();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [newMessage, setNewMessage] = useState("");
  const queryClient = useQueryClient();

  const { checkedIn } = checkStudentsStatus(students);

  const isCheckedIn = newMessage?.status === "checkedin";

  // console.log("~~~ message !== newMessage", message !== newMessage);
  // console.log("~~~ checkedIn", checkedIn);

  useEffect(() => {
    if (message && message !== newMessage) {
      setNewMessage(message);
    }
  }, [message, newMessage]);

  // useEffect(() => {
  //   if (newMessage && newMessage.status === "checkedin") {
  //     // Check if the student is already in the list of checked-in students
  //     if (!checkedIn.find((student) => student["user-id"] === newMessage["user-id"])) {
  //       // console.log('~~~ show modal')
  //       setIsModalVisible(true);

  //       // Automatically hide the modal after 3 seconds
  //       const timeoutId = setTimeout(() => {
  //         setIsModalVisible(false);
  //       }, 3000);

  //       return () => clearTimeout(timeoutId);
  //     }
  //     // console.log('~~~ DONT show modal')
  //   }
  // }, [newMessage, checkedIn]);

  useEffect(() => {
    if (newMessage && isCheckedIn) {
      setIsModalVisible(true);

      const timeoutId = setTimeout(() => {
        setIsModalVisible(false);
      }, 3000);

      return () => clearTimeout(timeoutId);
    }
  }, [newMessage, isCheckedIn, queryClient]);

  return (
    <div
      className={`modal-overlay ${isModalVisible ? "visible" : ""} ${
        lightMode ? "overlay-light-bg-primary" : "overlay-dark-bg-primary"
      }`}
    >
      <div
        className={`modal-content ${
          lightMode ? "light-bg-secondary" : "dark-bg-secondary"
        }`}
      >
        {newMessage && (
          <>
            <p>{newMessage.reward}</p>
            <h1 className="student-name">{newMessage.name}</h1>
          </>
        )}
        <h2>You are checked in ✅</h2>
      </div>
    </div>
  );
};

export default Modal;
