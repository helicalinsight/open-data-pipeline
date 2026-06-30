import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import SidebarJobs from "../../../../app/sidebar/components/SidebarJobs";
import configureStore from "redux-mock-store";
import "../../../__mocks__/matchMedia";
import SidebarEachJob from "../../../../app/sidebar/components/SidebarEachJob";

const mockStore = configureStore();

const mockProps = {
  sessionId: "sessionid",
  searchResults: [
    {
      chat_id: "65ae401aa8b667c71898d3c9",
      chat_name: "Job 11",
    },
  ],
  handleChatClick: jest.fn(),
  allJobs: [],
  setAllJobs: jest.fn(),
};

const store = mockStore({
  chat: {
    selectedChat: {},
  },
  app: {
    isSidebarCollapsed: false,
  },
});

jest.mock("../../../../app/sidebar/components/SidebarEachJob", () => {
  return jest.fn(() => <></>);
});

// reusable function for render
const renderComponent = (props) => {
  render(
    <reactRedux.Provider store={store}>
      <Router>
        <SidebarJobs {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("SidebarJobs component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without error", () => {
    renderComponent(mockProps);
  });

  it("render the sidebar job component if search result has some thing", () => {
    renderComponent(mockProps);
    expect(SidebarEachJob).toHaveBeenCalled();
  });

  it("should show no results found if search result is empty and jobs are present", () => {
    renderComponent({
      ...mockProps,
      searchResults: [],
      allJobs: [
        {
          chat_id: "65ae401aa8b667c71898d3c9",
          chat_name: "Job 11",
        },
      ],
    });
    expect(screen.getByText("No Results Found!!"));
  });

  it("should show no jobs found if search result and all jobs are empty", () => {
    renderComponent({ ...mockProps, searchResults: [], allJobs: [] });
    expect(screen.getByText("No Jobs Found!!"));
  });
});
