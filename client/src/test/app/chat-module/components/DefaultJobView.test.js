import React from "react";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import DefaultJobView from "../../../../app/chat-module/components/DefaultJobView.jsx";
import { createChat } from "../../../../apis/chatService.js";
import { addNewChatAction } from "../../../../store/actions/chatAction.js";

const mockStore = configureStore();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

// mock for api service
jest.mock("../../../../apis/chatService.js", () => ({
  createChat: jest.fn(),
}));

// component props
const mockProps = {
  setShowDefaultPage: jest.fn(),
};

// store mock
const store = mockStore({
  app: {
    user: {
      id: "1234",
      firstName: "Alice",
    },
  },
  chat: {
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
// reusable function for render
const renderComponent = (props, appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <DefaultJobView {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Default Job view component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should render the component without error", () => {
    renderComponent(mockProps, store);
    expect(screen.getByTestId("default-job-view-id")).toBeInTheDocument();
  });

  it("should create a new job when user clicks on create job button with success network request", async () => {
    renderComponent(mockProps, store);
    createChat.mockImplementationOnce((params) => {
      params.onSuccess("");
    });
    fireEvent.click(screen.getByTestId("create-job-id"));
    await waitFor(() => {
      // Check that create chat api has been called with the correct arguments
      expect(createChat).toHaveBeenCalledWith({
        payload: {
          chat_name: "Job 16",
          user_id: "1234",
        },
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
    });
  });

  it("should not create a new job when user clicks on create job button with failed network request", () => {
    renderComponent(mockProps, store);
    createChat.mockImplementationOnce((params) => {
      params.onError("");
    });
    fireEvent.click(screen.getByTestId("create-job-id"));
  });
});
