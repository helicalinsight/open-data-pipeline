import actionsTypes from "../../../store/actions/actionTypes";
import { databaseReducer } from "../../../store/reducers";

const {
  SET_DATASOURCES,
  SET_SELECTED_DATASOURCE,
  SET_SAVED_CONNECTIONS,
  SET_SAVE_CONNECTION_API_STATUS,
  SET_EDIT_CONNECTION,
  DELETE_SAVED_CONNECTION,
  UPDATE_SAVED_CONNECTION,
  SET_TABLE_COLUMS,
  SET_FORM_DATA,
  CLEAR_FORM_DATA,
  SET_DS_CONNECTION_NAME,
  SET_DATASOURCE_NAMES,
  SET_CONNECTION_STATUS,
  SET_SELECTED_CONNECTION,
  SET_TESTCONNECTION_MSG
} = actionsTypes.database;

describe("databaseReducer", () => {
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
    testConnectionMessage: ""
  };

  it("should return the initial state", () => {
    expect(databaseReducer(undefined, {})).toEqual(initialState);
  });

  it("should handle SET_FORM_DATA", () => {
    const action = {
      type: SET_FORM_DATA,
      payload: { key1: "value1", key2: "value2" },
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      formData: { key1: "value1", key2: "value2" },
    });
  });

  it("should handle SET_FORM_DATA with existing formData", () => {
    const state = {
      ...initialState,
      formData: { key1: "oldValue" },
    };
    const action = {
      type: SET_FORM_DATA,
      payload: { key2: "newValue" },
    };
    expect(databaseReducer(state, action)).toEqual({
      ...state,
      formData: { key1: "oldValue", key2: "newValue" },
    });
  });

  it("should handle CLEAR_FORM_DATA", () => {
    const state = {
      ...initialState,
      formData: { key1: "value1", key2: "value2" },
    };
    const action = { type: CLEAR_FORM_DATA };
    expect(databaseReducer(state, action)).toEqual({
      ...state,
      formData: {},
    });
  });

  it("should handle SET_DATASOURCES", () => {
    const action = {
      type: SET_DATASOURCES,
      payload: [
        { id: 1, name: "DB1" },
        { id: 2, name: "DB2" },
      ],
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      datasources: action.payload,
    });
  });

  it("should handle SET_SELECTED_DATASOURCE", () => {
    const action = {
      type: SET_SELECTED_DATASOURCE,
      payload: { id: 1, name: "DB1" },
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      selectedDatasource: action.payload,
    });
  });

  it("should handle SET_SAVED_CONNECTIONS with insert", () => {
    const action = {
      type: SET_SAVED_CONNECTIONS,
      payload: { key: "insert", data: [{ id: 1, name: "Conn1" }] },
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      savedConnections: action.payload.data,
    });
  });

  it("should handle SET_SAVED_CONNECTIONS without insert", () => {
    const action = {
      type: SET_SAVED_CONNECTIONS,
      payload: { key: "replace", data: [{ id: 1, name: "Conn1" }] },
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      savedConnections: action.payload.data,
    });
  });

  it("should handle SET_SAVE_CONNECTION_API_STATUS", () => {
    const action = {
      type: SET_SAVE_CONNECTION_API_STATUS,
      payload: "success",
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      savedConnApiStatus: action.payload,
    });
  });

  it("should handle SET_EDIT_CONNECTION", () => {
    const action = {
      type: SET_EDIT_CONNECTION,
      payload: { id: 1, name: "EditConn" },
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      editConnection: action.payload,
    });
  });

  it("should handle DELETE_SAVED_CONNECTION", () => {
    const state = {
      ...initialState,
      savedConnections: [{ _id: 1 }, { _id: 2 }, { _id: 3 }],
    };
    const action = {
      type: DELETE_SAVED_CONNECTION,
      payload: [1, 3],
    };
    expect(databaseReducer(state, action)).toEqual({
      ...state,
      savedConnections: [{ _id: 2 }],
    });
  });

  it("should handle UPDATE_SAVED_CONNECTION", () => {
    const state = {
      ...initialState,
      savedConnections: [
        { _id: 1, alias: "Old1" },
        { _id: 2, alias: "Old2" },
      ],
    };
    const action = {
      type: UPDATE_SAVED_CONNECTION,
      payload: { connection_id: 1, connection_alias: "New1" },
    };
    expect(databaseReducer(state, action)).toEqual({
      ...state,
      savedConnections: [
        { _id: 1, alias: "New1" },
        { _id: 2, alias: "Old2" },
      ],
    });
  });

  it("should handle SET_TABLE_COLUMS", () => {
    const action = {
      type: SET_TABLE_COLUMS,
      payload: { table: "users", cols: ["id", "name", "email"] },
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      tableColumns: { users: ["id", "name", "email"] },
    });
  });

  it("should handle RESET_STATE", () => {
    const state = {
      datasources: [{ id: 1 }],
      selectedDatasource: { id: 1 },
      savedConnections: [{ id: 1 }],
      savedConnApiStatus: "success",
      editConnection: { id: 1 },
      tableColumns: { users: ["id"] },
      dataSourceName: "test",
      isConnected: true,
      selectedConnection: { id: 1 },
      testConnectionMessage: "Success"
    };
    const action = { type: "RESET_STATE" };
    expect(databaseReducer(state, action)).toEqual(initialState);
  });

  it("should return current state for unknown action", () => {
    const state = { ...initialState, datasources: [{ id: 1 }] };
    expect(databaseReducer(state, { type: "UNKNOWN_ACTION" })).toEqual(state);
  });

  it("should handle SET_DS_CONNECTION_NAME", () => {
    const action = {
      type: SET_DS_CONNECTION_NAME,
      payload: "test-connection",
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      connectionName: "test-connection",
    });
  });

  it("should handle SET_DATASOURCE_NAMES", () => {
    const action = {
      type: SET_DATASOURCE_NAMES,
      payload: "test-datasource",
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      dataSourceName: "test-datasource",
    });
  });

  it("should handle SET_CONNECTION_STATUS", () => {
    const action = {
      type: SET_CONNECTION_STATUS,
      payload: true,
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      isConnected: true,
    });
  });

  it("should handle SET_SELECTED_CONNECTION", () => {
    const connection = { id: 1, name: "test-connection" };
    const action = {
      type: SET_SELECTED_CONNECTION,
      payload: connection,
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      selectedConnection: connection,
    });
  });

  it("should handle SET_TESTCONNECTION_MSG", () => {
    const action = {
      type: SET_TESTCONNECTION_MSG,
      payload: "Connection successful",
    };
    expect(databaseReducer(initialState, action)).toEqual({
      ...initialState,
      testConnectionMessage: "Connection successful",
    });
  });
});