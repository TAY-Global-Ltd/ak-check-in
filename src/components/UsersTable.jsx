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
            <div className="name-wrapper">
              <p className="reward">{student.reward}</p>
              <p className="name">{student.name}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default UsersTable;
