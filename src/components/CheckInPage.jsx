import UsersTable from "./UsersTable";
import NextClass from "./NextClass";
import Clock from "./Clock";
import Modal from "./Modal";
import CurrentClass from "./CurrentClass";

const CheckInPage = () => {
  return (
    <div className="App">
      <header className="App-header">
        <NextClass />
        <CurrentClass />
        <div className="clock-wrapper">
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
