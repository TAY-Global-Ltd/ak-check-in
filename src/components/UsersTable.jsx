import "./UsersTable.css";
import { students40 } from "../__mocks__/users";

const isCheckedIn = true;

// const students = [
//   "SapphireOwl",
//   "InfiniteBadger",
//   "LunarLynx",
//   "VividPanda",
//   "ZephyrRaccoon",
//   "AuroraBear",
//   "PixelatedGazelle",
//   "QuasarKoala",
//   "GalacticFox88",
//   "CelestialHawk",
//   "MagneticPenguin",
// ];

// const student = [
//   "SapphireOwl",
//   "Sapphire",
// ];

const UsersTable = () => {
  return (
    <div className="wrapper">
      {students40.map((user) => {
        return (
          <div
            className={`users-table ${isCheckedIn ? "checked" : "unChecked"}`}
          >
            <p>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="#abb1ac40"
              >
                <path d="M19 7.001c0 3.865-3.134 7-7 7s-7-3.135-7-7c0-3.867 3.134-7.001 7-7.001s7 3.134 7 7.001zm-1.598 7.18c-1.506 1.137-3.374 1.82-5.402 1.82-2.03 0-3.899-.685-5.407-1.822-4.072 1.793-6.593 7.376-6.593 9.821h24c0-2.423-2.6-8.006-6.598-9.819z" />
              </svg>
            </p>
            <p>{user}</p>
            <p>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill={isCheckedIn ? "green" : "#1d1d1d"}
              >
                <path d="M20.285 2l-11.285 11.567-5.286-5.011-3.714 3.716 9 8.728 15-15.285z" />
              </svg>
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default UsersTable;
