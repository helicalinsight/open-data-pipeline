import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import * as reactRedux from "react-redux";
import DownloadFiles from "../../../../app/message-module/components/DownloadFiles";
import { downloadFileApi } from "../../../../apis/fileService";

// Mock for useDispatch and useSelector
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
  useSelector: jest.fn(),
}));

const useDispatchMock = reactRedux.useDispatch;
const useSelectorMock = reactRedux.useSelector;

// Mock the download file API
jest.mock("../../../../apis/fileService.js", () => ({
  downloadFileApi: jest.fn(),
}));

// Mock createObjectURL function
global.URL.createObjectURL = jest.fn(() => "mocked-url");
global.URL.revokeObjectURL = jest.fn();
// Test props
const mockProps = {
  message: "Select the files that you wish to load in the Job!",
  files: [
    {
      source_id: "23bc55e3-70cf-4694-ad06-99baaffc4f45",
      export_name: "free-test-data.csv",
    },
    {
      source_id: "7fbca03d-f69c-486e-ad4f-358b516812ad",
      export_name: "new-air-travel.csv",
    },
  ],
};

const mockSelectedChat = { chat_id: "12345" };

// Helper function to render component
const renderComponent = (props) => {
  render(<DownloadFiles {...props} />);
};

describe("DownloadFiles Component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => jest.fn());
    useSelectorMock.mockReturnValue(mockSelectedChat);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without errors", () => {
    renderComponent(mockProps);
    expect(screen.getByTestId("download-files")).toBeInTheDocument();
  });

  it("should render the message correctly", () => {
    renderComponent(mockProps);
    expect(screen.getByTestId("message-id")).toHaveTextContent(
      "Select the files that you wish to load in the Job!"
    );
  });

  it("should call downloadFileApi and handle file download on button click", async () => {
    renderComponent(mockProps);
    const mockResponse = new Blob(["mock file content"], {
      type: "text/plain",
    });
    downloadFileApi.mockImplementationOnce(({ onSuccess }) => {
      onSuccess(mockResponse);
    });
    const fileButtons = screen.getAllByTestId("export-file-id");
    fireEvent.click(fileButtons[0]);
    await waitFor(() => {
      expect(downloadFileApi).toHaveBeenCalledWith({
        chat_id: "12345",
        featherId: "23bc55e3-70cf-4694-ad06-99baaffc4f45",
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
      expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockResponse);
    });
  });

  it("should handle error when file download fails", async () => {
    renderComponent(mockProps);
    downloadFileApi.mockImplementationOnce(({ onError }) => {
      onError(new Error("Download failed"));
    });
    const fileButtons = screen.getAllByTestId("export-file-id");
    fireEvent.click(fileButtons[0]);
    await waitFor(() => {
      expect(downloadFileApi).toHaveBeenCalledWith({
        chat_id: "12345",
        featherId: "23bc55e3-70cf-4694-ad06-99baaffc4f45",
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
    });
  });
});
