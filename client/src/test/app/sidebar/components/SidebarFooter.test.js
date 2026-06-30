import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import SideBarFooter from "../../../../app/sidebar/components/SidebarFooter";
import "../../../__mocks__/matchMedia";
import { resetRedux } from "../../../../store/actions/sessionActions";

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

// Mock for useDispatch
const mockDispatch = jest.fn();
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: () => mockDispatch,
  useSelector: jest.fn(),
}));

// Mock actions
jest.mock("../../../../store/actions/sessionActions", () => ({
  resetRedux: jest.fn(),
}));

// Mock for useNavigate
const mockedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

jest.mock("../../../../utils/userData", () => ({
  removeLocalStorageData: jest.fn(),
}));

// sidebar footer component props
const mockProps = {
  user: {
    given_name: "John",
    picture: "user-picture.jpg",
  },
  isSidebarCollapsed: false,
};

// reusable function for render
const renderComponent = (props = mockProps) => {
  return render(
    <Router>
      <SideBarFooter {...props} />
    </Router>
  );
};

describe("SideBarFooter component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockDispatch.mockClear();
    mockedNavigate.mockClear();
    localStorageMock.getItem.mockClear();
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === "app_version") {
        return '"1.0.0"'; 
      }
      return null;
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("renders the component with user and version information", async () => {
    renderComponent();
    expect(screen.getByText("Welcome John !")).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("dash-icon"));
    await waitFor(() => {
      expect(screen.getByText(/version -\s*1.0.0/i)).toBeInTheDocument();
    })
  });

  it("should handle app_version being invalid JSON in localStorage", async () => {
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === "app_version") {
        return "invalid-json";
      }
      return null;
    });
    renderComponent();
    fireEvent.click(screen.getByTestId("dash-icon"));
    await waitFor(() => {
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });
  });

  it("should show logout and settings popover when sidebar is not collapsed and I click on dash icon", async () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("dash-icon"));
    await waitFor(() => {
      expect(screen.getByText("Sign out")).toBeInTheDocument();
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Sign out"));
    fireEvent.click(screen.getByText("Settings"));
    expect(mockedNavigate).toHaveBeenCalledWith("/setting");
  });
  it("should show logout and settings popover when sidebar is collapsed and I click on more icon", async () => {
    renderComponent({
      ...mockProps,
      isSidebarCollapsed: true,
    });
    fireEvent.click(screen.getByTestId("more-icon"));
    await waitFor(() => {
      expect(screen.getByText("Sign out")).toBeInTheDocument();
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Sign out"));
  });

  it("should logout when user clicks on Sign out and confirms modal", async () => {
    renderComponent()
    fireEvent.click(screen.getByTestId("dash-icon"));
    await waitFor(() => {
      expect(screen.getByText("Sign out")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId("logout"));
    await waitFor(() => {
      expect(screen.getByTestId("ad-modal")).toBeInTheDocument();
    }); 
    fireEvent.click(screen.getByTestId("modal-ok-button"));
    expect(resetRedux).toHaveBeenCalled();
    expect(mockedNavigate).toHaveBeenCalledWith("/login");
  });

  it("should show settings view when user clicks on settings", async () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("dash-icon"));
    await waitFor(() => {
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });
    act(() => {
      fireEvent.click(screen.getByTestId("settings-id"));
    });
    expect(mockedNavigate).toHaveBeenCalledWith("/setting");
  });

  it("should close the popover when settings is clicked", async () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("dash-icon"));
    await waitFor(() => {
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });
    act(() => {
      fireEvent.click(screen.getByTestId("settings-id"));
    });
    expect(mockedNavigate).toHaveBeenCalledWith("/setting");
  });

  it("should capitalize user's first name", () => {
    renderComponent({
      user: {
        given_name: "john",
        picture: "user-picture.jpg",
      },
      isSidebarCollapsed: false,
    });
    expect(screen.getByText("Welcome John !")).toBeInTheDocument();
  });

  it("should not show user name when sidebar is collapsed", () => {
    renderComponent({
      ...mockProps,
      isSidebarCollapsed: true,
    });
    expect(screen.queryByText("Welcome John !")).not.toBeInTheDocument();
  });
});