import React from "react";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";
import { BrowserRouter as Router } from "react-router-dom";
import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import DbListing from "../../../../app/database-module/components/DbListing";
import { getSavedConnections } from "../../../../apis/databaseService";
import { getAllFilesApi } from "../../../../apis/fileService";

const mockStore = configureStore();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

//mock apis
jest.mock("../../../../utils/isPremiumFeature", () => ({
  checkIsPremiumFeature: jest.fn(),
}));

//mock apis
jest.mock("../../../../apis/databaseService", () => ({
  getSavedConnections: jest.fn(),
}));

jest.mock("../../../../apis/fileService", () => ({
  getAllFilesApi: jest.fn(),
}));
// component props
const mockProps = {
  setCurrent: jest.fn(),
  current: 0,
};

// store mock
const store = mockStore({
  database: {
    datasources: [
      {
        categoryType: "flat_files",
        driver: "flat_files",
        available: true,
        name: "Flat Files",
      },
      {
        categoryType: "nosql",
        driver: "cassandra",
        available: true,
        name: "Cassandra",
        verified: true,
      },
      {
        categoryType: "Cloud",
        driver: "bigquery",
        available: false,
        name: "Google BigQuery",
      },
    ],
  },
  app: {
    userConfig: {
      chat: ["jobs", "create", "schedule"],
      job: ["histroy", "dataPreview", "reset", "load", "trigger"],
      datasources: ["flat_files", "cassandra"],
    },
  },
});

const noConnectorsStore = mockStore({
  ...store.getState(),
  database: {
    datasources: [],
  },
});

// reusable function for render
const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <DbListing {...props} />
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

describe("DB Listing component", () => {
  it("should show no connectors found message if there are no datasources", () => {
    renderComponent(noConnectorsStore, mockProps);
    expect(screen.getByText(/No Connectors Found !!/i)).toBeInTheDocument();
  });
  it("should show category select dropdown on the screen", () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("category-select-id")).toBeInTheDocument();
  });

  it("should show All, Flat files, Cloud and Nosql in category filter tab", () => {
    renderComponent(store, mockProps);
    expect(screen.getByText("All")).toBeInTheDocument();
    expect(screen.getByText(/Nosql/i)).toBeInTheDocument();
    expect(screen.getByText(/Flat_Files/i)).toBeInTheDocument();
    expect(screen.getByText(/Cloud/i)).toBeInTheDocument();
  });

  it("should show all datasources if user has selected all from the category dropdown", async () => {
    renderComponent(store, mockProps);
    // const selectInput = screen.getByTestId("category-select-id");
    // fireEvent.change(selectInput, { value: "all" });
    const combobox = screen.getByRole("combobox");
    fireEvent.change(combobox, {
      target: { value: ["all"] },
    });
  });

  it("should show the cassandra, google big query and flat files if user has clicked on all from category tabs", async () => {
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("category-name-id")[0])
    );
    expect(screen.getByText("Flat Files")).toBeInTheDocument();
    expect(screen.getByText("Cassandra")).toBeInTheDocument();
    expect(screen.getByText("Google BigQuery")).toBeInTheDocument();
  });

  it("should show the Files if user has clicked on flat files from category tabs", async () => {
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("category-name-id")[1])
    );
    expect(screen.getByText("Flat Files")).toBeInTheDocument();
  });

  it("should show the cassandra if user has clicked on nosql from category tabs", async () => {
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("category-name-id")[2])
    );
    expect(screen.getByText("Cassandra")).toBeInTheDocument();
  });

  it("should show the Google BigQuery if user has clicked on cloud from category tabs", async () => {
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("category-name-id")[3])
    );
    expect(screen.getByText("Google BigQuery")).toBeInTheDocument();
  });

  it("should show verfied icon", async () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("verified")).toBeInTheDocument();
  });

  it("should show the searched connectors based on user search in search input", async () => {
    renderComponent(store, mockProps);
    fireEvent.change(screen.getByTestId("search-connectors"), {
      target: { value: "flat files" },
    });
    expect(screen.getByText("Flat Files")).toBeInTheDocument();
  });

  it("should not show any connectors if the item doesn't exists for teh search term", async () => {
    renderComponent(store, mockProps);
    fireEvent.change(screen.getByTestId("search-connectors"), {
      target: { value: "astra" },
    });
    expect(screen.getByText(/No Connectors Found !!/i)).toBeInTheDocument();
  });

  it("should fetch all the saved database connections if user has clicked on any database from the list", async () => {
    const databases = [
      {
        _id: "65cef844922bd07ed3aca713",
        alias: "cassandra connection news",
        type: "cassandra",
      },
    ];
    getSavedConnections.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(databases)
    );
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("data-connector-id")[1])
    );
  });

  it("should fetch the files list if user has clicked on flat files from the list", async () => {
    const filesList = [
      {
        _id: "415a9e3d-1b11-4a88-afe2-6b60903662f5",
        alias: "csv file",
        fileType: ".csv",
      },
    ];
    getAllFilesApi.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(filesList)
    );
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("data-connector-id")[2])
    );
  });

  it("should not show saved connections with failed network", async () => {
    const errorResponse = "Something went wrong!!";
    getSavedConnections.mockImplementationOnce(({ onError }) =>
      onError(errorResponse)
    );
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("data-connector-id")[1])
    );
  });

  it("should not show files list with failed network", async () => {
    const errorResponse = "Something went wrong!!";
    getAllFilesApi.mockImplementationOnce(({ onError }) =>
      onError(errorResponse)
    );
    renderComponent(store, mockProps);
    await waitFor(() =>
      fireEvent.click(screen.getAllByTestId("data-connector-id")[2])
    );
  });
});
