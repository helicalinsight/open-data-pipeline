import actionsTypes from "../../../store/actions/actionTypes";
import { chatReducer } from "../../../store/reducers";

const {
  ADD_NEW_CHAT,
  DELETE_CHAT_ITEM,
  RENAME_CHAT_ITEM,
  SET_SELECTED_CHAT,
  SET_PREVIEW_REFRESH_DATA,
  SET_PREVIEW_TABLE_DATA,
  SET_UPLOAD_FILE_LIST,
  ADD_LOADED_FILES,
  SET_SELECTED_FILES,
  SET_FETCH_CHAT_HISTORY,
  SET_FOLLOW_UP_PROMPT,
  SET_CHAT_METADATA,
  SET_COLUMN_LIST,
  SET_FETCH_PIPELINE_HISTORY,
  SET_API_CALLS_STATUS,
  ADD_SCHEDULE_CONFIG,
  UPDATE_SCHEDULE_CONFIG,
  DELETE_SCHEDULE_CONFIG,
  SET_IS_YAML_SAVED,
  SET_JOB_MODE,
  SET_INDEX_RANGE,
  SET_SPLIT_INDEX,
  SET_OPEN_INFO,
  SET_RUN_NOW_HISTORY_ENGINETYPE,
  SET_RUN_NOW_HISTORY_FLAG,
} = actionsTypes.chats;

describe("chatReducer", () => {
  const initialState = {
    chatList: {},
    selectedChat: {},
    jobConfigs: {},
    previewRefresh: { id: "", refresh: false },
    previewTableData: {
      coloumns: [],
      datasource: [],
    },
    uploadFileList: [],
    scheduleConfig: [],
    jobMode: "",
    splitIndex: 2,
    indexRange: [0, 2],
    openInfo: false,
    runNowHistoryFlag: false,
    runNowHistoryEngineType: null,
  };

  it("should return the initial state", () => {
    expect(chatReducer(undefined, {})).toEqual(initialState);
  });

  it("should handle ADD_NEW_CHAT", () => {
    const chat = { chat_id: "1", chat_name: "New Chat" };
    const action = { type: ADD_NEW_CHAT, payload: chat };
    expect(chatReducer(initialState, action)).toEqual({
      ...initialState,
      chatList: { 1: chat },
    });
  });

  it("should handle DELETE_CHAT_ITEM", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1", chat_name: "Chat 1" } },
    };
    const action = { type: DELETE_CHAT_ITEM, payload: { chat_id: "1" } };
    expect(chatReducer(state, action)).toEqual({
      ...initialState,
      chatList: {},
    });
  });

  it("should handle RENAME_CHAT_ITEM", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1", chat_name: "Chat 1" } },
      selectedChat: { chat_id: "1", chat_name: "Chat 1" },
    };
    const action = {
      type: RENAME_CHAT_ITEM,
      payload: { chat_id: "1", chat_name: "Renamed Chat" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", chat_name: "Renamed Chat" } },
      selectedChat: { chat_id: "1", chat_name: "Renamed Chat" },
    });
  });

  it("should handle SET_SELECTED_CHAT", () => {
    const selectedChat = { chat_id: "1", chat_name: "Selected Chat" };
    const action = { type: SET_SELECTED_CHAT, payload: selectedChat };
    expect(chatReducer(initialState, action)).toEqual({
      ...initialState,
      selectedChat,
    });
  });

  it("should handle SET_PREVIEW_REFRESH_DATA", () => {
    const previewRefresh = { id: "1", refresh: true };
    const action = { type: SET_PREVIEW_REFRESH_DATA, payload: previewRefresh };
    expect(chatReducer(initialState, action)).toEqual({
      ...initialState,
      previewRefresh,
    });
  });

  it("should handle SET_PREVIEW_TABLE_DATA", () => {
    const previewTableData = {
      coloumns: ["col1", "col2"],
      datasource: [{ col1: "data1", col2: "data2" }],
    };
    const action = { type: SET_PREVIEW_TABLE_DATA, payload: previewTableData };
    expect(chatReducer(initialState, action)).toEqual({
      ...initialState,
      previewTableData,
    });
  });

  it("should handle SET_UPLOAD_FILE_LIST", () => {
    const uploadFileList = {
      message_id: "1",
      files: ["file1.txt", "file2.txt"],
    };
    const action = { type: SET_UPLOAD_FILE_LIST, payload: uploadFileList };
    expect(chatReducer(initialState, action)).toEqual({
      ...initialState,
      uploadFileList: [uploadFileList],
    });
  });

  it("should handle ADD_LOADED_FILES", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1", loadedFiles: [] } },
    };
    const files = [{ source_id: "1", name: "file1.txt" }];
    const action = { type: ADD_LOADED_FILES, payload: { files, chat_id: "1" } };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", loadedFiles: files } },
    });
  });

  it("should handle SET_SELECTED_FILES", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1", selectedFiles: [] } },
    };
    const files = [{ source_id: "1", name: "file1.txt" }];
    const action = {
      type: SET_SELECTED_FILES,
      payload: { files, chat_id: "1" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", selectedFiles: files } },
    });
  });

  it("should handle SET_FETCH_CHAT_HISTORY", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
    };
    const action = {
      type: SET_FETCH_CHAT_HISTORY,
      payload: { chat_id: "1", value: true },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", fetchChatHistory: true } },
    });
  });

  it("should handle SET_FOLLOW_UP_PROMPT", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
    };
    const prompts = ["Prompt 1", "Prompt 2"];
    const action = {
      type: SET_FOLLOW_UP_PROMPT,
      payload: { chat_id: "1", prompts },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", followUpPrompts: prompts } },
    });
  });

  it("should handle SET_CHAT_METADATA", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
    };
    const metadata = { key: "value" };
    const action = {
      type: SET_CHAT_METADATA,
      payload: { chat_id: "1", metadata },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", metadata } },
    });
  });

  it("should handle SET_COLUMN_LIST", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
    };
    const files = ["column1", "column2"];
    const action = { type: SET_COLUMN_LIST, payload: { chat_id: "1", files } };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", columnList: files } },
    });
  });

  it("should handle SET_FETCH_PIPELINE_HISTORY", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
    };
    const action = {
      type: SET_FETCH_PIPELINE_HISTORY,
      payload: { chat_id: "1", value: true },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", pipelineHistory: true } },
    });
  });

  it("should handle SET_API_CALLS_STATUS", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1", apiCallsStatus: [] } },
    };
    const apiData = { name: "API1", status: "success" };
    const action = {
      type: SET_API_CALLS_STATUS,
      payload: { apiData, chat_id: "1" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", apiCallsStatus: [apiData] } },
    });
  });

  it("should handle ADD_SCHEDULE_CONFIG", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1", scheduleConfig: [] } },
    };
    const config = { key: "1", schedule: "0 0 * * *" };
    const action = {
      type: ADD_SCHEDULE_CONFIG,
      payload: { data: config, chat_id: "1" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", scheduleConfig: [config] } },
    });
  });

  it("should handle UPDATE_SCHEDULE_CONFIG", () => {
    const state = {
      ...initialState,
      chatList: {
        1: {
          chat_id: "1",
          scheduleConfig: [{ key: "1", schedule: "0 0 * * *" }],
        },
      },
    };
    const updatedConfig = [{ key: "1", schedule: "0 12 * * *" }];
    const action = {
      type: UPDATE_SCHEDULE_CONFIG,
      payload: { data: updatedConfig, chat_id: "1" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", scheduleConfig: updatedConfig } },
    });
  });

  it("should handle DELETE_SCHEDULE_CONFIG", () => {
    const state = {
      ...initialState,
      chatList: {
        1: {
          chat_id: "1",
          scheduleConfig: [{ key: "1", schedule: "0 0 * * *" }],
        },
      },
    };
    const action = {
      type: DELETE_SCHEDULE_CONFIG,
      payload: { key: "1", chat_id: "1" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", scheduleConfig: [] } },
    });
  });

  it("should handle SET_IS_YAML_SAVED", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
    };
    const action = {
      type: SET_IS_YAML_SAVED,
      payload: { saved: true, chat_id: "1" },
    };
    expect(chatReducer(state, action)).toEqual({
      ...state,
      chatList: { 1: { chat_id: "1", isYamlSaved: true } },
    });
  });

  it("should handle SET_JOB_MODE", () => {
    const newJobMode = "llm";
    const action = { type: SET_JOB_MODE, payload: newJobMode };
    const expectedState = {
      ...initialState,
      jobMode: newJobMode,
    };
    expect(chatReducer(initialState, action)).toEqual(expectedState);
  });

  it("should handle SET_SPLIT_INDEX", () => {
    const action = { type: SET_SPLIT_INDEX, payload: 5 };
    const expectedState = {
      ...initialState,
      splitIndex: 5,
    };
    expect(chatReducer(initialState, action)).toEqual(expectedState);
  });

  it("should handle SET_INDEX_RANGE", () => {
    const action = { type: SET_INDEX_RANGE, payload: [1, 3] };
    const expectedState = {
      ...initialState,
      indexRange: [1, 3],
    };
    expect(chatReducer(initialState, action)).toEqual(expectedState);
  });

  it("should handle SET_OPEN_INFO to true", () => {
    const action = { type: SET_OPEN_INFO, payload: true };
    const expectedState = {
      ...initialState,
      openInfo: true,
    };
    expect(chatReducer(initialState, action)).toEqual(expectedState);
  });

  it("should handle SET_OPEN_INFO to false", () => {
    const state = { ...initialState, openInfo: true };
    const action = { type: SET_OPEN_INFO, payload: false };
    const expectedState = {
      ...initialState,
      openInfo: false,
    };
    expect(chatReducer(state, action)).toEqual(expectedState);
  });

  it("should handle SET_RUN_NOW_HISTORY_FLAG to true", () => {
    const action = { type: SET_RUN_NOW_HISTORY_FLAG, payload: true };
    const expectedState = {
      ...initialState,
      runNowHistoryFlag: true,
    };
    expect(chatReducer(initialState, action)).toEqual(expectedState);
  });

  it("should handle SET_RUN_NOW_HISTORY_FLAG to false", () => {
    const state = { ...initialState, runNowHistoryFlag: true };
    const action = { type: SET_RUN_NOW_HISTORY_FLAG, payload: false };
    const expectedState = {
      ...initialState,
      runNowHistoryFlag: false,
    };
    expect(chatReducer(state, action)).toEqual(expectedState);
  });
  it("should handle SET_RUN_NOW_HISTORY_ENGINETYPE", () => {
    const newhistoryEngineType = null;
    const action = {
      type: SET_RUN_NOW_HISTORY_ENGINETYPE,
      payload: newhistoryEngineType,
    };
    const expectedState = {
      ...initialState,
      runNowHistoryEngineType: newhistoryEngineType,
    };
    expect(chatReducer(initialState, action)).toEqual(expectedState);
  });
  it("should handle RESET_STATE", () => {
    const state = {
      ...initialState,
      chatList: { 1: { chat_id: "1" } },
      selectedChat: { chat_id: "1" },
    };
    const action = { type: "RESET_STATE" };
    expect(chatReducer(state, action)).toEqual(initialState);
  });

  it("should return current state for unknown action type", () => {
    const state = { ...initialState, chatList: { 1: { chat_id: "1" } } };
    const action = { type: "UNKNOWN_ACTION" };
    expect(chatReducer(state, action)).toEqual(state);
  });
});
