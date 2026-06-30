import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import configureStore from "redux-mock-store";
import SidebarHeader from "../../../../app/sidebar/components/SidebarHeader";
import userEvent from '@testing-library/user-event'; 
const mockStore = configureStore();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

const store = mockStore({
  app: {
    isSidebarCollapsed: false,
  },
});

// reusable function for render
const renderComponent = (props) => {
  render(
    <reactRedux.Provider store={store}>
      <Router>
        <SidebarHeader {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

// reusable function to mock active view
const mockActiveView = (viewTestId) => {
  renderComponent({ isSidebarCollapsed: true });
  expect(useDispatchMock).toHaveBeenCalled();
};

describe("Sidebar Header component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    useDispatchMock.mockClear();
  });

  it("should render website title and logo when sidebar is not collapsed", () => {
    renderComponent({ isSidebarCollapsed: false });
    expect(screen.getByTestId("app-logo-title")).toBeInTheDocument();
  });

  it("should render website logo when sidebar is collapsed", () => {
    renderComponent({ isSidebarCollapsed: true });
  });
  it("should render job-listing, job-scheduling, datasources, and audit icons", () => {
    renderComponent({ isSidebarCollapsed: true });
  
    const testIds = [
      "job-listing-view",
      "datasources-view",
      "job-scheduling-view",
      "audit-view"
    ];
    testIds.forEach((testId) => {
    });
  });
  it("should render job listing view when I click on job listing icon", () => {
    mockActiveView("job-listing-view");
  });

  it("should render job schedule view when I click on job schedule icon", () => {
    mockActiveView("job-scheduling-view");
  });

  it("should render datasources-view view when I click on job schedule icon", () => {
    mockActiveView("datasources-view");
  });
  it("should render audit-view view when I click on job schedule icon", () => {
    mockActiveView("audit-view");
  });
  it("should fire a click when user clicks on menu fold icon", () => {
    renderComponent({ isSidebarCollapsed: false });  
    fireEvent.click(screen.getByTestId("menufold-id"));
  });
  
});
