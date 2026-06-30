import React from "react";
import { render, fireEvent } from "@testing-library/react";
import UploadItem from "../../../../app/message-module/components/UploadItem";
import "@testing-library/jest-dom/extend-expect";

describe("UploadItem component", () => {
  const mockFile = {
    status: "uploading",
    name: "example.txt",
    progress: 50,
    size: 3000000,
  };

  const mockHandleFileRemove = jest.fn();

  it("renders UploadItem component correctly", () => {
    const { getByText, getByTestId } = render(
      <UploadItem
        file={mockFile}
        handleFileRemove={mockHandleFileRemove}
        index={1}
      />
    );

    // Check if the file name is displayed
    expect(getByText("1. example.txt")).toBeInTheDocument();

    // Check if Progress component is rendered for uploading status
    expect(getByTestId("progress-bar")).toBeInTheDocument();
  });

  it("renders error message for failed status", () => {
    const failedFile = {
      status: "failed",
      name: "example.txt",
      progress: 0,
      size: 3000000,
    };

    const { getByText } = render(
      <UploadItem
        file={failedFile}
        handleFileRemove={mockHandleFileRemove}
        index={1}
      />
    );

    // Check if error message is rendered for failed status
    expect(getByText("1. example.txt")).toHaveStyle("color: red");
  });

  it("calls handleFileRemove when delete icon is clicked", () => {
    const delteMockFile = {
      name: "example.txt",
      progress: 50,
      size: 3000000,
    };
    const { getByTestId } = render(
      <UploadItem
        file={delteMockFile}
        handleFileRemove={mockHandleFileRemove}
        index={1}
      />
    );

    // Try to find the delete icon
    const deleteIcon = getByTestId("remove-file");

    // Click the delete icon
    fireEvent.click(deleteIcon);

    expect(mockHandleFileRemove).toHaveBeenCalledWith(delteMockFile);
  });

  it("renders loading icon when progress is 99", () => {
    const progressMock = {
      status: "failed",
      name: "example.txt",
      progress: 99,
      size: 3000000,
    };

    const { getByTestId } = render(
      <UploadItem
        file={progressMock}
        handleFileRemove={mockHandleFileRemove}
        index={1}
      />
    );

    // Check if Loading icon is rendered
    expect(getByTestId("loading-icon")).toBeInTheDocument();
  });

  it("renders Progress with showInfo set to true", () => {
    const { getByTestId, queryByText } = render(
      <UploadItem file={mockFile} handleFileRemove={() => {}} index={1} />
    );

    const progressBar = getByTestId("progress-bar");

    // Check if Progress component is rendered
    expect(progressBar).toBeInTheDocument();

    // Check if progress information is present
    expect(queryByText(/50%/i)).toBeInTheDocument();
  });

  it("renders Progress with showInfo set to false when progress is 99", () => {
    const mockFileWithShowInfoFalse = {
      status: "uploading",
      name: "example.txt",
      progress: 99, // it will set showInfo to false
      size: 3000000,
    };
    const { getByTestId, queryByText } = render(
      <UploadItem
        file={mockFileWithShowInfoFalse}
        handleFileRemove={() => {}}
        index={1}
      />
    );

    const progressBar = getByTestId("progress-bar");

    // Check if Progress component is rendered
    expect(progressBar).toBeInTheDocument();

    // Check if progress information is not present
    expect(queryByText(/99%/i)).toBeNull();
  });

  it("does not render Progress when status is failed", () => {
    const mockFileFailedStatus = {
      ...mockFile,
      status: "failed",
    };

    const { queryByTestId } = render(
      <UploadItem
        file={mockFileFailedStatus}
        handleFileRemove={() => {}}
        index={1}
      />
    );

    // Check if Progress component is not present
    expect(queryByTestId("progress-bar")).toBeNull();
  });
});
