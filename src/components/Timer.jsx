import "./Timer.css";
import Clock from "./Clock";

const nextClass = "Kickboxing Kids";
const startTime = "23:55";
const checkedInCount = 12;
const signedUpCount = 50;

const Timer = () => {
  return (
    <div className="timer-container">
      <Clock/>
      <p>
        Signed up: {signedUpCount} / Checked in: {checkedInCount}
      </p>
      <h2 className="next-class">
        <strong>{nextClass} </strong>class starts in {startTime}
      </h2>
    </div>
  );
};

export default Timer;
