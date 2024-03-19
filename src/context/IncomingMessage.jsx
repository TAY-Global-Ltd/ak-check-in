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
        removeUser(userId);
      }

      // Check if the user already exists in the list
      const existingUserIndex = students.findIndex(
        (user) => user["user-id"] === userId
      );

      if (existingUserIndex !== -1) {
        // User already exists in the list, update status if it's different
        if (
          students[existingUserIndex].event_id === event_id &&
          students[existingUserIndex].status !== status
        ) {
          const updatedStudents = [...students];
          updatedStudents[existingUserIndex] = {
            "user-id": userId,
            ...userData,
            status,
          };
          setStudents(updatedStudents);
        } else {
          // Add same user for different class
          setStudents((prevStudents) => [
            ...prevStudents,
            { "user-id": userId, ...userData, status, event_id },
          ]);
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

  const removeUser = (userId) => {
    setStudents((prevStudents) =>
      prevStudents.filter((user) => user["user-id"] !== userId)
    );
  };

  return { students, handleIncomingMessage };
};

export default useIncomingMessage;
