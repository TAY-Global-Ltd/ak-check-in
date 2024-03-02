import { useState, useCallback } from "react";

// Define a custom hook to handle PubNub message updates
export const usePubNubMessage = () => {
  const [message, setMessage] = useState(null);

  const handleMessage = useCallback((message) => {
    setMessage(message);
  }, []);

  return { message, handleMessage };
};
