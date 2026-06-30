import React from "react";
import { render, act } from "@testing-library/react";
import "@testing-library/jest-dom/extend-expect";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import CustomResponses from "../../../../app/message-module/components/CustomResponses";
import { BrowserRouter as Router } from "react-router-dom";

// Mock Redux store
const mockStore = configureStore({
  reducer: {
    chat: () => ({
      selectedChat: { chat_id: "12345" },
    }),
  },
});

jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));

describe("CustomResponses component", () => {
  const sampleQuickReplies = {
    item: {
      text: "Hello!",
      quick_replies: [
        { payload: "Option1", title: "Option1" },
        { payload: "Option2", title: "Option2" },
      ],
    },
    index: 0,
  };

  const sampleLoadFiles = {
    item: {
      text: "Loading files...",
      shipment: {
        load_files: true,
      },
    },
    index: 5,
  };

  const sampleFileUpload = {
    item: {
      type: "upload_file",
      text: "Please upload a file",
    },
    index: 1,
  };

  const sampleListFiles = {
    item: {
      text: "Here are your files:",
      shipment: {
        list_files: ["file1.txt", "file2.txt"],
      },
    },
    index: 2,
  };

  const sampleDownloadFiles = {
    item: {
      text: "Download your files:",
      shipment: {
        download_files: [
          { source_id: 1, export_name: "file3.txt" },
          { source_id: 2, export_name: "file4.txt" },
        ],
      },
    },
    index: 3,
  };

  const sampleNoShipment = {
    item: {
      text: "No shipment information",
    },
    index: 4,
  };

  it("renders ButtonsPrompt for messages with quick replies", () => {
    const { getByTestId } = render(
      <Router>
        <CustomResponses {...sampleQuickReplies} />
      </Router>
    );
    expect(getByTestId("buttons-prompt")).toBeInTheDocument();
  });

  it("renders ListFiles", () => {
    act(() => {
      render(
        <Router>
          <CustomResponses {...sampleListFiles} />
        </Router>
      );
    });
    const listFilesElement = document.querySelector(
      '[data-testid="list-files"]'
    );
    expect(listFilesElement).toBeInTheDocument();
  });

  it("renders DownloadFiles", () => {
    const { getByTestId, getByText } = render(
      <Provider store={mockStore}>
        <Router>
          <CustomResponses {...sampleDownloadFiles} />
        </Router>
      </Provider>
    );
    expect(getByText(sampleDownloadFiles.item.text)).toBeInTheDocument();
    expect(getByTestId("download-files")).toBeInTheDocument();
    sampleDownloadFiles.item.shipment.download_files.forEach((file) => {
      expect(getByText(file.export_name)).toBeInTheDocument();
    });
  });

  it("returns item.text for messages with shipment.load_files", () => {
    const { getByText } = render(
      <Router>
        <CustomResponses {...sampleLoadFiles} />
      </Router>
    );
    expect(getByText(sampleLoadFiles.item.text)).toBeInTheDocument();
  });

  it("renders default text for messages without shipment information", () => {
    const { getByText } = render(
      <Router>
        <CustomResponses {...sampleNoShipment} />
      </Router>
    );
    expect(getByText(sampleNoShipment.item.text)).toBeInTheDocument();
  });
});
