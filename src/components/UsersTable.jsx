import "./UsersTable.css";
import { students50 } from "../__mocks__/users";

const isCheckedIn = true;

const students = [
  "SapphireOwl",
  "InfiniteBadger",
  "LunarLynx",
  "VividPanda",
  "ZephyrRaccoon",
  "AuroraBear",
  "PixelatedGazelle",
  "QuasarKoala",
  "GalacticFox88",
  "CelestialHawk",
  "MagneticPenguin",
];

const student = [
  "SapphireOwl",
  "Sapphire",
];

const UsersTable = () => {
  return (
    <div className="wrapper">
      {students50.map((user) => {
        return (
          <div
            className={`users-table ${isCheckedIn ? "checked" : "unChecked"}`}
          >
            <p>✅</p> <p>{user} </p> <p></p>
          </div>
        );
      })}
    </div>
  );
};

export default UsersTable;
