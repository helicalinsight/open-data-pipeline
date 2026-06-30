import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import "@testing-library/jest-dom";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";
import "../../../__mocks__/matchMedia";
import Preferences from "../../../../app/settings-module/components/Preferences";
import {
  getPreferences,
  postPreferences,
} from "../../../../apis/settingsService";

const mockStore = configureStore();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

// mock for api service
jest.mock("../../../../apis/settingsService", () => ({
  getPreferences: jest.fn(),
  postPreferences: jest.fn(),
}));

const mockProps = {
  activeTab: "2",
};

const mockUpdatedProps = {
  activeTab: "1",
};

const store = mockStore({
  settings: {
    allPreferences: {
      files: {
        file_size: 5,
        num_records: 100,
      },
    },
  },
  app: {
    userConfig: {
      role: "admin",
      chat: ["jobs", "create", "schedule"],
      job: [
        "histroy",
        "dataPreview",
        "reset",
        "load",
        "trigger",
        "undo",
        "redo",
      ],
      datasources: [
        "flat_files",
        "redshift",
        "mysql",
        "snowflake",
        "postgres",
        "astra",
        "cassandra",
        "firebird",
      ],
    },
  },
});

const mockSuccessResponse = {
  files: {
    file_size: 5,
    num_records: 100,
  },
};

const mockErrorResponse = {
  success: false,
  msg: "something went wrong",
};
const renderComponent = (props, appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <Preferences {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Preferences component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should not fetch data preferences when active tab is not preferences", () => {
    renderComponent(mockUpdatedProps, store);
    expect(getPreferences).not.toHaveBeenCalled();
  });
  it("should fetch data preferences at the initial loading with success network requests", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
  });

  it("should not fetch data preferences at the initial loading with failed network requests", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onError(mockErrorResponse);
    });
    renderComponent(mockProps, store);
  });
  it("should show data preferences and choose the number of records to show on screen", () => {
    renderComponent(mockProps, store);
    expect(screen.getByText("Data Preferences")).toBeInTheDocument();
    expect(
      screen.getByText("Choose the number of records to show")
    ).toBeInTheDocument();
  });

  it("should file size input on the screen", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    expect(screen.getByTestId("file-input-id")).toBeInTheDocument();
  });

  it("user should be able to change file size in file input box", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    const fileInput = screen.getByTestId("file-input-id");
    fireEvent.change(fileInput, { target: { value: "100" } });
  });

  it("should show radio buttons for full and custom on the screen", () => {
    renderComponent(mockProps, store);
    expect(screen.getByTestId("radio-full")).toBeInTheDocument();
    expect(screen.getByTestId("radio-custom")).toBeInTheDocument();
  });

  it("it should show records input field when custom radio button is selected", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("radio-custom"));
    });
    expect(screen.queryByTestId("input-custom-id")).toBeInTheDocument();
  });

  it("user should be able to change number of records in input box", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    const recordsInput = screen.getByTestId("input-custom-id");
    fireEvent.change(recordsInput, { target: { value: "100" } });
  });

  it("it should not show records input field when full radio button is selected", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("radio-full"));
    });
    expect(screen.queryByTestId("input-custom-id")).not.toBeInTheDocument();
  });

  it("should make an api call to save the preferences on save preferences button click with success networks", () => {
    postPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("save-button-id"));
    });
  });

  it("should not make an api call to save the preferences on save preferences button click with failed networks", () => {
    postPreferences.mockImplementationOnce((params) => {
      params.onError(mockErrorResponse);
    });
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("save-button-id"));
    });
  });
  it("should show an error message and not save preferences when file size is negative", async () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
  
    const fileInput = screen.getByTestId("file-input-id");
    fireEvent.change(fileInput, { target: { value: "-5" } });
  
    const saveButton = screen.getByTestId("save-button-id");
    act(() => {
      fireEvent.click(saveButton);
    });
  
    expect(postPreferences).not.toHaveBeenCalled();
  });
  it("should show an error message and not save preferences when the number of records is not positive in custom preference mode", () => {
    getPreferences.mockImplementationOnce((params) => {
      params.onSuccess(mockSuccessResponse);
    });
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("radio-custom"));
    });
    const recordsInput = screen.getByTestId("input-custom-id");
    fireEvent.change(recordsInput, { target: { value: "0" } });
    const saveButton = screen.getByTestId("save-button-id");
    act(() => {
      fireEvent.click(saveButton);
    });
    expect(postPreferences).not.toHaveBeenCalled();
  });
});
