import CryptoJS from "crypto-js";

export const hashString = (key) => {
  return Promise.resolve(CryptoJS.SHA256(key).toString(CryptoJS.enc.Hex));
};
