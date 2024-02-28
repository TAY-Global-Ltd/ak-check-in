import { createContext, useContext, useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import PubNub from "pubnub";

import {
  getCheckInData,
  getCurrentClassData,
  getNextClassData,
} from "../services/getCheckInData";
import { isClassOver } from "../utils/time";

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
  const [students, setStudents] = useState(null);
  const [lightMode, setLightMode] = useState(false);
  const queryClient = useQueryClient();

  const handleMessage = (message) => {
    if (!checkInData) {
      return;
    }

    const { status, "user-id": userId, ...userData } = message;

    if (status === "cancelled") {
      // Remove user from the list
      removeUser(userId);
    } else {
      // Check if the user already exists in the list
      const existingUser = students.find((user) => user["user-id"] === userId);

      if (existingUser) {
        // User already exists in the list, update status if it's different
        if (existingUser.status !== status) {
          const updatedStudents = students.map((user) =>
            user["user-id"] === userId ? { ...user, status, ...userData } : user
          );
          setStudents(updatedStudents);
        }
      } else {
        // User not found in the list, add the user
        setStudents((prevStudents) => [
          ...prevStudents,
          { "user-id": userId, ...userData, status },
        ]);
      }
    }
    setMessage(message);
  };

  const removeUser = (userId) => {
    setStudents((prevStudents) =>
      prevStudents.filter((user) => user["user-id"] !== userId)
    );
  };

  const subscribeToUpdates = async (channel, subscribeKey, uuid) => {
    const pubnub = new PubNub({
      subscribeKey: subscribeKey,
      uuid: uuid,
    });

    pubnub.addListener({
      error: (error) => console.log("Error:", error),
      status: function (status) {
        if (status.category === "PNUnsubscribedCategory") {
          console.log(`Unsubscribed from channel: ${status.affectedChannels}`);
        }
        if (status.category === "PNDisconnectedCategory") {
          console.log("Attempting to reconnect...");
          pubnub.reconnect();
        }
        if (status.category === "PNNetworkDownCategory") {
          console.log("No Network conncetion, attempting to reconnect...");
          pubnub.reconnect();
        }
        if (status.category === "PNUnknownCategory") {
          console.error("An unknown error occurred:", status.errorData);
        }
      },
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
    isLoading: checkInIsLoading,
    error: checkInError,
  } = useQuery({
    queryKey: ["CheckInData"],
    queryFn: getCheckInData,
  });

  const {
    data: currentClassData,
    isLoading: currentClassIsLoading,
    error: currentClassError,
  } = useQuery({
    queryKey: ["CurrentClassData"],
    queryFn: getCurrentClassData,
  });

  const {
    data: nextClassData,
    isLoading: nextClassIsLoading,
    error: nextClassError,
  } = useQuery({
    queryKey: ["NextClassData"],
    queryFn: getNextClassData,
  });

  // get initial data and sub to Pubnub
  useEffect(() => {
    if (!!checkInData) {
      const subInfo = checkInData.subscription_info;
      subscribeToUpdates(
        subInfo.channel,
        subInfo.subscribe_key,
        subInfo.user_id
      );

      // set theme mode based on server settings
      if (checkInData.settings.display_mode !== "dark") setLightMode(true);

      setStudents(checkInData?.attendees);

      const interval = setInterval(() => {
        queryClient.invalidateQueries("");
      }, checkInData?.settings.refresh_interval * 1000); // Invalidate the query every 1 hour

      return () => clearInterval(interval); // Clear the interval on component unmount
    }
  }, [checkInData, queryClient]);

  if (checkInError || currentClassError || nextClassError) {
    console.log(`Error fetching data:
    ${
      checkInError?.message ||
      currentClassError?.message ||
      nextClassError?.message
    }`);
  }

  // refetch all data ince current class is over
  useEffect(() => {
    if (!!currentClassData) {
      if (isClassOver(currentClassData.end_time)) {
        queryClient.invalidateQueries([""]);
      }
    }
  }, [currentClassData, queryClient]);

  // handle message once received from Pubnub
  useEffect(() => {
    if (!!message) {
      handleMessage(message);
    }
  }, [message]);

  // Theme toggle
  const toggleTheme = () => {
    setLightMode((prevMode) => !prevMode);
  };

  return (
    <CheckInContext.Provider
      value={{
        students,
        checkInData,
        nextClassData,
        currentClassData,
        message,
        lightMode,
        toggleTheme,
        checkInIsLoading,
        currentClassIsLoading,
        nextClassIsLoading,
      }}
    >
      {children}
    </CheckInContext.Provider>
  );
};

export default CheckInProvider;
