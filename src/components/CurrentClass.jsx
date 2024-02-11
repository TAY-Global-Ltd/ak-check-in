import "./CurrentClass.css";
import { useCheckInContext } from "../context/CheckInContext";
import { filterStudentsByClass } from "../utils/studentSorting";

const CurrentClass = () => {
  const { students, currentClassData } = useCheckInContext();
  const { title, description, icon, id } = currentClassData;
  const filteredStudents = filterStudentsByClass(students, id);

  return (
    <div className="current-class-container box">
      <div className="title-container">
        <img src={icon} className="current-icon" alt="current class icon" />
        <h1 className="title">{title}</h1>
      </div>
      <p>{description}</p>
      <p>
        Signed up: <strong>{filteredStudents.length}</strong> / Checked in:{" "}
        <strong>{filteredStudents.length}</strong>
      </p>
    </div>
  );
};

export default CurrentClass;
