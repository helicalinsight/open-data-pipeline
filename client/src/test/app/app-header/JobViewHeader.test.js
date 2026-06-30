import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import JobViewHeader from "../../../app/app-header/index.jsx";
import MockedSocket from "socket.io-mock";
import configureStore from "redux-mock-store";
import { Provider } from "react-redux";
import { setSidebarState } from "../../../store/actions/appActions";
import "@testing-library/jest-dom";
import "../../__mocks__/matchMedia.js";

jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));

const chatRoutes = {
  chat: "/chat",
  datasource: "/datasource",
  schedule: "/schedule",
  audit: "/audit",
  setting: "/setting",
};

const mockStore = configureStore();

let userConfig = {
  chat: ["jobs", "create", "schedule"],
  job: ["histroy", "dataPreview", "reset", "load", "trigger"],
  datasources: [
    "flat_files",
    "redshift",
    "mysql",
    "snowflake",
    "postgres",
    "astra",
    "cassandra",
  ],
};

const getMockStore = ({ isJobScheduled = false, individualJob = false, isDetailedView = false }) => {
  return mockStore({
    app: {
      isSidebarCollapsed: false,
      userConfig,
      jobHelpInfo: {
        python: "",
        yaml: "",
      },
    },
    chat: {
      selectedChat: {
        chat_id: "65e9a2dfec340145378dfd52",
        chat_name: "Job 20",
      },
      chatList: {
        "65e9a2dfec340145378dfd52": {
          chat_id: "65e9a2dfec340145378dfd52",
          chat_name: "Job 20",
          isJobScheduled,
          loadedFiles: [
            {
              source_id: "65e9a33aec340145378dfd54",
              alias: "free-test-data",
              type: "csv",
            },
          ],
        },
      },
      jobMode: "test-mode", 
    },
      dms: {                   
      step: 0,
      selectedDmsChat: null,
    },
    messages: {
      params: {
        offset: 100,
        limit: 30,
      },
    },
    database: {
      datasources: [],
      savedConnections: [],
    },
    audit: { 
      isDetailedView: isDetailedView,
    },
    jobSchedule: { 
      individualJob: individualJob,
      dagInfo: { 
        basic_info: { 
          job_name: "Test Job" 
        } 
      },
      jobModal: false,
    },
  });
};

const store = getMockStore({ isJobScheduled: false });

const mockSidebarCollapsedStore = mockStore({
  ...store.getState(),
  app: {
    ...store.getState().app,
    isSidebarCollapsed: true,
  },
});

let socket = new MockedSocket();

const renderComponent = (appStore, pathname = "/") => {
  return render(
    <Provider store={appStore}>
      <Router initialEntries={[pathname]}>
        <JobViewHeader socket={socket} />
      </Router>
    </Provider>
  );
};

describe("JobViewHeader Component", () => {
  const useDispatchMock = jest.spyOn(require("react-redux"), "useDispatch");

  beforeEach(() => {
    useDispatchMock.mockClear();
  });

  it("should show the menu unfold icon when sidebar is collapsed", () => {
    renderComponent(mockSidebarCollapsedStore);
    expect(screen.getByTestId("menu-unfold-id")).toBeInTheDocument();
  });

  it("should toggle sidebar when menu icon is clicked", () => {
    const mockDispatch = jest.fn();
    useDispatchMock.mockReturnValue(mockDispatch);
    renderComponent(mockSidebarCollapsedStore);
    fireEvent.click(screen.getByTestId("menu-unfold-id"));
    expect(mockDispatch).toHaveBeenCalledWith(setSidebarState(false));
  });

  it("should display the correct breadcrumb for /datasource route", () => {
    renderComponent(store, chatRoutes.datasource);
    expect(screen.getByText(/Home/)).toBeInTheDocument();
  });

  it("should show correct breadcrumb for datasource detail page", () => {
    const mockStoreWithDatasource = mockStore({
      ...store.getState(),
      database: {
        datasources: [{ driver: "test-id", name: "Test Database" }],
      },
    });
    renderComponent(mockStoreWithDatasource, "/datasource/test-id");
    expect(screen.getByText(/Home/)).toBeInTheDocument();
  });

  it("should show correct breadcrumb for individual job schedule", () => {
    const mockStoreWithJob = getMockStore({ individualJob: true });
    renderComponent(mockStoreWithJob, chatRoutes.schedule);
    expect(screen.getByText(/Home/)).toBeInTheDocument();
  });

  it("should display file list when in chat view with search params", () => {
    renderComponent(store, `${chatRoutes.chat}?chatId=test`);
  });

  it("should show correct breadcrumb for user setup route", () => {
    renderComponent(store, "/user-setup");
    expect(screen.getByText(/Home/)).toBeInTheDocument();
  });
});