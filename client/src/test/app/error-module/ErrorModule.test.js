import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import ErrorModule from "../../../app/error-module/index.jsx";
import { getLocalStorageItem } from "../../../utils/userData.js";

const mockedNavigate = jest.fn();

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

jest.mock("../../../utils/userData.js", () => ({
  getLocalStorageItem: jest.fn(),
}));

// reusable function for render
const renderComponent = () => {
  render(<ErrorModule />);
};

const hasToken = () => {
  const mockToken = "yourMockToken";
  getLocalStorageItem.mockReturnValue({ token: mockToken });
};

const noToken = () => {
  getLocalStorageItem.mockReturnValue(null);
};

describe("Error component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component 404 message", () => {
    renderComponent();
    expect(screen.getByText(/404/i)).toBeInTheDocument();
    expect(screen.getByText(/Oops!! Page Not Found/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Sorry, we couldn't find the page you are looking for/i)
    ).toBeInTheDocument();
  });

  it("renders a button which performs navigation to homepage or login", () => {
    renderComponent();
    expect(screen.getByTestId("btn-id")).toBeInTheDocument();
  });

  it("should show Return to Homepage button if user is logged in", () => {
    hasToken();
    renderComponent();
    expect(screen.getByText(/Return to Homepage/i)).toBeInTheDocument();
  });

  it("should show login button if user is not logged in", () => {
    noToken();
    renderComponent();
    expect(screen.getByText(/Login/i)).toBeInTheDocument();
  });

  it("should navigate to login page when user clicks on login button", () => {
    noToken();
    renderComponent();
    fireEvent.click(screen.getByTestId("btn-id"));
    expect(mockedNavigate).toHaveBeenCalledWith("/login");
  });

  it("should navigate to home page when user clicks on return to homepage button", () => {
    hasToken();
    renderComponent();
    fireEvent.click(screen.getByTestId("btn-id"));
    expect(mockedNavigate).toHaveBeenCalledWith("/app-space");
  });
});
