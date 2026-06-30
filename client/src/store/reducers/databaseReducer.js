import actionsTypes from "../actions/actionTypes";

const initialState = {
  datasources: [],
  selectedDatasource: {},
  savedConnections: [],
  savedConnApiStatus: "",
  editConnection: {},
  tableColumns: {},
  formData: {},
  connectionName: "",
  dataSourceName: "",
  isConnected: false,
  selectedConnection: null,
  testConnectionMessage: "",
};

const {
  SET_DATASOURCES,
  SET_SELECTED_DATASOURCE,
  SET_SAVED_CONNECTIONS,
  SET_EDIT_CONNECTION,
  DELETE_SAVED_CONNECTION,
  UPDATE_SAVED_CONNECTION,
  SET_SAVE_CONNECTION_API_STATUS,
  SET_TABLE_COLUMS,
  SET_FORM_DATA,
  CLEAR_FORM_DATA,
  SET_DS_CONNECTION_NAME,
  SET_DATASOURCE_NAMES,
  SET_CONNECTION_STATUS,
  SET_SELECTED_CONNECTION,
  SET_TESTCONNECTION_MSG,
} = actionsTypes.database;

function databaseReducer(state = initialState, action) {
  switch (action.type) {
    case SET_DATASOURCES: {
      return {
        ...state,
        datasources: [...action.payload],
      };
    }
    case SET_SELECTED_DATASOURCE: {
      return {
        ...state,
        selectedDatasource: action.payload,
      };
    }
    case SET_SAVED_CONNECTIONS: {
      const { key, data } = action.payload;
      return {
        ...state,
        savedConnections:
          key === "insert" ? [...state.savedConnections, ...data] : data,
      };
    }
    case SET_SAVE_CONNECTION_API_STATUS: {
      return {
        ...state,
        savedConnApiStatus: action.payload,
      };
    }
    case SET_DS_CONNECTION_NAME: {
      return {
        ...state,
        connectionName: action.payload,
      };
    }
    case SET_DATASOURCE_NAMES: {
      return {
        ...state,
        dataSourceName: action.payload,
      };
    }
    case SET_CONNECTION_STATUS:
      return {
        ...state,
        isConnected: action.payload,
      };
    case SET_SELECTED_CONNECTION:
      return {
        ...state,
        selectedConnection: action.payload,
      };
    case SET_TESTCONNECTION_MSG:
      return {
        ...state,
        testConnectionMessage: action.payload,
      };
    case SET_EDIT_CONNECTION: {
      return {
        ...state,
        editConnection: action.payload,
      };
    }
    case DELETE_SAVED_CONNECTION: {
      return {
        ...state,
        savedConnections: state.savedConnections.filter(
          (item) => !action.payload.includes(item._id)
        ),
      };
    }
    case SET_FORM_DATA:
      return {
        ...state,
        formData: { ...state.formData, ...action.payload },
      };

    case CLEAR_FORM_DATA:
      return {
        ...state,
        formData: {},
      };
    case UPDATE_SAVED_CONNECTION: {
      const { connection_id, connection_alias } = action.payload;
      let updatedConnections = state.savedConnections.map((connection) =>
        connection._id === connection_id
          ? { ...connection, alias: connection_alias }
          : connection
      );

      return {
        ...state,
        savedConnections: updatedConnections,
      };
    }
    case SET_TABLE_COLUMS: {
      const { table, cols } = action.payload;
      const prevCols = { ...state.tableColumns };
      prevCols[table] = cols;
      return {
        ...state,
        tableColumns: prevCols,
      };
    }
    case "RESET_STATE":
      return initialState;

    default: {
      return { ...state };
    }
  }
}

export default databaseReducer;
