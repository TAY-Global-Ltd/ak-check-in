import "./CurrentClass.css";
import { useCheckInContext } from "../../context/CheckInContext";
import {
  filterStudentsByClass,
  checkStudentsStatus,
} from "../../utils/studentSorting";

const CurrentClass = () => {
  const { students, currentClassData } = useCheckInContext();

  const {
    title = "Classes unavailable",
    description,
    icon,
    id,
    start_time,
    end_time,
  } = currentClassData || {};
  const currentClassStudents = filterStudentsByClass(students, id);
  const { totalCount, checkedIn } = checkStudentsStatus(currentClassStudents);

  return (
    <div className="current-class-container box">
      <div className="title-container">
        <img
          src={icon}
          className={icon ? "current-icon" : "hide"}
          alt="current class icon"
        />
        <h1 className="title">{title}</h1>
      </div>
      <h4 style={{margin: "0"}} >{description}</h4>
      <h4>
        Signed up: <strong>{totalCount}</strong> / Checked in:{" "}
        <strong>{checkedIn.length}</strong>
        <br />
        {start_time}-{end_time}
      </h4>
    </div>
  );
};

export default CurrentClass;
