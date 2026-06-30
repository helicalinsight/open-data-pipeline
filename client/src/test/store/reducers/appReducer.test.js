import actionsTypes from "../../../store/actions/actionTypes";
import { appReducer } from "../../../store/reducers";

const {
  SET_APP_VERSION,
  SIDEBAR_STATE,
  PREVIEW_STATE,
  IS_SESSION_EXPIRED,
  SET_USER_DATA,
  SET_ACTIVE_VIEW,
  SET_USER_CONFIG,
  SET_SELECTED_EXTENSIONS,
  SET_EDITOR_SUGGESTIONS,
  SET_JOB_HELP_INFO,
} = actionsTypes.app;

describe("appReducer", () => {
  const initialState = {
    version: "",
    isSidebarCollapsed: false,
    previewState: false,
    isSessionExpired: false,
    user: {},
    activeViewState: "job-listing-view",
    userConfig: {},
    selectedExtensions: [],
    jobHelpInfo: {
      python: "",
      yaml: "",
    },
    editorSuggestions: {
      python: [],
      yaml: [],
    },
  };

  it("should return the initial state", () => {
    expect(appReducer(undefined, {})).toEqual(initialState);
  });

  it("should handle SET_APP_VERSION", () => {
    const action = { type: SET_APP_VERSION, payload: "1.0.0" };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      version: "1.0.0",
    });
  });

  it("should handle SET_USER_CONFIG", () => {
    const userConfig = { theme: "dark" };
    const action = { type: SET_USER_CONFIG, payload: userConfig };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      userConfig,
    });
  });

  it("should handle SIDEBAR_STATE", () => {
    const action = { type: SIDEBAR_STATE, payload: true };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      isSidebarCollapsed: true,
    });
  });

  it("should handle PREVIEW_STATE", () => {
    const action = { type: PREVIEW_STATE, payload: true };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      previewState: true,
    });
  });

  it("should handle IS_SESSION_EXPIRED", () => {
    const action = { type: IS_SESSION_EXPIRED, payload: true };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      isSessionExpired: true,
    });
  });

  it("should handle SET_USER_DATA", () => {
    const userData = { name: "John Doe", email: "john@example.com" };
    const action = { type: SET_USER_DATA, payload: userData };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      user: userData,
    });
  });

  it("should handle SET_SELECTED_EXTENSIONS - add extension", () => {
    const action = {
      type: SET_SELECTED_EXTENSIONS,
      payload: { value: "js", isSelected: true },
    };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      selectedExtensions: ["js"],
    });
  });

  it("should handle SET_SELECTED_EXTENSIONS - remove extension", () => {
    const state = { ...initialState, selectedExtensions: ["js", "py"] };
    const action = {
      type: SET_SELECTED_EXTENSIONS,
      payload: { value: "js", isSelected: false },
    };
    expect(appReducer(state, action)).toEqual({
      ...state,
      selectedExtensions: ["py"],
    });
  });

  it("should handle SET_ACTIVE_VIEW", () => {
    const action = { type: SET_ACTIVE_VIEW, payload: "settings-view" };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      activeViewState: "settings-view",
    });
  });

  it("should handle SET_JOB_HELP_INFO", () => {
    const jobHelpInfo = { python: "# Python help", yaml: "# YAML help" };
    const action = { type: SET_JOB_HELP_INFO, payload: jobHelpInfo };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      jobHelpInfo,
    });
  });

  it("should handle SET_EDITOR_SUGGESTIONS", () => {
    const editorSuggestions = {
      python: ["suggestion1"],
      yaml: ["suggestion2"],
    };
    const action = { type: SET_EDITOR_SUGGESTIONS, payload: editorSuggestions };
    expect(appReducer(initialState, action)).toEqual({
      ...initialState,
      editorSuggestions,
    });
  });

  it("should handle RESET_STATE", () => {
    const state = {
      ...initialState,
      version: "1.0.0",
      isSidebarCollapsed: true,
    };
    const action = { type: "RESET_STATE" };
    expect(appReducer(state, action)).toEqual(initialState);
  });

  it("should return current state for unknown action type", () => {
    const state = { ...initialState, version: "1.0.0" };
    const action = { type: "UNKNOWN_ACTION" };
    expect(appReducer(state, action)).toEqual(state);
  });
});
