import { createContext, useContext, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import PubNub from "pubnub";

import {
  getCheckInData,
  getCurrentClassData,
  getNextClassData,
} from "../services/getCheckInData";
import Loader from "../components/Loader";

const CheckInContext = createContext();

export const useCheckInContext = () => {
  const context = useContext(CheckInContext);
  if (context === undefined) {
    throw new Error("useCheckInContext must be used within a CheckInProvider");
  }
  return context;
};

const CheckInProvider = ({ children }) => {
  const [message, setMessage] = useState(null);
  const [lightMode, setLightMode] = useState(false);

  const subscribeToUpdates = async (channel, subscribeKey, uuid) => {
    const pubnub = new PubNub({
      subscribeKey: subscribeKey,
      uuid: uuid,
    });

    pubnub.addListener({
      message: function (event) {
        setMessage(event.message);
      },
    });

    pubnub.subscribe({
      channels: [channel],
      withPresence: true,
    });
  };

  const {
    data: checkInData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["CheckInData"],
    queryFn: getCheckInData,
  });

  const { data: currentClassData, isLoading: currentClassIsLoading } = useQuery(
    {
      queryKey: ["CurrentClassData"],
      queryFn: getCurrentClassData,
    }
  );

  const { data: nextClassData, isLoading: nextClassIsLoading } = useQuery({
    queryKey: ["NextClassData"],
    queryFn: getNextClassData,
  });

  useEffect(() => {
    if (checkInData) {
      const subInfo = checkInData.subscription_info;
      subscribeToUpdates(
        subInfo.channel,
        subInfo.subscribe_key,
        subInfo.user_id
      );
      document.title = "AK Attendance";
    }
  }, [checkInData]);

  if (isLoading || currentClassIsLoading || nextClassIsLoading) {
    return <Loader />;
  }

  if (error) {
    return <p>Error: {error.message}</p>;
  }

  const students = checkInData.attendees;

  // Theme toggle
  const toggleTheme = () => {
    setLightMode((prevMode) => !prevMode);
  };

  return (
    <CheckInContext.Provider
      value={{
        students,
        nextClassData,
        currentClassData,
        message,
        lightMode,
        toggleTheme,
      }}
    >
      {children}
    </CheckInContext.Provider>
  );
};

export default CheckInProvider;
