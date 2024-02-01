import "./App.css";
import UsersTable from "./components/UsersTable";
import Timer from "./components/Timer";
import Clock from "./components/Clock";
import { students } from "./__mocks__/students";
import { countCheckedInStudents } from "./utils/studentSorting";

const currentClass = "🤼‍♂️  BJJ with Jack";
const { checkedIn, signedUp } = countCheckedInStudents(students);

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <Timer />
        <div>
          <h3 className="m-12">{currentClass}</h3>
          <p>
            Signed up: <strong>{signedUp}</strong> / Checked in:{" "}
            <strong>{checkedIn}</strong>
          </p>
        </div>
        <div className="logo-container">
          <img src="ak-logo.png" className="logo" alt="ak-logo" />
          <Clock />
        </div>
      </header>
      <main>
        <UsersTable />
      </main>
    </div>
  );
};

export default App;
