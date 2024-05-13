import { useEffect, useState } from "react";

import UsersTable from "./UsersTable/UsersTable";
import NextClass from "./NextClass/NextClass";
import Clock from "./Clock";
import Modal from "./ModalMessage/Modal";
import CurrentClass from "./CurrentClass/CurrentClass";
import { useCheckInContext } from "../context/CheckInContext";
import lightBackground from "../assets/diesel_ak_light_bg.png";
import darkBackground from "../assets/diesel_ak_bg.png";
import KeyInputModal from "./KeyInputModal/KeyInputModal";
import "../global.css";

const CheckInPage = () => {
  const { lightMode, checkInData, checkInError } = useCheckInContext();
  const backgroundImage = lightMode ? lightBackground : darkBackground;
  const [showKeyModal, setShowKeyModal] = useState(false);

  useEffect(() => {
    const hasAuthToken = localStorage.getItem("authorization_token") !== null;
    if (!hasAuthToken) {
      setShowKeyModal(true);
    }

    // show auth key modal if token invalid
    if (!!hasAuthToken && checkInError) {
      setShowKeyModal(true);
    }
  }, [checkInError]);

  const closeKeyModal = () => {
    setShowKeyModal(false);
  };

  useEffect(() => {
    if (!!checkInData) {
      // Set the meta title
      document.title = checkInData?.settings.title;

      // Set the meta icon's href
      const existingFaviconLink = document.getElementById("app-icon");
      existingFaviconLink.setAttribute("href", checkInData?.settings.icon);

      // Set the description by updating the <meta> tag
      const metaDescription = document.getElementById("app-description");
      metaDescription.setAttribute(
        "content",
        checkInData?.settings.description
      );
    }
  }, [checkInData]);

  return (
    <div
      className={`App ${lightMode ? "light-font" : "dark-font"}`}
      style={{
        backgroundImage: `url(${backgroundImage})`,
        minHeight: "100vh",
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        backgroundPosition: "center",
      }}
    >
      <header
        className={`App-header ${
          lightMode ? "light-bg-secondary" : "dark-bg-secondary"
        }`}
      >
        <NextClass />
        <CurrentClass />
        <div className="clock-wrapper">
          <Clock />
        </div>
      </header>
      <main>
        <Modal />
        <UsersTable />
        <KeyInputModal isOpen={showKeyModal} onClose={closeKeyModal} />
      </main>
    </div>
  );
};

export default CheckInPage;
