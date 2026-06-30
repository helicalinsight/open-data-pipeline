import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import { runCode } from "../../../../../apis/jobScheduleService";

import ExecuteModal from "../../../../../app/app-header/components/job-schedule/components/ExecuteModal";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";

jest.mock("../../../../../apis/jobScheduleService", () => ({
  runCode: jest.fn(),
}));

const mockStore = configureStore();

const appStore = mockStore({
  chat: {
    selectedChat: {
      chat_id: "absd",
      chat_id: "Job1",
    },
  },
});

const props = {
  open: true,
  setOpen: jest.fn(),
};

const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <ExecuteModal {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Custom Scheduling  component", () => {
  it("render the component without erros", () => {
    renderComponent(appStore, props);
  });

  it("should trigger run code API:sucess", () => {
    runCode.mockImplementationOnce(({ onSuccess }) => {
      onSuccess({
        success: true,
      });
    });
    renderComponent(appStore, props);
    act(() => {
      fireEvent.click(screen.getByTestId("modal-ok-button"));
    });
  });

  it("should trigger run code API:failed", () => {
    runCode.mockImplementationOnce(({ onSuccess }) => {
      onSuccess({
        success: false,
      });
    });
    renderComponent(appStore, props);
    act(() => {
      fireEvent.click(screen.getByTestId("modal-ok-button"));
    });
  });

  it("should trigger run code API:error", () => {
    runCode.mockImplementationOnce(({ onError }) => {
      onError("error");
    });
    renderComponent(appStore, props);
    act(() => {
      fireEvent.click(screen.getByTestId("modal-ok-button"));
    });
  });

  it("should not trigger run code API on cancel", () => {
    renderComponent(appStore, props);
    act(() => {
      fireEvent.click(screen.getByTestId("modal-cancel-button"));
    });
  });
});
