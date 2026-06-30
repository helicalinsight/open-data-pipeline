import axios from "./axios.js";
import { databaseServiceConstants } from "./apiUrlConstants";

// to get all the databases or datasources e.g mongodb, cassandra etc
export async function getDataSources({ onSuccess, onError }) {
  try {
    const response = await axios.get(databaseServiceConstants.datasources, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess?.(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
// to get all the saved connections
export async function getSavedConnections({ query, onSuccess, onError }) {
  try {
    const response = await axios.get(
      databaseServiceConstants.savedConnections + "?type=" + query,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess?.(response.data);
  } catch (error) {
    onError?.(error?.response?.data);
  }
}

// test connection
export async function testConnection({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      databaseServiceConstants.connections,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

// to save a connection for selected datasource
export async function saveConnection({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      databaseServiceConstants.dataConnectors,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
    
  }
}

// delete connection
export async function deleteConnection({ payload, onSuccess, onError }) {
  try {
    const response = await axios.delete(
      databaseServiceConstants.dataConnectors,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
        data: payload,
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

// update connection
export async function updateConnection({ onSuccess, onError, payload }) {
  try {
    const response = await axios.patch(
      databaseServiceConstants.dataConnectors,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

// get connection
export async function getConnection({ onSuccess, onError, query }) {
  try {
    const response = await axios.get(
      databaseServiceConstants.dataConnectors + "?" + query,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

// get connection
export async function fecthDbsAndTables({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      databaseServiceConstants.listCatalogs,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}

export async function dataLoads({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      databaseServiceConstants.dataLoads,
      {
        filesInfo: payload,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}

export async function fetchColumns({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      databaseServiceConstants.fetchColumns,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}
