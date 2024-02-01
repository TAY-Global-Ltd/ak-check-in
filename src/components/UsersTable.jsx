import "./UsersTable.css";
import { sortStudentsByCheckInStatus } from "../utils/studentSorting";
import { students } from "../__mocks__/students";

const sortedStudents = sortStudentsByCheckInStatus(students);

const UsersTable = () => {
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
