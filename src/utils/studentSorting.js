export function filterStudentsByClass(students, id) {
  if (!students || !id) return [];
  return students.filter((student) => student.event_id === id);
}

export function updateStudentStatus(checkInStudents, signUpStudents) {
  checkInStudents.forEach((checkInStudent) => {
    // Find the corresponding student in the signUpStudents array by ID
    const signedUpStudent = signUpStudents.find(
      (student) => student["user-id"] === checkInStudent["user-id"]
    );

    // If the student exists in both arrays
    if (signedUpStudent) {
      // Remove the student from the signUpStudents array
      const index = signUpStudents.indexOf(signedUpStudent);
      signUpStudents.splice(index, 1);

      // Add the isSigned property to the student object in the checkInStudents array
      checkInStudent.isSigned = true;
    }
  });

  // Return the updated checkInStudents array and the modified signUpStudents array
  return { checkInStudents, signUpStudents };
}

export function checkStudentsStatus(students) {
  if (!students)
    return {
      checkedIn: [],
      signedUp: [],
      cancelled: [],
      totalCount: 0,
      attendees: [],
    };

  let checkedInStudents = [];
  let signedUpStudents = [];
  let cancelledStudents = [];

  students.forEach((student) => {
    if (student.status === "checkedin") {
      checkedInStudents.push(student);
    } else if (student.status === "signedup") {
      signedUpStudents.push(student);
    } else if (student.status === "cancelled") {
      cancelledStudents.push(student);
    }
  });

  const { checkInStudents, signUpStudents } = updateStudentStatus(
    checkedInStudents,
    signedUpStudents
  );

  const totalCount = checkInStudents.length + signUpStudents.length;
  const attendees = [...checkInStudents, ...signUpStudents];

  return {
    checkedIn: checkInStudents,
    signedUp: signUpStudents,
    cancelled: cancelledStudents,
    totalCount,
    attendees,
  };
}
