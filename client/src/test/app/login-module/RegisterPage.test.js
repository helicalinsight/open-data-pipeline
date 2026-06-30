import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import RegisterPage from "../../../app/login-module/register";
import { BrowserRouter as Router } from "react-router-dom";
import axios from "axios";
import { baseApi } from "../../../apis/apiUrlConstants";
import { userRoutes } from "../../../router/uiRouteConstants";
import "@testing-library/jest-dom/extend-expect";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";

jest.mock("axios");
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: jest.fn(),
}));

// Mock for window.matchMedia
window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };

const mockedNavigate = require("react-router-dom").useNavigate;

describe("RegisterPage Component", () => {
  beforeEach(() => {
    mockedNavigate.mockClear();
  });
const mockStore = configureStore();

const store = mockStore({
  settings: { messageData:null},
})
const renderComponent = (appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <RegisterPage />
      </Router>
    </reactRedux.Provider>
  );
}

  it("renders RegisterPage component", () => {
    renderComponent(store);
    expect(screen.getByTestId("sign-up-button")).toBeInTheDocument();
  });
  it("renders RegisterPage component", () => {
    renderComponent(store);
    const signUpButton = screen.getByRole("button", { name: /sign up/i });
    expect(signUpButton).toBeInTheDocument();
  });
  it("renders RegisterPage component", () => {
    renderComponent(store);
    const signUpElements = screen.getAllByText(/Sign Up/i);
    expect(signUpElements.length).toBeGreaterThan(0);
  });

  it("displays error message when registration fails", async () => {
    axios.post.mockRejectedValueOnce(new Error("Network Error"));
    renderComponent(store);
    const signUpButton = screen.getByTestId("sign-up-button");
    fireEvent.click(signUpButton);
  });
  it("displays success message and navigates on successful registration", async () => {
    const mockData = {
      success: true,
      msg: "Registration successful!",
      userid: 1,
    };
    axios.post.mockResolvedValueOnce({ data: mockData });
    renderComponent(store);
    const signUpButton = screen.getByTestId("sign-up-button");
    fireEvent.change(screen.getByPlaceholderText("Enter your First Name"), {
      target: { value: "John" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your Last Name"), {
      target: { value: "Doe" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your Email"), {
      target: { value: "john.doe@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(signUpButton);
  });

  it("displays an error message if the API response does not indicate success", async () => {
    const mockData = { success: false, msg: "Registration failed!" };
    axios.post.mockResolvedValueOnce({ data: mockData });
    renderComponent(store);
    const signUpButton = screen.getByTestId("sign-up-button");
    fireEvent.change(screen.getByPlaceholderText("Enter your First Name"), {
      target: { value: "Jane" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your Last Name"), {
      target: { value: "Doe" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your Email"), {
      target: { value: "jane.doe@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(signUpButton);
  });

  it("validates email format and displays appropriate error messages", async () => {
    renderComponent(store);
    const emailInput = screen.getByPlaceholderText("Enter your Email");
    const signUpButton = screen.getByTestId("sign-up-button");

    // Test case 1: Entering an invalid email (missing @ symbol)
    fireEvent.change(emailInput, { target: { value: "invalidemail.com" } });
    fireEvent.click(signUpButton);
    await waitFor(() => {
      expect(
        screen.getByText(/please enter a valid email/i)
      ).toBeInTheDocument();
    });

    // Test case 2: Entering an invalid email (missing domain name)
    fireEvent.change(emailInput, { target: { value: "user@" } });
    fireEvent.click(signUpButton);
    await waitFor(() => {
      expect(
        screen.getByText(/please enter a valid email/i)
      ).toBeInTheDocument();
    });

    // Test case 3: Entering an invalid email (missing TLD)
    fireEvent.change(emailInput, { target: { value: "user@example" } });
    fireEvent.click(signUpButton);
    await waitFor(() => {
      expect(
        screen.getByText(/please enter a valid email/i)
      ).toBeInTheDocument();
    });

    // Test case 4: Entering a valid email
    fireEvent.change(emailInput, {
      target: { value: "valid.email@example.com" },
    });
    fireEvent.click(signUpButton);
    await waitFor(() => {
      expect(
        screen.queryByText(/please enter a valid email/i)
      ).not.toBeInTheDocument();
    });
  });

  it("shows validation error when passwords do not match", async () => {
  renderComponent(store);
  fireEvent.change(screen.getByPlaceholderText("Enter your Password"), {
    target: { value: "password123" },
  });
  fireEvent.change(screen.getByPlaceholderText("Enter your Confirm Password"), {
    target: { value: "password321" },
  });
  fireEvent.click(screen.getByTestId("sign-up-button"));
  await waitFor(() => {
    expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
  });
});

it("does not show error when passwords match", async () => {
  renderComponent(store);
  fireEvent.change(screen.getByPlaceholderText("Enter your Password"), {
    target: { value: "password123" },
  });
  fireEvent.change(screen.getByPlaceholderText("Enter your Confirm Password"), {
    target: { value: "password123" },
  });
  fireEvent.click(screen.getByTestId("sign-up-button"));
  await waitFor(() => {
    expect(screen.queryByText(/passwords do not match/i)).not.toBeInTheDocument();
  });
});
});
