import { v4 as uuidv4 } from "uuid";
import {
  addLoadedFilesAction,
  addScheduleConfig,
  setColumnListAction,
  setFetchPipelineHistoryAction,
  setJobMode,
  setPreviewRefreshData,
  setSelectedFilesAction,
} from "../store/actions/chatAction";
import { handleSessionExpiry } from "../utils/handleSessionExpiry";
import { getInformationApi, pipelineHistoryApi } from "./chatService";
import { convertToString } from "../utils/appUtils";
import {
  setAppVersion,
  setEditorSuggestions,
  setJobHelpInfo,
  setPreviewState,
  setUserConfig,
} from "../store/actions/appActions";
import { getApplication } from "./featureService";
import {
  setDatasourcesAction,
} from "../store/actions/databaseActions";
import { getDataSources } from "./databaseService";

export const triggerGetInfoAPI = (dispatch, chatId, rest) => {
  getInformationApi({
    query: "chat_id=" + chatId,
    onSuccess: (data) => {
      if (data.success) {
        const { chats } = data;
        if (data?.chats) {
          dispatch(setJobMode(chats?.job_mode));
        }
        if (chats?.loaded_files) {
          dispatch(
            addLoadedFilesAction({
              chat_id: chatId,
              files: chats.loaded_files,
            })
          );
        }
        if (chats?.cwf) {
          dispatch(
            setSelectedFilesAction({
              chat_id: chatId,
              files: [chats?.cwf],
            })
          );
        }
        if (chats?.metadata) {
          dispatch(
            setColumnListAction({
              chat_id: chatId,
              files: chats.metadata,
            })
          );
        }

        if (chats?.configurations) {
          const updated = Object.entries(chats.configurations).map(
            ([configKey, configValue]) => {
              return {
                configValue: convertToString(configValue),
                configKey,
                key: uuidv4(),
              };
            }
          );
          const payload = {
            chat_id: chatId,
            data: updated,
            event: "update",
          };
          dispatch(addScheduleConfig(payload));
        }

        if (rest?.refresh) {
          dispatch(
            setPreviewRefreshData({
              id: chatId,
              refresh: true,
            })
          );
        }
        if (rest?.showPreview) {
          dispatch(setPreviewState(true));
        }
      }
    },
    onError: (error) => {
      handleSessionExpiry(dispatch, error);
    },
  });
};

export const triggerPipelineHistory = (dispatch, chatId) => {
  pipelineHistoryApi({
    query: "chat_id=" + chatId,
    onSuccess: (data) => {
      dispatch(
        setFetchPipelineHistoryAction({
          chat_id: chatId,
          value: data,
        })
      );
    },
    onError: (error) => {
      handleSessionExpiry(dispatch, error);
    },
  });
};

export const triggerGetApplication = (dispatch) => {
  getApplication({
    onSuccess: (response) => {
      if (response?.configuration) {
        dispatch(setUserConfig(response.configuration));
      }
      if (response?.schedule_configuration) {
        localStorage.setItem(
          "schedule_configuration",
          JSON.stringify(response.schedule_configuration)
        );
      }
      if (response?.job_help_info) {
        dispatch(setJobHelpInfo(response.job_help_info));
      }
      if (response.editor_configuration) {
        dispatch(setEditorSuggestions(response.editor_configuration));
      }
      if (response?.version) {
        localStorage.setItem("app_version", JSON.stringify(response.version));
      }
    },
    onError: (error) => {
      handleSessionExpiry(dispatch, error);
    },
  });
};

export const triggerGetDatasources = (dispatch) => {
  getDataSources({
    onSuccess: (response) => {
      dispatch(setDatasourcesAction(response?.configuration?.datasources));
    },
    onError: (error) => {
      handleSessionExpiry(dispatch, error);
    },
  });
};

