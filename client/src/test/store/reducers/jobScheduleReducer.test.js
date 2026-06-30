import actionsTypes from "../../../store/actions/actionTypes";
import { jobScheduleReducer } from "../../../store/reducers";

const {
  SET_DAGS_LIST,
  SET_DB_LIST,
  SET_LOG_VALUE,
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
  SET_RUN_NOW_LOG_VALUE,
  SET_RUN_NOW_STATUS,
  SET_RUN_NOW_HISTORY_STATUS,
  SET_SCHEDULE_STATUS,
} = actionsTypes.jobSchedule;

describe("jobScheduleReducer", () => {
  const initialState = {
    dagList: [],
    dbList: [],
    logValue: "",
    logDetails: {},
    jobModal: false,
    jobListDetails: {},
    isScheduleEditMode: false,
    runnowLogValue: "",
    childDrawer: false,
    runHistory: {},
    logModal: false,
    individualJob: false,
    dagInfo: {},
    dagTotal: null,
    currentPageInfo: 1,
    pageSizeInfo: 10,
    runNowStatus: "",
    runNowHistoryStatus: "",
    scheduleStatus: "",
  };

  it("should return the initial state", () => {
    expect(jobScheduleReducer(undefined, {})).toEqual(initialState);
  });

  it("should handle SET_DAGS_LIST", () => {
    const action = {
      type: SET_DAGS_LIST,
      payload: [
        { id: 1, name: "DAG1" },
        { id: 2, name: "DAG2" },
      ],
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      dagList: action.payload,
    });
  });

  it("should handle SET_DB_LIST", () => {
    const action = {
      type: SET_DB_LIST,
      payload: [
        { id: 1, name: "DB1" },
        { id: 2, name: "DB2" },
      ],
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      dbList: action.payload,
    });
  });

  it("should handle SET_LOG_VALUE by appending the payload", () => {
    const action = {
      type: SET_LOG_VALUE,
      payload: "Some log message",
    };
    // First call - append to empty string
    let state = jobScheduleReducer(initialState, action);
    expect(state).toEqual({
      ...initialState,
      logValue: "Some log message",
    });
    state = jobScheduleReducer(state, action);
    expect(state).toEqual({
      ...initialState,
      logValue: "Some log messageSome log message",
    });
  });

  it("should handle SET_RUN_NOW_LOG_VALUE by appending the payload", () => {
    const action = {
      type: SET_RUN_NOW_LOG_VALUE,
      payload: "Some log message",
    };
    let state = jobScheduleReducer(initialState, action);
    expect(state).toEqual({
      ...initialState,
      runnowLogValue: "Some log message",
    });
    state = jobScheduleReducer(state, action);
    expect(state).toEqual({
      ...initialState,
      runnowLogValue: "Some log messageSome log message",
    });
  });

  it("should handle SET_RUN_NOW_LOG_VALUEE with initial undefined runnowLogValue", () => {
    const stateWithUndefined = {
      ...initialState,
      runnowLogValue: undefined,
    };
    const action = {
      type: SET_RUN_NOW_LOG_VALUE,
      payload: "Some log message",
    };
    const result = jobScheduleReducer(stateWithUndefined, action);
    expect(result).toEqual({
      ...initialState,
      runnowLogValue: "Some log message",
    });
  });

  it("should handle SET_LOG_DETAILS", () => {
    const action = {
      type: SET_LOG_DETAILS,
      payload: { run_id: "run_123", job_id: "job_456" },
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      logDetails: action.payload,
    });
  });

  it("should handle SET_LOG_DETAILS with nul payload", () => {
    const action = {
      type: SET_LOG_DETAILS,
      payload: null,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      logDetails: {},
    });
  });

  it("should handle SET_LOG_MODAL", () => {
    const action = {
      type: SET_LOG_MODAL,
      payload: true,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      logModal: true,
    });
  });

  it("should handle RESET_LOG_VALUE", () => {
    const stateWithLogs = {
      ...initialState,
      logValue: "Some logs",
      runnowLogValue: "Some runnow logs",
      logDetails: { run_id: "123" },
    };
    const action = { type: "RESET_LOG_VALUE" };
    expect(jobScheduleReducer(stateWithLogs, action)).toEqual({
      ...initialState,
      logValue: "",
      runnowLogValue: "",
      logDetails: {},
    });
  });

  it("should handle SET_RUN_HISTORY", () => {
    const action = {
      type: SET_RUN_HISTORY,
      payload: {
        job_id: "job1",
        run_id: "run1",
        timestamp: "2023-01-01",
        local: false,
        engine_type: "spark",
      },
    };
    const result = jobScheduleReducer(initialState, action);
    expect(result).toEqual({
      ...initialState,
      runHistory: {
        job1: [
          {
            run_id: "run1",
            timestamp: "2023-01-01",
            local: false,
            engine_type: "spark",
          },
        ],
      },
    });
  });

  it("should handle SET_RUN_HISTORY multiple runss for same job", () => {
    const firstAction = {
      type: SET_RUN_HISTORY,
      payload: {
        job_id: "job1",
        run_id: "run1",
        timestamp: "2023-01-01",
        local: false,
        engine_type: "spark",
      },
    };
    const secondAction = {
      type: SET_RUN_HISTORY,
      payload: {
        job_id: "job1",
        run_id: "run2",
        timestamp: "2023-01-02",
        local: true,
        engine_type: "python",
      },
    };
    let state = jobScheduleReducer(initialState, firstAction);
    state = jobScheduleReducer(state, secondAction);
    expect(state.runHistory.job1).toHaveLength(2);
    expect(state.runHistory.job1[0].run_id).toBe("run2");
    expect(state.runHistory.job1[1].run_id).toBe("run1");
  });

  it("should handle SET_RUN_HISTORY and limit to 10 entries per job", () => {
    let state = initialState;
    for (let i = 1; i <= 11; i++) {
      const action = {
        type: SET_RUN_HISTORY,
        payload: {
          job_id: "job1",
          run_id: `run${i}`,
          timestamp: `2023-01-${i.toString().padStart(2, "0")}`,
          local: false,
          engine_type: "spark",
        },
      };
      state = jobScheduleReducer(state, action);
    }
    expect(state.runHistory.job1).toHaveLength(10);
    expect(state.runHistory.job1[0].run_id).toBe("run11"); // Most recent
    expect(state.runHistory.job1[9].run_id).toBe("run2"); // Oldest of the 10
  });

  it("should handle RESET_STATE", () => {
    const state = {
      dagList: [{ id: 1, name: "DAG1" }],
      dbList: [{ id: 1, name: "DB1" }],
      logValue: "Some log message",
      runnowLogValue: "Some runnow log message",
      logDetails: { run_id: "run_123", job_id: "job_456" },
      runHistory: { job1: [] },
      logModal: true,
      runNowStatus: "success",
      runNowHistoryStatus: "loading",
      scheduleStatus: "error",
    };
    const action = { type: "RESET_STATE" };
    expect(jobScheduleReducer(state, action)).toEqual(initialState);
  });

  it("should return current state for unknown action", () => {
    const state = { ...initialState, dagList: [{ id: 1 }] };
    expect(jobScheduleReducer(state, { type: "UNKNOWN_ACTION" })).toEqual(
      state
    );
  });
  it("should handle SET_OPEN_JOB_MODAL", () => {
    const action = {
      type: SET_OPEN_JOB_MODAL,
      payload: true,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      jobModal: true,
    });
  });

  it("should handle SET_JOB_LIST_DETAILSS with new type", () => {
    const initialJobDetails = {
      job_details: {
        configuration: [{ key: "existing", value: "config" }],
      },
    };
    const stateWithJobDetails = {
      ...initialState,
      jobListDetails: initialJobDetails,
    };
    const action = {
      type: SET_JOB_LIST_DETAILS,
      payload: {
        type: "new",
        data: { key: "new", value: "config" },
      },
    };
    const result = jobScheduleReducer(stateWithJobDetails, action);
    expect(result.jobListDetails.job_details.configuration).toHaveLength(2);
    expect(result.jobListDetails.job_details.configuration[1]).toEqual({
      key: "new",
      value: "config",
    });
  });

  it("should handle SET_JOB_LIST_DETAILS without new type", () => {
    const action = {
      type: SET_JOB_LIST_DETAILS,
      payload: { job_id: 123, status: "running" },
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      jobListDetails: { job_id: 123, status: "running" },
    });
  });
  it("should handle UPDATE_JOB_LIST_DETAILS", () => {
    const stateWithJobDetails = {
      ...initialState,
      jobListDetails: {
        job_details: {
          configuration: [
            { key: "key1", value: "value1", extra: "extra1" },
            { key: "key2", value: "value2", extra: "extra2" },
          ],
        },
      },
    };
    const action = {
      type: UPDATE_JOB_LIST_DETAILS,
      payload: {
        data: [
          { key: "key1", value: "updated1", extra: "extra1" },
          { key: "key2", value: "updated2", extra: "extra2" },
        ],
      },
    };
    const result = jobScheduleReducer(stateWithJobDetails, action);
    expect(result.jobListDetails.job_details.configuration).toEqual([
      { value: "updated1", extra: "extra1" },
      { value: "updated2", extra: "extra2" },
    ]);
  });

  it("should handle SET_JOB_READ_MODE", () => {
    const action = {
      type: SET_JOB_READ_MODE,
      payload: true,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      isScheduleEditMode: true,
    });
  });

  it("should handle SET_CHILD_DRAWER", () => {
    const action = {
      type: SET_CHILD_DRAWER,
      payload: true,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      childDrawer: true,
    });
  });

  it("should handle SET_INDIVIDUAL_JOB", () => {
    const action = {
      type: SET_INDIVIDUAL_JOB,
      payload: true,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      individualJob: true,
    });
  });

  it("should handle SET_DAG_INFO", () => {
    const dagInfoData = {
      dag_id: "test_dag",
      schedule_interval: "@daily",
      tags: ["test"],
    };
    const action = {
      type: SET_DAG_INFO,
      payload: dagInfoData,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      dagInfo: dagInfoData,
    });
  });

  it("should handle SET_DAG_INFO with empty payload", () => {
    const action = {
      type: SET_DAG_INFO,
      payload: null,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      dagInfo: {},
    });
  });

  it("should reset individualJob and dagInfo when RESET_STATE is called", () => {
    const state = {
      ...initialState,
      individualJob: true,
      dagInfo: { dag_id: "test" },
    };
    const action = { type: "RESET_STATE" };
    expect(jobScheduleReducer(state, action)).toEqual(initialState);
  });

  it("should handle SET_DAGS_TOTAL", () => {
    const action = {
      type: SET_DAGS_TOTAL,
      payload: 42,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      dagTotal: 42,
    });
  });

  it("should handle SET_CURRENT_PAGE", () => {
    const action = {
      type: SET_CURRENT_PAGE,
      payload: 3,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      currentPageInfo: 3,
    });
  });

  it("should handle SET_PAGE_SIZE", () => {
    const action = {
      type: SET_PAGE_SIZE,
      payload: 25,
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      pageSizeInfo: 25,
    });
  });

  it("should reset pagination values when RESET_STATE is called", () => {
    const state = {
      ...initialState,
      dagTotal: 100,
      currentPageInfo: 5,
      pageSizeInfo: 50,
    };
    const action = { type: "RESET_STATE" };
    expect(jobScheduleReducer(state, action)).toEqual({
      ...initialState,
      dagTotal: null,
      currentPageInfo: 1,
      pageSizeInfo: 10,
    });
  });
  it("should handle SET_RUN_NOW_STATUS", () => {
    const action = {
      type: SET_RUN_NOW_STATUS,
      payload: "loading",
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      runNowStatus: "loading",
    });
  });

  it("should handle SET_RUN_NOW_HISTORY_STATUS", () => {
    const action = {
      type: SET_RUN_NOW_HISTORY_STATUS,
      payload: "success",
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      runNowHistoryStatus: "success",
    });
  });

  it("should handle SET_SCHEDULE_STATUS", () => {
    const action = {
      type: SET_SCHEDULE_STATUS,
      payload: "error",
    };
    expect(jobScheduleReducer(initialState, action)).toEqual({
      ...initialState,
      scheduleStatus: "error",
    });
  });

  it("should reset status fields when RESET_STATE is called", () => {
    const state = {
      ...initialState,
      runNowStatus: "loading",
      runNowHistoryStatus: "success",
      scheduleStatus: "error",
    };
    const action = { type: "RESET_STATE" };
    expect(jobScheduleReducer(state, action)).toEqual(initialState);
  });

  it("should reset dmsStatus when RESET_STATE is called", () => {
    const state = {
      ...initialState,
      dmsStatus: "success",
    };
    const action = { type: "RESET_STATE" };
    expect(jobScheduleReducer(state, action)).toEqual(initialState);
  });

});
