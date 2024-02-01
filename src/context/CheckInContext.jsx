import { createContext, useContext, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import PubNub from "pubnub";

import { getCheckInData } from "../services/getCheckInData";
import Loader from "../components/Loader";

const CheckInContext = createContext();

const subscribeToUpdates = async (channel, subscribeKey, uuid) => {
  const pubnub = new PubNub({
    subscribeKey: subscribeKey,
    uuid: uuid,
  });

  pubnub.addListener({
    message: function (event) {
      // TODO invalidate checkInData query
      console.log("~~~ event", event.message);
    },
    presence: function (presenceEvent) {
      console.log("~~~ Presence Event:", presenceEvent);
    },
  });

  pubnub.subscribe({
    channels: [channel],
    withPresence: true,
  });
};

export const useCheckInContext = () => {
  const context = useContext(CheckInContext);
  if (context === undefined) {
    throw new Error("useCheckInContext must be used within a CheckInProvider");
  }
  return context;
};

const CheckInProvider = ({ children }) => {
  const {
    data: checkInData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["CheckInData"],
    queryFn: getCheckInData,
  });

  useEffect(() => {
    if (checkInData) {
      console.log("~~~ checkInData", checkInData.attendees);

      const subInfo = checkInData.subscription_info;
      subscribeToUpdates(
        subInfo.channel,
        subInfo.subscribe_key,
        subInfo.user_id
      );
      document.title = "AK Attendance";
    }
  });

  if (isLoading) {
    return <Loader />;
  }

  if (error) {
    return <p>Error: {error.message}</p>;
  }

  const students = checkInData.attendees;

  return (
    <CheckInContext.Provider
      value={{
        students,
      }}
    >
      {children}
    </CheckInContext.Provider>
  );
};

export default CheckInProvider;
