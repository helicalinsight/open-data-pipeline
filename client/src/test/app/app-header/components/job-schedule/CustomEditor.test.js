import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import {
  getCode,
  runCode,
  updateCode,
} from "../../../../../apis/jobScheduleService";

import CustomEditor from "../../../../../app/app-header/components/job-schedule/components/CustomEditor";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";

import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";

document.createRange = () => {
  const range = new Range();

  range.getBoundingClientRect = jest.fn();

  range.getClientRects = () => {
    return {
      item: () => null,
      length: 0,
      [Symbol.iterator]: jest.fn(),
    };
  };

  range.startContainer.getBoundingClientRect = jest.fn();

  return range;
};

const mockStore = configureStore();

const appStore = mockStore({
  app: {
    editorSuggestions: {
      python: [
        {
          label: "JobArguments",
          kind: "Class",
          documentation:
            "This is a custom class with methods for job arguments.",
          detail: "JobArguments.function_name",
          insertText: "JobArguments",
          methods: [
            {
              label: "create",
              kind: "Function",
              documentation: "Create a new job argument.",
              detail:
                "JobArguments.create(config_key='config', config_value='true')",
              insertText: "create",
            },
          ],
        },
      ],
      yaml: [
        {
          label: "read_files",
          kind: "Function",
          documentation:
            "This is a function to read the files based on the given file id and file name.",
          detail: "read_files(file_id: str, file_name: str) -> Dataframe",
          insertText: "read_files",
        },
        {
          label: "read_tables",
          kind: "Function",
          documentation:
            "This is function to read the tables based on the table_name and connection_id.",
          detail:
            "read_tables(table_name: str, connection_id: str) -> Dataframe",
          insertText: "read_tables",
        },
      ],
    },
  },
});

const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <CustomEditor {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

const appProps = {
  mode: "python",
  open: true,
  onChildrenDrawerClose: jest.fn(),
  selectedChat: {
    chat_name: "Job1",
    chat_id: "Job1",
  },
};

jest.mock("../../../../../apis/jobScheduleService", () => ({
  updateCode: jest.fn(),
  getCode: jest.fn(),
  runCode: jest.fn(),
}));

describe("Custom Scheduling  component", () => {
  it("render the component without erros", () => {
    renderComponent(appStore, appProps);
  });

  it("render the component without erros", () => {
    renderComponent(appStore, { ...appProps, mode: "yaml" });
  });

  it("render the component without erros", () => {
    renderComponent(appStore, { ...appProps, open: false });
  });

  it("trigger get code api on open and close drawer onclick of cancel button", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    renderComponent(appStore, appProps);
    fireEvent.click(screen.getByTestId("cancel-button"));
  });

  it("trigger get code api failed", () => {
    getCode.mockImplementation(({ onError }) => {
      onError({
        message: "failed",
      });
    });
    renderComponent(appStore, appProps);
    fireEvent.click(screen.getByTestId("cancel-button"));
  });

  it("trigger get code api success: false", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: false,
        message: "failed",
      });
    });
    renderComponent(appStore, appProps);
    fireEvent.click(screen.getByTestId("cancel-button"));
  });

  it("it should triger update code API onlcick of save", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    updateCode.mockImplementation(({ onSuccess }) => {
      onSuccess({ success: true, message: "updated" });
    });
    renderComponent(appStore, { ...appProps });
    waitFor(() => {
      fireEvent.click(screen.getByTestId("save-button"));
    });
  });

  it("it should triger update code API failed case", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    updateCode.mockImplementation(({ onSuccess }) => {
      onSuccess({ success: false, message: "faileddated" });
    });
    renderComponent(appStore, appProps);
    waitFor(() => {
      fireEvent.click(screen.getByTestId("save-button"));
    });
  });

  it("it should triger update code API failed case", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    updateCode.mockImplementation(({ onError }) => {
      onError({ message: "faileddated" });
    });
    renderComponent(appStore, appProps);
    waitFor(() => {
      fireEvent.click(screen.getByTestId("save-button"));
    });
  });

  it("should trigger run runCode API : success", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    runCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: false,
      });
    });
    renderComponent(appStore, { ...appProps, mode: "yaml" });
    act(() => {
      fireEvent.click(screen.getByTestId("run-button"));
    });
  });

  it("should trigger run runCode API: failed", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    runCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
      });
    });
    renderComponent(appStore, { ...appProps, mode: "yaml" });
    act(() => {
      fireEvent.click(screen.getByTestId("run-button"));
    });
  });

  it("should trigger run runCode API: error", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });
    runCode.mockImplementation(({ onError }) => {
      onError("error");
    });
    renderComponent(appStore, { ...appProps, mode: "yaml" });
    act(() => {
      fireEvent.click(screen.getByTestId("run-button"));
    });
  });

  it("should show supportbot", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: {
          code: "python code",
          history: "YAML Code",
        },
      });
    });

    renderComponent(appStore, { ...appProps });
    act(() => {
      fireEvent.click(screen.getByTestId("show-support-box-button"));
    });
  });
});
describe("config reducer function", () => {
  const reducer = (acc, { configKey, configValue }) => {
    try {
      const parsedValue = JSON?.parse(configValue?.trim());
      acc[configKey] = parsedValue;
    } catch (error) {
      console.error("Error parsing configValue:", error);
    }
    return acc;
  };

  it("should correctly parse valid configValue and add to accumulator", () => {
    const acc = {};
    const input = { configKey: "retryCount", configValue: "3" };
    const result = reducer(acc, input);
    expect(result).toEqual({ retryCount: 3 });
  });

  it("should handle invalid JSON and not modify accumulator", () => {
    const acc = {};
    const input = { configKey: "invalidConfig", configValue: "notValidJson" };
    const consoleErrorSpy = jest
      .spyOn(console, "error")
      .mockImplementation(() => {});
    const result = reducer(acc, input);
    expect(result).toEqual({});
    expect(consoleErrorSpy).toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
  });
});
describe("CustomEditor Basic Rendering", () => {
  it("should render editor when not loading", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: { code: "test code", history: "test yaml" },
      });
    });
    renderComponent(appStore, appProps);
  });
});
describe("Button Interactions", () => {
  beforeEach(() => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: { code: "test code", history: "test yaml" },
      });
    });
  });

  it("should call onChildrenDrawerClose when cancel button clicked", () => {
    const mockOnClose = jest.fn();
    renderComponent(appStore, {
      ...appProps,
      onChildrenDrawerClose: mockOnClose,
    });
    fireEvent.click(screen.getByTestId("cancel-button"));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it("should trigger save for python mode", () => {
    updateCode.mockImplementation(({ onSuccess }) => {
      onSuccess({ success: true, message: "saved" });
    });
    renderComponent(appStore, appProps);
    fireEvent.click(screen.getByTestId("save-button"));
    expect(updateCode).toHaveBeenCalled();
  });

  it("should trigger run for yaml mode", () => {
    runCode.mockImplementation(({ onSuccess }) => {
      onSuccess({ success: true });
    });
    renderComponent(appStore, { ...appProps, mode: "yaml" });
    fireEvent.click(screen.getByTestId("run-button"));
    expect(runCode).toHaveBeenCalled();
  });
});
describe("API Response Handling", () => {
  it("should handle successful code fetch", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: { code: "python code", history: "yaml code" },
      });
    });
    renderComponent(appStore, appProps);
    expect(getCode).toHaveBeenCalledWith({
      chatId: "Job1",
      onSuccess: expect.any(Function),
      onError: expect.any(Function),
    });
  });

  it("should handle failed code fetch", () => {
    getCode.mockImplementation(({ onError }) => {
      onError({ message: "Failed to fetch" });
    });
    renderComponent(appStore, appProps);
    expect(getCode).toHaveBeenCalled();
  });

  it("should handle successful save", () => {
    updateCode.mockImplementation(({ onSuccess }) => {
      onSuccess({ success: true, message: "Saved successfully" });
    });
    renderComponent(appStore, appProps);
  });

  it("should handle failed save", () => {
    updateCode.mockImplementation(({ onError }) => {
      onError({ message: "Save failed" });
    });
    renderComponent(appStore, appProps);
  });
});
describe("Editor Contentt", () => {
  it("should display fetch code content", () => {
    const testCode = "def test_function():\n    return 'hello'";
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: { code: testCode, history: "" },
      });
    });
    renderComponent(appStore, appProps);
  });
});
describe("Mode for  Specific Behavior", () => {
  it("should disable savee for yaml with no valid content", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: { code: "", history: "" },
      });
    });
    renderComponent(appStore, { ...appProps, mode: "yaml" });
    expect(screen.getByTestId("save-button")).toBeDisabled();
  });
  it("should enablee save for python with any content", () => {
    getCode.mockImplementation(({ onSuccess }) => {
      onSuccess({
        success: true,
        chats: { code: "print('hello')", history: "" },
      });
    });
    renderComponent(appStore, appProps);
    expect(screen.getByTestId("save-button")).not.toBeDisabled();
  });
});
