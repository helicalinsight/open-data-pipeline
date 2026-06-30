import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import { getSavedConnections } from "../../../../../apis/databaseService";

import ConnectionMapping from "../../../../../app/app-header/components/job-schedule/components/ConnectionMapping";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";

import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";

//mock apis
jest.mock("../../../../../apis/databaseService", () => ({
  getSavedConnections: jest.fn(),
}));

jest.mock("../../../../../apis/fileService", () => ({
  getAllFilesApi: jest.fn(),
}));

const dbList = [
  {
    driver: "flat_files",
    name: "Flat Files",
    categoryName: "Flat File",
    categoryType: "Flat Files",
    available: true,
  },

  {
    driver: "postgres",
    name: "Postgres",
    verified: true,
    spark: "postgresql-42.7.1",
    categoryName: "RDBMS",
    categoryType: "sql",
    available: true,
    connection_string: {
      driver: "postgresql+psycopg2",
      username: "None",
      password: "None",
      host: "None",
      port: "None",
      database: "None",
    },
    description:
      "# PostgreSQL Connector Documentation\n\nThe PostgreSQL Connector allows you to establish a connection between your application and a PostgreSQL database. This connector facilitates the seamless interaction and data exchange between your application and the PostgreSQL database.\n\n## Required Fields\n\nTo successfully configure the PostgreSQL Connector, you need to provide the following essential information:\n\n1. **Hostname:**\n   - The hostname or IP address of the machine where your PostgreSQL database is hosted.\n\n2. **Username:**\n   - The username used to authenticate and access the PostgreSQL database.\n\n3. **Password:**\n   - The password associated with the provided username for authentication.\n\n4. **Port:**\n   - The port number on which the PostgreSQL database is listening for connections.\n\n5. **Database:**\n   - The name of the PostgreSQL database you want to connect to.\n\n## Pooling Options\n\n **Pooling options for PostgreSQL:**\n\n **`pool_size`:**\n - Specifies the number of connections to maintain in the pool. Default is 5.\n\n **`max_overflow`:**\n - Controls the number of connections that can be created beyond the pool size. Default is 10.\n\n **`pool_timeout`:**\n - Defines the number of seconds to wait before giving up on getting a connection from the pool. Default is 30 seconds.\n\n **`pool_recycle`:**\n - Determines the number of seconds after which a connection will be recycled. This helps to prevent potential connection leaks. Default is -1 (no recycling).\n\n **`poolclass`:**\n - Allows you to specify a custom pool class. The default pool class is `QueuePool`.\n\n \n For more detailed information on these parameters, refer to the [Postgres Pooling Documentation](https://docs.sqlalchemy.org/en/20/core/pooling.html).\n",
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
          default: 5432,
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
        {
          name: "Database",
          variable: "database",
          default: "",
          type: "string",
          category: "input",
        },
      ],
    },
  },
];

const dataSource = [
  {
    key: "fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6",
    pipeline: "read_files",
    databaseAlias: "flat_files",
    fileName: "sample",
    id: "fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6",
    mappedName: "enrollments",
  },
  {
    key: "fd681b18-8cc3-46ce-afb7-1d260e967960",
    pipeline: "read_files",
    databaseAlias: "flat_files",
    fileName: "enrollments",
    id: "fd681b18-8cc3-46ce-afb7-1d260e967960",
  },
];

const databases = [
  {
    _id: "65cef844922bd07ed3aca713",
    alias: "cassandra connection news",
    type: "cassandra",
  },
];

const savedConnections = [
  {
    _id: "66c59c8673063bd15218318e",
    alias: "testing",
    type: "postgres",
  },
];

const mockStore = configureStore();
const appStore = mockStore({
  database: {
    datasources: dbList,
    savedConnections,
    selectedDatasource: {
      name: "enrollments",
    },
  },
  selectedChat: {
    chat_id: "chat_id",
  },
  chat: {
    chatList: {
      chat_id: {
        pipelineHistory: {
          history: [
            {
              function: "read_files",
              parameters: [
                {
                  alias: "sample",
                  _id: "fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6",
                },
              ],
              files: null,
              database_alias: "flat_files",
            },
            {
              function: "read_files",
              parameters: [
                {
                  alias: "enrollments",
                  _id: "fd681b18-8cc3-46ce-afb7-1d260e967960",
                },
              ],
              files: null,
              database_alias: "flat_files",
            },
          ],
          next: [
            {
              function: "rename_columns",
              parameters: [
                {
                  old_name: "film_id",
                  new_name: "id",
                },
              ],
              files: [
                {
                  alias: ["film"],
                },
              ],
            },
          ],
        },
      },
    },
  },
  app: {
    activeViewState: "job-listing-view",
  },
   dms: {
    step: 2,
  },
});

// reusable function for render
const renderComponent = (props, appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <ConnectionMapping {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

const mappedData = {
  "fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6":
    "aba1ecae-a52c-47a7-aad3-317ba5c19e06",
};

const props = {
  openDbDrawer: true,
  setOpenDbDrawer: jest.fn(),
  mappedData,
  setMappedData: jest.fn(),
  dataSource,
  setDataSource: jest.fn(),
};

describe("Connection Mapping Component", () => {
  it("render without any errors with no data", () => {
    renderComponent(props, appStore);
  });

  it("render without any errors with data", () => {
    renderComponent(props, appStore);
  });

  it("update connection on click of update button", () => {
    getSavedConnections.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(databases)
    );
    renderComponent(props, appStore);

    const updateButton = screen.getByTestId(
      "update-conn-button-fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6"
    );

    act(() => {
      fireEvent.click(updateButton);
    });

    const card = screen.getAllByTestId("data-connector-id")[0];
    act(() => {
      fireEvent.click(card);
    });

    const getLoadButton = screen.getByTestId(
      "load-button-66c59c8673063bd15218318e"
    );
    act(() => {
      fireEvent.click(getLoadButton);
    });
  });

  it("should open new connection", () => {
    renderComponent(props, appStore);
    act(() => {
      fireEvent.click(screen.getByTestId("new-connection-button"));
    });
  });

  it("new connection saving", () => {
    getSavedConnections.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(databases)
    );
    renderComponent(props, appStore);

    act(() => {
      fireEvent.click(screen.getByTestId("new-connection-button"));
    });

    const card = screen.getAllByTestId("data-connector-id")[0];
    act(() => {
      fireEvent.click(card);
    });

    const getLoadButton = screen.getByTestId(
      "load-button-66c59c8673063bd15218318e"
    );
    act(() => {
      fireEvent.click(getLoadButton);
    });
  });

  it("shoud remove mapping", () => {
    renderComponent(props, appStore);
    fireEvent.click(screen.getAllByRole("img")[2]);
  });

  it("close drawer", () => {
    renderComponent(props, appStore);
    act(() => {
      fireEvent.click(screen.getByLabelText("Close"));
    });
  });
  
  it("should initialize with job details in edit mode", () => {
  const editModeProps = {
    ...props,
    isScheduleEditMode: true,
    jobListDetails: {
      job_details: {
        replace_connections: {
          "test-id": {
            connectionId: "conn-123",
            connectionName: "Test Connection",
            connectionType: "postgres"
          }
        }
      }
    }
  };
  const editModeStore = mockStore({
    ...appStore.getState(),
    jobSchedule: {
      isScheduleEditMode: true,
      jobListDetails: editModeProps.jobListDetails
    }
  });
  renderComponent(editModeProps, editModeStore);
  expect(screen.getByText("Test Connection")).toBeInTheDocument();
});

it("should correctly combine edit mode and normal data sources", () => {
  const combinedProps = {
    ...props,
    isScheduleEditMode: true,
    jobListDetails: {
      job_details: {
        replace_connections: {
          "edit-mode-id": {
            connectionId: "edit-conn-123",
            connectionName: "Edit Mode Connection",
            connectionType: "postgres"
          }
        }
      }
    }
  };
  const combinedStore = mockStore({
    ...appStore.getState(),
    jobSchedule: {
      isScheduleEditMode: true,
      jobListDetails: combinedProps.jobListDetails
    }
  });
  renderComponent(combinedProps, combinedStore);
  expect(screen.getByText("Edit Mode Connection")).toBeInTheDocument();
  expect(screen.getByText("sample")).toBeInTheDocument();
});

it("should correctly show/hide tags based on mapping state", () => {
  const tagProps = {
    ...props,
    dataSource: [
      {
        key: "mapped-id",
        id: "mapped-id",
        fileName: "Mapped File",
        databaseAlias: "flat_files",
        mappedName: "Mapped Connection"
      },
      {
        key: "unmapped-id",
        id: "unmapped-id",
        fileName: "Unmapped File",
        databaseAlias: "flat_files"
      }
    ],
    mappedData: {
      "mapped-id": {
        connectionId: "conn-123",
        connectionName: "Mapped Connection",
        connectionType: "flat_files"
      }
    }
  };
  renderComponent(tagProps, appStore);
  expect(screen.getByText("Mapped Connection")).toBeInTheDocument();
  expect(screen.queryByText("Unmapped Connection")).not.toBeInTheDocument();
});
});
