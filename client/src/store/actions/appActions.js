import actionsTypes from "./actionTypes";

export const setAppVersion = (payload) => {
  return {
    type: actionsTypes.app.SET_APP_VERSION,
    payload,
  };
};

export const setSidebarState = (payload) => {
  return {
    type: actionsTypes.app.SIDEBAR_STATE,
    payload,
  };
};

export const setPreviewState = (payload) => {
  return {
    type: actionsTypes.app.PREVIEW_STATE,
    payload,
  };
};

export const setSessionExpiry = (payload) => {
  return {
    type: actionsTypes.app.IS_SESSION_EXPIRED,
    payload,
  };
};

export const setUserDataAction = (payload) => {
  return {
    type: actionsTypes.app.SET_USER_DATA,
    payload,
  };
};

export const setActiveView = (payload) => {
  return {
    type: actionsTypes.app.SET_ACTIVE_VIEW,
    payload,
  };
};

export const setUserConfig = (payload) => {
  return {
    type: actionsTypes.app.SET_USER_CONFIG,
    payload,
  };
};

export const setJobHelpInfo = (payload) => {
  return {
    type: actionsTypes.app.SET_JOB_HELP_INFO,
    payload,
  };
};

export const setSelectedExtensions = (payload) => {
  return {
    type: actionsTypes.app.SET_SELECTED_EXTENSIONS,
    payload,
  };
};

export const setEditorSuggestions = (payload) => {
  return {
    type: actionsTypes.app.SET_EDITOR_SUGGESTIONS,
    payload,
  };
};
