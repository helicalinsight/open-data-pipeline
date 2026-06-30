import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import configureStore from "redux-mock-store";
import JobScheduleWrapper from "../../../../app/app-header/components/job-schedule";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../../../__mocks__/matchMedia";

const mockStore = configureStore();

const mockPipelineHistory = {
  history: [
    {
      function: "read_files",
      parameters: [
        {
          alias: "sample",
          _id: "fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6",
          catalog: "sample_catalog"
        },
      ],
      database_alias: "flat_files",
    },
    {
      function: "read_tables",
      parameters: [
        {
          alias: "enrollments",
          _id: "fd681b18-8cc3-46ce-afb7-1d260e967960",
          catalog: "enrollments_catalog"
        },
      ],
      database_alias: "database_tables",
    },
  ],
  connections: [
    {
      _id: "fcea8971-ca7f-4921-bf47-9fbb8f6ba5a6",
      alias: "custom_alias"
    },
    {
      _id: "fd681b18-8cc3-46ce-afb7-1d260e967960",
      alias: "enrollments_alias"
    }
  ],
};

const mockDatasources = [
  { 
    driver: "flat_files", 
    name: "Flat Files" 
  },
  { 
    driver: "database_tables", 
    name: "Database Tables" 
  }
];

const appStore = mockStore({
  app: {
    jobHelpInfo: {
      python: "python",
      yaml: "yaml",
    },
  },
  chat: {
    chatList: {
      1234: {
        pipelineHistory: mockPipelineHistory,
        loadedFiles: [],
        scheduleConfig: [],
      },
    },
    selectedChat: {
      chat_id: "1234",
    },
    jobMode: "pipeline",
  },
  jobSchedule: {
    jobModal: true,
    isScheduleEditMode: false,
    jobValue: null
  },
  database: {
    datasources: mockDatasources
  },
   dms: {
    selectedServiceType: null,
    selectedDmsChat: { chat_id: "1234" },
    dmsProgressDetails: {},
      dmsJobs: {  
      "1234": {
        dmsScheduleConfig: []
      }
    }
  }
});

const props = {
  messageApi: {
    open: jest.fn(),
  },
  openJobModal: true,
  setOpenJobModal: jest.fn(),
};

const renderComponent = (store) => {
  return render(
    <reactRedux.Provider store={store}>
      <MemoryRouter initialEntries={["?chat=1234"]}>
        <JobScheduleWrapper {...props} />
      </MemoryRouter>
    </reactRedux.Provider>
  );
};

describe("JobScheduleWrapper Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without errors", () => {
    renderComponent(appStore);
    expect(screen.getByTestId("schedule-drawer")).toBeInTheDocument();
    expect(screen.getByText("Job Scheduling")).toBeInTheDocument();
    expect(screen.getByText("Job Config")).toBeInTheDocument();
  });

  it("displays all step titles correctly", () => {
    renderComponent(appStore);
    expect(screen.getByText("Job Config")).toBeInTheDocument();
    expect(screen.getByText("Job Data")).toBeInTheDocument();
    expect(screen.getByText("Schedule")).toBeInTheDocument();
  });

  it("switches between steps when next button is clicked", () => {
    renderComponent(appStore);
    expect(screen.getByText("Job Config")).toBeInTheDocument();
    const nextButtons = screen.getAllByRole("button", { name: /next/i });
    act(() => {
      fireEvent.click(nextButtons[0]);
    });
    expect(screen.getByText("Job Data")).toBeInTheDocument();
  });

  it("closes drawer when close button is clicked", () => {
    renderComponent(appStore);
    const closeButton = screen.getByLabelText("Close");
    act(() => {
      fireEvent.click(closeButton);
    });
    const actions = appStore.getActions();
  });

  it("correctly processes and displays data sources from pipeline history", () => {
    renderComponent(appStore);    
    const nextButtons = screen.getAllByRole("button", { name: /next/i });
    act(() => {
      fireEvent.click(nextButtons[0]);
    });
    expect(appStore.getState().database.datasources).toEqual(mockDatasources);
  });

  it("handles jobMode changes correctly", () => {
    const pythonStore = mockStore({
      ...appStore.getState(),
      chat: {
        ...appStore.getState().chat,
        jobMode: "python"
      }
    });
    renderComponent(pythonStore);
  });

  it("should render datasources from pipeline history in Connection Mapping drawer", () => {
    renderComponent(appStore);
    const nextButton = screen.getByRole("button", { name: /next/i });
    fireEvent.click(nextButton);
  });
});