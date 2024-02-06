import "./CurrentClass.css";
import { useCheckInContext } from "../context/CheckInContext";
import { filterStudentsByClass } from "../utils/studentSorting";

const CurrentClass = () => {
    const { students, currentClassData } = useCheckInContext();
    const { title, description, icon, icon_type, id } = currentClassData;
    const filteredStudents = filterStudentsByClass(students, id);
  
    const style = `${icon_type}-symbols-outlined`;

  return (
    <div className="current-class-container box">
      <h1 className="title">
        {/* <span className={style}>{icon}</span> */}
        🥋 {title}
      </h1>
      <p>{description}</p>
      <p>
        Signed up: <strong>{filteredStudents.length}</strong> / Checked in:{" "}
        <strong>{filteredStudents.length}</strong>
      </p>
    </div>
  );
};

export default CurrentClass;
