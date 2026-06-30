import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";

import configureStore from "redux-mock-store";
import SuppportBot from "../../../../../app/app-header/components/job-schedule/components/SuppportBot";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";
import { resetBot, triggerBot } from "../../../../../apis/jobScheduleService";

jest.mock("../../../../../apis/jobScheduleService", () => ({
  triggerBot: jest.fn(),
  resetBot: jest.fn(),
}));

const mockStore = configureStore();

const appStore = mockStore({});

const props = {
  messages: [
    {
      isUser: false,
      text: "text",
    },
    {
      isUser: true,
      text: "text",
    },
  ],
  setMessages: jest.fn(),
  selectedChat: {
    chat_id: "chat_id",
  },
  setEditorValue: jest.fn(),
};

const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <SuppportBot {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Custom Scheduling  component", () => {
  it("render the component without erros", () => {
    renderComponent(appStore, props);
  });

  it("should the message to backend and API Success", () => {
    triggerBot.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true, code: "code", message: "message" })
    );
    renderComponent(appStore, props);

    const input = screen.getByTestId("user-test-input");
    act(() => {
      fireEvent.change(input, { target: { value: "new value" } });
    });

    const sendButton = screen.getByTestId("send-message-button");
    act(() => {
      fireEvent.click(sendButton);
    });
  });

  it("should the message to backend and API failed", () => {
    triggerBot.mockImplementationOnce(({ onError }) => onError("error"));
    renderComponent(appStore, props);

    const input = screen.getByTestId("user-test-input");
    act(() => {
      fireEvent.change(input, { target: { value: "new value" } });
    });

    const sendButton = screen.getByTestId("send-message-button");
    act(() => {
      fireEvent.click(sendButton);
    });
  });

  it("it should not send message to backend when text is empty", () => {
    renderComponent(appStore, props);
    act(() => {
      const sendButton = screen.getByTestId("send-message-button");
      fireEvent.click(sendButton);
    });
  });

  it("should the trigger reset API : success ", () => {
    resetBot.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    renderComponent(appStore, props);

    const resetButton = screen.getByTestId("reset-messages-button");
    act(() => {
      fireEvent.click(resetButton);
    });
  });

  it("should the trigger reset API : failed ", () => {
    resetBot.mockImplementationOnce(({ onError }) => onError("error"));
    renderComponent(appStore, props);

    const resetButton = screen.getByTestId("reset-messages-button");
    act(() => {
      fireEvent.click(resetButton);
    });
  });
});
