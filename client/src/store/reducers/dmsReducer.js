import actionsTypes from "../actions/actionTypes";
import { produce } from "immer";

const initialState = {
  selectedPipelineMode: "",
  selectedSourceTable: [],
  selectedDestinationTable :[],
  queryMode: "replace",
  primaryKey: "",
  incrementKey:"",
  customSql: "",
  targetTableName: "",
  targetSchemaName: "public",
  selectedServiceType: null,
  dmsJobs: {},
  selectedDmsChat: {},
  step: 0,
  selectedSourceTypeForDrawer: null,
  selectedDestinationTypeForDrawer: null,
  pipelineModeSourceType: null,
  pipelineModeDestinationType: null,
  sourceTypeError: "",
  destinationTypeError: "",
  sourceConnectionId:"",
  destinationConnectionId:"",
  dmsProgressDetails:{},
  dmsLogValue:"",
  dmsStatus:"",
  dmsRunHistory: {},
};

const {
  SET_PIPELINE_MODE,
  SET_SELECTED_SOURCE_TABLE,
  SET_SELECTED_DESTINATION_TABLE,
  SET_QUERY_MODE,
  SET_PRIMARY_KEY,
  SET_INCREMENT_KEY,
  SET_CUSTOM_SQL,
  SET_SELECTED_SERVICE_TYPE,
  SET_DMS_JOBS,
  ADD_NEW_DMS_CHAT,
  SET_DMS_SELECTED_CHAT,
  DMS_STEPS,
  DELETE_DMS_CHAT_ITEM,
  RENAME_DMS_CHAT_ITEM,
  SET_SELECTED_SOURCE_TYPE_FOR_DRAWER,
  SET_SELECTED_DESTINATION_TYPE_FOR_DRAWER,
  SET_PIPELINE_MODE_SOURCE_AND_DESTINATION_TYPES,
  SET_SOURCE_TYPE_ERROR,
  SET_DESTINATION_TYPE_ERROR,
  SET_TARGET_TABLE_NAME,
  SET_TARGET_SCHEMA_NAME,
  SET_SOURCE_CONNECTION_ID,
  SET_DESTINATION_CONNECTION_ID,
  SET_DMS_PROGRESS_DETAILS,
  SET_DMS_LOG_VALUE,
  SET_DMS_LOG_STATUS,
  SET_DMS_RUN_HISTORY,
  ADD_DMS_SCHEDULE_CONFIG,
  ADD_DMS_SCHEDULE_CONFIG_BULK,
  UPDATE_DMS_SCHEDULE_CONFIG,
  DELETE_DMS_SCHEDULE_CONFIG,
} = actionsTypes.dms;

function dmsReducer(state = initialState, action) {
  switch (action.type) {
    case SET_PIPELINE_MODE: {
      return {
        ...state,
        selectedPipelineMode: action.payload,
      };
    }
    case SET_SELECTED_SOURCE_TABLE: {
      return {
        ...state,
        selectedSourceTable: action.payload,
      };
    }
    case SET_SELECTED_DESTINATION_TABLE: {
      return {
        ...state,
        selectedDestinationTable: action.payload,
      };
    }
    case SET_QUERY_MODE: {
      return {
        ...state,
        queryMode: action.payload,
      };
    }
    case SET_PRIMARY_KEY: {
      return {
        ...state,
        primaryKey: action.payload,
      };
    }
    case SET_INCREMENT_KEY: {
      return {
        ...state,
        incrementKey: action.payload,
      };
    }
    case SET_CUSTOM_SQL: {
      return {
        ...state,
        customSql: action.payload,
      };
    }
    case SET_SELECTED_SERVICE_TYPE:
      return {
        ...state,
        selectedServiceType: action.payload,
      };
    case SET_DMS_JOBS: {
      const jobsArray = action.payload;
      const jobsObject = {};
      if (Array.isArray(jobsArray)) {
        jobsArray.forEach((job) => {
          jobsObject[job.chat_id] = job;
        });
      }
      return {
        ...state,
        dmsJobs: jobsObject,
      };
    }
    case ADD_NEW_DMS_CHAT: {
      const chat = action.payload;
      return produce(state, (draft) => {
        draft.dmsJobs[chat.chat_id] = chat;
      });
    }
    case SET_DMS_SELECTED_CHAT: {
      return produce(state, (draft) => {
        draft.selectedDmsChat = action.payload;
      });
    }
    case DMS_STEPS: {
      return produce(state, (draft) => {
        draft.step = action.payload;
      });
    }
    case DELETE_DMS_CHAT_ITEM: {
      const { chat_id } = action.payload;
      return produce(state, (draft) => {
        delete draft.dmsJobs[chat_id];
      });
    }
    case RENAME_DMS_CHAT_ITEM: {
      const { chat_id, chat_name } = action.payload;
      return produce(state, (draft) => {
        draft.dmsJobs[chat_id] = {
          ...state.dmsJobs[chat_id],
          chat_name,
        };
        if (
          draft.selectedDmsChat &&
          draft.selectedDmsChat.chat_id === chat_id
        ) {
          draft.selectedDmsChat.chat_name = chat_name;
        }
      });
    }
    case SET_SELECTED_SOURCE_TYPE_FOR_DRAWER: {
      return {
        ...state,
        selectedSourceTypeForDrawer: action.payload,
      };
    }
    case SET_SELECTED_DESTINATION_TYPE_FOR_DRAWER: {
      return {
        ...state,
        selectedDestinationTypeForDrawer: action.payload,
      };
    }
    case SET_PIPELINE_MODE_SOURCE_AND_DESTINATION_TYPES: {
      return {
        ...state,
        pipelineModeSourceType: action.payload.sourceType,
        pipelineModeDestinationType: action.payload.destinationType,
      };
    }
    case SET_SOURCE_TYPE_ERROR: {
      return {
        ...state,
        sourceTypeError: action.payload,
      };
    }

    case SET_DESTINATION_TYPE_ERROR: {
      return {
        ...state,
        destinationTypeError: action.payload,
      };
    }
    case SET_TARGET_TABLE_NAME: {
      return {
        ...state,
        targetTableName: action.payload,
      };
    }

    case SET_TARGET_SCHEMA_NAME: {
      return {
        ...state,
        targetSchemaName: action.payload,
      };
    }

    case SET_SOURCE_CONNECTION_ID: {
      return {
        ...state,
        sourceConnectionId: action.payload,
      };
    }
    case SET_DESTINATION_CONNECTION_ID: {
      return {
        ...state,
        destinationConnectionId: action.payload,
      };
    }
    case SET_DMS_PROGRESS_DETAILS: {
      return {
        ...state,
        dmsProgressDetails: action.payload,
      };
    }
    case SET_DMS_LOG_VALUE: {
      return {
        ...state,
        dmsLogValue: `${state.dmsLogValue}${action.payload}`,
      };
    }
    case SET_DMS_LOG_STATUS: {
      return {
        ...state,
        dmsStatus: action.payload,
      };
    }
    case SET_DMS_RUN_HISTORY: {
      const { job_id, run_id, timestamp, local, engine_type } = action.payload;
      const jobRuns = state.dmsRunHistory[job_id] || [];
      const updatedHistory = [
        { run_id, timestamp, local, engine_type },
        ...jobRuns,
      ]
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 10);
      return {
        ...state,
        dmsRunHistory: {
          ...state.dmsRunHistory,
          [job_id]: updatedHistory,
        },
      };
    }
    case ADD_DMS_SCHEDULE_CONFIG: {
      const { chat_id, data, event } = action.payload;
      return produce(state, (draft) => {
        if (!draft.dmsJobs[chat_id]) {
          draft.dmsJobs[chat_id] = { chat_id };
        }
        if (event === "update") {
          draft.dmsJobs[chat_id].dmsScheduleConfig = data;
        } else {
          let prevConfigs = draft.dmsJobs[chat_id].dmsScheduleConfig || [];
          draft.dmsJobs[chat_id].dmsScheduleConfig = [...prevConfigs, data];
        }
      });
    }
    case ADD_DMS_SCHEDULE_CONFIG_BULK: {
      const { chat_id, data, event } = action.payload;
      return produce(state, (draft) => {
        if (!draft.dmsJobs[chat_id]) {
          draft.dmsJobs[chat_id] = { chat_id };
        }
        if (event === "update") {
          draft.dmsJobs[chat_id].dmsScheduleConfig = data;
        } else {
          draft.dmsJobs[chat_id].dmsScheduleConfig = [...data];
        }
      });
    }
    case DELETE_DMS_SCHEDULE_CONFIG: {
      const { key, chat_id } = action.payload;
      return produce(state, (draft) => {
        const filteredData = draft.dmsJobs[chat_id]?.dmsScheduleConfig?.filter(
          (config) => config.key !== key,
        );
        draft.dmsJobs[chat_id].dmsScheduleConfig = filteredData;
      });
    }
    case UPDATE_DMS_SCHEDULE_CONFIG: {
      const { data, chat_id } = action.payload;
      return produce(state, (draft) => {
        if (draft.dmsJobs[chat_id]) {
          draft.dmsJobs[chat_id].dmsScheduleConfig = data;
        }
      });
    }
    case "RESET_DMS_STATE": {
      return {
        ...initialState,
        dmsJobs: state.dmsJobs,
        selectedDmsChat: state.selectedDmsChat,
        dmsRunHistory:state.dmsRunHistory,
      };
    }
    case "RESET_DMS_LOG_VALUE": {
      return {
        ...state,
        dmsLogValue: "",
      };
    }
    default: {
      return { ...state };
    }
  }
}

export default dmsReducer;
