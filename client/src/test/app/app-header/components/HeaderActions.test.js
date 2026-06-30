import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import HeaderActions from "../../../../app/app-header/components/HeaderActions.jsx";
import {
  chatHistoryApi,
  clearChatMessageHistory,
  dataPreview,
  getInformationApi,
  pipelineHistoryApi,
  redoPipelineHistory,
  undoPipelineHistory,
  updateJobMode,
} from "../../../../apis/chatService.js";
import { handleSessionExpiry } from "../../../../utils/handleSessionExpiry.js";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../../apis/commonAPIs";
import { act } from "react-dom/test-utils";
import "../../../__mocks__/matchMedia.js";
import { setJobModal,setJobReadMode } from "../../../../store/actions/jobScheduleActions.js";
import { getStreamLogs } from "../../../../apis/jobScheduleService.js";

const mockStore = configureStore();
// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useLocation: () => ({
    search: "?test=1",
  }),
}));
jest.mock("../../../../apis/jobScheduleService.js", () => ({
  getStreamLogs: jest.fn(),
}));
jest.mock("../../../../store/actions/jobScheduleActions", () => ({
  setLogModal: jest.fn(),
  setLogValue: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

jest.mock("../../../../utils/handleSessionExpiry.js", () => ({
  handleSessionExpiry: jest.fn(),
}));
jest.mock("../../../../store/actions/jobScheduleActions.js", () => ({
  setJobModal: jest.fn().mockImplementation((value) => ({
    type: "SET_JOB_MODAL",
    payload: value,
  })),
  setJobReadMode: jest.fn().mockImplementation((value) => ({
    type: "SET_JOB_READ_MODE",
    payload: value,
  })),
}));
// mock for api service
jest.mock("../../../../apis/chatService.js", () => ({
  clearChatMessageHistory: jest.fn(),
  chatHistoryApi: jest.fn(),
  pipelineHistoryApi: jest.fn(),
  undoPipelineHistory: jest.fn(),
  redoPipelineHistory: jest.fn(),
  getInformationApi: jest.fn(),
  dataPreview: jest.fn(),
  updateJobMode: jest.fn(),
}));

// component props
const mockProps = {
  setOpenDbModal: jest.fn(),
  message: {
    success: jest.fn(),
    error: jest.fn(),
    useMessage: () => {
      return [{ open: jest.fn() }, jest.fn()];
    },
  },
  setOpenJobModal: jest.fn(),
};

// store mock
const store = mockStore({
  app: {
    previewState: true,
  },
  chat: {
    selectedChat: {
      chat_id: "65d303abc6619e0b2bf7f114",
      chat_name: "Job 20",
    },
    chatList: {
      "65d303abc6619e0b2bf7f114": {
        chat_id: "65d303abc6619e0b2bf7f114",
        chat_name: "Job 14",
        selectedFiles: [
          {
            alias: "alias",
            source_id: "source_id",
          },
        ],
      },
      "65d303abc6619e0b2bf7f115": {
        chat_id: "65d303abc6619e0b2bf7f115",
        chat_name: "Job 15",
      },
    },
    jobMode: "llm",
  },
  messages: {
    params: {
      offset: 100,
      limit: 30,
    },
  },
});

// store mock when previewstate is off
const updatedStore = mockStore({
  ...store.getState(),
  app: {
    previewState: false,
  },
});

const noSelectedChatStore = mockStore({
  ...updatedStore.getState(),
  chat: {
    selectedChat: {},
    chatList: {
      "65d303abc6619e0b2bf7f114": {
        chat_id: "65d303abc6619e0b2bf7f114",
        chat_name: "Job 14",
      },
      "65d303abc6619e0b2bf7f115": {
        chat_id: "65d303abc6619e0b2bf7f115",
        chat_name: "Job 15",
      },
    },
  },
});

const mockResetHistoryResponse = { message: "chat history has been reset" };
const mockHistoryResponse = {
  chat_history: [],
  has_more: false,
  selected_files: [],
  loaded_files: [],
  columns: [],
  metadata: {},
};
const mockPipelineHistoryRes = { success: true, history: [] };
const mockErrorResponse = { msg: "Something went wrong!!" };

// reusable function for render
const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <HeaderActions {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

const mockGetInfoResponse = {
  success: true,
  loaded_files: [{ alias: "file1" }],
  cwf: {
    alias: "file2",
  },
  metadata: ["col1", "col2"],
};

describe("Header File List component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should render connect to datasource icon, pipeline history icon, rest chat icon and trigger job icon", () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("connect-db-icon")).toBeInTheDocument();
    expect(screen.getByTestId("pipeline-history-id")).toBeInTheDocument();
    expect(screen.getByTestId("reset-chat-id")).toBeInTheDocument();
    expect(screen.getByTestId("trigger-job-id")).toBeInTheDocument();
  });

  it("should not toggle between preview and chat mode when user clicks on preview icon", () => {
    renderComponent(noSelectedChatStore, mockProps);
    fireEvent.click(screen.getByTestId("open-preview"));
  });

  it("should open the preview mode when user clicks on show preview icon", () => {
    renderComponent(updatedStore, mockProps);
    fireEvent.click(screen.getByTestId("open-preview"));
  });

  it("should open datasources listing drawer when user clicks on connect to datasources icon", () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("connect-db-icon"));
    expect(mockProps.setOpenDbModal).toHaveBeenCalled();
  });

  it("should not open datasources listing drawer when user clicks on connect to datasources icon with no selected chats", () => {
    renderComponent(noSelectedChatStore, mockProps);
    fireEvent.click(screen.getByTestId("connect-db-icon"));
    expect(mockProps.setOpenDbModal).not.toHaveBeenCalled();
  });

  it("should open trigger job modal when user clicks on trigger job icon", () => {
    const dispatchMock = jest.fn();
    useDispatchMock.mockReturnValue(dispatchMock);
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("trigger-job-id"));
    expect(dispatchMock).toHaveBeenCalledWith(setJobModal(true));
    expect(dispatchMock).toHaveBeenCalledWith(setJobReadMode(false));
  });

  it("should not open trigger job modal when user clicks on trigger job icon and there are no selected chats", () => {
    renderComponent(noSelectedChatStore, mockProps);
    fireEvent.click(screen.getByTestId("trigger-job-id"));
    expect(mockProps.setOpenJobModal).not.toHaveBeenCalled();
  });

  it("should show confirm popup when user clicks on clear chat history", async () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("reset-chat-id"));
    expect(
      screen.getByText(/Are you sure you want to clear the chat history for/i)
    ).toBeInTheDocument();
    expect(screen.getByText("Job 20")).toBeInTheDocument();
    expect(
      screen.getByText(/This action cannot be undone./i)
    ).toBeInTheDocument();
  });

  it("should close the confirm popup when user clicks on cancel", async () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("reset-chat-id"));
    fireEvent.click(screen.getByText(/Cancel/i));
    expect(clearChatMessageHistory).not.toHaveBeenCalled();
  });
  it("should clear the history when user clicks on ok from confirm popup and fetch the history and pipeline history again", async () => {
    clearChatMessageHistory.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockResetHistoryResponse)
    );
    chatHistoryApi.mockImplementation(({ onSuccess }) =>
      onSuccess(mockHistoryResponse)
    );
    pipelineHistoryApi.mockImplementation(({ onSuccess }) =>
      onSuccess(mockPipelineHistoryRes)
    );
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("reset-chat-id"));
    fireEvent.click(screen.getByText(/Ok/i));
  });

  it("should not fetch chat history and pipeline history with failed network or request issues", async () => {
    clearChatMessageHistory.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockResetHistoryResponse)
    );
    chatHistoryApi.mockImplementation(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("reset-chat-id"));
    fireEvent.click(screen.getByText(/Ok/i));
  });

  it("should not fetch pipeline history with failed network or request issues", async () => {
    clearChatMessageHistory.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockResetHistoryResponse)
    );
    chatHistoryApi.mockImplementation(({ onSuccess }) =>
      onSuccess(mockHistoryResponse)
    );
    pipelineHistoryApi.mockImplementation(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("reset-chat-id"));
    fireEvent.click(screen.getByText(/Ok/i));
  });

  it("should not clear the chat history with failed network requests", async () => {
    clearChatMessageHistory.mockImplementationOnce(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("reset-chat-id"));
    fireEvent.click(screen.getByText(/Ok/i));
    expect(handleSessionExpiry).toHaveBeenCalled();
  });

  it("should trigger undo when user clicks on undo", () => {
    undoPipelineHistory.mockImplementationOnce(({ onSuccess }) => {
      onSuccess("success");
    });
    chatHistoryApi.mockImplementationOnce((params) => {
      params.onSuccess("success");
    });
    dataPreview.mockImplementationOnce((params) => {
      params.onSuccess([{ sample: "data" }, { sample: "data" }]);
    });
    getInformationApi.mockImplementationOnce((params) => {
      params.onSuccess(mockGetInfoResponse);
    });

    renderComponent(store, mockProps);
    act(() => {
      fireEvent.click(screen.getByTestId("undo-id"));
    });
  });

  it("should trigger redo when user clicks on redo", () => {
    redoPipelineHistory.mockImplementationOnce(({ onSuccess }) => {
      onSuccess("success");
    });
    chatHistoryApi.mockImplementationOnce((params) => {
      params.onSuccess("success");
    });
    dataPreview.mockImplementationOnce((params) => {
      params.onSuccess([{ sample: "data" }, { sample: "data" }]);
    });
    getInformationApi.mockImplementationOnce((params) => {
      params.onSuccess(mockGetInfoResponse);
    });

    renderComponent(store, mockProps);
    act(() => {
      fireEvent.click(screen.getByTestId("redo-id"));
    });
  });

  it("should show vertical menu icon for screens less than 760px", async () => {
    global.innerWidth = 720;
    window.dispatchEvent(new Event("resize"));
    renderComponent(store, mockProps);
    act(() => {
      fireEvent.click(screen.getByTestId("menu-icon"));
    });
    await waitFor(() => {
      expect(screen.getByTestId("vertical-menu-id")).toBeInTheDocument();
    });
  });

  it("should show horizontal menu when screen size is 1080px", async () => {
    global.innerWidth = 1080;
    window.dispatchEvent(new Event("resize"));
    renderComponent(store, mockProps);
    await waitFor(() => {
      expect(screen.getByTestId("horizontal-menu")).toBeInTheDocument();
    });
  });

  it("dispatches actions and shows success message when modal confirmation is clicked", async () => {
    const storeWithYamlMode = mockStore({
      ...store.getState(),
      chat: {
        ...store.getState().chat,
        selectedChat: {
          chat_id: "65d303abc6619e0b2bf7f114",
          chat_name: "Job 20",
        },
        jobMode: "yaml",
      },
    });
    updateJobMode.mockImplementationOnce(({ payload, onSuccess }) => {
      expect(payload).toEqual({
        name: "llm",
        chatId: "65d303abc6619e0b2bf7f114",
      });
      onSuccess({ message: "Job Mode : LLM" });
    });
    const triggerGetInfoAPISpy = jest.spyOn(
      require("../../../../apis/commonAPIs"),
      "triggerGetInfoAPI"
    );
    const triggerPipelineHistorySpy = jest.spyOn(
      require("../../../../apis/commonAPIs"),
      "triggerPipelineHistory"
    );
    render(
      <reactRedux.Provider store={storeWithYamlMode}>
        <Router>
          <HeaderActions {...mockProps} />
        </Router>
      </reactRedux.Provider>
    );
    const closeBtn = screen.getByText("Close");
    fireEvent.click(closeBtn);
    const changeButton = await screen.findByText("Change");
    fireEvent.click(changeButton);

    await waitFor(() => {
      expect(triggerGetInfoAPISpy).toHaveBeenCalledWith(
        expect.any(Function),
        "65d303abc6619e0b2bf7f114"
      );
      expect(triggerPipelineHistorySpy).toHaveBeenCalledWith(
        expect.any(Function),
        "65d303abc6619e0b2bf7f114"
      );
    });
  });

  it("dispatches actions and shows success message when modal confirmation is clicked", async () => {
    const storeWithYamlMode = mockStore({
      ...store.getState(),
      chat: {
        ...store.getState().chat,
        selectedChat: {
          chat_id: "65d303abc6619e0b2bf7f114",
          chat_name: "Job 20",
        },
        jobMode: "yaml",
      },
    });
    updateJobMode.mockImplementationOnce(({ payload, onSuccess }) => {
      expect(payload).toEqual({
        name: "llm",
        chatId: "65d303abc6619e0b2bf7f114",
      });
      onSuccess({ message: "Job Mode : LLM" });
    });
    const triggerGetInfoAPISpy = jest.spyOn(
      require("../../../../apis/commonAPIs"),
      "triggerGetInfoAPI"
    );
    const triggerPipelineHistorySpy = jest.spyOn(
      require("../../../../apis/commonAPIs"),
      "triggerPipelineHistory"
    );
    render(
      <reactRedux.Provider store={storeWithYamlMode}>
        <Router>
          <HeaderActions {...mockProps} />
        </Router>
      </reactRedux.Provider>
    );
    const closeBtn = screen.getByText("Close");
    fireEvent.click(closeBtn);
    const changeButton = await screen.findByText("Change");
    fireEvent.click(changeButton);
    await waitFor(() => {
      expect(triggerGetInfoAPISpy).toHaveBeenCalledWith(
        expect.any(Function),
        "65d303abc6619e0b2bf7f114"
      );
      expect(triggerPipelineHistorySpy).toHaveBeenCalledWith(
        expect.any(Function),
        "65d303abc6619e0b2bf7f114"
      );
    });
  });
  it("should render Run Now Logs icon", () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("run-now-logs-id")).toBeInTheDocument();
  });

  it("should render Run Now Logs icon", () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("run-now-logs-id")).toBeInTheDocument();
  });

  it("should show popover when Run Now Logs icon is clicked", async () => {
    renderComponent(store, mockProps);
    fireEvent.click(screen.getByTestId("run-now-logs-id"));
    await waitFor(() => {
      expect(screen.getByText("Run Now Logs")).toBeInTheDocument();
    });
  });

  it('should show "No Run now logs found!" when history is empty', () => {
    const emptyHistoryStore = mockStore({
      ...store.getState(),
      jobSchedule: { runHistory: {} },
    });
    renderComponent(emptyHistoryStore, mockProps);
    fireEvent.click(screen.getByTestId("run-now-logs-id"));
    expect(screen.getByText("No Run now logs found!")).toBeInTheDocument();
  });

  it("should display a list of run logs when history exists", () => {
    const storeWithRunHistory = mockStore({
      ...store.getState(),
      jobSchedule: {
        runHistory: {
          "65d303abc6619e0b2bf7f114": [
            { run_id: "run1", timestamp: "2024-01-01T00:00:00Z", local: false },
          ],
        },
      },
    });
    renderComponent(storeWithRunHistory, mockProps);
    fireEvent.click(screen.getByTestId("run-now-logs-id"));
  });

  it("should open LogViewerDrawer when a run log is clicked", async () => {
    const storeWithRunHistory = mockStore({
      ...store.getState(),
      jobSchedule: {
        runHistory: {
          "65d303abc6619e0b2bf7f114": [
            { run_id: "run1", timestamp: "2024-01-01T00:00:00Z", local: false },
          ],
        },
      },
    });
    getStreamLogs.mockImplementation(({ onSuccess }) =>
      onSuccess({ logs: "Sample log content" })
    );
    renderComponent(storeWithRunHistory, mockProps);
    fireEvent.click(screen.getByTestId("run-now-logs-id"));
  });
});
