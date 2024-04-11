import { updateStudentStatus } from "./studentSorting";

// Test case for updateStudentStatus function
describe("updateStudentStatus", () => {
  test("should update checkInStudents array and signUpStudents array correctly", () => {
    // Sample input arrays
    const checkedInStudents = [
      { "user-id": 1, name: "John" },
      { "user-id": 2, name: "Jane" },
    ];
    const signedUpStudents = [
      { "user-id": 1, name: "John" },
      { "user-id": 3, name: "Alice" },
    ];

    // Call the function
    const { checkInStudents, signUpStudents } = updateStudentStatus(
      checkedInStudents,
      signedUpStudents
    );

    // Assert the results
    expect(checkInStudents).toEqual([
      { "user-id": 1, name: "John", isSigned: true },
      { "user-id": 2, name: "Jane", isSigned: undefined },
    ]);
    expect(signUpStudents).toEqual([{ "user-id": 3, name: "Alice" }]);
  });
});
