import actionsTypes from "./actionTypes";

//get all dags list
export const setDagsListAction = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_DAGS_LIST,
    payload,
  };
};
export const setDagsTotalCount = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_DAGS_TOTAL,
    payload,
  };
};
export const setCurrentPage = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_CURRENT_PAGE,
    payload,
  };
};
export const setPageSize = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_PAGE_SIZE,
    payload,
  };
};
export const setDbList = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_DB_LIST,
    payload,
  };
};
export const setLogValue = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_LOG_VALUE,
    payload,
  };
};
export const setRunNowStatus = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_RUN_NOW_STATUS,
    payload,
  };
};
export const setRunNowHistoryStatus = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_RUN_NOW_HISTORY_STATUS,
    payload,
  };
};
export const setScheduleStatus = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_SCHEDULE_STATUS,
    payload,
  };
};

export const setRunNowLogValue = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_RUN_NOW_LOG_VALUE,
    payload,
  };
};
export const setJobModal = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_OPEN_JOB_MODAL,
    payload,
  };
};
export const setJobReadMode = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_JOB_READ_MODE,
    payload,
  };
};
export const setChildDrawer = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_CHILD_DRAWER,
    payload,
  };
};
export const setJobListDetails = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_JOB_LIST_DETAILS,
    payload,
  };
};

export const updateJobListDetails = (payload) => {
  return {
    type: actionsTypes.jobSchedule.UPDATE_JOB_LIST_DETAILS,
    payload,
  };
};

export const setJobDetails = (run_id, job_id, local, schedule_id, message) => {
  return {
    type: actionsTypes.jobSchedule.SET_LOG_DETAILS,
    payload: { run_id, job_id, local, schedule_id, message },
  };
};
export const setRunHistory = ({
  job_id,
  run_id,
  timestamp,
  local,
  engine_type,
  schedule_id
}) => {
  return {
    type: actionsTypes.jobSchedule.SET_RUN_HISTORY,
    payload: { job_id, run_id, timestamp, local, engine_type,schedule_id },
  };
};

export const setLogModal = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_LOG_MODAL,
    payload,
  };
};

export const setIndividualJob = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_INDIVIDUAL_JOB,
    payload,
  };
};

export const setDagInfo = (payload) => {
  return {
    type: actionsTypes.jobSchedule.SET_DAG_INFO,
    payload,
  };
};
