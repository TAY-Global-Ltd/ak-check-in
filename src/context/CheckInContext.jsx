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
    isLoading: checkInIsLoading,
    error: checkInError,
  } = useQuery({
    queryKey: ["CheckInData"],
    queryFn: getCheckInData,
  });

  const {
    data: currentData,
    isLoading: currentClassIsLoading,
    error: currentClassError,
  } = useQuery({
    queryKey: ["CurrentClassData"],
    queryFn: getCurrentClassData,
  });

  const {
    data: nextData,
    isLoading: nextClassIsLoading,
    error: nextClassError,
  } = useQuery({
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

  const checkinMockData = [
    {
      event_id: "event-1",
      "user-id": "user0004",
      name: "Peter Parker",
      icon: "person_check",
      icon_type: "material",
      reward: "",
      status: "checkedin",
    },
  ];

  const nextClassMockData = [
    {
      event_id: "event-1",
      "user-id": "user0004",
      name: "Peter Parker",
      icon: "person_check",
      icon_type: "material",
      reward: "",
      status: "checkedin",
    },
  ];

  const currentClassMockData = [
    {
      id: "event-1",
      title: "BJJ",
      description: "BJJ Fundamentals",
      start_time: "18:00",
      end_time: "19:30",
      icon_type: "url",
      icon: "http://127.0.0.1:8765/static/images/bjj.png",
    },
  ];

  if (checkInIsLoading || currentClassIsLoading || nextClassIsLoading) {
    return <Loader />;
  }

  // if (checkInError || currentClassError || nextClassError) {
  //   return (
  //     <p>
  //       Error fetching data:{" "}
  //       {checkInError?.message ||
  //         currentClassError?.message ||
  //         nextClassError?.message}
  //     </p>
  //   );
  // }

  const students = checkInData ? checkInData.attendees : checkinMockData;
  const nextClassData = nextData ? nextData : nextClassMockData;
  const currentClassData = currentData ? currentData : currentClassMockData;

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
