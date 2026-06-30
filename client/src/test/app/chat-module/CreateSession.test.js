import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import CreateSession from "../../../app/chat-module/CreateSession.jsx";
import { getLocalStorageItem } from "../../../utils/userData.js";
import { getAllJobsApi } from "../../../apis/chatService.js";
import { getDataSources } from "../../../apis/databaseService.js";
import { getApplication } from "../../../apis/featureService.js";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry.js";

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

const mockedNavigate = jest.fn();

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

jest.mock("../../../utils/handleSessionExpiry.js", () => ({
  handleSessionExpiry: jest.fn(),
}));

jest.mock("../../../utils/userData.js", () => ({
  getLocalStorageItem: jest.fn(),
}));

jest.mock("../../../apis/chatService.js", () => ({
  getAllJobsApi: jest.fn(),
}));

jest.mock("../../../apis/databaseService.js", () => ({
  getDataSources: jest.fn(),
}));

jest.mock("../../../apis/featureService.js", () => ({
  getApplication: jest.fn(),
}));

// if user is logged in
const hasToken = () => {
  const mockToken = "yourMockToken";
  getLocalStorageItem.mockReturnValue({ token: mockToken });
};

// if user is not logged in
const noToken = () => {
  getLocalStorageItem.mockReturnValue(null);
};

// reusable function for render
const renderComponent = () => {
  render(
    <Router>
      <CreateSession />
    </Router>
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

  it("should render the component with loading message", () => {
    renderComponent();
    expect(
      screen.getByText(/please wait. we are setting up your workspace./i)
    ).toBeInTheDocument();
  });

  it("should navigate to login page, when user is not logged in", () => {
    noToken();
    renderComponent();
    expect(mockedNavigate).toHaveBeenCalledWith("/login");
  });

  it("should show all jobs or chats when user is logged in and chats are present", () => {
    hasToken();
    const chatData = { chats: [{ chat_id: "123" }] };
    getAllJobsApi.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(chatData)
    );
    renderComponent();
  });

  it("should navigate to default chat when chats are not present", () => {
    hasToken();
    const chatData = { chats: [] };
    getAllJobsApi.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(chatData)
    );
    renderComponent();
  });

  it("should render all datasources with success network request", () => {
    hasToken();
    const dataSourceData = {
      configuration: {
        datasources: [
          {
            driver: "flat_files",
            name: "Flat Files",
            categoryName: "Big Data",
            categoryType: "flat_files",
            available: true,
          },
        ],
      },
    };
    getDataSources.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(dataSourceData)
    );
    renderComponent();
  });

  it("should not show datasources when there is any error or failed network request", () => {
    hasToken();
    getDataSources.mockImplementationOnce(({ onError }) =>
      onError("something went wrong")
    );
    renderComponent();
    expect(handleSessionExpiry).toHaveBeenCalled();
  });

  it("should show application feature for free and premium user with success network request", () => {
    hasToken();
    const response = {
      configuration: {
        chat: ["jobs", "create", "schedule"],
        job: ["histroy", "dataPreview", "reset", "load", "trigger"],
        datasources: ["flat_files", "redshift", "mysql"],
      },
    };
    getApplication.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(response)
    );
    renderComponent();
  });

  it("should not show applicaion feature when there is any error or failed network request", () => {
    hasToken();
    getApplication.mockImplementationOnce(({ onError }) =>
      onError("something went wrong")
    );
    renderComponent();
    expect(handleSessionExpiry).toHaveBeenCalled();
  });
});
