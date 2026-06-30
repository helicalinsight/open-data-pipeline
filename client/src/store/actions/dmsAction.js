import actionsTypes from "./actionTypes";
export const setSelectPipelineModeAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_PIPELINE_MODE,
    payload,
  };
};
export const setSelectedSourceTableAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_SELECTED_SOURCE_TABLE,
    payload,
  };
};
export const setSelectedDestinationTableAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_SELECTED_DESTINATION_TABLE,
    payload,
  };
};

export const setQueryModeAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_QUERY_MODE,
    payload,
  };
};
export const setPrimaryKeyAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_PRIMARY_KEY,
    payload,
  };
};
export const setIncrementKeyAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_INCREMENT_KEY,
    payload,
  };
};
export const setCustomSqlAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_CUSTOM_SQL,
    payload,
  };
};
export const setSelectedServiceType = (payload) => {
  return {
    type: actionsTypes.dms.SET_SELECTED_SERVICE_TYPE,
    payload,
  };
};
export const setDmsJobsAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_DMS_JOBS,
    payload,
  };
};

export const setDmsSelectedChatAction =(payload)=> {
  return {
    type: actionsTypes.dms.SET_DMS_SELECTED_CHAT,
    payload,
  };
}

export const  addNewDmsChatAction=(payload)=> {
  return {
    type: actionsTypes.dms.ADD_NEW_DMS_CHAT,
    payload,
  };
}
export const  addsetDmsStepsAction=(payload)=> {
  return {
    type: actionsTypes.dms.DMS_STEPS,
    payload,
  };
}
export const deleteDmsChatAction= (payload)=> {
  return {
    type: actionsTypes.dms.DELETE_DMS_CHAT_ITEM,
    payload,
  };
}
export const updateDmsChatName = (payload) => {
  return {
    type: actionsTypes.dms.RENAME_DMS_CHAT_ITEM,
    payload,
  };
};

export const setSelectedSourceTypeForDrawerAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_SELECTED_SOURCE_TYPE_FOR_DRAWER,
    payload,
  };
};

export const setSelectedDestinationTypeForDrawerAction = (payload) => {
  return {
    type: actionsTypes.dms.SET_SELECTED_DESTINATION_TYPE_FOR_DRAWER,
    payload,
  };
};

export const setPipelineModeSourceAndDestinationTypesAction = (sourceType, destinationType) => {
  return {
    type: actionsTypes.dms.SET_PIPELINE_MODE_SOURCE_AND_DESTINATION_TYPES,
    payload: { sourceType, destinationType },
  };
};

export const setSourceTypeErrorAction = (payload) => ({
  type: actionsTypes.dms.SET_SOURCE_TYPE_ERROR,
  payload,
});

export const setDestinationTypeErrorAction = (payload) => ({
  type: actionsTypes.dms.SET_DESTINATION_TYPE_ERROR,
  payload,
});
export const setTargetTableNameAction = (payload) => ({
  type: actionsTypes.dms.SET_TARGET_TABLE_NAME,
  payload,
});

export const setTargetSchemaNameAction = (payload) => ({
  type: actionsTypes.dms.SET_TARGET_SCHEMA_NAME,
  payload,
});   

export const setSourceConnectionIdAction = (payload) => ({
  type: actionsTypes.dms.SET_SOURCE_CONNECTION_ID,
  payload,
}); 
export const setDestinationConnectionIdAction = (payload) => ({
  type: actionsTypes.dms.SET_DESTINATION_CONNECTION_ID,
  payload,
});
export const setDmsProgessDetailsAction = (payload) => ({
  type: actionsTypes.dms.SET_DMS_PROGRESS_DETAILS,
  payload,
});

export const setDmsLogValue = (payload) => {
  return {
    type: actionsTypes.dms.SET_DMS_LOG_VALUE,
    payload,
  };
};

export const setDmsLogStatus = (payload) => {
  return {
    type: actionsTypes.dms.SET_DMS_LOG_STATUS,
    payload,
  };
};
export const setDmsRunHistory = ({
  job_id,
  run_id,
  timestamp,
  local,
  engine_type,
}) => {
  return {
    type: actionsTypes.dms.SET_DMS_RUN_HISTORY,
    payload: { job_id, run_id, timestamp, local, engine_type },
  };
};

export const addDmsScheduleConfig = (payload) => {
  return {
    type: actionsTypes.dms.ADD_DMS_SCHEDULE_CONFIG,
    payload,
  };
};

export const addDmsScheduleConfigBulk = (payload) => {
  return {
    type: actionsTypes.dms.ADD_DMS_SCHEDULE_CONFIG_BULK,
    payload,
  };
};

export const deleteDmsScheduleConfig = (payload) => {
  return {
    type: actionsTypes.dms.DELETE_DMS_SCHEDULE_CONFIG,
    payload,
  };
};

export const updateDmsScheduleConfig = (payload) => {
  return {
    type: actionsTypes.dms.UPDATE_DMS_SCHEDULE_CONFIG,
    payload,
  };
};