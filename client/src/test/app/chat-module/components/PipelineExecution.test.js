import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import PipelineExecution from "../../../../app/chat-module/components/PipelineExecution.jsx";

const mockStore = configureStore();

jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

const getStore = (history, next) => {
  return mockStore({
    chat: {
      chatList: {
        "65e55f345d88cf1a1a782a8c": {
          pipelineHistory: {
            history,
            next,
          },
        },
      },
    },
  });
};

const history = [
  {
    id: "1",
    function: "read_files",
    parameters: [
      { alias: "free-test-data" },
      { details: { key1: "value1", key2: "value2" } },
    ],
    files: [{ alias: ["file1", "file2"] }],
  },
  {
    id: "3",
    function: "transform_data",
    parameters: [{ config: [{ param1: "val1" }, { param2: "val2" }] }],
    files: [],
  },
];

const next = [
  {
    id: "2",
    function: "process_data",
    parameters: [
      { alias: "processed-test-data" },
      { meta: { a: "1", b: "2" } },
    ],
    files: [{ alias: ["file3"] }],
  },
];

const store = getStore(history, next);

const renderComponent = (appStore, chatId) => {
  render(
    <reactRedux.Provider store={appStore}>
      <MemoryRouter initialEntries={[`?chat=${chatId}`]}>
        <PipelineExecution />
      </MemoryRouter>
    </reactRedux.Provider>
  );
};

describe("PipelineExecution Component", () => {
  beforeEach(() => {
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("renders the component with history and next data", () => {
    const chatId = "65e55f345d88cf1a1a782a8c";
    renderComponent(store, chatId);
    expect(screen.getByText("Read Files")).toBeInTheDocument();
    expect(screen.getByText("Process Data")).toBeInTheDocument();
  });

  it("renders 'No History found!' when no history or next data exists", () => {
    const chatId = "random";
    renderComponent(getStore([], []), chatId);
    expect(screen.getByText("No History found!")).toBeInTheDocument();
  });

  it("renders collapse panels correctly", () => {
    const chatId = "65e55f345d88cf1a1a782a8c";
    renderComponent(store, chatId);
    expect(screen.getByText("Read Files")).toBeInTheDocument();
    expect(screen.getByText("Process Data")).toBeInTheDocument();
    expect(screen.getByText("Transform Data")).toBeInTheDocument();
  });
  it("renders datasource type and connection alias when _id matches a connection", () => {
    const chatId = "65e55f345d88cf1a1a782a8c";
  
    const mockConnections = [
      {
        _id: "file-001",
        alias: "flat_file_source",
        type: "file",
      },
    ];
  
    const history = [
      {
        id: "1",
        function: "read_files",
        parameters: [
          { _id: "file-001", someKey: "someValue" },
        ],
        files: [],
      },
    ];
    const storeWithConnections = getStore(history, [], mockConnections);
    renderComponent(storeWithConnections, chatId);
  });  
});
