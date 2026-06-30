import actionsTypes from "./actionTypes";

//use action as suffix for all action methods
function addNewChatAction(payload) {
  return {
    type: actionsTypes.chats.ADD_NEW_CHAT,
    payload,
  };
}

function deleteChatAction(payload) {
  return {
    type: actionsTypes.chats.DELETE_CHAT_ITEM,
    payload,
  };
}

const updateChatName = (payload) => {
  return {
    type: actionsTypes.chats.RENAME_CHAT_ITEM,
    payload,
  };
};

function setSelectedChatAction(payload) {
  return {
    type: actionsTypes.chats.SET_SELECTED_CHAT,
    payload,
  };
}

const setPreviewRefreshData = (payload) => {
  return {
    type: actionsTypes.chats.SET_PREVIEW_REFRESH_DATA,
    payload,
  };
};

const setPreviewTableData = (payload) => {
  return {
    type: actionsTypes.chats.SET_PREVIEW_TABLE_DATA,
    payload,
  };
};

function setUploadFileList(payload) {
  return {
    type: actionsTypes.chats.SET_UPLOAD_FILE_LIST,
    payload,
  };
}

function addLoadedFilesAction(payload) {
  return {
    type: actionsTypes.chats.ADD_LOADED_FILES,
    payload,
  };
}

function setSelectedFilesAction(payload) {
  return {
    type: actionsTypes.chats.SET_SELECTED_FILES,
    payload,
  };
}

function setFetchChatHistoryAction(payload) {
  return {
    type: actionsTypes.chats.SET_FETCH_CHAT_HISTORY,
    payload,
  };
}

function setFollowUpPromptAction(payload) {
  return {
    type: actionsTypes.chats.SET_FOLLOW_UP_PROMPT,
    payload,
  };
}
function setChatMetadataAction(payload) {
  return {
    type: actionsTypes.chats.SET_CHAT_METADATA,
    payload,
  };
}

function setColumnListAction(payload) {
  return {
    type: actionsTypes.chats.SET_COLUMN_LIST,
    payload,
  };
}

function setFetchPipelineHistoryAction(payload) {
  return {
    type: actionsTypes.chats.SET_FETCH_PIPELINE_HISTORY,
    payload,
  };
}

function setAPICallStatus(payload) {
  return {
    type: actionsTypes.chats.SET_API_CALLS_STATUS,
    payload,
  };
}

function addScheduleConfig(payload) {
  return {
    type: actionsTypes.chats.ADD_SCHEDULE_CONFIG,
    payload,
  };
}

function addScheduleConfigBulk(payload) {
  return {
    type: actionsTypes.chats.ADD_SCHEDULE_CONFIG_BULK,
    payload,
  };
}

function delteScheduleConfig(payload) {
  return {
    type: actionsTypes.chats.DELETE_SCHEDULE_CONFIG,
    payload,
  };
}

function updateScheduleConfig(payload) {
  return {
    type: actionsTypes.chats.UPDATE_SCHEDULE_CONFIG,
    payload,
  };
}

const setIsYamlSaved = (payload) => {
  return {
    type: actionsTypes.chats.SET_IS_YAML_SAVED,
    payload,
  };
};
const setIndexRanges = (range) => ({
  type: actionsTypes.chats.SET_INDEX_RANGE,
  payload: range,
});
const setSplitIndex = (splitIndex) => ({
  type: actionsTypes.chats.SET_SPLIT_INDEX,
  payload: splitIndex,
});
const setOpenInfo = (payload) => {
  return {
    type: actionsTypes.chats.SET_OPEN_INFO,
    payload,
  };
};

function setJobMode(payload) {
  return {
    type: actionsTypes.chats.SET_JOB_MODE,
    payload,
  };
}
function setRunNowHistoryFlag(payload) {
  return {
    type: actionsTypes.chats.SET_RUN_NOW_HISTORY_FLAG,
    payload,
  };
}
function setRunNowHistoryEngineType(payload) {
  return {
    type: actionsTypes.chats.SET_RUN_NOW_HISTORY_ENGINETYPE,
    payload,
  };
}
export {
  addNewChatAction,
  updateChatName,
  deleteChatAction,
  setSelectedChatAction,
  setPreviewRefreshData,
  setPreviewTableData,
  setIndexRanges,
  setSplitIndex,
  setUploadFileList,
  addLoadedFilesAction,
  setSelectedFilesAction,
  setFetchChatHistoryAction,
  setFollowUpPromptAction,
  setChatMetadataAction,
  setColumnListAction,
  setFetchPipelineHistoryAction,
  setAPICallStatus,
  addScheduleConfig,
  addScheduleConfigBulk,
  delteScheduleConfig,
  updateScheduleConfig,
  setIsYamlSaved,
  setJobMode,
  setOpenInfo,
  setRunNowHistoryFlag,
  setRunNowHistoryEngineType,
};
