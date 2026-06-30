import actionsTypes from "../actions/actionTypes";

const initialState = {
  dagList: [],
  dagTotal: null,
  currentPageInfo: 1,
  pageSizeInfo: 10,
  dbList: [],
  logValue: "",
  runnowLogValue: "",
  logDetails: {},
  jobModal: false,
  jobListDetails: {},
  isScheduleEditMode: false,
  childDrawer: false,
  runHistory: {},
  logModal: false,
  individualJob: false,
  dagInfo: {},
  runNowStatus: "",
  runNowHistoryStatus: "",
  scheduleStatus: "",
};

const {
  SET_DAGS_LIST,
  SET_DB_LIST,
  SET_LOG_VALUE,
  SET_RUN_NOW_LOG_VALUE,
  SET_LOG_DETAILS,
  SET_OPEN_JOB_MODAL,
  SET_JOB_LIST_DETAILS,
  UPDATE_JOB_LIST_DETAILS,
  SET_JOB_READ_MODE,
  SET_CHILD_DRAWER,
  SET_LOG_MODAL,
  SET_RUN_HISTORY,
  SET_INDIVIDUAL_JOB,
  SET_DAG_INFO,
  SET_DAGS_TOTAL,
  SET_PAGE_SIZE,
  SET_CURRENT_PAGE,
  SET_RUN_NOW_STATUS,
  SET_RUN_NOW_HISTORY_STATUS,
  SET_SCHEDULE_STATUS,
} = actionsTypes.jobSchedule;

function jobScheduleReducer(state = initialState, action) {
  switch (action.type) {
    case SET_DAGS_LIST: {
      return {
        ...state,
        dagList: [...action.payload],
      };
    }
    case SET_DB_LIST: {
      return {
        ...state,
        dbList: [...action.payload],
      };
    }
    case SET_LOG_VALUE: {
      return {
        ...state,
        logValue: `${state.logValue}${action.payload}`,
      };
    }
    // case SET_RUN_NOW_LOG_VALUE: {
    //   return {
    //     ...state,
    //     runnowLogValue: `${state.runnowLogValue}${action.payload}`,
    //   };
    // }
    case SET_RUN_NOW_LOG_VALUE: {
      return {
        ...state,
        runnowLogValue: `${state.runnowLogValue || ""}${action.payload}`,
      };
    }
    case SET_OPEN_JOB_MODAL: {
      return {
        ...state,
        jobModal: action.payload,
      };
    }
    case SET_DAGS_TOTAL: {
      return {
        ...state,
        dagTotal: action.payload,
      };
    }
    case SET_CURRENT_PAGE: {
      return {
        ...state,
        currentPageInfo: action.payload,
      };
    }
    case SET_PAGE_SIZE: {
      return {
        ...state,
        pageSizeInfo: action.payload,
      };
    }
    case SET_JOB_READ_MODE: {
      return {
        ...state,
        isScheduleEditMode: action.payload,
      };
    }
    case SET_CHILD_DRAWER: {
      return {
        ...state,
        childDrawer: action.payload,
      };
    }
    case SET_INDIVIDUAL_JOB: {
      return {
        ...state,
        individualJob: action.payload,
      };
    }
    case SET_DAG_INFO: {
      return {
        ...state,
        dagInfo: action.payload || {},
      };
    }
    case SET_LOG_MODAL: {
      return {
        ...state,
        logModal: action.payload,
      };
    }
    case SET_RUN_NOW_STATUS: {
      return {
        ...state,
        runNowStatus: action.payload,
      };
    }
    case SET_RUN_NOW_HISTORY_STATUS: {
      return {
        ...state,
        runNowHistoryStatus: action.payload,
      };
    }
    case SET_SCHEDULE_STATUS: {
      return {
        ...state,
        scheduleStatus: action.payload,
      };
    }
    case "RESET_LOG_VALUE": {
      return {
        ...state,
        logValue: "",
        logDetails: {},
        runnowLogValue: "",
      };
    }
    case SET_LOG_DETAILS: {
      return {
        ...state,
        logDetails: action.payload || {},
      };
    }
    case SET_JOB_LIST_DETAILS: {
      // const dataUpdated = [
      //   ...state.jobListDetails.job_details.configuration,
      //   action.payload.data,
      // ];
      // console.log("combinedConfig0001", dataUpdated);
      return {
        ...state,
        jobListDetails:
          action.payload.type === "new"
            ? {
                ...state.jobListDetails,
                job_details: {
                  ...state.jobListDetails.job_details,
                  configuration: [
                    ...state.jobListDetails.job_details.configuration,
                    action.payload.data,
                  ],
                },
              }
            : action.payload || {},
        // jobListDetails: action.payload,
      };
    }

    case UPDATE_JOB_LIST_DETAILS: {
      const newArr = action.payload?.data.map(({ key, ...rest }) => rest);
      return {
        ...state,
        jobListDetails: {
          ...state.jobListDetails,
          job_details: {
            ...state.jobListDetails.job_details,
            configuration: [...newArr],
          },
        },
      };
    }

    case SET_RUN_HISTORY: {
      const { job_id, run_id, timestamp, local, engine_type,schedule_id } = action.payload;
      const jobRuns = state.runHistory[job_id] || [];
      const updatedHistory = [
        { run_id, timestamp, local, engine_type,schedule_id },
        ...jobRuns,
      ]
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 10);
      return {
        ...state,
        runHistory: {
          ...state.runHistory,
          [job_id]: updatedHistory,
        },
      };
    }
    case "RESET_STATE":
      return initialState;
    default: {
      return { ...state };
    }
  }
}

export default jobScheduleReducer;
