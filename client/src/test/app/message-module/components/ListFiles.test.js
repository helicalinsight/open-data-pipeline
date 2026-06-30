import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ListFiles from "../../../../app/message-module/components/ListFiles";
import { act } from "react-dom/test-utils";
import { ChatContext } from "../../../../app/chat-module/components/ChatContext";

const mockFiles = [
  {
    source_id: "23bc55e3-70cf-4694-ad06-99baaffc4f45",
    alias: "free-test-data.csv",
  },
  {
    source_id: "7fbca03d-f69c-486e-ad4f-358b516812ad",
    alias: "new-air-travel.csv",
  },
  {
    source_id: "c17dac32-2524-4bca-a4c6-abef9ee87f9c",
    alias: "free-test-data_1.csv",
  },
  { source_id: 1, alias: "file1.txt" },
  { source_id: 2, alias: "file2.txt" },
  {
    source_id: "c90e9950-81ba-42e7-806a-a57101e55fad",
    alias: "free-test-data_2.csv",
  },
  {
    source_id: "4cbab749-d340-490f-9a6e-23106bcc760c",
    alias: "free-test-data_3.csv",
  },
  {
    source_id: "717c4aa0-ebb6-4219-b751-1887eb951f59",
    alias: "free-test-data_4.csv",
  },
  {
    source_id: "d3a99b92-ce9b-4571-b999-cd63be392153",
    alias: "free-test-data_5.csv",
  },
];

const mockMessage = "Select the files that you wish to load in the Job!";

jest.mock("../../../../app/chat-module/components/ChatContext");

describe("ListFiles component", () => {
  it("renders the component without errors", () => {
    act(() => {
      render(
        <ListFiles message={mockMessage} files={mockFiles} isLastItem={true} />
      );
    });
  });

  it("renders the component with all props without errors", () => {
    act(() => {
      render(
        <ListFiles message={mockMessage} files={mockFiles} isLastItem={true} />
      );
    });
  });

  it("handles item selection", () => {
    act(() => {
      render(
        <ListFiles message={mockMessage} files={mockFiles} isLastItem={true} />
      );
    });

    // Select an item in the menu
    act(() => {
      fireEvent.click(screen.getByText("file1.txt"));
    });
    act(() => {
      fireEvent.click(screen.getByText("free-test-data_1.csv"));
    });
    act(() => {
      fireEvent.click(screen.getByText("new-air-travel.csv"));
    });
  });

  const files = [
    { source_id: 1, alias: "File1" },
    { source_id: 2, alias: "File2" },
    // Add more files as needed
  ];

  it("handles file selection and click event", () => {
    const handleMessageMock = jest.fn();

    // Wrap your component with the real context provider
    const { getByText } = render(
      <ChatContext.Provider value={{ handleMessage: handleMessageMock }}>
        <ListFiles message="Test Message" files={files} isLastItem />
      </ChatContext.Provider>
    );

    // Simulate file selection
    act(() => {
      fireEvent.click(getByText("File1"));
      fireEvent.click(getByText("File2"));
    });

    // Simulate clicking the "Load File" button
    act(() => {
      fireEvent.click(getByText("Load File"));
    });

    // You can check if the handleMessageMock was called with the correct parameters
    expect(handleMessageMock).toHaveBeenCalledWith({
      title: expect.any(String),
      type: "load_file",
      payload: expect.any(Array),
      isCustom: true,
    });
  });
});
