// Utill function for getting and setting data in Local storage.

export const getLocalStorageItem = (key = "user") => {
  return JSON.parse(localStorage.getItem(key));
};

export const setLocalStorageItem = (data, key = "user") => {
  return localStorage.setItem(key, JSON.stringify(data));
};

export const removeLocalStorageData = (key = "user") => {
  return localStorage.removeItem(key);
};
