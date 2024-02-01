import "./Timer.css";

const nextClass = "Kickboxing Kids";
const startTime = "23:55";


const Timer = () => {
  return (
    <div className="timer-container">
      <p>
        <strong>{nextClass}</strong>
      </p>
      <p>starts in {startTime}</p>
    </div>
  );
};

export default Timer;
