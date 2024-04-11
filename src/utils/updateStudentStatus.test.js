import updateStudentStatus from "./studentSorting";

// Test case for updateStudentStatus function
describe("updateStudentStatus", () => {
  test("should update checkInStudents array and signUpStudents array correctly", () => {
    // Sample input arrays
    const checkInStudents = [
      { "user-id": 1, name: "John" },
      { "user-id": 2, name: "Jane" },
    ];
    const signUpStudents = [
      { "user-id": 1, name: "John" },
      { "user-id": 3, name: "Alice" },
    ];

    // Call the function
    const { updatedCheckInStudents, updatedSignUpStudents } =
      updateStudentStatus(checkInStudents, signUpStudents);

    // Assert the results
    expect(updatedCheckInStudents).toEqual([
      { "user-id": 1, name: "John", isSigned: true },
      { "user-id": 2, name: "Jane", isSigned: undefined },
    ]);
    expect(updatedSignUpStudents).toEqual([{ "user-id": 3, name: "Alice" }]);
  });
});
