import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import { FlatFiles } from "../../../../app/database-module/components/FlatFiles";
import "../../../__mocks__/matchMedia";
import { deleteFile, uploadFileApi } from "../../../../apis/fileService";
global.setImmediate = jest.useRealTimers;

const mockStore = configureStore();

const store = mockStore({
  database: {
    datasources: [],
    selectedDatasource: {},
    savedConnections: [
      {
        _id: "928439fc-c762-40be-b078-777048df0776",
        alias: "new-air-travel - Copy",
        fileType: ".csv",
      },
      {
        _id: "7a03e444-d81c-4456-af91-c5d6942308db",
        alias: "new-air-travel",
        fileType: ".csv",
      },
      {
        _id: "8817d8a1-05c4-4361-a6f9-0d395504088e",
        alias: "travel_details",
        fileType: ".csv",
      },
    ],
    savedConnApiStatus: "",
    editConnection: {},
  },
});

// mock for api service
jest.mock("../../../../apis/fileService.js", () => ({
  deleteFile: jest.fn(),
  uploadFileApi: jest.fn(),
}));

const renderComponent = (appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <FlatFiles />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Flat files component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error", () => {
    renderComponent(store);
  });

  it("should trigger the change event and upload file when user tries to upload new files and click on upload button", async () => {
    const mockResponse = {
      success: true,
      filesUploaded: {
        _id: "928439fc-c762-40be-b078-777048df0776",
      },
    };
    uploadFileApi.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockResponse)
    );
    renderComponent(store);
    const uploadInput = screen.getByTestId("upload-input");
    act(() => {
      fireEvent.change(uploadInput, {
        target: {
          files: [new File(["test file content"], "testfile.txt")],
        },
      });
    });
    const uploadBtn = screen.getByTestId("upload-files-btn");
    act(() => {
      fireEvent.click(uploadBtn);
    });
  });
  
  it("uploadFileApi :: FAILED", () => {
    uploadFileApi.mockImplementationOnce(({ onError }) => onError("ERROR"));
    renderComponent(store);
    const uploadInput = screen.getByTestId("upload-input");

    act(() => {
      fireEvent.change(uploadInput, {
        target: {
          files: [new File(["test file content"], "testfile.txt")],
        },
      });
    });

    const uploadBtn = screen.getByTestId("upload-files-btn");

    act(() => {
      fireEvent.click(uploadBtn);
    });
  });

  it("uploadFileApi :: progressEvent", () => {
    const mockResponse = {
      loaded: 8584,
      total: 8584,
      progress: 1,
      bytes: 8584,
      event: {
        isTrusted: true,
      },
      upload: true,
    };
    uploadFileApi.mockImplementationOnce(({ progressEvent }) =>
      progressEvent(mockResponse)
    );
    renderComponent(store);
    const uploadInput = screen.getByTestId("upload-input");

    act(() => {
      fireEvent.change(uploadInput, {
        target: {
          files: [new File(["test file content"], "testfile.txt")],
        },
      });
    });

    const uploadBtn = screen.getByTestId("upload-files-btn");

    act(() => {
      fireEvent.click(uploadBtn);
    });
  });

  it("should show the success message when user uploaded a different file", () => {
    const mockResponse = {
      success: true,
      filesUploaded: {
        _id: "8c8a2f52c4",
        alias: "new-air-travel",
        fileType: ".csv",
      },
      message: "File uploaded successfully",
    };

    uploadFileApi.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockResponse)
    );
    renderComponent(store);
    const uploadInput = screen.getByTestId("upload-input");
    act(() => {
      fireEvent.change(uploadInput, {
        target: {
          files: [new File(["test file content"], "testfile.txt")],
        },
      });
    });

    const uploadBtn = screen.getByTestId("upload-files-btn");
    act(() => {
      fireEvent.click(uploadBtn);
    });
  });

  it("should trigger handleFileRemove on remove button", () => {
    uploadFileApi.mockImplementationOnce(({ progressEvent }) =>
      progressEvent({
        loaded: 98304,
        total: 114358,
        progress: 0.8596162926948705,
        bytes: 98304,
        event: {
          isTrusted: true,
        },
        upload: true,
      })
    );

    uploadFileApi.mockImplementationOnce(({ onError }) => onError("error"));

    renderComponent(store);

    const uploadInput = screen.getByTestId("upload-input");
    act(() => {
      fireEvent.change(uploadInput, {
        target: {
          files: [new File(["test file content"], "testfile.txt")],
        },
      });
    });

    act(() => {
      fireEvent.click(screen.getByTestId("upload-files-btn"));
    });

    waitFor(() => {
      fireEvent.click(screen.getByTestId("popover"));
    });

    act(() => {
      waitFor(() => {
        fireEvent.click(screen.getByTestId("remove-file"));
      });
    });
  });

  it("should not upload file when user clicks on upload button with failed network requests", () => {
    const mockErrorResponse = {
      success: false,
      msg: "Somthing went wrong!!",
    };
    uploadFileApi.mockImplementationOnce(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(store);
    const uploadBtn = screen.getByTestId("upload-files-btn");
    act(() => {
      fireEvent.click(uploadBtn);
    });
  });

  it("it should TRIGGER MULTI DELETE ON SELECTION:: SUCCESS", () => {
    const { container } = render(
      <reactRedux.Provider store={store}>
        <Router>
          <FlatFiles />
        </Router>
      </reactRedux.Provider>
    );

    // get all checkboxes
    const checkbox = container.querySelector(".ant-checkbox-input");

    //trigger click
    act(() => {
      fireEvent.click(checkbox);
    });

    const table = screen.getByTestId("flat-files-table");
    expect(table).toBeInTheDocument();

    const deleteButton = screen.getByTestId("multi-file-delete-btn");
    expect(deleteButton).toBeInTheDocument();

    deleteFile.mockImplementationOnce((params) => {
      params.onSuccess({
        success: true,
        message: "File deleted successfully.",
        failed_file_ids: [],
      });
    });

    act(() => {
      fireEvent.click(deleteButton);
    });

    act(() => {
      fireEvent.click(screen.getByTestId("modal-ok-button"));
    }); // trigger API

    const deleteButtonAfter = screen.queryByTestId("multi-file-delete-btn");

    expect(deleteButtonAfter).toBeNull();
  });

  it("it should TRIGGER MULTI DELETE ON SELECTION:: FAILED", () => {
    const { container } = render(
      <reactRedux.Provider store={store}>
        <Router>
          <FlatFiles />
        </Router>
      </reactRedux.Provider>
    );

    // get all checkboxes
    const checkbox = container.querySelector(".ant-checkbox-input");

    //trigger click
    act(() => {
      fireEvent.click(checkbox);
    });

    const table = screen.getByTestId("flat-files-table");
    expect(table).toBeInTheDocument();

    const deleteButton = screen.getByTestId("multi-file-delete-btn");
    expect(deleteButton).toBeInTheDocument();

    deleteFile.mockImplementationOnce((params) => {
      params.onError({ failed_file_ids: ["1234"] });
    });

    act(() => {
      fireEvent.click(deleteButton);
    }); // trigger API
  });
});
