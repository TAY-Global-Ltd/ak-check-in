import "./NextClass.css";
import { useCheckInContext } from "../../context/CheckInContext";
import {
  filterStudentsByClass,
  checkStudentsStatus,
} from "../../utils/studentSorting";
import Clock from "../Clock";

const NextClass = () => {
  const { nextClassData, students, lightMode } = useCheckInContext();

  const {
    start_time = "00:00",
    title = "No Next Class",
    id,
    icon,
  } = nextClassData || {};
  const currentClassStudents = filterStudentsByClass(students, id);
  const { totalCount } = checkStudentsStatus(currentClassStudents);

  return (
    <div className="next-class-container">
      <div className="clock-container">
        <Clock />
      </div>
      <div
        className={`next-class box ${
          lightMode
            ? "light-bg-primary light-box-shadow"
            : "dark-bg-primary dark-box-shadow"
        }`}
      >
        <img
          src={icon}
          style={{ width: "30px", marginTop: "6px" }}
          alt="next class icon"
        />
        <h4 style={{ margin: "0" }}>{title}</h4>
        <h6 style={{ margin: "6px 0 0 0" }}>
          Next Class
          <br />
          starts at {start_time}
          <br />
          Signed up:{" "}
          <span style={{ color: "var(--main-color)" }}>{totalCount}</span>
        </h6>
      </div>
    </div>
  );
};

export default NextClass;
