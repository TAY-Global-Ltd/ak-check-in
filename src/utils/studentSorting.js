export function sortStudentsByCheckInStatus(students) {
  const checkedInStudents = students.filter((student) => student.event_id === 'event-1');
  const notCheckedInStudents = students.filter((student) => student.event_id !== 'event-1');

  const sortedStudents = notCheckedInStudents.concat(checkedInStudents);

  return sortedStudents;
}

export function countCheckedInStudents(students) {
  const counts = students.reduce((accumulator, student) => {
    if (student.event_id === 'event-1') {
      accumulator.checkedIn += 1;
    }

    accumulator.signedUp += 1;

    return accumulator;
  }, { checkedIn: 0, signedUp: 0 });

  const { checkedIn, signedUp } = counts;
  return { checkedIn, signedUp };
}
