const baseUrl = process.env.REACT_APP_CHECKIN_API_SERVER_URL;
// const authToken = process.env.AUTHORIZATION_TOKEN;

const responseHandler = async (url) => {
  const authToken = localStorage.getItem('authorization_token');
  console.log('~~~ responseHandler authToken', authToken)

  const res = await fetch(`${baseUrl}${url}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  });
  if (res.status === 200) {
    const data = await res.json();
    return data;
  }
  throw new Error(res.statusText);
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
