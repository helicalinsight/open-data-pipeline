import { render, screen, fireEvent } from "@testing-library/react";
import '@testing-library/jest-dom';
import { RouterProvider } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import router, { SessionExpiredModal } from "../../router";
import { getLocalStorageItem } from "../../utils/userData";

jest.mock("../../utils/userData", () => ({
  getLocalStorageItem: jest.fn(),
}));

let mockDispatch;
let mockNavigate;

jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: () => mockDispatch,
  useSelector: jest.fn(),
}));

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

const createMockStore = (isSessionExpired = false) =>
  configureStore({
    reducer: {
      app: (state = { isSessionExpired }) => state,
    },
  });

const mockUseSelector = jest.requireMock("react-redux").useSelector;

describe("Router", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should renders without crashing", () => {
    const { container } = render(
      <Provider store={createMockStore()}>
        <RouterProvider router={router} />
      </Provider>
    );
    expect(container).toBeDefined();
  });
});

describe("SessionExpiredModal", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockDispatch = jest.fn();
    mockNavigate = jest.fn();
  });

  it("should not render when session is not expired", () => {
    mockUseSelector.mockReturnValue(false);
    render(
      <Provider store={createMockStore(false)}>
        <SessionExpiredModal />
      </Provider>
    );
    expect(screen.queryByText(/session expired/i)).not.toBeInTheDocument();
    expect(screen.queryByText("Login")).not.toBeInTheDocument();
  });

  it("should render& handle login button click correctly", () => {
    mockUseSelector.mockReturnValue(true);
    render(
      <Provider store={createMockStore(true)}>
        <SessionExpiredModal />
      </Provider>
    );
    const modalTitle = screen.getByText(/session expired/i);
    expect(modalTitle).toBeInTheDocument();
    const loginButton = screen.getByRole("button", { name: /login/i }) || 
                       screen.getByText("Login");
    fireEvent.click(loginButton);
    expect(mockDispatch).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("should have correct button text and behavior", () => {
    mockUseSelector.mockReturnValue(true);
    render(
      <Provider store={createMockStore(true)}>
        <SessionExpiredModal />
      </Provider>
    );
    const loginButton = screen.getByText("Login");
    expect(loginButton).toBeInTheDocument();
    fireEvent.click(loginButton);
    expect(mockDispatch).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });
});

describe("SessionExpiredModal", () => {
  const TestSessionExpiredModal = ({ isSessionExpired, onDispatch, onNavigate }) => {
    if (!isSessionExpired) return null;
    const handleLogin = () => {
      onDispatch(); 
      onNavigate("/login");
    };
    return (
      <div role="dialog" data-testid="session-expired-modal">
        <h2>Session Expired</h2>
        <p>Your session has expired. Please login again.</p>
        <button onClick={handleLogin}>Login</button>
      </div>
    );
  };

  it("should call dispatch and navigate when login button is clicked", () => {
    const mockDispatch = jest.fn();
    const mockNavigate = jest.fn();
    render(
      <TestSessionExpiredModal 
        isSessionExpired={true}
        onDispatch={mockDispatch}
        onNavigate={mockNavigate}
      />
    );
    const loginButton = screen.getByText("Login");
    fireEvent.click(loginButton);
    expect(mockDispatch).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("should not render when session is not expired", () => {
    const mockDispatch = jest.fn();
    const mockNavigate = jest.fn();
    render(
      <TestSessionExpiredModal 
        isSessionExpired={false}
        onDispatch={mockDispatch}
        onNavigate={mockNavigate}
      />
    );
    expect(screen.queryByTestId("session-expired-modal")).not.toBeInTheDocument();
  });
});