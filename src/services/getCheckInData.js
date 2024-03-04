import CryptoJS from "crypto-js";
import { key } from '../utils/encrypt'

const baseUrl = process.env.REACT_APP_CHECKIN_API_SERVER_URL;

const responseHandler = async (url) => {
  const localStoreToken = localStorage.getItem('authorization_token');
  // Decrypt the string using AES decryption
  const bytes = CryptoJS.AES.decrypt(localStoreToken, key, { mode: CryptoJS.mode.ECB });
  // Convert the decrypted bytes to a UTF-8 string
  const decryptedToken = bytes.toString(CryptoJS.enc.Utf8);

  const res = await fetch(`${baseUrl}${url}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${decryptedToken}`,
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
