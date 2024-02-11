import "./NextClass.css";
import { useCheckInContext } from "../context/CheckInContext";
import { filterStudentsByClass } from "../utils/studentSorting";
import Clock from "./Clock";

const NextClass = () => {
  const { nextClassData, students, lightMode } = useCheckInContext();
  const { start_time, title, id, icon } = nextClassData;
  const filteredStudents = filterStudentsByClass(students, id);

  return (
    <div className="next-class-container">
      <div className="clock-container">
        <Clock />
      </div>
      <div
        className={`next-class box ${
          lightMode ? "light-bg-primary" : "dark-bg-primary"
        } ${
          lightMode ? "light-box-shadow" : "dark-box-shadow"
        }`}
      >
        <img src={icon} style={{width: '30px'}} alt="next class icon" />
        <p style={{margin: '6px'}}>
          <strong>{title}</strong>
          <span> is next</span>
          <br />
          Checked in: {filteredStudents.length}
          <br />
          starts at {start_time}
        </p>
      </div>
    </div>
  );
};

export default NextClass;
