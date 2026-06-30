import actionsTypes from "./actionTypes";

export const setPreferencesAction = (payload) => {
  return {
    type: actionsTypes.preferences.SET_PREFERENCES,
    payload,
  };
};
export const setMessageAction = (payload) => {
  return {
    type: actionsTypes.preferences.SET_MESSAGE,
    payload,
  };
};
export const setHideMessageAction = (payload) => {
  return {
    type: actionsTypes.preferences.SET_HIDE_MESSAGE,
    payload,
  };
};
export const setApiKeys = (payload) => ({
  type: actionsTypes.preferences.SET_API_KEYS,
  payload,
});
