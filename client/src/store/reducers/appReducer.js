import actionsTypes from "../actions/actionTypes";

const intialState = {
  version: "",
  isSidebarCollapsed: false,
  previewState: JSON?.parse(localStorage?.getItem("previewState")) ?? false,
  isSessionExpired: false,
  user: {},
  activeViewState: "job-listing-view",
  userConfig: {},
  selectedExtensions: [],
  jobHelpInfo: {
    python: "",
    yaml: "",
  }, // expecting mardown from backend
  editorSuggestions: {
    python: [],
    yaml: [],
  },
};

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

function appReducer(state = intialState, action) {
  switch (action.type) {
    case SET_APP_VERSION: {
      return {
        ...state,
        version: action.payload,
      };
    }
    case SET_USER_CONFIG: {
      return {
        ...state,
        userConfig: action.payload,
      };
    }
    case SIDEBAR_STATE: {
      return {
        ...state,
        isSidebarCollapsed: action.payload,
      };
    }
    case PREVIEW_STATE: {
      localStorage.setItem("previewState", JSON.stringify(action.payload));
      return {
        ...state,
        previewState: action.payload,
      };
    }

    case IS_SESSION_EXPIRED: {
      return {
        ...state,
        isSessionExpired: action.payload,
      };
    }
    case SET_USER_DATA: {
      return {
        ...state,
        user: { ...action.payload },
      };
    }
    case SET_SELECTED_EXTENSIONS: {
      const { value, isSelected } = action.payload;
      let extensions = [...state.selectedExtensions];
      if (isSelected && !extensions.includes(value)) {
        extensions.push(value);
      } else {
        extensions = extensions.filter((eachValue) => eachValue !== value);
      }
      return {
        ...state,
        selectedExtensions: extensions,
      };
    }
    case SET_ACTIVE_VIEW: {
      return {
        ...state,
        activeViewState: action.payload,
      };
    }
    case SET_JOB_HELP_INFO: {
      return {
        ...state,
        jobHelpInfo: action.payload,
      };
    }
    case SET_EDITOR_SUGGESTIONS: {
      return {
        ...state,
        editorSuggestions: action.payload,
      };
    }
    case "RESET_STATE":
      return intialState;
    default: {
      return { ...state };
    }
  }
}

export default appReducer;
