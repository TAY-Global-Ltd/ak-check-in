import "./UsersTable.css";
import { useCheckInContext } from "../context/CheckInContext";
import {
  filterStudentsByClass,
  checkStudentsStatus,
} from "../utils/studentSorting";
import Toggle from "./Toggle";

const UsersTable = () => {
  const { students, currentClassData, lightMode } = useCheckInContext();
  const currentClassStudents = filterStudentsByClass(
    students,
    currentClassData?.id
  );
  const { attendees } = checkStudentsStatus(currentClassStudents);

  return (
    <div className="wrapper">
      {attendees.map((student, index) => {
        const isStudentCheckedIn = student.status === "checkedin";
        const style = `${student.icon_type}-symbols-outlined`;
        return (
          <div
            key={index}
            className={`users-table ${
              isStudentCheckedIn ? "checked" : "unChecked"
            } ${
              lightMode
                ? "light-bg-secondary light-box-shadow"
                : "dark-bg-secondary dark-box-shadow"
            }
            `}
          >
            <span
              className={style}
              style={isStudentCheckedIn ? { color: "green" } : {}}
            >
              {student.icon}
            </span>
            <div className="name-wrapper">
              <p className="reward">{student.reward}</p>
              <p className="name">{student.name}</p>
            </div>
          </div>
        );
      })}
      <Toggle />
    </div>
  );
};

export default UsersTable;
