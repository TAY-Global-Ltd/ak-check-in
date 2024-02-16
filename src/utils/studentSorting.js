export function filterStudentsByClass(students, id) {
  if (students) {
    return students.filter((student) => student.event_id === id);
  }
}

export function checkStudentsStatus(students) {
  let checkedInStudents = [];
  let signedUpStudents = [];
  let cancelledStudents = [];

  students?.forEach((student) => {
    if (student.status === "checkedin") {
      checkedInStudents.push(student);
    } else if (student.status === "signedup") {
      signedUpStudents.push(student);
    } else if (student.status === "cancelled") {
      cancelledStudents.push(student);
    }
  });

  const totalCount = checkedInStudents.length + signedUpStudents.length;
  const attendees = [...signedUpStudents, ...checkedInStudents];

  return {
    checkedIn: checkedInStudents,
    signedUp: signedUpStudents,
    cancelled: cancelledStudents,
    totalCount,
    attendees,
  };
}
