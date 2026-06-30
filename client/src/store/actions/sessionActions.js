import actionsTypes from "./actionTypes";

export const resetRedux = () => {
  return {
    type: actionsTypes.sessions.RESET_STATE,
  };
};
