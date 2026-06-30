import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter as Router, MemoryRouter } from "react-router-dom";
import { Form } from "antd";
import {
  fecthDbsAndTables,
  getSavedConnections,
} from "../../../../../apis/databaseService";
import JobData from "../../../../../app/app-header/components/job-schedule/components/JobData";
import configureStore from "redux-mock-store";
import "@testing-library/jest-dom";
import * as reactRedux from "react-redux";
import "../../../../__mocks__/matchMedia";

jest.mock("../../../../../apis/databaseService", () => ({
  fecthDbsAndTables: jest.fn(),
  getSavedConnections: jest.fn(),
}));

const mockStore = configureStore();

const appStore = mockStore({
  chat: {
    selectedChat: {
      chat_name: "Job1",
      chat_id: "Job1",
    },
    chatList: {
      Job1: {
        loadedFiles: [
          {
            alias: "2017_Order_Data",
            type: "xlsx",
            source_id: "66f1851054cb9e3659c390bd",
          },
          {
            alias: "split_test_data",
            type: "csv",
            source_id: "66f26e0a37760e0a0ddea063",
          },
        ],
      },
    },
    jobMode: "sql",
    yamlSave: false,
  },
  jobSchedule: {
    isScheduleReadMode: false,
  },
  dms: {
    selectedServiceType: null,
  },
});

const FormWrapper = (props) => {
  const [form] = Form.useForm();
  return <JobData jobDataForm={form} {...props} />;
};

const renderComponent = (appStore, props) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <MemoryRouter initialEntries={[`?chat=${"Job1"}`]}>
        <FormWrapper {...props} />
      </MemoryRouter>
    </reactRedux.Provider>
  );
};

const appProps = {
  handleScheduleJob: jest.fn(),
  setCurrent: jest.fn(),
  setJobData: jest.fn(),
  loading: false,
  executionType: "Pipeline",
  setExecutionType: jest.fn(),
  setOpenDbDrawer: jest.fn(),
  dataSource: [
    {
      key: "fd681b18-8cc3-46ce-afb7-1d260e967960",
      pipeline: "read_files",
      databaseAlias: "flat_files",
      fileName: "enrollments",
      id: "fd681b18-8cc3-46ce-afb7-1d260e967960",
    },
    {
      key: "66e28124c92f4b5d853b696b",
      fileName: "google_1",
      id: "66e28124c92f4b5d853b696b",
      databaseAlias: "google_sheets",
    },
  ],
  setOpenJobModal: jest.fn(),
};

const savedConnectionsMockRes = {
  success: true,
  databases: [
    {
      _id: "66e28124c92f4b5d853b696b",
      alias: "google_1",
      type: "google_sheets",
    },
    {
      _id: "66e3d3a38e586e5b800627bc",
      alias: "Test",
      type: "google_sheets",
    },
    {
      _id: "66e3ec00036252b0023a5f67",
      alias: "Postgres Connector 2",
      type: "google_sheets",
    },
    {
      _id: "66e3edbb2601d90a3465f9f9",
      alias: "Postgres Connector 2",
      type: "google_sheets",
    },
  ],
  msg: "Fetched connections successfully.",
};

const listCatalogMockRes = {
  success: true,
  dataCatlog: [
    {
      title: "demo_connector",
      value: "demo_connector",
      children: [
        {
          title: "film",
          value: "film",
          children: [],
        },
      ],
    },
  ],
  msg: "Data catalog fetched successfully from google_sheets.",
};

describe("JobData component", () => {
  beforeEach(() => {
    getSavedConnections.mockImplementation(({ onSuccess }) => {
      onSuccess(savedConnectionsMockRes);
    });
    fecthDbsAndTables.mockImplementation(({ onSuccess }) => {
      onSuccess(listCatalogMockRes);
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without errors", () => {
    renderComponent(appStore, appProps);
    expect(screen.getByTestId("job-data-form")).toBeInTheDocument();
  });

  it("renders the Engine Type dropdown with default value", () => {
    renderComponent(appStore, appProps);
    const engineTypeDropdown = screen.getByLabelText("Engine Type");
    expect(engineTypeDropdown).toBeInTheDocument();
  });

 it("allows changing Engine Type value", async () => {
  jest.setTimeout(10000)
  renderComponent(appStore, appProps);
  const engineTypeDropdown = await screen.findByLabelText("Engine Type");
  await act(async () => {
    await userEvent.click(engineTypeDropdown);
  });
  const options = await screen.findAllByRole("option");
  expect(options.length).toBeGreaterThan(0);
  await act(async () => {
    await userEvent.click(options[1]);
  });
}, 10000);

  it("renders the notification switch", () => {
    renderComponent(appStore, appProps);
    expect(screen.getByRole("switch")).toBeInTheDocument();
  });

  it("toggles notification switch", async () => {
    renderComponent(appStore, appProps);
    const notificationSwitch = screen.getByRole("switch");
    
    expect(notificationSwitch).not.toBeChecked();
    
    await act(async () => {
      await userEvent.click(notificationSwitch);
    });
    
    expect(notificationSwitch).toBeChecked();
  });

  it("renders Schedule Name input field", () => {
    renderComponent(appStore, appProps);
    expect(screen.getByPlaceholderText("Schedule Name")).toBeInTheDocument();
  });

  it("renders Destination dropdown", () => {
    renderComponent(appStore, appProps);
  });

  it("click on update connections button", () => {
    renderComponent(appStore, appProps);
    act(() => {
      fireEvent.click(screen.getByTestId("update-connections-btn"));
    });
    expect(appProps.setOpenDbDrawer).toHaveBeenCalledWith(true);
  });

  it("trigger onclick of back button", () => {
    renderComponent(appStore, appProps);
    act(() => {
      fireEvent.click(screen.getByTestId("back-btn"));
    });
    expect(appProps.setCurrent).toHaveBeenCalled();
  });

  it("throw error when fields not filled on next button click", async () => {
    renderComponent(appStore, appProps);
    act(() => {
      fireEvent.click(screen.getByTestId("next-button"));
    });
  });

  it("throw error when fields not filled on run now button click", async () => {
    renderComponent(appStore, appProps);
    act(() => {
      fireEvent.click(screen.getByTestId("run-now-button"));
    });
  });

  it("renders correctly in read-only mode", () => {
    const readOnlyStore = mockStore({
      ...appStore.getState(),
      jobSchedule: {
        isScheduleReadMode: true,
        jobListDetails: {
          schedule_name: "Test Schedule",
          job_details: {
            files_list: [{ alias: "test_file" }],
            destination: [{
              destination: "database",
              connection_name: "test_connection",
              catalog: "test_catalog"
            }]
          },
          files_list: [{ alias: "test_file" }]
        }
      }
    });
    renderComponent(readOnlyStore, appProps);
  });
});
describe("Execution Type functionality", () => {
  it("should not render Execution Type dropdown in normal mode (not edit mode)", () => {
    renderComponent(appStore, appProps);
    expect(screen.queryByLabelText("Execution Type")).not.toBeInTheDocument();
  });

  it("should render Execution Type dropdown in schedule edit mode with meta_schedule_version = 1", () => {
    const editModeStore = mockStore({
      ...appStore.getState(),
      jobSchedule: {
        isScheduleEditMode: true,
        jobListDetails: {
          meta_schedule_version: 1,
          job_details: {
            execution_type: "pipeline",
            export_files_list: [],
            destination: [{
              destination: "database",
              connection_name: "test_connection",
              catalog: "test_catalog"
            }],
            files_list: [
              { alias: "test_file", source_id: "test_id" }
            ]
          },
          schedule_name: "Test Schedule"
        }
      }
    });
    renderComponent(editModeStore, appProps);
    expect(screen.getByLabelText("Execution Type")).toBeInTheDocument();
  });

  it("should not render Execution Type dropdown in schedule edit mode with meta_schedule_version != 1", () => {
    const editModeStore = mockStore({
      ...appStore.getState(),
      jobSchedule: {
        isScheduleEditMode: true,
        jobListDetails: {
          meta_schedule_version: 2,
          job_details: {
            execution_type: "pipeline",
            export_files_list: [],
            destination: [{
              destination: "database",
              connection_name: "test_connection",
              catalog: "test_catalog"
            }],
            files_list: [
              { alias: "test_file", source_id: "test_id" }
            ]
          },
          schedule_name: "Test Schedule"
        }
      }
    });
    renderComponent(editModeStore, appProps);
    expect(screen.queryByLabelText("Execution Type")).not.toBeInTheDocument();
  });

  it("should have all execution type options available", async () => {
    const editModeStore = mockStore({
      ...appStore.getState(),
      jobSchedule: {
        isScheduleEditMode: true,
        jobListDetails: {
          meta_schedule_version: 1,
          job_details: {
            execution_type: "pipeline",
            export_files_list: [],
            destination: [{
              destination: "database",
              connection_name: "test_connection",
              catalog: "test_catalog"
            }],
            files_list: [
              { alias: "test_file", source_id: "test_id" }
            ]
          },
          schedule_name: "Test Schedule"
        }
      }
    });
    renderComponent(editModeStore, appProps);
    const executionTypeDropdown = screen.getByLabelText("Execution Type");
    await act(async () => {
      await userEvent.click(executionTypeDropdown);
    });
    const options = await screen.findAllByRole("option");
    const optionTexts = options.map(option => option.textContent);
    expect(optionTexts).toContain("Pipeline");
  });
});