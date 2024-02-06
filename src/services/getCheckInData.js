import { baseUrl } from "../constants/constants";

const responseHandler = async (url) => {
  const res = await fetch(`${baseUrl}${url}`);
  if (res.status === 200) {
    const data = await res.json();
    return data;
  }
  throw new Error(
    `Error [${res.status}][${res.url}]: ${res.body?.errors
      ?.map(({ message }) => message)
      ?.join("")}`
  );
};

export const getCheckInData = async () => {
  const checkInData = responseHandler("initial_state").then((data) => data);
  return checkInData;
};

export const getCurrentClassData = async () => {
  const currentClassData = responseHandler("current_event").then(
    (data) => data
  );
  return currentClassData;
};

export const getNextClassData = async () => {
  const nextClassData = responseHandler("next_event").then((data) => data);
  return nextClassData;
};
