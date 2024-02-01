import "./UsersTable.css";
import { useCheckInContext } from "../context/CheckInContext";
import { sortStudentsByCheckInStatus } from "../utils/studentSorting";
import { students } from "../__mocks__/students";



const UsersTable = () => {
  const { checkInData } = useCheckInContext();
  const sortedStudents = sortStudentsByCheckInStatus(checkInData.attendees);

  return (
    <div className="wrapper">
      {sortedStudents.map((student, index) => {
        const isStudentCheckedIn = student.event_id === "event-1";
        const style = `${student.icon_type}-symbols-outlined`;
        return (
          <div
            key={index}
            className={`users-table ${
              isStudentCheckedIn ? "checked" : "unChecked"
            }`}
          >
            <span
              className={style}
              style={isStudentCheckedIn ? { color: "green" } : {}}
            >
              {student.icon}
            </span>
            <p>{student.name}</p>
            <p>{student.reward}</p>
          </div>
        );
      })}
    </div>
  );
};

export default UsersTable;
