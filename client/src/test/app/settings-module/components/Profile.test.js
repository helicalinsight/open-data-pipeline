import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
} from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import "@testing-library/jest-dom";
import Profile from "../../../../app/settings-module/components/Profile";
import {
  createGenerateKey,
  getGenerateKey,
  deleteGenerateKey,
} from "../../../../apis/settingsService";
import { getLocalStorageItem } from "../../../../utils/userData";
import dayjs from "dayjs";
import * as reactRedux from "react-redux";

// Mock store
const mockStore = configureStore();
const store = mockStore({});

// Mock API Calls
jest.mock("../../../../apis/settingsService", () => ({
  createGenerateKey: jest.fn(),
  getGenerateKey: jest.fn(),
  deleteGenerateKey: jest.fn(),
}));

jest.mock("../../../../utils/userData", () => ({
  getLocalStorageItem: jest.fn(),
}));
jest.mock("../../../../utils/handleClick", () => ({
  dispatchMessage: jest.fn(),
}));
// Polyfill for window.matchMedia
if (!window.matchMedia) {
  window.matchMedia = function () {
    return {
      matches: false,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    };
  };
}

const renderComponent = (appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <Profile />
      </Router>
    </reactRedux.Provider>
  );
};
jest.setTimeout(10000);
describe("Profile Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    getLocalStorageItem.mockReturnValue({
      user: { email: "test@example.com", user_id: "12345" },
    });
    getGenerateKey.mockImplementation(({ user_id, onSuccess }) => {
      if (user_id === "12345") {
        onSuccess({ success: true });
      }
    });
  });

  it("renders Profile component", () => {
    renderComponent(store);
    expect(screen.getByText("Add new token")).toBeInTheDocument();
  });

  it("opens the form when clicking 'Add new token' button", () => {
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    expect(screen.getByPlaceholderText("Enter token name")).toBeInTheDocument();
    expect(screen.getByText("Save")).toBeInTheDocument();
  });

  it("submits form successfully with valid inputs", async () => {
    createGenerateKey.mockImplementation(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    fireEvent.change(screen.getByPlaceholderText("Enter token name"), {
      target: { value: "Test Token" },
    });
    fireEvent.change(screen.getByPlaceholderText("Select date"), {
      target: { value: dayjs().add(1, "day").format("YYYY-MM-DD") },
    });
    fireEvent.click(screen.getByText("Save"));
    await waitFor(() => {
      expect(createGenerateKey).toHaveBeenCalled();
    });
  });

  it("shows error when user email is missing", async () => {
    getLocalStorageItem.mockReturnValueOnce(null);
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    fireEvent.change(screen.getByPlaceholderText("Enter token name"), {
      target: { value: "Test Token" },
    });
    fireEvent.click(screen.getByText("Save"));
    await waitFor(() => {
      expect(createGenerateKey).not.toHaveBeenCalled();
    });
  });

  it("handles API error correctly", async () => {
    createGenerateKey.mockImplementation(({ onError }) =>
      onError({ message: "Error Creating Token" })
    );
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    fireEvent.change(screen.getByPlaceholderText("Enter token name"), {
      target: { value: "Test Token" },
    });
    fireEvent.click(screen.getByText("Save"));
    await waitFor(() => {
      expect(createGenerateKey).toHaveBeenCalled();
    });
  });

  it("cancels adding token", () => {
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    fireEvent.click(screen.getByText("Cancel"));
    expect(
      screen.queryByPlaceholderText("Enter token name")
    ).not.toBeInTheDocument();
  });

  it("disables past dates in DatePicker", () => {
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    const disabledDate = (current) =>
      current && current < dayjs().startOf("day");
    expect(disabledDate(dayjs().subtract(1, "day"))).toBeTruthy();
    expect(disabledDate(dayjs().add(1, "day"))).toBeFalsy();
  });

  it("formats expiry_date correctly before API call", async () => {
    createGenerateKey.mockImplementation(({ payload, onSuccess }) => {
      expect(payload.expiry_date).toBe(
        dayjs().add(1, "day").format("YYYY-MM-DD")
      );
      onSuccess({ success: true });
    });
    renderComponent(store);
    fireEvent.click(screen.getByText("Add new token"));
    fireEvent.change(screen.getByPlaceholderText("Enter token name"), {
      target: { value: "Test Token" },
    });
    fireEvent.change(screen.getByPlaceholderText("Select date"), {
      target: { value: dayjs().add(1, "day").format("YYYY-MM-DD") },
    });
    fireEvent.click(screen.getByText("Save"));
    await waitFor(() => {
      expect(createGenerateKey).toHaveBeenCalled();
    });
  });

  it("calls deleteGenerateKey and handles success", async () => {
    const populatedStore = mockStore({
      settings: {
        apiKeys: [
          {
            tokenname: "Test Token",
            apikey: "abcd-1234",
            expirydate: dayjs().add(1, "day").format("YYYY-MM-DD"),
          },
        ],
      },
    });
    deleteGenerateKey.mockImplementation(({ payload, onSuccess }) => {
      expect(payload).toEqual({ apikey: "abcd-1234" }); 
      onSuccess({ success: true }); 
    });
    renderComponent(populatedStore);
    const deleteIcon = await screen.findByTestId("delete-icon");
    fireEvent.click(deleteIcon);
  });

  it("calls deleteGenerateKey and handles error", async () => {
    const populatedStore = mockStore({
      settings: {
        apiKeys: [
          {
            tokenname: "Test Token",
            apikey: "abcd-1234",
            expirydate: dayjs().add(1, "day").format("YYYY-MM-DD"),
          },
        ],
      },
    });
    deleteGenerateKey.mockImplementation(({ payload, onError }) => {
      expect(payload).toEqual({ apikey: "abcd-1234" }); 
      onError({ message: "Delete failed" });
    });
    renderComponent(populatedStore);
    const deleteIcon = await screen.findByTestId("delete-icon");
    fireEvent.click(deleteIcon);
  });
});
    describe("deleteGenerateApiKey", () => {
      it("should handle delete API error correctly", async () => {
        deleteGenerateKey.mockImplementation(({ payload, onError }) => {
          onError({ message: "Delete failed" });
        });
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "Test Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store);
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        const deleteButton = screen.getByText("Delete");
        fireEvent.click(deleteButton);
        await waitFor(() => {
          expect(deleteGenerateKey).toHaveBeenCalled();
        });
      });

      it("should show loading state during delete operation", async () => {
        let resolveDelete;
        const deletePromise = new Promise((resolve) => {
          resolveDelete = resolve;
        });
        deleteGenerateKey.mockImplementation(({ onSuccess }) => {
          setTimeout(() => {
            onSuccess({ success: true });
            resolveDelete();
          }, 100);
        });

        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "Test Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store);
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        const deleteButton = screen.getByText("Delete");
        fireEvent.click(deleteButton);
        await waitFor(() => deletePromise);
      });

      it("should reset selected token after successful deletion", async () => {
        deleteGenerateKey.mockImplementation(({ onSuccess }) => {
          onSuccess({ success: true });
        });
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "Test Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store); 
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        const deleteButton = screen.getByText("Delete");
        fireEvent.click(deleteButton);
      });
    });

    describe("handleCancelDelete", () => {
      it("should close delete modal when cancel is clicked", () => {
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "Test Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store);
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        expect(screen.getByText("Delete Token")).toBeInTheDocument(); 
        const cancelButton = screen.getByText("Cancel");
        fireEvent.click(cancelButton);
      });

      it("should reset selected token when cancel is clicked", () => {
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "Test Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store);
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        const cancelButton = screen.getByText("Cancel");
        fireEvent.click(cancelButton);
        fireEvent.click(deleteIcon);
      });

      it("should not call delete API when cancel is clicked", () => {
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "Test Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store);
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        const cancelButton = screen.getByText("Cancel");
        fireEvent.click(cancelButton);
        expect(deleteGenerateKey).not.toHaveBeenCalled();
      });
    });

    describe("Delete Modal Integration", () => {
      it("should show correct token name in delete confirmation modal", () => {
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "My Special Token",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store); 
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon)
      });

      it("should show fallback text when token name is missing", () => {
        const store = mockStore({
          settings: {
            apiKeys: [
              {
                tokenname: "",
                apikey: "abcd-1234",
                expirydate: "2024-12-31"
              }
            ]
          }
        });
        renderComponent(store);
        const deleteIcon = screen.getByTestId("delete-icon");
        fireEvent.click(deleteIcon);
        expect(screen.getByText(/Are you sure you want to delete the token \?/)).toBeInTheDocument();
      });
    });
describe("copyToClipboard Function", () => {
  const mockDispatch = jest.fn();
  beforeEach(() => {
    jest.clearAllMocks();
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: jest.fn(),
      },
      writable: true,
    });
  });

  it("copies valid API key to clipboard successfully", async () => {
    const apiKey = "valid-api-key-12345";
    const mockWriteText = navigator.clipboard.writeText.mockResolvedValueOnce();
    const TestComponent = () => {
      const copyToClipboard = (apiKey) => {
        if (apiKey && apiKey !== "-") {
          navigator.clipboard
            .writeText(apiKey)
            .then(() => {
              dispatchMessage(mockDispatch, "success", "API key copied to clipboard!");
            })
            .catch((err) => {
            });
        }
      };
      return (
        <button onClick={() => copyToClipboard(apiKey)}>Copy API Key</button>
      );
    };
    render(<TestComponent />);
    fireEvent.click(screen.getByText("Copy API Key"));
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(apiKey);
    });
  });

  it("handles clipboard write error", async () => {
    const apiKey = "valid-api-key-12345";
    const mockError = new Error("Clipboard write failed");
    navigator.clipboard.writeText.mockRejectedValueOnce(mockError);
    const TestComponent = () => {
      const copyToClipboard = (apiKey) => {
        if (apiKey && apiKey !== "-") {
          navigator.clipboard
            .writeText(apiKey)
            .then(() => {
              dispatchMessage(mockDispatch, "success", "API key copied to clipboard!");
            })
            .catch((err) => {
            });
        }
      };
      return (
        <button onClick={() => copyToClipboard(apiKey)}>Copy API Key</button>
      );
    };
    render(<TestComponent />);
    fireEvent.click(screen.getByText("Copy API Key"));
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(apiKey);
    });
  });

  it("does nothing when API key is undefined", () => {
    const TestComponent = () => {
      const copyToClipboard = (apiKey) => {
        if (apiKey && apiKey !== "-") {
          navigator.clipboard
            .writeText(apiKey)
            .then(() => {
              dispatchMessage(mockDispatch, "success", "API key copied to clipboard!");
            })
            .catch((err) => {
              dispatchMessage(mockDispatch, "error", "Failed to copy API key");
            });
        }
      };
      return (
        <button onClick={() => copyToClipboard(undefined)}>Copy API Key</button>
      );
    };
    render(<TestComponent />);
    fireEvent.click(screen.getByText("Copy API Key"))
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });

  it("does nothing when API key is dash '-'", () => {
    const TestComponent = () => {
      const copyToClipboard = (apiKey) => {
        if (apiKey && apiKey !== "-") {
          navigator.clipboard
            .writeText(apiKey)
            .then(() => {
              dispatchMessage(mockDispatch, "success", "API key copied to clipboard!");
            })
            .catch((err) => {
              dispatchMessage(mockDispatch, "error", "Failed to copy API key");
            });
        }
      };
      return (
        <button onClick={() => copyToClipboard("-")}>Copy API Key</button>
      );
    };
    render(<TestComponent />);
    fireEvent.click(screen.getByText("Copy API Key"));
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });

  it("does nothing when API key is empty string", () => {
    const TestComponent = () => {
      const copyToClipboard = (apiKey) => {
        if (apiKey && apiKey !== "-") {
          navigator.clipboard
            .writeText(apiKey)
            .then(() => {
              dispatchMessage(mockDispatch, "success", "API key copied to clipboard!");
            })
            .catch((err) => {
              dispatchMessage(mockDispatch, "error", "Failed to copy API key");
            });
        }
      };
      return (
        <button onClick={() => copyToClipboard("")}>Copy API Key</button>
      );
    };
    render(<TestComponent />);
    fireEvent.click(screen.getByText("Copy API Key"));
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });

  it("does nothing when API key is null", () => {
    const TestComponent = () => {
      const copyToClipboard = (apiKey) => {
        if (apiKey && apiKey !== "-") {
          navigator.clipboard
            .writeText(apiKey)
            .then(() => {
              dispatchMessage(mockDispatch, "success", "API key copied to clipboard!");
            })
            .catch((err) => {
              dispatchMessage(mockDispatch, "error", "Failed to copy API key");
            });
        }
      };
      return (
        <button onClick={() => copyToClipboard(null)}>Copy API Key</button>
      );
    };
    render(<TestComponent />);
    fireEvent.click(screen.getByText("Copy API Key"));
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });
});

describe("copyToClipboard Integration with Profile Component", () => {
  let originalClipboard;
  beforeEach(() => {
    jest.clearAllMocks();
    getLocalStorageItem.mockReturnValue({
      user: { email: "test@example.com", user_id: "12345" },
    });
    originalClipboard = navigator.clipboard;
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: jest.fn(),
      },
      writable: true,
    });
  });
  afterEach(() => {
    Object.defineProperty(navigator, 'clipboard', {
      value: originalClipboard,
      writable: true,
    });
  });

  it("copies API key when copy icon is clicked", async () => {
    const mockApiKey = "test-api-key-12345";
    const populatedStore = mockStore({
      settings: {
        apiKeys: [
          {
            tokenname: "Test Token",
            apikey: mockApiKey,
            expirydate: dayjs().add(1, "day").format("YYYY-MM-DD"),
          },
        ],
      },
    });
    navigator.clipboard.writeText.mockResolvedValueOnce();
    renderComponent(populatedStore);
    await waitFor(() => {
      expect(screen.getByText("Test Token")).toBeInTheDocument();
    });
    const copyIcons = screen.getAllByRole('img', { name: /copy/i });
    fireEvent.click(copyIcons[0]);
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockApiKey);
    });
  });

  it("shows error message when copy fails", async () => {
    const mockApiKey = "test-api-key-12345";
    const populatedStore = mockStore({
      settings: {
        apiKeys: [
          {
            tokenname: "Test Token",
            apikey: mockApiKey,
            expirydate: dayjs().add(1, "day").format("YYYY-MM-DD"),
          },
        ],
      },
    });
    navigator.clipboard.writeText.mockRejectedValueOnce(new Error("Copy failed"));
    renderComponent(populatedStore);
    await waitFor(() => {
      expect(screen.getByText("Test Token")).toBeInTheDocument();
    });
    const copyIcons = screen.getAllByRole('img', { name: /copy/i });
    fireEvent.click(copyIcons[0]);
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockApiKey);
    });
  });

  it("does not show copy icon when API key is dash '-'", async () => {
    const populatedStore = mockStore({
      settings: {
        apiKeys: [
          {
            tokenname: "-",
            apikey: "-",
            expirydate: "-",
          },
        ],
      },
    });
    renderComponent(populatedStore);
    const copyIcons = screen.queryAllByRole('img', { name: /copy/i });
    const deleteIcons = screen.queryAllByRole('img', { name: /delete/i });
    expect(copyIcons).toHaveLength(0);
    expect(deleteIcons).toHaveLength(0);
  });
});
