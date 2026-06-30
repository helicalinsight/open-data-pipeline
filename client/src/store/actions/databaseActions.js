import actionsTypes from "./actionTypes";

export const setDatasourcesAction = (payload) => {
  return {
    type: actionsTypes.database.SET_DATASOURCES,
    payload,
  };
};

export const setSelectedDatasourceAction = (payload) => {
  return {
    type: actionsTypes.database.SET_SELECTED_DATASOURCE,
    payload,
  };
};

export const setSavedConnections = (payload) => {
  return {
    type: actionsTypes.database.SET_SAVED_CONNECTIONS,
    payload,
  };
};

export const setSavedConnectionsApiStatus = (payload) => {
  return {
    type: actionsTypes.database.SET_SAVE_CONNECTION_API_STATUS,
    payload,
  };
};

export const setEditConnection = (payload) => {
  return {
    type: actionsTypes.database.SET_EDIT_CONNECTION,
    payload,
  };
};

export const deleteSavedConnection = (payload) => {
  return {
    type: actionsTypes.database.DELETE_SAVED_CONNECTION,
    payload,
  };
};

export const updateSavedConnection = (payload) => {
  return {
    type: actionsTypes.database.UPDATE_SAVED_CONNECTION,
    payload,
  };
};

export const setTableColumns = (payload) => {
  return {
    type: actionsTypes.database.SET_TABLE_COLUMS,
    payload,
  };
};

export const setFormData = (data) => ({
  type: actionsTypes.database.SET_FORM_DATA,
  payload: data,
});

export const clearFormData = () => ({
  type: actionsTypes.database.CLEAR_FORM_DATA,
});

export const setDataSourceConnectionName = (payload) => ({
  type: actionsTypes.database.SET_DS_CONNECTION_NAME,
  payload,
});
export const setDataSourceNames = (payload) => ({
  type: actionsTypes.database.SET_DATASOURCE_NAMES,
  payload,
});
export const setConnectionsStatus = (payload) => ({
  type: actionsTypes.database.SET_CONNECTION_STATUS,
  payload,
});
export const setSelectedConnection = (payload) => ({
  type: actionsTypes.database.SET_SELECTED_CONNECTION,
  payload
});
export const setTestConnectionMessage = (payload) => ({
  type: actionsTypes.database.SET_TESTCONNECTION_MSG,
  payload
})