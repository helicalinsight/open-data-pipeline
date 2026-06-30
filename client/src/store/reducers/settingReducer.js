import { message } from "antd";
import actionsTypes from "../actions/actionTypes";

const initialState = {
  allPreferences: {},
  messageData: null,
  hideMessage: false,
  apiKeys: [],
};

const { SET_PREFERENCES, SET_MESSAGE, SET_HIDE_MESSAGE, SET_API_KEYS } =
  actionsTypes.preferences;

function settingReducer(state = initialState, action) {
  switch (action.type) {
    case SET_PREFERENCES: {
      return {
        ...state,
        allPreferences: action.payload,
      };
    }
    case SET_MESSAGE: {
      return {
        ...state,
        messageData: action.payload,
      };
    }
    case SET_HIDE_MESSAGE: {
      return {
        ...state,
        hideMessage: action.payload,
      };
    }
    case SET_API_KEYS:
      return { ...state, apiKeys: action.payload };
    case "RESET_STATE":
      return initialState;
    default: {
      return { ...state };
    }
  }
}

export default settingReducer;
