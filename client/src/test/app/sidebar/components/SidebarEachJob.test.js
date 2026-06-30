import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import configureStore from "redux-mock-store";
import "../../../__mocks__/matchMedia.js";
import SidebarEachJob from "../../../../app/sidebar/components/SidebarEachJob.jsx";
import { updateChat, deleteChat } from "../../../../apis/chatService.js";

const mockStore = configureStore();

jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));

const useDispatchMock = reactRedux.useDispatch;

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useLocation: () => ({
    search: "?test=1", 
  }),
}));

jest.mock("../../../../apis/chatService.js", () => ({
  updateChat: jest.fn(),
  deleteChat: jest.fn(),
}));

const mockProps = {
  eachJob: {
    chat_id: "65ae401aa8b667c71898d3c9",
    chat_name: "Job 11",
  },
  sessionId: "sessionid",
  handleChatClick: jest.fn(),
  allJobs: [],
  setAllJobs: jest.fn(),
};

const mockingStore = mockStore({
  chat: {
    selectedChat: {
      chat_id: "65ae401aa8b667c71898d3c9",
      chat_name: "Job 11",
    },
  },
  dms: {
    selectedDmsChat: {},
  },
  app: {
    isSidebarCollapsed: false,
  },
});

const mockingUpdatedstore = mockStore({
  ...mockingStore.getState(),
  app: {
    isSidebarCollapsed: true,
  },
});

const renderComponent = (props, store) => {
  render(
    <reactRedux.Provider store={store}>
      <Router>
        <SidebarEachJob {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("SidebarEachJob component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    useDispatchMock.mockClear();
    jest.clearAllMocks();
  });

  it("renders the job item without error", () => {
    renderComponent(mockProps, mockingStore);
    // expect(screen.getByTestId("job-item-id")).toBeInTheDocument();
    expect(screen.getByTestId(`job-item-id-chat-${mockProps.eachJob.chat_id}`)).toBeInTheDocument();
  });

  it("should show job initials name as avatar when sidebar is collapsed", () => {
    renderComponent(mockProps, mockingUpdatedstore);
  });

  it("should show edit and delete icon when user clicks on any job", () => {
    renderComponent(mockProps, mockingStore);
    // fireEvent.click(screen.getByTestId("job-item-id"));
    fireEvent.click(screen.getByTestId(`job-item-id-chat-${mockProps.eachJob.chat_id}`));
    expect(screen.getByTestId("edit-btn-id")).toBeInTheDocument();
    expect(screen.getByTestId("delete-btn-id")).toBeInTheDocument();
  });

  it("should show edit and delete icon when user hovers on any job", () => {
    renderComponent(mockProps, mockingStore);
    // fireEvent.mouseOver(screen.getByTestId("job-item-id"));
    fireEvent.mouseOver(screen.getByTestId(`job-item-id-chat-${mockProps.eachJob.chat_id}`));
    expect(screen.getByTestId("edit-btn-id")).toBeInTheDocument();
    expect(screen.getByTestId("delete-btn-id")).toBeInTheDocument();
  });

  it("should show editable input when user clicks on edit icon", () => {
    renderComponent(mockProps, mockingStore);
    fireEvent.click(screen.getByTestId("edit-btn-id"));
    expect(screen.getByTestId("editable-input")).toBeInTheDocument();
  });

  it("should show updated chat name when user types a new name and presses enter with successful network call", () => {
    renderComponent(mockProps, mockingStore);
    const editableInput = screen.getByTestId("editable-input");
    fireEvent.change(editableInput, { target: { value: "Job 1" } });
    updateChat.mockImplementationOnce((params) => params.onSuccess(""));
    fireEvent.keyDown(editableInput, { key: "Enter", code: "Enter", charCode: 13 });
  });

  it("should not update chat name when user types a new name and presses enter with failed network call", () => {
    renderComponent(mockProps, mockingStore);
    const editableInput = screen.getByTestId("editable-input");
    fireEvent.change(editableInput, { target: { value: "Job 1" } });
    updateChat.mockImplementationOnce((params) => params.onError(""));
    fireEvent.keyDown(editableInput, { key: "Enter", code: "Enter", charCode: 13 });
  });

  it("should revert to previous chat name if input is empty and user tries to save", () => {
    renderComponent(mockProps, mockingStore);
    const editableInput = screen.getByTestId("editable-input");
    fireEvent.change(editableInput, { target: { value: "" } });
    fireEvent.keyDown(editableInput, { key: "Enter", code: "Enter", charCode: 13 });
  });

  it("should revert to previous chat name when user clicks edit and then close", () => {
    renderComponent(mockProps, mockingStore);
    fireEvent.click(screen.getByTestId("edit-btn-id"));
    fireEvent.click(screen.getByTestId("close-btn-id"));
  });

  it("should show delete confirmation modal when user clicks delete icon", () => {
    renderComponent(mockProps, mockingStore);
    fireEvent.click(screen.getByTestId("delete-btn-id"));
  });

  it("should close delete confirmation modal when user clicks cancel", () => {
    renderComponent(mockProps, mockingStore);
    fireEvent.click(screen.getByTestId("delete-btn-id"));
    fireEvent.click(screen.getByText(/cancel/i));
  });

  it("should delete chat when user clicks delete with successful network call", () => {
    deleteChat.mockImplementationOnce((params) => {
      params.onSuccess({ chat_id: "662b9cb188e28e8af8679ead", msg: "Chat deleted successfully.", success: true });
    });
    renderComponent(mockProps, mockingStore);
    fireEvent.click(screen.getByTestId("delete-btn-id"));
    fireEvent.click(screen.getByText("Delete"));
  });

  it("should not delete chat when user clicks delete with failed network call", () => {
    deleteChat.mockImplementationOnce((params) => {
      params.onError({ success: false, msg: "something went wrong" });
    });
    renderComponent(mockProps, mockingStore);
    fireEvent.click(screen.getByTestId("delete-btn-id"));
    fireEvent.click(screen.getByText("Delete"));
  });

  it("should show job initials with first letters of job name if more than one word and not numeric", () => {
    renderComponent(
      { ...mockProps, eachJob: { ...mockProps.eachJob, chat_name: "latest chat" } },
      mockingUpdatedstore
    );
  });

  it("should show job initials with first and second letter of job name if it is one word and not numeric", () => {
    renderComponent(
      { ...mockProps, eachJob: { ...mockProps.eachJob, chat_name: "jobname" } },
      mockingUpdatedstore
    );
  });
});
