import CryptoJS from "crypto-js";

export const key = CryptoJS.enc.Utf8.parse("1234567890123456"); // (16 bytes key)
export const encryptKey = (string) => {
  return CryptoJS.AES.encrypt(string, key, {
    mode: CryptoJS.mode.ECB,
  }).toString();
};
