import { useCheckInContext } from "../context/CheckInContext";
import UsersTable from "./UsersTable";
import NextClass from "./NextClass";
import Clock from "./Clock";
import Modal from "./Modal";
import { filterStudentsByClass } from "../utils/studentSorting";

const currentClass = "🤼‍♂️  BJJ with Jack";

const CheckInPage = () => {
  const { students, currentClassData } = useCheckInContext();
  const { title, description, icon, icon_type, id } = currentClassData;
  const filteredStudents = filterStudentsByClass(students, id);

  const style = `${icon_type}-symbols-outlined`;

  return (
    <div className="App">
      <header className="App-header">
        <NextClass />
        <div>
          <h3 className="m-12">
            <span className={style}>{icon}</span> {title}
          </h3>
          <p>{description}</p>
          <p>
            Signed up: <strong>{filteredStudents.length}</strong> / Checked in:{" "}
            <strong>{filteredStudents.length}</strong>
          </p>
        </div>
        <div className="logo-container">
          <img src="logo192.png" className="logo" alt="ak-logo" />
          <Clock />
        </div>
      </header>
      <main>
        <Modal />
        <UsersTable />
      </main>
    </div>
  );
};

export default CheckInPage;
