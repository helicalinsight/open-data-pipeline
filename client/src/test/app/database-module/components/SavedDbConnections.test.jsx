import React from "react";
import { fireEvent, render, screen, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";

import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import SavedDbConnections from "../../../../app/database-module/components/SavedDbConnections";

import "@testing-library/jest-dom";
import "../../../__mocks__/matchMedia";
import { dataLoads, testConnection } from "../../../../apis/databaseService";

const mockStore = configureStore();

const appStore = mockStore({
  database: {
    selectedDatasource: {
      driver: "flat_files",
    },
    savedConnections: [
      {
        _id: "62cb179a-dd58-43fb-97de-c01526636b48",
        alias: "enrollments",
        fileType: ".csv",
        key: "62cb179a-dd58-43fb-97de-c01526636b48",
      },
      {
        _id: "0575afeb-8faa-4dbf-a3a3-c86734fc99a7",
        alias: "file_example_XLSX_100",
        fileType: ".xlsx",
        key: "0575afeb-8faa-4dbf-a3a3-c86734fc99a7",
      },
    ],
    savedConnApiStatus: "",
    editConnection: {},
  },
  chat: {
    chatList: {
      "65f97e88403f6d5fa967ac69": {
        chat_id: "65f97e88403f6d5fa967ac69",
        chat_name: "Job 2",
        loadedFiles: [
          {
            source_id: "65fd3be778aa5af726d559cd",
            alias: "csv file",
            type: "csv",
          },
        ],
      },
    },
  },
  dms: {
    step: 2
  },
});

const dbStore = mockStore({
  database: {
    selectedDatasource: {
      driver: "postgress",
    },
    savedConnections: [
      {
        _id: "66ceb1c23d809392ae6f3cfd",
        alias: "Postgres Connector 2",
        type: "postgres",
      },
    ],
    savedConnApiStatus: "",
    editConnection: {},
  },
  chat: {
    chatList: {
      "65f97e88403f6d5fa967ac69": {
        chat_id: "65f97e88403f6d5fa967ac69",
        chat_name: "Job 2",
        loadedFiles: [
          {
            source_id: "65fd3be778aa5af726d559cd",
            alias: "csv file",
            type: "csv",
          },
        ],
      },
    },
  },
   dms: {
    step: 2
  },
});

const appProps = {
  module: "load",
  selectedConnection: { _id: "65cef844922bd07ed3aca714" },
  setSelectedConnection: jest.fn(),
  setIsConnected: jest.fn(),
  setActiveTab: jest.fn(),
  setIsEdit: jest.fn(),
  handleClose: jest.fn(),
};

// mock for api service
jest.mock("../../../../apis/databaseService", () => ({
  dataLoads: jest.fn(),
  deleteConnection: jest.fn(),
  getConnection: jest.fn(),
  testConnection: jest.fn(),
}));

jest.mock("../../../../store/actions/databaseActions", () => ({
  deleteSavedConnection: jest.fn(),
  setEditConnection: jest.fn(),
}));

jest.mock("../../../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));

const renderComponent = (store, props) => {
  return render(
    <reactRedux.Provider store={store}>
      <Router>
        <SavedDbConnections {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Saved Connections component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should show saved connections table if data is fetched -- flatfiles -- module - load", () => {
    renderComponent(appStore, appProps);
    expect(screen.getByTestId("saved-connections-table")).toBeInTheDocument();
  });

  it("should show saved connections table if data is fetched -- flatfiles -- module - normal", () => {
    renderComponent(appStore, { ...appProps, module: "" });
    expect(screen.getByTestId("saved-connections-table")).toBeInTheDocument();
  });

  it("should show saved connections table if data is fetched --db", () => {
    renderComponent(dbStore, appProps);
    expect(screen.getByTestId("saved-connections-table")).toBeInTheDocument();
  });

  it("it should connect on load -- multi load - success - true", () => {
    dataLoads.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({
        files_uploaded: ["col1"],
        message: "success",
        success: true,
      })
    );
    const { container } = renderComponent(appStore, appProps);
    const checkbox = container.querySelector(`input[name="enrollments"]`);
    act(() => {
      fireEvent.click(checkbox);
    });
    const multiLoad = screen.getByTestId("multi-file-load-btn");
    act(() => {
      fireEvent.click(multiLoad);
    });
  });

  it("it should connect on load -- multi load -- success - false", () => {
    dataLoads.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({
        message: "failed",
        success: false,
      })
    );
    const { container } = renderComponent(appStore, appProps);
    const checkbox = container.querySelector(`input[name="enrollments"]`);
    act(() => {
      fireEvent.click(checkbox);
    });
    const multiLoad = screen.getByTestId("multi-file-load-btn");
    act(() => {
      fireEvent.click(multiLoad);
    });
  });

  it("it should connect on load -- multi load -- error - false", () => {
    dataLoads.mockImplementationOnce(({ onError }) =>
      onError({
        message: "failed",
        success: false,
      })
    );
    const { container } = renderComponent(appStore, appProps);
    const checkbox = container.querySelector(`input[name="enrollments"]`);
    act(() => {
      fireEvent.click(checkbox);
    });
    const multiLoad = screen.getByTestId("multi-file-load-btn");
    act(() => {
      fireEvent.click(multiLoad);
    });
  });

  it("it should trigger test connection API - success", () => {
    testConnection.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({
        msg: "Connection Tested successfully!!",
      })
    );
    const props = {
      ...appProps,
      module: "",
      setIsConnected: null,
    };
    renderComponent(dbStore, props);
  });

  it("it should trigger test connection API - failed", () => {
    testConnection.mockImplementationOnce(({ onError }) =>
      onError({
        message: "Test Connection Failed!!",
      })
    );
    const props = {
      ...appProps,
      module: "",
      setIsConnected: null,
    };
    renderComponent(dbStore, props);
  });
  it("should show loading skeleton when savedConnApiStatus is FETCHING", () => {
  const loadingStore = mockStore({
    ...appStore.getState(),
    database: {
      ...appStore.getState().database,
      savedConnApiStatus: "FETCHING"
    }
  });
  renderComponent(loadingStore, appProps);
  expect(screen.getByTestId("loading-id")).toBeInTheDocument();
});

it("should render empty table when no saved connections exist", () => {
  const emptyStore = mockStore({
    ...appStore.getState(),
    database: {
      ...appStore.getState().database,
      savedConnections: []
    }
  });
  renderComponent(emptyStore, appProps);
  expect(screen.getByTestId("saved-connections-table")).toBeInTheDocument();
  expect(screen.queryByText("enrollments")).not.toBeInTheDocument();
});

it("should filter connections based on search term", () => {
  renderComponent(appStore, { ...appProps, searchTerm: "enroll" });
  expect(screen.getByText("enrollments")).toBeInTheDocument();
  expect(screen.queryByText("file_example_XLSX_100")).not.toBeInTheDocument();
});
});
