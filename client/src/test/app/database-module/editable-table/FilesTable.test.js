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
import "../../../__mocks__/matchMedia";
import FilesTable from "../../../../app/database-module/components/editable-table/FilesTable";
import { deleteFile, renameFile } from "../../../../apis/fileService";
global.setImmediate = jest.useRealTimers;

// mock for api service
jest.mock("../../../../apis/fileService.js", () => ({
  deleteFile: jest.fn(),
  renameFile: jest.fn(),
}));

const mockStore = configureStore();
const getStore = ({ savedConnApiStatus }) => {
  return mockStore({
    database: {
      savedConnections: [
        {
          _id: "4acc3c60",
          alias: "citiestr",
          fileType: ".csv",
        },
        {
          _id: "38c62f8c",
          alias: "new-air-travel",
          fileType: ".csv",
        },
      ],
      savedConnApiStatus,
    },
  });
};

const appStore = getStore({ savedConnApiStatus: "" });

const props = {
  searchTerm: "",
  selectedRowKeys: [],
  setSelectedRowKeys: jest.fn(),
  deleteFileIds: [],
  setDeleteFileIds: jest.fn(),
  setOpenDeleteModal: jest.fn(),
  handleDeleteFiles: jest.fn(),
  messageApi: {
    open: jest.fn(),
  },
};

const renderComponent = (props, appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <FilesTable {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Files Table", () => {
  it("IT SHOULD RENDER THE COMPONENT WITHOUT ANY ERRORS", () => {
    renderComponent(props, appStore);
  });

  it("IT SHOULD SKLETON WHEN SAVED CONNECTIONS API STATUS IS FETCHING", async () => {
    const updatedStore = getStore({ savedConnApiStatus: "FETCHING" });
    const { container } = renderComponent(props, updatedStore);
    const skeletonElement = container.querySelector(".ant-skeleton");
    expect(skeletonElement).toBeInTheDocument();
  });

  it("IT SHOULD DELETE THE FILE: DELETE FILE API:: SUCCESS: true", () => {
    deleteFile.mockImplementationOnce((params) => {
      params.onSuccess({ success: true });
    });
    renderComponent(props, appStore);
    waitFor(() =>
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-delete"));
      })
    );
    waitFor(() => expect(screen.getByTestId("ad-modal")).toBeInTheDocument());
    waitFor(() => fireEvent.click(screen.getByTestId("modal-ok-button")));
  });

  it("IT NOT SHOULD DELETE THE FILE: DELETE FILE API:: SUCCESS; false", () => {
    deleteFile.mockImplementationOnce((params) => {
      params.onSuccess({ success: false });
    });
    renderComponent(props, appStore);
    waitFor(() =>
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-delete"));
      })
    );
    waitFor(() => expect(screen.getByTestId("ad-modal")).toBeInTheDocument());
    waitFor(() => fireEvent.click(screen.getByTestId("modal-ok-button")));
  });

  it("IT SHOULD DELETE THE FILE: DELETE FILE API:: FAILED", () => {
    deleteFile.mockImplementationOnce((params) => {
      params.onError("failed");
    });
    renderComponent(props, appStore);
    waitFor(() =>
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-delete"));
      })
    );
    waitFor(() => expect(screen.getByTestId("ad-modal")).toBeInTheDocument());
    waitFor(() => fireEvent.click(screen.getByTestId("modal-ok-button")));
  });

  it("IT SHOULD EDIT THE FILE NAME: RENAME FILE API:: SUCCESS : true", () => {
    renameFile.mockImplementationOnce((params) => {
      params.onSuccess({ success: true, message: "success" });
    });
    renderComponent(props, appStore);
    waitFor(() => {
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-edit"));
      });
    });
  });

  it("IT SHOULD NOT RENAME THE FILE NAME: RENAME FILE API:: SUCCESS: false", () => {
    renameFile.mockImplementationOnce((params) => {
      params.onSuccess({ success: false, message: "failed" });
    });
    renderComponent(props, appStore);
    waitFor(() => {
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-edit"));
      });
    });
  });

  it("IT SHOULD EDIT THE FILE NAME: RENAME FILE API:: FAILED", () => {
    renameFile.mockImplementationOnce((params) => {
      params.onError("error");
    });
    renderComponent(props, appStore);
    waitFor(() => {
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-edit"));
      });
    });
  });

  it("IT SHOULD CLOSE THE MODAL ON CANCEL BUTTON CLICK", () => {
    deleteFile.mockImplementationOnce((params) => {
      params.onError("failed");
    });
    renderComponent(props, appStore);
    waitFor(() =>
      act(() => {
        fireEvent.click(screen.getByTestId("4acc3c60-delete"));
      })
    );
    waitFor(() => expect(screen.getByTestId("ad-modal")).toBeInTheDocument());
    waitFor(() => fireEvent.click(screen.getByTestId("modal-cancel-button")));
    waitFor(() => {
      expect(screen.queryByTestId("ad-modal")).not.toBeInTheDocument();
    });
  });

  it("IT SHOULD SHOW MULTI FILE DELETE BUTTON ON SELECTION AND TRIGGER DELETE FILE API:: SUCCESS: true", () => {
    deleteFile.mockImplementationOnce((params) => {
      params.onSuccess({ success: true });
    });
    renderComponent(props, appStore);
    waitFor(() =>
      act(() => fireEvent.click(screen.getAllByClassName("ant-checkbox-inner")))
    );
    waitFor(() => {
      const deleteButton = screen.getByTestId("multi-file-delete-btn");
      return act(() => fireEvent.click(deleteButton));
    });
  });
});
