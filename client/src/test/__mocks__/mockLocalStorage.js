export const setLocalStorage = (id, data) => {
  window.localStorage.setItem(id, JSON.stringify(data));
};
