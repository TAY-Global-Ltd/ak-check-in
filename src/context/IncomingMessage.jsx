import { useCallback, useState } from "react";

const useIncomingMessage = () => {
  const [students, setStudents] = useState([]);

  const handleIncomingMessage = useCallback(
    (message, checkInData) => {
      if (!checkInData) {
        return;
      }

      const { status, "user-id": userId, event_id, ...userData } = message;

      if (status === "cancelled") {
        removeUser(userId, event_id); // Call removeUser with userId and event_id
        return; // Return early since the user is removed
      }

      // Check if the user already exists in the list
      const existingUserIndex = students.findIndex(
        (user) => user["user-id"] === userId && user.event_id === event_id
      );

      if (existingUserIndex !== -1) {
        // User already exists in the list, update status if it's different
        if (
          Object.keys(students[existingUserIndex]).some(
            (key) => students[existingUserIndex][key] !== message[key]
          )
        ) {
          const updatedStudents = [...students];
          updatedStudents[existingUserIndex] = {
            "user-id": userId,
            ...userData,
            status,
            event_id,
          };
          setStudents(updatedStudents);
        }
      } else {
        // User not found in the list, add the user
        setStudents((prevStudents) => [
          ...prevStudents,
          { "user-id": userId, ...userData, status, event_id },
        ]);
      }
    },
    [students]
  );

  const removeUser = (userId, event_id) => {
    setStudents((prevStudents) =>
      prevStudents.filter(
        (user) => user["user-id"] !== userId && user.event_id !== event_id // Use AND condition to remove based on userId and event_id
      )
    );
  };

  return { students, handleIncomingMessage };
};

export default useIncomingMessage;
