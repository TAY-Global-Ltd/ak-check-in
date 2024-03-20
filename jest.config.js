module.exports = {
  testMatch: ["**/*.test.js", "**/*.test.jsx"],
  transform: {
    "^.+\\.jsx?$": "babel-jest",
  },
  testEnvironment: "jsdom",
};
