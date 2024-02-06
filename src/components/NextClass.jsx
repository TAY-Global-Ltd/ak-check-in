import "./NextClass.css";
import { useCheckInContext } from "../context/CheckInContext";
import { filterStudentsByClass } from "../utils/studentSorting";
import Clock from "./Clock";

const NextClass = () => {
  const { nextClassData, students } = useCheckInContext();
  const { description, icon, icon_type, start_time, title, id } = nextClassData;
  const style = `${icon_type}-symbols-outlined`;
  const filteredStudents = filterStudentsByClass(students, id);

  return (
    <div className="next-class-container">
      <div className="clock-container">
        <Clock />
      </div>
      <div className="next-class box">
        <p>
          <strong>
            {/* <span className={style}>{icon}</span>  */}
            🇹🇭 {title}
          </strong>
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
