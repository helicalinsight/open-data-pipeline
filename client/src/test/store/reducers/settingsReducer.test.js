import actionsTypes from "../../../store/actions/actionTypes";
import { settingReducer } from "../../../store/reducers";

const { SET_PREFERENCES,SET_MESSAGE ,SET_HIDE_MESSAGE} = actionsTypes.preferences;

describe("settingReducer", () => {
  const initialState = {
    allPreferences: {},
    messageData: null,
    hideMessage: false,
    apiKeys: [],
  };

  it("should return the initial state", () => {
    expect(settingReducer(undefined, {})).toEqual(initialState);
  });

  it("should handle SET_PREFERENCES", () => {
    const preferences = { theme: "dark", fontSize: "large" };
    const action = {
      type: SET_PREFERENCES,
      payload: preferences,
    };
    const expectedState = {
      ...initialState,
      allPreferences: preferences,
    };
    expect(settingReducer(initialState, action)).toEqual(expectedState);
  });

  it("should handle RESET_STATE", () => {
    const currentState = {
      allPreferences: { theme: "dark", fontSize: "large" },
      messageData: "Some message",
      hideMessage: true
    };
    const action = { type: "RESET_STATE" };
    expect(settingReducer(currentState, action)).toEqual(initialState);
  });

  it("should return the current state for unknown action types", () => {
    const currentState = {
      allPreferences: { theme: "light" },
      messageData: "Another message",
      hideMessage: true
    };
    const action = { type: "UNKNOWN_ACTION" };
    expect(settingReducer(currentState, action)).toEqual(currentState);
  });
  it("should handle SET_MESSAGE", () => {
    const message = "Preferences updated successfully";
    const action = {
      type: SET_MESSAGE,
      payload: message,
    };
    const expectedState = {
      ...initialState,
      messageData: message,
    };
    expect(settingReducer(initialState, action)).toEqual(expectedState);
  });
  it("should handle SET_API_KEYS", () => {
    const apiKeys = ["key1", "key2", "key3"];
    const action = {
      type: actionsTypes.preferences.SET_API_KEYS,
      payload: apiKeys,
    };
    const expectedState = {
      ...initialState,
      apiKeys,
    };
    expect(settingReducer(initialState, action)).toEqual(expectedState);
  });
});
