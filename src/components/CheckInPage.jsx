import { useCheckInContext } from "../context/CheckInContext";
import UsersTable from "./UsersTable";
import Timer from "./Timer";
import Clock from "./Clock";
import { countCheckedInStudents } from "../utils/studentSorting";

const currentClass = "🤼‍♂️  BJJ with Jack";

const CheckInPage = () => {
  const { checkInData } = useCheckInContext();

  const { checkedIn, signedUp } = countCheckedInStudents(checkInData.attendees);

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
          <img src="logo192.png" className="logo" alt="ak-logo" />
          <Clock />
        </div>
      </header>
      <main>
        <UsersTable />
      </main>
    </div>
  );
};

export default CheckInPage;
