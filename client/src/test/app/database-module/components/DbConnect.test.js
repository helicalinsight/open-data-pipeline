import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import DbConnect from "../../../../app/database-module/components/DbConnect.jsx";
import "../../../__mocks__/matchMedia.js";

const mockStore = configureStore();
// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

// component props
const mockProps = {
  formData: [],
  setFormData: jest.fn(),
};

// store mock
const store = mockStore({
  database: { selectedDatasource: { driver: "cassandra", name:"Cassandra" }, editConnection: [] },
  dms: {
    step: 2,
  },
});

// store mock
const updatedStore = mockStore({
  database: {
    selectedDatasource: { driver: "flat_files", name:"Flat Files" },
    editConnection: [],
  },
});

const editConnectionStore = mockStore({
  database: {
    ...store.getState(),
    editConnection: {
      connection_id: "65cef844922bd07ed3aca713",
      connection_details: {
        sourceName: "cassandra connection news",
        host: "57.128.161.235",
        port: "9042",
        username: "cassandra",
        password: "cassandra",
      },
    },
  },
   dms: {
    step: 2,
  },
});
// reusable function for render
const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <DbConnect {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("DB Connect component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should show create connection tab when selected data source is not flat files", () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("create-connection")).toBeInTheDocument();
  });

  it("should file upload screen when selected data source is flat files", () => {
    const { container } = render(
      <reactRedux.Provider store={updatedStore}>
        <Router>
          <DbConnect {...mockProps} />
        </Router>
      </reactRedux.Provider>
    );
    const flatFiles = container.querySelector(".flat-files-container");
    expect(flatFiles).toBeInTheDocument();
  });
 
  it("should change the tab items when user clicks on it", () => {
    renderComponent(store, mockProps);
    const savedConnectionsTab = screen.getByText("Saved Connections");
    fireEvent.click(savedConnectionsTab);
    
    const createConnectionsTab = screen.getByText("Create");
    fireEvent.click(createConnectionsTab);
  });

  it("should change the tab items when user clicks on it", () => {
    renderComponent(editConnectionStore, mockProps);
    const savedConnectionsTab = screen.getByText("Saved Connections");
    fireEvent.click(savedConnectionsTab);
  });
});
