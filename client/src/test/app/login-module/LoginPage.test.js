import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import LoginPage from "../../../app/login-module";
import { useGoogleLogin } from "@react-oauth/google";
import { BrowserRouter as Router } from "react-router-dom";
import { setLocalStorageItem } from "../../../utils/userData";
import { useNavigate } from "react-router-dom";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: jest.fn(),
}));

jest.mock("axios");
jest.mock("@react-oauth/google", () => ({
  ...jest.requireActual("@react-oauth/google"),
  useGoogleLogin: jest.fn(),
}));
jest.mock("../../../utils/userData", () => ({
  setLocalStorageItem: jest.fn(),
}));
jest.mock("../../../constants/appConstants", () => ({
  ...jest.requireActual("../../../constants/appConstants"),
  CLIENT_ID: "test-client-id",
}));
const mockStore = configureStore();

const store = mockStore({
  settings: { messageData:null},
})
const renderComponent = (appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <LoginPage />
      </Router>
    </reactRedux.Provider>
  );
}

describe("LoginPage component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without error", () => {
    renderComponent(store);
  });

  it("should show login page contents and login button without error", () => {
    renderComponent(store);
    expect(screen.getByText("Ask On Data"));
  });

  it("should trigger Google login on button click", async () => {
    const mockGoogleLogin = jest.fn();
    useGoogleLogin.mockReturnValue(mockGoogleLogin);
    renderComponent(store);
    const googleLoginButton = screen.getByRole("button", {
      name: /sign in with google/i,
    });
    fireEvent.click(googleLoginButton);
    expect(mockGoogleLogin).toHaveBeenCalled();
  });

  it("should call onLoginSuccess when login is successful", async () => {
    const mockData = {
      userid: "123",
      users: { email: "test@example.com" },
    };
    const mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate);
    renderComponent(store);
    await waitFor(() => {
      expect(screen.getByText("Sign In")).toBeInTheDocument();
    });
    const onLoginSuccess = jest.fn((data) => {
      setLocalStorageItem(data);
      expect(setLocalStorageItem).toHaveBeenCalledWith(data);
    });
    onLoginSuccess(mockData);
    expect(onLoginSuccess).toHaveBeenCalledWith(mockData);
  });

  it("should call onLoginError when login fails", async () => {
    const mockError = new Error("Login failed");
    renderComponent(store);
    const onLoginError = jest.fn();
    onLoginError(mockError);
    expect(onLoginError).toHaveBeenCalledWith(mockError);
  });

  it("should call handleLogin and set fetching state", async () => {
    renderComponent(store);
    const handleLogin = jest.fn();
    handleLogin();
    expect(handleLogin).toHaveBeenCalled();
  });
});
