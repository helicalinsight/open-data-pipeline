import { updateOrAddObject } from "../../utils/updateOrAddObject";
import actionsTypes from "../actions/actionTypes";
import { produce } from "immer";

let intialState = {
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
  ADD_SCHEDULE_CONFIG_BULK,
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

function chatReducer(state = intialState, action) {
  switch (action.type) {
    case ADD_NEW_CHAT: {
      const chat = action.payload;
      return produce(state, (draft) => {
        draft.chatList[chat.chat_id] = chat;
      });
    }

    case DELETE_CHAT_ITEM: {
      const { chat_id } = action.payload;
      return produce(state, (draft) => {
        delete draft.chatList[chat_id];
      });
    }
    case SET_SPLIT_INDEX:
      return { ...state, splitIndex: action.payload };
    case SET_INDEX_RANGE:
      return { ...state, indexRange: action.payload };

    case RENAME_CHAT_ITEM: {
      const { chat_id, chat_name } = action.payload;
      return produce(state, (draft) => {
        draft.chatList[chat_id] = {
          ...state.chatList[chat_id],
          chat_name,
        };
        if (draft.selectedChat && draft.selectedChat.chat_id === chat_id) {
          draft.selectedChat.chat_name = chat_name;
        }
      });
    }
    case SET_SELECTED_CHAT: {
      return produce(state, (draft) => {
        draft.selectedChat = action.payload;
      });
    }
    case SET_PREVIEW_REFRESH_DATA: {
      return produce(state, (draft) => {
        draft.previewRefresh = action.payload;
      });
    }
    case SET_PREVIEW_TABLE_DATA: {
      return produce(state, (draft) => {
        draft.previewTableData = action.payload;
      });
    }

    case ADD_LOADED_FILES: {
      const { files, chat_id, payload } = action.payload;
      return produce(state, (draft) => {
        let prevFiles = draft.chatList[chat_id].loadedFiles || [];
        if (payload) {
          // payload when upating name
          draft.chatList[chat_id].loadedFiles = prevFiles.map((file) => {
            if (file.source_id === payload.source_id) {
              return {
                ...file,
                alias: payload.new_file_name,
              };
            }
            return file;
          });
        } else {
          if (prevFiles.length === files.length) {
            if (JSON.stringify(prevFiles) !== JSON.stringify(files)) {
              draft.chatList[chat_id].loadedFiles = [...files];
            }
          } else {
            draft.chatList[chat_id].loadedFiles = [...files];
          }
        }
      });
    }

    case SET_SELECTED_FILES: {
      const { files, chat_id } = action.payload;
      return produce(state, (draft) => {
        let prevFiles = draft.chatList[chat_id].selectedFiles || [];
        if (prevFiles.length === files.length) {
          if (JSON.stringify(prevFiles) !== JSON.stringify(files)) {
            draft.chatList[chat_id].selectedFiles = [...files];
          }
        } else {
          draft.chatList[chat_id].selectedFiles = [...files];
        }
      });
    }

    case ADD_SCHEDULE_CONFIG: {
      const { chat_id, data, event } = action.payload;
      return produce(state, (draft) => {
        if (event === "update") {
          draft.chatList[chat_id].scheduleConfig = data;
        } else {
          let prevFiles = draft.chatList[chat_id].scheduleConfig || [];
          draft.chatList[chat_id].scheduleConfig = [...prevFiles, data];
        }
      });
    }
    case ADD_SCHEDULE_CONFIG_BULK: {
      const { chat_id, data, event } = action.payload;
      return produce(state, (draft) => {
        if (!draft.chatList[chat_id]) {
          draft.chatList[chat_id] = {
            scheduleConfig: [],
          };
        }
        if (event === "update") {
          draft.chatList[chat_id].scheduleConfig = data;
        } else {
          draft.chatList[chat_id].scheduleConfig = [...data];
        }
      });
    }
    case DELETE_SCHEDULE_CONFIG: {
      const { key, chat_id } = action.payload;

      return produce(state, (draft) => {
        const filteredData = draft.chatList[chat_id]?.scheduleConfig?.filter(
          (config) => config.key !== key
        );
        draft.chatList[chat_id].scheduleConfig = filteredData;
      });
    }

    case UPDATE_SCHEDULE_CONFIG: {
      const { data, chat_id } = action.payload;

      return produce(state, (draft) => {
        draft.chatList[chat_id].scheduleConfig = data;
      });
    }

    case SET_IS_YAML_SAVED: {
      const { saved, chat_id } = action.payload;

      return produce(state, (draft) => {
        draft.chatList[chat_id].isYamlSaved = saved;
      });
    }

    case SET_COLUMN_LIST: {
      const { files, chat_id } = action.payload;
      return produce(state, (draft) => {
        draft.chatList[chat_id].columnList = files;
      });
    }

    case SET_FETCH_CHAT_HISTORY: {
      const { chat_id, value } = action.payload;
      return produce(state, (draft) => {
        draft.chatList[chat_id].fetchChatHistory = value;
      });
    }

    case SET_FOLLOW_UP_PROMPT: {
      const { chat_id, prompts } = action.payload;
      return produce(state, (draft) => {
        draft.chatList[chat_id].followUpPrompts = prompts;
      });
    }

    case SET_UPLOAD_FILE_LIST: {
      if (!action.payload) {
        return produce(state, (draft) => {
          draft.uploadFileList = [];
        });
      }
      const { message_id, files } = action.payload;
      let data = {
        message_id,
        files,
      };

      return produce(state, (draft) => {
        draft.uploadFileList = [data];
      });
    }
    case SET_CHAT_METADATA: {
      const { chat_id, metadata } = action.payload;
      return produce(state, (draft) => {
        if (draft.chatList[chat_id]) {
          draft.chatList[chat_id].metadata = metadata;
        }
      });
    }

    case SET_API_CALLS_STATUS: {
      const { chat_id, apiData } = action.payload;
      return produce(state, (draft) => {
        const apiCallsStatuses = draft.chatList[chat_id]?.apiCallsStatus || [];
        const condition = (item) => item.name === apiData.name;

        const updatedStauses = updateOrAddObject(
          apiCallsStatuses,
          condition,
          apiData
        );

        if (draft.chatList[chat_id]) {
          draft.chatList[chat_id].apiCallsStatus = updatedStauses;
        }
      });
    }

    case SET_FETCH_PIPELINE_HISTORY: {
      const { chat_id, value } = action.payload;
      return produce(state, (draft) => {
        draft.chatList[chat_id].pipelineHistory = value;
      });
    }

    case SET_JOB_MODE: {
      return produce(state, (draft) => {
        draft.jobMode = action.payload;
      });
    }
    case SET_OPEN_INFO: {
      return produce(state, (draft) => {
        draft.openInfo = action.payload;
      });
    }
    case SET_RUN_NOW_HISTORY_FLAG: {
      return produce(state, (draft) => {
        draft.runNowHistoryFlag = action.payload;
      });
    }
    case SET_RUN_NOW_HISTORY_ENGINETYPE: {
      return produce(state, (draft) => {
        draft.runNowHistoryEngineType = action.payload;
      });
    }
    case "RESET_STATE":
      return intialState;

    default: {
      return { ...state };
    }
  }
}

export default chatReducer;
