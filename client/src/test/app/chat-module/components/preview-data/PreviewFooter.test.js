const mockDispatch = jest.fn();

jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: () => mockDispatch,
}));

import React, { useState } from "react";
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
import PreviewFooter from "../../../../../app/chat-module/components/preview-data/PreviewFooter.jsx";
import "../../../../__mocks__/matchMedia.js";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry.js";
import { switchSelectedFile } from "../../../../../apis/fileService.js";

const mockStore = configureStore();
jest.mock("../../../../../apis/fileService.js", () => ({
  switchSelectedFile: jest.fn(),
}));

jest.mock("../../../../../store/actions/chatAction.js", () => ({
  setSelectedFilesAction: jest.fn(() => ({ type: "mockSetSelectedFiles" })),
  setPreviewTableData: jest.fn(() => ({ type: "mockSetPreviewData" })),
}));

jest.mock("../../../../../utils/handleSessionExpiry.js", () => ({
  handleSessionExpiry: jest.fn(),
}));
jest.mock("../../../../../store/actions/chatAction.js", () => ({
  ...jest.requireActual("../../../../../store/actions/chatAction.js"),
  setIndexRanges: jest.fn(),
}));

const mockProps = {
  previewInfo: {
    info: {
      total_records: 100,
    },
  },
  setActiveTabData: jest.fn(),
  activeTabData: {
    source_id: "1",
    alias: "free-test-data",
  },
  paginationData: {
    limit_by: 10,
  },
  chatId: "65d303abc6619e0b2bf7f114",
  currentPage: 2,
  setCurrentPage: jest.fn(),
  previewTableData: { datasource: { total_records: 100 } },
  setPaginationData: jest.fn(),
};

const store = mockStore({
  chat: {
    chatList: {
      "65d303abc6619e0b2bf7f114": {
        chat_id: "65d303abc6619e0b2bf7f114",
        chat_name: "Job 14",
        loadedFiles: [
          {
            source_id: "1",
            alias: "free-test-data1",
            type: "csv",
          },
          {
            source_id: "2",
            alias: "free-test-data2",
            type: "csv",
          },
          {
            source_id: "3",
            alias: "free-test-data3",
            type: "csv",
          },
          {
            source_id: "4",
            alias: "free-test-data4",
            type: "csv",
          },
          {
            source_id: "5",
            alias: "free-test-data5",
            type: "csv",
          },
          {
            source_id: "6",
            alias: "free-test-data6",
            type: "csv",
          },
          {
            source_id: "7",
            alias: "free-test-data7",
            type: "csv",
          },
          {
            source_id: "8",
            alias: "free-test-data8",
            type: "csv",
          },
          {
            source_id: "9",
            alias: "free-test-data9",
            type: "csv",
          },
        ],
      },
    },
  },
});
// reusable function for render
const renderComponent = (props, appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <PreviewFooter {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Preview Footer component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error", () => {
    renderComponent(mockProps, store);
  });

  it("should display paginationa and files info container without error", () => {
    renderComponent(mockProps, store);
    expect(screen.getByTestId("pagination-id")).toHaveTextContent(
      "11-20 of 100"
    );
    expect(screen.getByTestId("file-info-id")).toBeInTheDocument();
  });

  it("should select the file when user clicks on it", () => {
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("file-1"));
    });
  });

  it("should updates index range on left navigation button click", () => {
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("left-arrow-id"));
    });
    act(() => {
      fireEvent.click(screen.getByTestId("right-arrow-id"));
    });
    act(() => {
      fireEvent.click(screen.getByTestId("left-arrow-id"));
    });
  });
  it("should updates index range on right navigation button click", () => {
    renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(screen.getByTestId("right-arrow-id"));
    });
    act(() => {
      fireEvent.click(screen.getByTestId("left-arrow-id"));
    });
    act(() => {
      fireEvent.click(screen.getByTestId("right-arrow-id"));
    });
  });

  it("should update current page", () => {
    const { container } = renderComponent(mockProps, store);
    act(() => {
      fireEvent.click(
        container.getElementsByClassName("ant-pagination-next")[0]
      );
    });
  });
  it("should show dropdown on click of menu icon", async () => {
    renderComponent(mockProps, store);
    fireEvent.mouseEnter(screen.getByTestId("menu-icon"));
    const fileElement = await screen.findByText(/free-test-data9/i);
    fireEvent.click(fileElement);
  });
  
  it("set load files to empty [], when there are no load files", () => {
    const store = mockStore({
      chat: {
        chatList: {
          "65d303abc6619e0b2bf7f114": {
            chat_id: "65d303abc6619e0b2bf7f114",
            chat_name: "Job 14",
          },
        },
      },
    });
    renderComponent(mockProps, store);
  });
  it("should update pagination data when page size changes", () => {
    const mockSetPaginationData = jest.fn();
    const mockSetCurrentPage = jest.fn();
    const updatedMockProps = {
      ...mockProps,
      setPaginationData: mockSetPaginationData,
      setCurrentPage: mockSetCurrentPage,
    };

    const newSize = 20;
    const totalRecords = 100;

    const newPage = Math.min(1, Math.ceil(totalRecords / newSize));
  });

  it("should handle error from switchSelectedFile and call handleSessionExpiry", async () => {
    const mockError = { message: "Session expired" };
    switchSelectedFile.mockImplementation(({ onError }) => {
      onError(mockError);
    });
    renderComponent(mockProps, store);
    fireEvent.click(screen.getByTestId("file-2"));
    await waitFor(() => {
      expect(switchSelectedFile).toHaveBeenCalledWith({
        payload: {
          chat_id: mockProps.chatId,
          source_id: "2",
        },
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
      expect(handleSessionExpiry).toHaveBeenCalledWith(mockDispatch, mockError);
    });
  });
  it("should call switchSelectedFile and update states on success", async () => {
    const mockSuccessResponse = { success: true };
    const splitIndex = 3; 
    switchSelectedFile.mockImplementation(({ onSuccess }) => {
      onSuccess(mockSuccessResponse);
    });
    renderComponent({ ...mockProps, splitIndex }, store);
    const fileElement = screen.getByTestId("file-2");
    fireEvent.click(fileElement);
    await waitFor(() => {
      expect(switchSelectedFile).toHaveBeenCalledWith({
        payload: {
          chat_id: mockProps.chatId,
          source_id: "2",
        },
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
      expect(mockProps.setActiveTabData).toHaveBeenCalledWith({
        source_id: "2",
        alias: "free-test-data2",
      });
    });
  });
  
  it("should handle error from switchSelectedFile and call handleSessionExpiry", async () => {
    const mockError = { message: "Session expired" };
    switchSelectedFile.mockImplementation(({ onError }) => {
      onError(mockError);
    });
    renderComponent(mockProps, store);
    const fileElement = screen.getByTestId("file-2");
    fireEvent.click(fileElement);
    await waitFor(() => {
      expect(handleSessionExpiry).toHaveBeenCalledWith(mockDispatch, mockError);
    });
  });

  it("should return early if clicked file is already active", () => {
    const mockDomEvent = {
      target: {
        innerText: "free-test-data",
      },
    };
    const onClick =
      PreviewFooter.prototype?.onClick ||
      store.getState().chat.chatList[mockProps.chatId].loadedFiles[0];
    renderComponent(mockProps, store);
    const fileElement = screen.getByTestId("file-1");
    fireEvent.click(fileElement);
    expect(switchSelectedFile).not.toHaveBeenCalled();
  });
});
