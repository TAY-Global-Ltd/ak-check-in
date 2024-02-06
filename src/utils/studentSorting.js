export function filterStudentsByClass(students, id) {
  return students.filter((student) => student.event_id === id);
}

// TODO update once issue #25 is closed
export function countCheckedStatus(students) {
  let checkedCount = 0;
  let uncheckedCount = 0;

  students.forEach((student) => {
    if (student.status === "checkedIn") {
      checkedCount++;
    } else if (student.status === "signedUp") {
      uncheckedCount++;
    }
  });

  return {
    checkedIn: checkedCount,
    signedUp: uncheckedCount,
  };
}
