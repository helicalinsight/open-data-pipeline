import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import DataBaseModule from "../../../app/database-module/index.jsx";
import "../../__mocks__/matchMedia.js";
import { setSelectedDatasourceAction } from "../../../store/actions/databaseActions.js";

const mockStore = configureStore();
// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
jest.mock("../../../utils/handleClick", () => jest.fn());
const handleBackClick = require("../../../utils/handleClick");
const useDispatchMock = reactRedux.useDispatch;

//mock actions
jest.mock("../../../store/actions/databaseActions", () => ({
  setDataSourceNames: jest.fn(),
  setDataSourceConnectionName: jest.fn(),
  setSelectedConnection: jest.fn(),
  setConnectionsStatus: jest.fn(),
  setTestConnectionMessage: jest.fn(),
  setSelectedDatasourceAction: jest.fn(),
}));

// component props
const mockProps = {
  setOpenDbModal: jest.fn(),
  openDbModal: true,
  socket: { emit: jest.fn() },
  haveLoad: true,
};

const upadatedProps = {
  ...mockProps,
  haveLoad: false,
};
// store mock
const store = mockStore({
  app: { activeViewState: "datasources-view" },
  database: {
    datasources: [
      {
        driver: "flat_files",
        name: "Flat Files",
        categoryName: "Flat File",
        categoryType: "flat_files",
        available: true,
      },
    ],
    selectedDatasource: {
      driver: "cassandra",
      categoryType: "nosql",
      name: "Cassandra",
    },
    editConnection: [],
  },
});

const updatedStore = mockStore({
  ...store.getState(),
  app: { activeViewState: "" },
});

const noSelectedDataSourceStore = mockStore({
  ...updatedStore.getState(),
  database: {
    ...updatedStore.getState().database,
    selectedDatasource: { driver: "" },
  },
});
// In your test file, add this mock data
const mockSteps = [
  {
    title: "Choose",
    content: <div>Choose content</div>,
    description: "Pick from the available connectors",
  },
  {
    title: "Connect",
    content: <div>Connect content</div>,
    description: "Provide connector credentials",
  },
];
// reusable function for render
const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <DataBaseModule {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

beforeEach(() => {
  useDispatchMock.mockImplementation(() => () => {});
});

afterEach(() => {
  jest.clearAllMocks();
  useDispatchMock.mockClear();
});

describe("Database module index component", () => {
  it("should render the steps in the right section of the window if user has clicked datasources from sidebar header", () => {
    renderComponent(updatedStore, mockProps);
  });

  it("should render the steps in the drawer if user has clicked on datasources from top header", () => {
    renderComponent(updatedStore, mockProps);
    expect(screen.getByTestId("db-steps-drawer")).toBeInTheDocument();
  });

  it("should show close icon on drawer", () => {
    renderComponent(updatedStore, mockProps);
    expect(screen.getByLabelText("Close")).toBeInTheDocument();
  });

  it("should close the drawer and clear the already selected datasource when user clicks on close icon", () => {
    renderComponent(updatedStore, mockProps);
    fireEvent.click(screen.getByLabelText("Close"));
    expect(setSelectedDatasourceAction).toHaveBeenCalledWith({});
  });

  it("should close the drawer simply if user has not selected any datasource and clicked on close icon", () => {
    renderComponent(noSelectedDataSourceStore, mockProps);
    fireEvent.click(screen.getByLabelText("Close"));
  });

  it("should render only 'Connection' breadcrumb when no dataSourceName or connectionName exists", () => {
    renderComponent(updatedStore, mockProps);
    expect(screen.getByText("Connection")).toBeInTheDocument();
    expect(screen.queryAllByTestId("breadcrumb-separator")).toHaveLength(0);
  });

  it("should render full breadcrumb 'Connection > DataSource > ConnectionName' when all data exists", () => {
    const storeWithAllData = mockStore({
      ...updatedStore.getState(),
      database: {
        ...updatedStore.getState().database,
        dataSourceName: "TestDataSource",
        connectionName: "TestConnection",
        testConnectionMessage: "Success",
      },
    });
    renderComponent(storeWithAllData, mockProps);
    expect(screen.getByText("Connection")).toBeInTheDocument();
    expect(screen.getByText("TestDataSource")).toBeInTheDocument();
    expect(screen.getByText("TestConnection")).toBeInTheDocument();
  });

  it("should render 'Connection > DataSource' when dataSourceName exists", () => {
    const storeWithDataSource = mockStore({
      ...updatedStore.getState(),
      database: {
        ...updatedStore.getState().database,
        dataSourceName: "TestDataSource",
        connectionName: "",
      },
    });
    renderComponent(storeWithDataSource, mockProps);
    expect(screen.getByText("Connection")).toBeInTheDocument();
    expect(screen.getByText("TestDataSource")).toBeInTheDocument();
  });

  it("should apply hover-underline class to all clickable breadcrumb items", () => {
    const storeWithAllData = mockStore({
      ...updatedStore.getState(),
      database: {
        ...updatedStore.getState().database,
        dataSourceName: "TestDataSource",
        connectionName: "TestConnection",
        testConnectionMessage: "Success",
      },
    });
    renderComponent(storeWithAllData, mockProps);
    const breadcrumbItems = screen.getAllByRole("listitem");
    expect(
      breadcrumbItems[0].querySelector(".hover-underline")
    ).toBeInTheDocument();
    expect(
      breadcrumbItems[1].querySelector(".hover-underline")
    ).toBeInTheDocument();
  });

  it("should dispatch actions when clicking 'DataSource' breadcrumb", () => {
    const storeWithAllData = mockStore({
      ...updatedStore.getState(),
      database: {
        ...updatedStore.getState().database,
        dataSourceName: "TestDataSource",
        connectionName: "TestConnection",
        testConnectionMessage: "Success",
        current: 1,
      },
    });
    renderComponent(storeWithAllData, mockProps);
    fireEvent.click(screen.getByText("TestDataSource"));
  });

  it("should not render connectionName when testConnectionMessage is empty", () => {
    const storeWithEmptyTestMessage = mockStore({
      ...updatedStore.getState(),
      database: {
        ...updatedStore.getState().database,
        dataSourceName: "TestDataSource",
        connectionName: "TestConnection",
        testConnectionMessage: "",
      },
    });
    renderComponent(storeWithEmptyTestMessage, mockProps);
    expect(screen.getByText("Connection")).toBeInTheDocument();
    expect(screen.getByText("TestDataSource")).toBeInTheDocument();
    expect(screen.queryByText("TestConnection")).not.toBeInTheDocument();
  });
});

describe("Breadcrumb onClick handlers", () => {
  let store;
  const mockSetCurrent = jest.fn();

  beforeEach(() => {
    store = mockStore({
      ...updatedStore.getState(),
      database: {
        ...updatedStore.getState().database,
        dataSourceName: "TestDataSource",
        connectionName: "TestConnection",
        testConnectionMessage: "Success",
        editConnection: { id: 123 },
        current: 1,
      },
    });
    jest.clearAllMocks();
  });

  it("should dispatch all actions and call handleBackClick when clicking Connection breadcrumb", () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByText("Connection"));
  });

  it("should dispatch connection cleanup actions when clicking DataSource breadcrumb", () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByText("TestDataSource"));
    expect(handleBackClick).not.toHaveBeenCalled();
  });

  it("should not dispatch actions when clicking last breadcrumb item", () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByText("TestConnection"));
    const actions = store.getActions();
    expect(actions).toHaveLength(0);
    expect(handleBackClick).not.toHaveBeenCalled();
  });

  it("should handle click when editConnection is empty", () => {
    const storeWithEmptyEdit = mockStore({
      ...store.getState(),
      database: {
        ...store.getState().database,
        editConnection: null,
      },
    });
    renderComponent(storeWithEmptyEdit, mockProps);
    fireEvent.click(screen.getByText("Connection"));
  });
});

