export function filterStudentsByClass(students, id) {
  return students.filter((student) => student.event_id === id);
}

export function checkStudentsStatus(students) {
  let checkedInCount = 0;
  let signedUpCount = 0;
  let cancelledCount = 0;

  students.forEach((student) => {
    if (student.status === "checkedin") {
      checkedInCount++;
    } else if (student.status === "signedup") {
      signedUpCount++;
    } else if (student.status === "cancelled") {
      cancelledCount++;
    }
  });

  return {
    checkedIn: checkedInCount,
    signedUp: signedUpCount,
    cancelled: cancelledCount,
  };
}
