import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";
import { databaseServiceConstants ,dmsConstants} from "../../apis/apiUrlConstants";
import {
  getDataSources,
  getSavedConnections,
  testConnection,
  saveConnection,
  deleteConnection,
  updateConnection,
  getConnection,
  fecthDbsAndTables,
  dataLoads,
  fetchColumns
} from "../../apis/databaseService";

describe("Database Service", () => {
  const mock = new MockAdapter(axiosInstance, { onNoMatch: "throwException" });

  beforeEach(() => {
    setLocalStorage("user", { token: "mock-token" });
  });

  afterEach(() => {
    mock.reset();
  });

  afterAll(() => {
    cleanup();
    jest.restoreAllMocks();
    window.localStorage.clear();
  });

  describe("getDataSources", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { sources: ["mongodb", "cassandra"] };

      mock.onGet(databaseServiceConstants.datasources).reply(200, responseData);

      await getDataSources({ onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onGet(databaseServiceConstants.datasources)
        .reply(500, errorResponse);

      await getDataSources({ onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getSavedConnections", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const query = "mongodb";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { connections: [{ id: 1, name: "MongoDB1" }] };

      mock
        .onGet(`${databaseServiceConstants.savedConnections}?type=${query}`)
        .reply(200, responseData);

      await getSavedConnections({ query, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const query = "mongodb";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onGet(`${databaseServiceConstants.savedConnections}?type=${query}`)
        .reply(500, errorResponse);

      await getSavedConnections({ query, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("testConnection", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { type: "mongodb", host: "localhost", port: 27017 };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true, message: "Connection successful" };

      mock
        .onPost(databaseServiceConstants.connections)
        .reply(200, responseData);

      await testConnection({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { type: "mongodb", host: "localhost", port: 27017 };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Connection failed" };

      mock
        .onPost(databaseServiceConstants.connections)
        .reply(500, errorResponse);

      await testConnection({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("saveConnection", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = {
        name: "MongoDB1",
        type: "mongodb",
        host: "localhost",
        port: 27017,
      };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true, message: "Connection saved" };

      mock
        .onPost(databaseServiceConstants.dataConnectors)
        .reply(200, responseData);

      await saveConnection({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = {
        name: "MongoDB1",
        type: "mongodb",
        host: "localhost",
        port: 27017,
      };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to save connection" };

      mock
        .onPost(databaseServiceConstants.dataConnectors)
        .reply(500, errorResponse);

      await saveConnection({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("deleteConnection", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { id: 1 };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true, message: "Connection deleted" };

      mock
        .onDelete(databaseServiceConstants.dataConnectors)
        .reply(200, responseData);

      await deleteConnection({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { id: 1 };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to delete connection" };

      mock
        .onDelete(databaseServiceConstants.dataConnectors)
        .reply(500, errorResponse);

      await deleteConnection({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("updateConnection", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { id: 1, name: "UpdatedMongoDB1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true, message: "Connection updated" };

      mock
        .onPatch(databaseServiceConstants.dataConnectors)
        .reply(200, responseData);

      await updateConnection({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { id: 1, name: "UpdatedMongoDB1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to update connection" };

      mock
        .onPatch(databaseServiceConstants.dataConnectors)
        .reply(500, errorResponse);

      await updateConnection({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getConnection", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const query = "id=1";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { id: 1, name: "MongoDB1", type: "mongodb" };

      mock
        .onGet(`${databaseServiceConstants.dataConnectors}?${query}`)
        .reply(200, responseData);

      await getConnection({ query, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const query = "id=1";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to get connection" };

      mock
        .onGet(`${databaseServiceConstants.dataConnectors}?${query}`)
        .reply(500, errorResponse);

      await getConnection({ query, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("fecthDbsAndTables", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { connectionId: 1 };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        databases: ["db1", "db2"],
        tables: ["table1", "table2"],
      };

      mock
        .onPost(databaseServiceConstants.listCatalogs)
        .reply(200, responseData);

      await fecthDbsAndTables({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { connectionId: 1 };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to fetch databases and tables" };

      mock
        .onPost(databaseServiceConstants.listCatalogs)
        .reply(500, errorResponse);

      await fecthDbsAndTables({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("dataLoads", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = [{ fileName: "file1.csv", size: 1024 }];
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        success: true,
        message: "Data loaded successfully",
      };

      mock.onPost(databaseServiceConstants.dataLoads).reply(200, responseData);

      await dataLoads({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = [{ fileName: "file1.csv", size: 1024 }];
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to load data" };

      mock.onPost(databaseServiceConstants.dataLoads).reply(500, errorResponse);

      await dataLoads({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("fetchColumns", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { connectionId: 1, database: "db1", table: "table1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { columns: ["col1", "col2", "col3"] };

      mock
        .onPost(databaseServiceConstants.fetchColumns)
        .reply(200, responseData);

      await fetchColumns({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { connectionId: 1, database: "db1", table: "table1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to fetch columns" };

      mock
        .onPost(databaseServiceConstants.fetchColumns)
        .reply(500, errorResponse);

      await fetchColumns({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
});
