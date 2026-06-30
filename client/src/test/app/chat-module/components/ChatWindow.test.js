import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import DefaultJobView from "../../../../app/chat-module/components/DefaultJobView.jsx";
import {
  createChat,
  getInformationApi,
  pipelineHistoryApi,
} from "../../../../apis/chatService.js";
import { addNewChatAction } from "../../../../store/actions/chatAction.js";
import ChatWindow from "../../../../app/chat-module/components/ChatWindow.jsx";
import { transformChatHistoryData } from "../../../../app/chat-module/utils.js";

const mockStore = configureStore();
window.HTMLElement.prototype.scrollIntoView = function () {};
// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

// mock for api service
jest.mock("../../../../apis/chatService.js", () => ({
  createChat: jest.fn(),
  getInformationApi: jest.fn(),
  pipelineHistoryApi: jest.fn(),
}));

jest.mock("../../../../app/chat-module/utils.js", () => ({
  transformChatHistoryData: jest.fn(),
}));

// component props
const mockProps = {
  showPreview: true,
};

// store mock
const store = mockStore({
  app: {
    previewState: true,
    userConfig: {
      role: "free",
    },
  },
  chat: {
    chatList: {
      "65d303abc6619e0b2bf7f114": {
        chat_id: "65d303abc6619e0b2bf7f114",
        chat_name: "Job 14",
        columnList: ["index", "customer_id", "first_name", "last_name"],
        selectedFiles: [
          {
            source_id: "662ba55788e28e8af8679eb1",
            alias: "customers-100",
            type: "csv",
          },
        ],
        loadedFiles: [
          {
            source_id: "662ba40f88e28e8af8679eb0",
            alias: "free-test-data",
            type: "csv",
          },
        ],
        fetchChatHistory: false,
      },
    },
    selectedChat: {
      chat_id: "65d303abc6619e0b2bf7f114",
      chat_name: "Job 14",
    },
  },
  messages: {
    allMessages: {
      "65d303abc6619e0b2bf7f114": [
        {
          isUser: false,
          text: "Final Output: Renamed column(s) city with current_city.",
          timestamp: 1714136590.032909,
          message_id: "6298256c-b588-4b33-82dc-e4b18141a910",
          time: "6:33 PM",
          id: "6298256c-b588-4b33-82dc-e4b18141a910",
        },
      ],
    },
  },
});
// reusable function for render
const renderComponent = (props, appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <ChatWindow {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Chat window component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should render the component without error", () => {
    renderComponent(mockProps, store);
  });

  it("send message to backend on click of send", () => {
    act(() => {
      renderComponent(mockProps, store);
    });

    act(() => {
      fireEvent.click(screen.getByTestId("send-button"));
    });
  });
});
