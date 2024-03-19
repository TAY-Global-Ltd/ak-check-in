import { renderHook, act } from "@testing-library/react-hooks";
import useIncomingMessage from "./IncomingMessage"; // Import the hook containing handleIncomingMessage

describe("useIncomingMessage", () => {
  it("should update students count correctly for a new user", () => {
    // Render the hook
    const { result } = renderHook(() => useIncomingMessage());

    // Simulate an incoming message
    const message = {
      status: "checkedIn",
      "user-id": "123",
      event_id: "event123",
      name: "Foo",
    };
    act(() => {
      result.current.handleIncomingMessage(message, true);
    });

    // Get the updated students array
    const { students } = result.current;

    // Assert that the handleIncomingMessage function was called
    expect(students?.length).toBe(1); // One new student should be added

    // Assert that the new student has the same properties as the message
    const newStudent = students[0];
    expect(newStudent["user-id"]).toBe(message["user-id"]);
    expect(newStudent.event_id).toBe(message.event_id);
    expect(newStudent.name).toBe(message.name);
    expect(newStudent.status).toBe(message.status);
  });

  it("should remove user correctly when status is 'cancelled'", () => {
    // Render the hook
    const { result } = renderHook(() => useIncomingMessage());

    // Add a user to the students list
    act(() => {
      result.current.handleIncomingMessage(
        {
          status: "checkedIn",
          "user-id": "123",
          event_id: "event123",
          name: "Foo",
        },
        true
      );
    });

    // Simulate an incoming message with status 'cancelled'
    const message = {
      status: "cancelled",
      "user-id": "123",
      event_id: "event123",
      name: "Foo",
    };
    act(() => {
      result.current.handleIncomingMessage(message, true);
    });

    // Get the updated students array
    const { students } = result.current;

    // Assert that the user was removed from the students list
    expect(students?.length).toBe(0); // No students should remain after cancellation
  });

  it("should update user correctly when status changes", () => {
    // Render the hook
    const { result } = renderHook(() => useIncomingMessage());

    // Add a user to the students list
    act(() => {
      result.current.handleIncomingMessage(
        {
          status: "checkedIn",
          "user-id": "123",
          event_id: "event123",
          name: "Foo",
        },
        true
      );
    });

    // Simulate an incoming message with updated status
    const message = {
      status: "checkedOut",
      "user-id": "123",
      event_id: "event123",
      name: "Foo",
    };
    act(() => {
      result.current.handleIncomingMessage(message, true);
    });

    // Get the updated students array
    const { students } = result.current;

    // Assert that the user's status was updated
    const updatedStudent = students[0];
    expect(updatedStudent.status).toBe(message.status);
  });

  it("should duplicate user with different event_id when receiving same user with same status and different event_id", () => {
    // Render the hook
    const { result } = renderHook(() => useIncomingMessage());

    // Add a user to the students list with event_id '123'
    act(() => {
      result.current.handleIncomingMessage(
        {
          status: "checkedIn",
          "user-id": "123",
          event_id: "123",
          name: "Foo",
        },
        true
      );
    });

    // Simulate an incoming message with same status but different event_id '456'
    const message = {
      status: "checkedIn",
      "user-id": "123",
      event_id: "456",
      name: "Foo",
    };
    act(() => {
      result.current.handleIncomingMessage(message, true);
    });

    // Get the updated students array
    const { students } = result.current;

    // Assert that the user is present twice in the students list with different event_ids
    expect(students?.length).toBe(2);
    expect(students[0].event_id).toBe("123");
    expect(students[1].event_id).toBe("456");
  });
});
