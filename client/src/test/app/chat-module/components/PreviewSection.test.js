import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import { dataPreview } from "../../../../apis/chatService.js";
import configureStore from "redux-mock-store";
import ADPreview from "../../../../app/chat-module/components/PreviewSection.jsx";
import "../../../__mocks__/matchMedia.js";
const mockStore = configureStore();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

// mock for api service
jest.mock("../../../../apis/chatService.js", () => ({
  dataPreview: jest.fn(),
}));

const store = mockStore({
  app: {
    previewState: true,
  },
  chat: {
    chatList: {
      "6613d0a3826c74a534dcfca2": {},
    },
    selectedChat: {
      chat_id: "6613d0a3826c74a534dcfca2",
      chat_name: "Job 6",
    },
    previewRefresh: {},
  },
});

const updatedStore = mockStore({
  chat: {
    chatList: {
      "6613d0a3826c74a534dcfca2": {
        loadedFiles: [
          {
            source_id: 1,
            alias: "free-test-data",
            type: "csv",
          },
        ],
        selectedFiles: [
          {
            source_id: 1,
            alias: "free-test-data",
            type: "csv",
          },
        ],
      },
    },
    selectedChat: {
      chat_id: "6613d0a3826c74a534dcfca2",
      chat_name: "Job 6",
    },
    previewRefresh: {
      refresh: true,
      id: 1,
    },
  },
  app: {
    previewState: true,
  },
});

const updatedStore2 = mockStore({
  chat: {
    chatList: {
      "6613d0a3826c74a534dcfca2": {
        loadedFiles: [
          {
            source_id: 1,
            alias: "free-test-data",
            type: "csv",
          },
        ],
        selectedFiles: [],
      },
    },
    selectedChat: {
      chat_id: "6613d0a3826c74a534dcfca2",
      chat_name: "Job 6",
    },
    previewRefresh: {
      refresh: true,
      id: 1,
    },
  },
  app: {
    previewState: true,
  },
});

// reusable function for render
const renderComponent = (appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <ADPreview />
      </Router>
    </reactRedux.Provider>
  );
};

const mockSuccessResponse = [
  {
    _id: "1",
    alias: "free-test-data",
    total_records: 12,
    total_records_dataframe: 12,
    columns: [
      {
        name: "month",
        dataType: "object",
      },
      {
        name: "_1958_",
        dataType: "int64",
      },
      {
        name: "_1959_",
        dataType: "int64",
      },
      {
        name: "_1960_",
        dataType: "int64",
      },
    ],
    data: [
      {
        month: "JAN",
        _1958_: 340,
        _1959_: 360,
        _1960_: 417,
      },
      {
        month: "FEB",
        _1958_: 318,
        _1959_: 342,
        _1960_: 391,
      },
      {
        month: "MAR",
        _1958_: 362,
        _1959_: 406,
        _1960_: 419,
      },
      {
        month: "APR",
        _1958_: 348,
        _1959_: 396,
        _1960_: 461,
      },
      {
        month: "MAY",
        _1958_: 363,
        _1959_: 420,
        _1960_: 472,
      },
      {
        month: "JUN",
        _1958_: 435,
        _1959_: 472,
        _1960_: 535,
      },
      {
        month: "JUL",
        _1958_: 491,
        _1959_: 548,
        _1960_: 622,
      },
      {
        month: "AUG",
        _1958_: 505,
        _1959_: 559,
        _1960_: 606,
      },
      {
        month: "SEP",
        _1958_: 404,
        _1959_: 463,
        _1960_: 508,
      },
      {
        month: "OCT",
        _1958_: 359,
        _1959_: 407,
        _1960_: 461,
      },
      {
        month: "NOV",
        _1958_: 310,
        _1959_: 362,
        _1960_: 390,
      },
      {
        month: "DEC",
        _1958_: 337,
        _1959_: 405,
        _1960_: 432,
      },
    ],
  },
];

describe("Preview Section component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should show empty preview when there are no loaded files", () => {
    renderComponent(store);
    expect(screen.getByTestId("preview-empty-container")).toBeInTheDocument();
  });

  it("should show of loaded files are there", () => {
    renderComponent(updatedStore);
  });

  it("should trigger the dataPreview API: SUCCESS", () => {
    dataPreview.mockImplementationOnce((params) =>
      params.onSuccess(mockSuccessResponse)
    );
    renderComponent(updatedStore);
  });

  it("should trigger the dataPreview API: ERROR", () => {
    dataPreview.mockImplementationOnce((params) => params.onError("error"));
    renderComponent(updatedStore);
  });

  it("should trigger the dataPreview API: SUCCESS", () => {
    dataPreview.mockImplementationOnce((params) => params.onSuccess());
    renderComponent(updatedStore2);
  });
});
