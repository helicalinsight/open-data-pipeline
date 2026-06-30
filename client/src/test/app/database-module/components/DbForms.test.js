import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import * as reactRedux from "react-redux";
import { BrowserRouter as Router } from "react-router-dom";
import "@testing-library/jest-dom";
import configureStore from "redux-mock-store";
import { DbForms } from "../../../../app/database-module/components/DbForms";

import "../../../__mocks__/matchMedia";
import { uploadFileApi } from "../../../../apis/fileService";
import {
  saveConnection,
  testConnection,
  updateConnection,
} from "../../../../apis/databaseService";

global.setImmediate = jest.useRealTimers;

// mock for api service
jest.mock("../../../../apis/fileService.js", () => ({
  uploadFileApi: jest.fn(),
}));

// mock for api service
jest.mock("../../../../apis/databaseService", () => ({
  saveConnection: jest.fn(),
  updateConnection: jest.fn(),
  testConnection: jest.fn(),
}));

const mockStore = configureStore();

const astra = {
  driver: "astra",
  name: "Astra",
  spark: "spark-cassandra-connector_2.12-3.3.0",
  categoryName: "AI Database",
  categoryType: "nosql",
  available: true,
  parameters: {
    basic_auth: [
      {
        name: "Client ID",
        variable: "client_id",
        default: "",
        type: "string",
        category: "input",
      },
      {
        name: "Secret Key",
        variable: "secret",
        default: "",
        type: "password",
        category: "input",
      },
      {
        name: "Upload Bundle",
        variable: "bundle",
        default: "None",
        type: "file",
        required: ["zip"],
        category: "upload",
      },
    ],
  },
  advanceParameters: {
    name: [
      {
        name: "Client ID1",
        variable: "client_id1",
        default: "",
        type: "string",
        category: "input",
      },
    ],
  },
  pooling: true,
};

const cassandra = {
  driver: "astra",
  name: "Astra",
  spark: "spark-cassandra-connector_2.12-3.3.0",
  categoryName: "AI Database",
  categoryType: "nosql",
  available: true,
  pooling: true,
};

const appStore = mockStore({
  database: {
    selectedDatasource: cassandra,
    editConnection: {},
  },
});

const mockProps = {
  formData: null,
  setFormData: jest.fn(),
  setActiveTab: jest.fn(),
  isEdit: false,
};

const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <DbForms {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("DbForms Component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error with cassandra", () => {
    renderComponent(appStore, mockProps);
  });

  it("should render the component without error with astra: uploadFileApi SUCCESS", () => {
    uploadFileApi.mockImplementationOnce((params) => {
      params.onSuccess("success");
    });
    const store = mockStore({
      database: {
        selectedDatasource: astra,
        editConnection: {},
      },
    });
    renderComponent(store, mockProps);

    const file2 = new File(["file content"], "file2.txt", {
      type: "text/plain",
    });
    const input = screen.getByTestId("upload-input");

    act(() => {
      fireEvent.change(input, { target: { files: [file2] } });
    });
  });

  it("should throw an error while upload uploadFileApi", () => {
    const store = mockStore({
      database: {
        selectedDatasource: astra,
        editConnection: {},
      },
    });
    uploadFileApi.mockImplementationOnce((params) => {
      params.onError("error");
    });
    renderComponent(store, mockProps);

    const file2 = new File(["file content"], "file2.txt", {
      type: "text/plain",
    });
    const input = screen.getByTestId("upload-input");

    act(() => {
      fireEvent.change(input, { target: { files: [file2] } });
    });

    expect(screen.getByTestId("secret")).toBeInTheDocument();
  });

  it("submit button text, TEST CONNECTION SUCCESS", () => {
    const store = mockStore({
      database: {
        selectedDatasource: astra,
        editConnection: {},
      },
    });
    testConnection.mockImplementationOnce((params) => {
      params.onSuccess({ success: true });
    });
    renderComponent(store, mockProps);
    expect(screen.getByText("Test Connection")).toBeInTheDocument();
    const testButton = screen.getByTestId("test-button");
    expect(testButton).toBeInTheDocument();

    act(() => {
      fireEvent.click(testButton);
    });
  });

  it("submit button text, TEST CONNECTION FAIL", () => {
    const store = mockStore({
      database: {
        selectedDatasource: astra,
        editConnection: {},
      },
    });
    testConnection.mockImplementationOnce((params) => {
      params.onError("error");
    });
    renderComponent(store, mockProps);
    expect(screen.getByText("Test Connection")).toBeInTheDocument();
    const testButton = screen.getByTestId("test-button");
    expect(testButton).toBeInTheDocument();

    act(() => {
      fireEvent.click(testButton);
    });
  });

  it("IT SHOULD TRIGGER, UPDATE CONNECTION success", async () => {
    const store = mockStore({
      database: {
        selectedDatasource: cassandra,
        editConnection: {
          connection_id: "65d494ec2af97aead75aa417",
          connection_details: {
            sourceName: "cassandra",
            host: "57.128.161.235",
            port: "9042",
            username: "cassandra",
            password: "cassandra",
            database: null,
          },
        },
      },
    });

    testConnection.mockImplementationOnce((params) => {
      params.onSuccess({ success: true, msg: "test connection tested" });
    });

    updateConnection.mockImplementationOnce((params) => {
      params.onSuccess({
        success: true,
        msg: "Connection updated successfully!!",
        connection_id: 1,
        connection_alias: "name",
      });
    });

    renderComponent(store, { ...mockProps, isEdit: true });

    const testButton = screen.getByTestId("test-button");
    expect(testButton).toBeInTheDocument();

    act(() => {
      fireEvent.click(testButton);
    });

    act(() => {
      fireEvent.submit(screen.getByTestId("form"));
    });
  });

  it("IT SHOULD TRIGGER, UPDATE CONNECTION FAIL", async () => {
    const store = mockStore({
      database: {
        selectedDatasource: cassandra,
        editConnection: {
          connection_id: "65d494ec2af97aead75aa417",
          connection_details: {
            sourceName: "cassandra",
            host: "57.128.161.235",
            port: "9042",
            username: "cassandra",
            password: "cassandra",
            database: null,
          },
        },
      },
    });

    testConnection.mockImplementationOnce((params) => {
      params.onSuccess({ success: true, msg: "test connection tested" });
    });

    updateConnection.mockImplementationOnce((params) => {
      params.onError("error");
    });

    renderComponent(store, { ...mockProps, isEdit: true });

    const testButton = screen.getByTestId("test-button");
    expect(testButton).toBeInTheDocument();

    act(() => {
      fireEvent.click(testButton);
    });

    await waitFor(() => {
      act(() => {
        fireEvent.submit(screen.getByTestId("form"));
      });
    });

    await waitFor(() => {
      const saveButton = screen.getByTestId("save-button");
      expect(saveButton).toBeInTheDocument();

      act(() => {
        fireEvent.click(saveButton);
      });
    });
  });

  it("IT SHOULD TRIGGER, SAVE CONNECTION success", async () => {
    const val = [
      {
        configKey: "poolSize",
        configValue: "10",
      },
      {
        configKey: "maxWaitTime",
        configValue: "1000",
      },
    ];
    const store = mockStore({
      database: {
        selectedDatasource: cassandra,
        editConnection: {
          connection_id: "65d494ec2af97aead75aa417",
          connection_details: {
            sourceName: "cassandra",
            host: "57.128.161.235",
            port: "9042",
            username: "cassandra",
            password: "cassandra",
            database: null,
          },
        },
      },
    });
    const connection_details = {
      ...store.getState().database.editConnection.connection_details,
      connection_pool: val.length > 0
        ? val.reduce((acc, item) => {
            acc[item.configKey] = item.configValue;
            return acc;
          }, {})
        : undefined,
    };
  
    testConnection.mockImplementationOnce((params) => {
      params.onSuccess({ success: true, msg: "test connection tested" });
    });

    saveConnection.mockImplementationOnce((params) => {
      params.onSuccess({
        success: true,
        msg: "Connection updated successfully!!",
        connection_id: 1,
        connection_alias: "name",
        connection_details
      });
    });

    renderComponent(store, { ...mockProps, isEdit: false });

    const testButton = screen.getByTestId("test-button");
    expect(testButton).toBeInTheDocument();

    act(() => {
      fireEvent.click(testButton);
    });

    await waitFor(() => {
      act(() => {
        fireEvent.submit(screen.getByTestId("form"));
      });
    });

    await waitFor(() => {
      const saveButton = screen.getByTestId("save-button");
      expect(saveButton).toBeInTheDocument();

      act(() => {
        fireEvent.click(saveButton);
      });
    });
  });

  it("IT SHOULD TRIGGER, SAVE CONNECTION FAIL", async () => {
    const store = mockStore({
      database: {
        selectedDatasource: cassandra,
        editConnection: {
          connection_id: "65d494ec2af97aead75aa417",
          connection_details: {
            sourceName: "cassandra",
            host: "57.128.161.235",
            port: "9042",
            username: "cassandra",
            password: "cassandra",
            database: null,
          },
        },
      },
    });

    testConnection.mockImplementationOnce((params) => {
      params.onSuccess({ success: true, msg: "test connection tested" });
    });

    saveConnection.mockImplementationOnce((params) => {
      params.onError({ message: "error" });
    });

    renderComponent(store, { ...mockProps, isEdit: false });

    const testButton = screen.getByTestId("test-button");
    expect(testButton).toBeInTheDocument();

    act(() => {
      fireEvent.click(testButton);
    });

    await waitFor(() => {
      act(() => {
        fireEvent.submit(screen.getByTestId("form"));
      });
    });

    await waitFor(() => {
      const saveButton = screen.getByTestId("save-button");
      expect(saveButton).toBeInTheDocument();

      act(() => {
        fireEvent.click(saveButton);
      });
    });
  });

  it("IT SHOULD OPEN POOLING ONCLICK OF ADVANCED BUTTON", () => {
    renderComponent(appStore, mockProps);
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByTestId("close-button"));
    });
  });
});
