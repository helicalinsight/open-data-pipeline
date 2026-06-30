import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import MessageLayout from "../../../app/message-module";
import "../../__mocks__/matchMedia";

const mockStore = configureStore();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

const store = mockStore({
  app: {
    previewState: false,
  },
});

const updatedstore = mockStore({
  app: {
    previewState: true,
  },
});

const mockbotProps = {
  chatItem: {
    message_id: "3fd4b288-39fd-40c5-814b-45610013aeaa",
    isUser: false,
    time: "11:52 AM",
    text: "Welcome to Ask On Data. The most Advanced Data Engineering AI Tool! We're thrilled to have you here. How can we assist you today?",
    typing: false,
  },
};

const mockUserProps = {
  chatItem: {
    isUser: true,
    text: "Rename Columns",
    timestamp: 1709810490.702004,
    message_id: "3e4f16a58b694a05a3a73d112b509e4b",
    time: "11:53 AM",
    id: "3e4f16a58b694a05a3a73d112b509e4b",
  },
};
// reusable function for render
const renderComponent = (props, appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <MessageLayout {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Download File component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should show connected message when socket is connected", () => {
    renderComponent(
      {
        chatItem: {
          type: "connected",
          text: "Connected",
        },
      },
      store
    );
    expect(screen.getByText(/Connected/i)).toBeInTheDocument();
  });

  it("should show disconnected message when socket is connected", () => {
    renderComponent(
      {
        chatItem: {
          type: "disconnected",
          text: "Disconnected",
        },
      },
      store
    );
    expect(screen.getByText(/Disconnected/i)).toBeInTheDocument();
  });

  it("should show question icon when message or text is not from user", () => {
    renderComponent(
      {
        chatItem: {
          isUser: false,
        },
      },
      store
    );
    expect(screen.getByTestId("bot-message")).toBeInTheDocument();
  });

  it("should show message box at left when message is from bot", () => {
    renderComponent(mockbotProps, store);
    expect(screen.getByTestId("message-id")).toBeInTheDocument();
  });

  it("should show message box at right when message is from user", () => {
    renderComponent(mockUserProps, updatedstore);
    expect(screen.getByTestId("message-id")).toBeInTheDocument();
  });

  it("should copy message text when copy button is clicked", async () => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(),
      },
    });
    renderComponent(mockbotProps, store);
    const messageContainer = screen
      .getByTestId("message-id")
      .closest(".message-container");
    fireEvent.mouseEnter(messageContainer);
    const copyButton = await screen.findByRole("button");
    fireEvent.click(copyButton);
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        "Welcome to Ask On Data. The most Advanced Data Engineering AI Tool! We're thrilled to have you here. How can we assist you today?"
      );
      expect(screen.getByText("Copied!")).toBeInTheDocument();
    });
  });

  it("should show different width when in preview state", () => {
    renderComponent(mockbotProps, updatedstore);
    const messageBox = screen.getByTestId("message-id").firstChild;
    expect(messageBox).toHaveStyle("maxWidth: 95%");
  });
});
