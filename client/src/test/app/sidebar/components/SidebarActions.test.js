import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import SidebarActions from "../../../../app/sidebar/components/SidebarActions";
import { createChat } from "../../../../apis/chatService.js";
import configureStore from "redux-mock-store";

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
jest.mock("../../../../apis/chatService.js", () => ({
  createChat: jest.fn(),
}));

jest.mock("../../../../utils/userData", () => ({
  getLocalStorageItem: () => ({
    user: { id: "test-id" },
  }),
}));
// sidebar actions component props
const mockProps = {
  searchValue: "",
  setSearchValue: jest.fn(),
  allJobs: [],
  socket: "",
};

const store = mockStore({
  app: {
    isSidebarCollapsed: false,
  },
});

const storeUpdated = mockStore({
  app: {
    isSidebarCollapsed: true,
  },
});

// reusable function for render
const renderComponent = (props, appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <SidebarActions {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("SideBarAction component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("renders the component with search bar and create job button", () => {
    renderComponent(mockProps, store);
    expect(screen.getByTestId("search-container-id")).toBeInTheDocument();
    expect(screen.getByTestId("create-chat-id")).toBeInTheDocument();
  });

  it("should show search input when mouse is entered over search button", () => {
    renderComponent(mockProps, store);
    fireEvent.mouseEnter(screen.getByTestId("search-button-id"));
    expect(screen.getByTestId("search-id")).toBeInTheDocument();
  });

  it("should show entered value when user types in search", () => {
    renderComponent({ ...mockProps, searchValue: "search" }, store);
    fireEvent.change(screen.getByTestId("search-id"), {
      target: { value: "job 1" },
    });
  });

  it("should hide search input when mouse is leaved from search button", async () => {
    renderComponent(mockProps, store);
    fireEvent.mouseLeave(screen.getByTestId("search-container-id"));
  });

  it("should create a new chat when i click on create a new job button", async () => {
    renderComponent(mockProps, store);
    const response = {
      success: true,
      chat_id: "65fae050b01410e946ca9bfc",
      chat_name: "Job 48",
    };
    createChat.mockImplementationOnce(({ onSuccess }) => onSuccess(response));
    fireEvent.click(screen.getByTestId("create-chat-id"));
  });

  it("should not create a new chat when there is an error", async () => {
    renderComponent(mockProps, store);
    const response = "Something went wrong";
    createChat.mockImplementationOnce(({ onError }) => onError(response));
    fireEvent.click(screen.getByTestId("create-chat-id"));
  });

  it("create chat button width should be 30px when sidebar is collapsed", () => {
    renderComponent(mockProps, storeUpdated);
    expect(screen.getByTestId("create-chat-id").style.width).toEqual("30px");
  });
  
  it("should dispatch actions when creating a new chat", async () => {
    const mockDispatch = jest.fn();
    useDispatchMock.mockReturnValue(mockDispatch);
    renderComponent(mockProps, store);
    const response = {
      success: true,
      chat_id: "65fae050b01410e946ca9bfc",
      chat_name: "Job 48",
    };
    createChat.mockImplementationOnce(({ onSuccess }) => onSuccess(response));
    fireEvent.click(screen.getByTestId("create-chat-id"));
  });
});
