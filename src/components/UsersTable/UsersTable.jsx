import { useEffect, useState } from "react";
import "./UsersTable.css";
import { useCheckInContext } from "../../context/CheckInContext";
import {
  filterStudentsByClass,
  checkStudentsStatus,
} from "../../utils/studentSorting";
import Toggle from "../Toggle/Toggle";
import Loader from "../common/Loader/Loader";

const UsersTable = () => {
  const [studentsList, setStudentsList] = useState(null);
  const {
    students,
    currentClassData,
    lightMode,
    checkInIsLoading,
    currentClassIsLoading,
    nextClassIsLoading,
  } = useCheckInContext();

  useEffect(() => {
    if (students !== null) {
      setStudentsList(students);
    }
  }, [students]);

  if (
    studentsList === null ||
    checkInIsLoading ||
    currentClassIsLoading ||
    nextClassIsLoading
  ) {
    return <Loader />;
  }

  const currentClassStudents = filterStudentsByClass(
    studentsList,
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
            }`}
          >
            <span
              className={style}
              style={
                isStudentCheckedIn
                  ? { color: "green" }
                  : { color: "var(--main-color)" }
              }
            >
              {student.icon}
            </span>
            <div className="name-wrapper">
              <p className="reward">{student.reward}</p>
              <p className="name">{student.name}</p>
              {student?.parent_name && (
                <p style={{ fontSize: "0.6em" }}>( {student?.parent_name} )</p>
              )}
            </div>
          </div>
        );
      })}
      <div style={{ position: "fixed", bottom: "8px", left: "8px" }}>
        <p style={{ margin: "0", fontSize: "12px", color: "#605F5F" }}>
          App v: {process.env.REACT_APP_CHECKIN_VERSION}
        </p>
      </div>
      <Toggle />
    </div>
  );
};

export default UsersTable;
