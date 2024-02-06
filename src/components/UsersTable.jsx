import "./UsersTable.css";
import { useCheckInContext } from "../context/CheckInContext";
import { filterStudentsByClass } from "../utils/studentSorting";

const UsersTable = () => {
  const { students, currentClassData } = useCheckInContext();
  const filteredStudents = filterStudentsByClass(students, currentClassData.id);

  return (
    <div className="wrapper">
      {filteredStudents.map((student, index) => {
        const isStudentCheckedIn = student.event_id === currentClassData.id;
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
