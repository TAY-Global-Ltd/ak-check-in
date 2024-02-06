import "./NextClass.css";
import { useCheckInContext } from "../context/CheckInContext";
import { filterStudentsByClass } from "../utils/studentSorting";

const NextClass = () => {
  const { nextClassData, students } = useCheckInContext();
  const { description, icon, icon_type, start_time, title, id } = nextClassData;
  const style = `${icon_type}-symbols-outlined`;
  const filteredStudents = filterStudentsByClass(students, id);

  return (
    <div className="next-class-container">
      <p>
        <strong>
          <span className={style}>{icon}</span> {title}
        </strong>
      </p>
      <p>Checked in: {filteredStudents.length}</p>
      <p>starts at {start_time}</p>
    </div>
  );
};

export default NextClass;
