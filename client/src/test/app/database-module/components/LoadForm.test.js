import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import { dataLoads, fecthDbsAndTables } from "../../../../apis/databaseService";
import { handleSessionExpiry } from "../../../../utils/handleSessionExpiry";

import configureStore from "redux-mock-store";
import LoadForm from "../../../../app/database-module/components/LoadForm";
import * as reactRedux from "react-redux";

import "../../../__mocks__/matchMedia";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

global.setImmediate = jest.useRealTimers;

const mockStore = configureStore();

// mock for api service
jest.mock("../../../../apis/databaseService", () => ({
  dataLoads: jest.fn(),
  fecthDbsAndTables: jest.fn(),
}));

jest.mock("../../../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));
const sortSchemasAndTables = (dbList) => {
  return dbList.sort((a, b) => a.title.localeCompare(b.title));
};

const appStore = mockStore({
  database: {
    selectedDatasource: {
      driver: "cassandra",
      name: "Cassandra",
      spark: "spark-cassandra-connector_2.12-3.3.0",
      categoryName: "Big Data",
      categoryType: "nosql",
      available: true,
      parameters: {
        basic_auth: [
          {
            name: "Host",
            variable: "host",
            default: "localhost",
            type: "string",
            category: "input",
          },
          {
            name: "Port",
            variable: "port",
            default: "5042",
            type: "int",
            category: "input",
          },
          {
            name: "Username",
            variable: "username",
            default: "",
            type: "string",
            category: "input",
          },
          {
            name: "Password",
            variable: "password",
            default: "",
            type: "password",
            category: "input",
          },
        ],
      },
    },
    savedConnections: [
      {
        _id: "connection_id",
        alias: "alias",
      },
    ],
  },
  chat: {
    chatList: {
      "65fac1bdebc12f47237277ca": {
        chat_id: "65fac1bdebc12f47237277ca",
        chat_name: "Job 3",
        loadedFiles: [
          {
            source_id: "6613e159826c74a534dcfcae",
            alias: "pg_catalog_pg_type",
            type: "table",
          },
        ],
      },
    },
  },
  dms: {
    step: 1,
    selectedSourceTable: [],
    selectedDestinationTable: [],
  },
});

const mockProps = {
  handleClose: jest.fn(),
  selectedConnection: {
    _id: "65d494ec2af97aead75aa417",
    alias: "cassandra",
    type: "cassandra",
    key: "65d494ec2af97aead75aa417",
  },
};

const mockDbAndTablesSuccess = {
  success: true,
  dataCatalog: [
    {
      title: "pg_catalog",
      value: "pg_catalog",
      children: [
        {
          title: "pg_type",
          value: "pg_catalog.pg_type",
        },
        {
          title: "pg_foreign_table",
          value: "pg_catalog.pg_foreign_table",
        },
      ],
    },
  ],
};

const mockDataLoadsSuccess = {
  success: true,
  message: "All files loaded successfully",
  files_uploaded: [
    {
      source_id: "65fd1ecd4d60cac9fd0c258b",
      alias: "testing_data_order_info",
      type: "table",
    },
    {
      source_id: "65fd1ecd4d60cac9fd0c258c",
      alias: "testing_data_order_details",
      type: "table",
    },
  ],
  files_failed: ["failed to load"],
};

const mockDbAndTablesError = {
  msg: "Something Went Wrong!!",
};
// reusable function for render
const renderComponent = (props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <LoadForm {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("SidebarJobs component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without error", () => {
    renderComponent(mockProps);
  });

  it("should fetch the available databases and tables on load", async () => {
    fecthDbsAndTables.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockDbAndTablesSuccess)
    );
    renderComponent(mockProps);

    const inputElement = screen.getByRole("combobox", { readOnly: true });
    expect(inputElement).toBeInTheDocument();

    expect(inputElement).toHaveAttribute("readonly");
  });

  it("should not fetch the available databases and tables on load with failed network requests", () => {
    fecthDbsAndTables.mockImplementationOnce(({ onError }) =>
      onError(mockDbAndTablesError)
    );
    renderComponent(mockProps);
  });

  it("should load the selected database ad table on submitting form", async () => {
  fecthDbsAndTables.mockImplementationOnce(({ onSuccess }) =>
    onSuccess(mockDbAndTablesSuccess)
  );
  dataLoads.mockImplementationOnce(({ onSuccess }) =>
    onSuccess(mockDataLoadsSuccess)
  );
  renderComponent(mockProps);

  const treeSelect = screen.getAllByRole("combobox");
  await userEvent.click(treeSelect[0]);
  const parentNodes = await screen.findAllByText("pg_catalog");
  await userEvent.click(parentNodes[0]);
  await userEvent.click(screen.getByTestId("load-button"));
});

  it("should load the selected database ad table on submitting form with error", async () => {
    fecthDbsAndTables.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockDbAndTablesSuccess)
    );
    dataLoads.mockImplementationOnce(({ onError }) =>
      onError({
        files_failed: ["error"],
        message: "message",
      })
    );
    renderComponent(mockProps);

    let treeSelect = screen.getAllByRole("combobox");
    userEvent.click(treeSelect[0]);
    const parentNode = await screen.findByText("pg_catalog");
    userEvent.click(parentNode);
    act(() => {
      fireEvent.submit(screen.getByTestId("load-form"));
    });
  });

  it("should trigger FetchDbsAndTables API with onError", async () => {
    fecthDbsAndTables.mockImplementationOnce((params) => {
      params.onError("something went wrong");
    });
    renderComponent(mockProps);
    expect(handleSessionExpiry).toHaveBeenCalled();
    const treeSelect = screen.queryByTestId("tree-select-load");
    expect(treeSelect).not.toBeNull();
  });

  it("fecthDbsAndTables api errror - success false", async () => {
    fecthDbsAndTables.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: false, msg: "failed" })
    );
    renderComponent(mockProps);
  });

  it("should not trigger FetchDbsAndTables when type is csv", async () => {
    renderComponent({
      ...mockProps,
      selectedConnection: {
        source: "flat_files",
        fileType: ".csv",
        connection_id: "connection_id",
      },
    });
  });
  it("should sort schemas and tables alphabetically by title", () => {
    const unsortedDbList = [
      {
        title: "pg_catalog",
        value: "pg_catalog",
        children: [
          { title: "pg_foreign_table", value: "pg_catalog.pg_foreign_table" },
          { title: "pg_type", value: "pg_catalog.pg_type" },
        ],
      },
      {
        title: "users",
        value: "users",
        children: [
          { title: "user_details", value: "users.user_details" },
          { title: "user_roles", value: "users.user_roles" },
        ],
      },
    ];
    const sortedDbList = sortSchemasAndTables(unsortedDbList);
    expect(sortedDbList[0].title).toBe("pg_catalog");
    expect(sortedDbList[1].title).toBe("users");
  });

  it("should return an empty array if input is empty", () => {
    const result = sortSchemasAndTables([]);
    expect(result).toEqual([]);
  });

  it("should handle a schema with no children", () => {
    const unsortedDbList = [
      {
        title: "pg_catalog",
        value: "pg_catalog",
        children: [],
      },
      {
        title: "users",
        value: "users",
        children: [],
      },
    ];
    const sortedDbList = sortSchemasAndTables(unsortedDbList);
    expect(sortedDbList[0].title).toBe("pg_catalog");
    expect(sortedDbList[1].title).toBe("users");
    expect(sortedDbList[0].children).toEqual([]);
    expect(sortedDbList[1].children).toEqual([]);
  });
});
