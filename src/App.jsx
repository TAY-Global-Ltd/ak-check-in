import "./App.css";
import UsersTable from "./components/UsersTable";
import Timer from "./components/Timer";

const currentClass = "BJJ";

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <img src="ak-logo.png" className="logo" alt="logo" />
        <h3>🤼‍♂️ {currentClass}</h3>
      </header>

      <UsersTable />
      <footer className="footer">
        <Timer />
      </footer>
    </div>
  );
};

export default App;
