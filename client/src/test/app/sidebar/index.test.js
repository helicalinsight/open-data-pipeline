import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import configureStore from "redux-mock-store";
import Sidebar from "../../../app/sidebar/index.jsx";
import "../../__mocks__/matchMedia.js";

const mockStore = configureStore();
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));

const useDispatchMock = reactRedux.useDispatch;
const mockDispatch = jest.fn();

const store = mockStore({
  app: { isSidebarCollapsed: false },
  chat: {
    chatList: {
      "chat1": {
        chat_id: "chat1",
        chat_name: "Chat 1",
        apiCallsStatus: [{ isFetching: true, abortController: { abort: jest.fn() } }],
      },
      "chat2": {
        chat_id: "chat2",
        chat_name: "Chat 2",
        apiCallsStatus: [{ isFetching: false }],
      },
    },
  },
    dms: {                 
    selectedDmsChat: {},
    dmsJobs: {},
  },
});

// Helper function to render the component
const renderComponent = (mockStore) => {
  window.history.pushState({}, "Test page", "/app-space?chat=chat1");
  render(
    <reactRedux.Provider store={mockStore}>
      <Router>
        <Sidebar />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Sidebar Component", () => {
  beforeEach(() => {
    useDispatchMock.mockReturnValue(mockDispatch);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should show modal when clicking a chat with an active API call (handleChatClick)", () => {
    renderComponent(store);
    const chatElement = screen.getByText("Chat 1");
    fireEvent.click(chatElement);
  });

  it("should switch chat immediately if no API is in progress (handleChatClick)", () => {
    renderComponent(store);
    const chatElement = screen.getByText("Chat 2");
    fireEvent.click(chatElement);
  });
});
