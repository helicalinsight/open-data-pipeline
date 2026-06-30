import React, { useState } from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import { switchSelectedFile } from "../../../../apis/fileService.js";

import configureStore from "redux-mock-store";
import HeaderFileList from "../../../../app/app-header/components/HeaderFileList.jsx";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useState: jest.fn(),
}));

jest.mock("../../../../apis/fileService.js", () => ({
  switchSelectedFile: jest.fn(),
}));

jest.mock("../../../../apis/chatService.js", () => ({
  getInformationApi: jest.fn(),
}));
// component props
const mockProps = {
  loadedFiles: [
    {
      source_id: "65e578faf5d110a56b007571",
      alias: "free-test-data",
      type: "csv",
    },
    {
      source_id: "65e578faf5d110a56b007570",
      alias: "free-test-data",
      type: "csv",
    },
  ],
  selectedFiles: [],
};

const updatedMockProps = {
  ...mockProps,
  loadedFiles: [
    {
      source_id: "65e578faf5d110a56b007570",
      alias: "free-test-data",
      type: "csv",
    },
    {
      source_id: "65e578faf5d110a56b007571",
      alias: "free-test-data1",
      type: "csv",
    },
    {
      source_id: "65e578faf5d117a56b007589",
      alias: "example-data",
      type: "csv",
    },
    {
      source_id: "65e578faf5d110a56b007529",
      alias: "employee-data",
      type: "csv",
    },
  ],
  selectedFiles: [
    {
      source_id: "65e578faf5d110a56b007570",
      alias: "free-test-data",
      type: "csv",
    },
  ],
};

const mockNoDataProps = {
  loadedFiles: [],
  selectedFiles: [],
};
const mockStore = configureStore();

const appStore = mockStore({
  chat: {
    splitIndex: 2,
    indexRange: [0, 2],
    chatList: {
      "67779a408598b32e512a7c70": {
        loadedFiles: [
          {
            source_id: "65e578faf5d110a56b007570",
            alias: "free-test-data",
            type: "csv",
          },
          {
            source_id: "65e578faf5d110a56b007571",
            alias: "free-test-data1",
            type: "csv",
          },
        ],
      },
    },
  },
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

// reusable function for render
const renderComponent = (props) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <HeaderFileList {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Header File List component", () => {
  // beforeEach(() => {
  //   useState.mockImplementation(jest.requireActual("react").useState);
  // });
  beforeEach(() => {
    window.history.pushState({}, "", "/?chat=67779a408598b32e512a7c70");
    useState.mockImplementation(jest.requireActual("react").useState);
  });
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error", () => {
    renderComponent(mockProps);
  });
  it("should show navigation arrows if loaded files are more than 3", () => {
    renderComponent(updatedMockProps);
    expect(screen.getByTestId("left-arrow-id")).toBeInTheDocument();
    expect(screen.getByTestId("right-arrow-id")).toBeInTheDocument();
  });
  it("should show new file when user clicks on right arrow", () => {
    renderComponent(updatedMockProps);
    fireEvent.click(screen.getByTestId("left-arrow-id"));
  });
  it("should update indexRange correctly when user clicks on right arrow", () => {
    renderComponent(updatedMockProps);
    fireEvent.click(screen.getByTestId("right-arrow-id"));
  });

  it("should not show any files when there are no loaded files", () => {
    renderComponent(mockNoDataProps);
    expect(screen.queryByTestId("file-text-id")).not.toBeInTheDocument();
    expect(screen.queryByTestId("loaded-files-id")).not.toBeInTheDocument();
  });

  it("should trigger switch CWF API:success onclick of File", () => {
    switchSelectedFile.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    renderComponent(mockProps);
    act(() => {
      fireEvent.click(screen.getAllByTestId("file-name-id")[0]);
    });
  });

  it("should trigger switch CWF API: Failed onclick of File", () => {
    switchSelectedFile.mockImplementationOnce(({ onError }) =>
      onError("error")
    );
    renderComponent(mockProps);
    act(() => {
      fireEvent.click(screen.getAllByTestId("file-name-id")[0]);
    });
  });

  it("should not trigger switch CWF API when user clicks on seleectd file", () => {
    renderComponent(updatedMockProps);
    act(() => {
      fireEvent.click(screen.getAllByTestId("file-name-id")[0]);
    });
    expect(switchSelectedFile).not.toHaveBeenCalled()
  });
  it("should display 'Files' when loadedFiles length is greater than 1", () => {
    renderComponent(updatedMockProps); 
    expect(screen.getByTestId("file-text-id")).toHaveTextContent("Files");
});

it("should display 'File' when loadedFiles length is equal to 1", () => {
    renderComponent({
        loadedFiles: [
            {
                source_id: "65e578faf5d110a56b007570",
                alias: "single-file",
                type: "csv",
            },
        ],
        selectedFiles: [],
    });
    expect(screen.getByTestId("file-text-id")).toHaveTextContent("File");
});

});
