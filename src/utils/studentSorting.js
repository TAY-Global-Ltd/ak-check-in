export function sortStudentsByCheckInStatus(students) {
  const checkedInStudents = students.filter((student) => student.event_id === 'event-1');
  const notCheckedInStudents = students.filter((student) => student.event_id !== 'event-1');

  const sortedStudents = notCheckedInStudents.concat(checkedInStudents);

  return sortedStudents;
}
