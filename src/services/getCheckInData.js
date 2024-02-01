export const getCheckInData = async () => {
  const res = await fetch("http://127.0.0.1:8765/initial_state");
  const checkInData = await res.json();
  return checkInData;
};
