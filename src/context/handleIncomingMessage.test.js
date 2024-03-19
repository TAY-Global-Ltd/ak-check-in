import { renderHook, act } from "@testing-library/react-hooks";
import * as React from "react"; // Import React for mocking context
import CheckInProvider from "./CheckInContext"; // Import your context provider
import { useCheckInContext } from "./CheckInContext"; // Import the hook containing handleIncomingMessage

describe("useCheckInContext", () => {
  // Mock the dependencies (removeUser, students, setStudents)
  jest.mock("./CheckInContext", () => jest.fn());

  it("should handle incoming message correctly", () => {
    // Mock the context value
    const setStudents = jest.fn();
    const students = [];
    const useContextSpy = jest.spyOn(React, "useContext");
    useContextSpy.mockReturnValue({ students, setStudents });

    // Render the hook within the context provider
    const { result } = renderHook(() => useCheckInContext(), {
      wrapper: CheckInProvider, // Provide your context provider as a wrapper
    });

    // Define a sample message
    const message = {
      status: "checkedIn",
      "user-id": "123",
      event_id: "event123",
      name: "Foo",
    };

    // Call the handleIncomingMessage function
    act(() => {
      result.current.handleIncomingMessage(message, true);
    });

    // Assert that the students list is updated as expected
    expect(setStudents).toHaveBeenCalledWith([
      {
        "user-id": "123",
        name: "Foo",
        status: "checkedIn",
        event_id: "event123",
      },
    ]);
  });

  // Add more test cases for other scenarios if needed
});
