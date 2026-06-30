import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";
import { jobScheduleServiceConstants } from "../../apis/apiUrlConstants";
import {
  exportConfig,
  triggerDag,
  getDagList,
  getIndividualDag,
  deleteSchedule,
  runDag,
  pauseDag,
  getDagLogs,
  downloadDagInfo,
  getCode,
  updateCode,
  runCode,
  triggerBot,
  resetBot,
  getStreamLogs,
  getListTags,
  triggerDms,
  getDmsList,
  getDmsDatasource,
  deleteDmsSchedule  
} from "../../apis/jobScheduleService";

const mock = new MockAdapter(axiosInstance, { onNoMatch: "throwException" });

global.TextEncoder = class {
  encode(str) {
    return new Uint8Array(Buffer.from(str));
  }
};

global.TextDecoder = class {
  decode(uint8Array, options) {
    return Buffer.from(uint8Array).toString();
  }
};
describe("getStreamLogs", () => {
  let mockOnSuccess;
  let mockOnError;
  const mockData = [
    "data: *** Found local files:\n***   * /airflow/logs/dag_id=run_now_dag/run_id=manual__2024-12-23T13:59:49.746928+05:30/task_id=run_now_job_task/attempt=1.log\n\n",
    "data: *** Found logs served from host http://524cbcf8abd3:8793/log/dag_id=run_now_dag/run_id=manual__2024-12-23T13:59:49.746928+05:30/task_id=run_now_job_task/attempt=1.log\n\n",
    "data: [2024-12-23T13:59:51.822+0530] {local_task_job_runner.py:120} INFO - ::group::Pre task execution logs\n\n",
    "data: [2024-12-23T13:59:51.849+0530] {taskinstance.py:2076} INFO - Dependencies all met for dep_context=non-requeueable deps ti=<TaskInstance: run_now_dag.run_now_job_task manual__2024-12-23T13:59:49.746928+05:30 [queued]>\n\n",
    "data: [2024-12-23T13:59:51.854+0530] {taskinstance.py:2076} INFO - Dependencies all met for dep_context=requeueable deps ti=<TaskInstance: run_now_dag.run_now_job_task manual__2024-12-23T13:59:49.746928+05:30 [queued]>\n\n",
  ];

  beforeEach(() => {
    mockOnSuccess = jest.fn();
    mockOnError = jest.fn();
    setLocalStorage("user", { token: "mock-token" });
  });

  afterEach(() => {
    jest.restoreAllMocks();
    window.localStorage.clear();
  });

  it("correctly processes multiple chunks of log data and calls onSuccess for each line", async () => {
    const mockReader = {
      read: jest
        .fn()
        .mockResolvedValueOnce({
          value: new TextEncoder().encode(mockData[0]),
          done: false,
        })
        .mockResolvedValueOnce({
          value: new TextEncoder().encode(mockData[1]),
          done: false,
        })
        .mockResolvedValueOnce({
          value: new TextEncoder().encode(mockData[2]),
          done: false,
        })
        .mockResolvedValueOnce({
          value: new TextEncoder().encode(mockData[3]),
          done: false,
        })
        .mockResolvedValueOnce({
          value: new TextEncoder().encode(mockData[4]),
          done: true,
        }),
    };

    const mockResponse = {
      body: { getReader: jest.fn().mockReturnValue(mockReader) },
    };

    global.fetch = jest.fn().mockResolvedValue(mockResponse);

    await getStreamLogs({
      payload: { dagId: "test-dag" },
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    });

    expect(mockOnSuccess).toHaveBeenCalledTimes(5);
    expect(mockOnSuccess).toHaveBeenCalledWith(
      "*** Found local files:\n***   * /airflow/logs/dag_id=run_now_dag/run_id=manual__2024-12-23T13:59:49.746928+05:30/task_id=run_now_job_task/attempt=1.log\n"
    );
    expect(mockOnSuccess).toHaveBeenCalledWith(
      "*** Found logs served from host http://524cbcf8abd3:8793/log/dag_id=run_now_dag/run_id=manual__2024-12-23T13:59:49.746928+05:30/task_id=run_now_job_task/attempt=1.log\n"
    );
    expect(mockOnSuccess).toHaveBeenCalledWith(
      "[2024-12-23T13:59:51.822+0530] {local_task_job_runner.py:120} INFO - ::group::Pre task execution logs\n"
    );
    expect(mockOnSuccess).toHaveBeenCalledWith(
      "[2024-12-23T13:59:51.849+0530] {taskinstance.py:2076} INFO - Dependencies all met for dep_context=non-requeueable deps ti=<TaskInstance: run_now_dag.run_now_job_task manual__2024-12-23T13:59:49.746928+05:30 [queued]>\n"
    );
    expect(mockOnSuccess).toHaveBeenCalledWith(
      "[2024-12-23T13:59:51.854+0530] {taskinstance.py:2076} INFO - Dependencies all met for dep_context=requeueable deps ti=<TaskInstance: run_now_dag.run_now_job_task manual__2024-12-23T13:59:49.746928+05:30 [queued]>\n"
    );
    expect(mockOnError).not.toHaveBeenCalled();
  });

  it("calls onError when the fetch request fails", async () => {
    const error = new Error("Network error");
    global.fetch = jest.fn().mockRejectedValue(error);

    await getStreamLogs({
      payload: { dagId: "test-dag" },
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    });
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it("calls onError when the response body is not a stream", async () => {
    const mockResponse = {
      body: null,
    };

    global.fetch = jest.fn().mockResolvedValue(mockResponse);

    await getStreamLogs({
      payload: { dagId: "test-dag" },
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    });
  });
});

describe("Job Schedule Service", () => {
  const mock = new MockAdapter(axiosInstance, { onNoMatch: "throwException" });

  beforeEach(() => {
    mock.reset();
    setLocalStorage("user", { token: "mock-token" });
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
    window.localStorage.clear();
  });

  describe("exportConfig", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { data: "test" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true };

      mock
        .onPost(jobScheduleServiceConstants.exportConfig)
        .reply(200, responseData);

      await exportConfig({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { data: "test" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(jobScheduleServiceConstants.exportConfig)
        .reply(500, errorResponse);

      await exportConfig({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("triggerDag", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true };

      mock.onPost(jobScheduleServiceConstants.dag).reply(200, responseData);

      await triggerDag({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock.onPost(jobScheduleServiceConstants.dag).reply(500, errorResponse);

      await triggerDag({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getDagList", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = {};
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { dags: ["dag1", "dag2"] };

      mock
        .onPost(jobScheduleServiceConstants.listDags)
        .reply(200, responseData);

      await getDagList({ payload, onSuccess, onError });
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = {};
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(jobScheduleServiceConstants.listDags)
        .reply(500, errorResponse);

      await getDagList({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
describe("getIndividualDag with query parameters", () => {
  beforeEach(() => {
    const mockUser = { token: "mock-token" };
    localStorage.getItem = jest.fn().mockReturnValue(JSON.stringify(mockUser));
  });
  it("should includedd date when dateRange has exactly 2 elements", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const dateRange = ["2023-01-01", "2023-01-31"];
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.start_date).toBe("2023-01-01");
        expect(config.params.end_date).toBe("2023-01-31");
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      dateRange,
      onSuccess,
      onError,
    });
  });

  it("should not included date range when dateRange is empty", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const dateRange = [];
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.start_date).toBeUndefined();
        expect(config.params.end_date).toBeUndefined();
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      dateRange,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should not includedd date range  when daterange has only 1 element", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const dateRange = ["2023-01-01"];
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.start_date).toBeUndefined();
        expect(config.params.end_date).toBeUndefined();
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      dateRange,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should not included date range  when daterange has more than 2 elements", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const dateRange = ["2023-01-01", "2023-01-31", "2023-02-01"];
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.start_date).toBeUndefined();
        expect(config.params.end_date).toBeUndefined();
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      dateRange,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });
  // Sortinggg
  it("should included sort  when both sortfield & sortorder are provided", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const sortField = "execution_date";
    const sortOrder = "desc";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.sort_field).toBe("execution_date");
        expect(config.params.sort_order).toBe("desc");
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      sortField,
      sortOrder,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should not included sort when sortfield is empty", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const sortField = "";
    const sortOrder = "desc";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.sort_field).toBeUndefined();
        expect(config.params.sort_order).toBeUndefined();
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      sortField,
      sortOrder,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should not included sort when sortorder is empty", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const sortField = "execution_date";
    const sortOrder = "";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.sort_field).toBeUndefined();
        expect(config.params.sort_order).toBeUndefined();
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      sortField,
      sortOrder,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should not included sort  when both sortfield & sortorder are empty", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const sortField = "";
    const sortOrder = "";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.sort_field).toBeUndefined();
        expect(config.params.sort_order).toBeUndefined();
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      sortField,
      sortOrder,
      onSuccess,
      onError,
    });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });
  // Combinationn
  it("should combined all parameters all optional filters are provided", async () => {
    const dagId = "test-dag";
    const current = 2;
    const pageSize = 20;
    const stateFilters = ["success", "running"];
    const dateRange = ["2023-01-01", "2023-01-31"];
    const sortField = "execution_date";
    const sortOrder = "asc";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { dag: { id: "test-dag", name: "Test DAG" } };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply((config) => {
        expect(config.params.page).toBe(2);
        expect(config.params.per_page).toBe(20);
        expect(config.params.state).toBe("success,running");
        expect(config.params.start_date).toBe("2023-01-01");
        expect(config.params.end_date).toBe("2023-01-31");
        expect(config.params.sort_field).toBe("execution_date");
        expect(config.params.sort_order).toBe("asc");
        return [200, responseData];
      });
    await getIndividualDag({
      dagId,
      current,
      pageSize,
      stateFilters,
      dateRange,
      sortField,
      sortOrder,
      onSuccess,
      onError,
    });
  });
});
 
describe("getIndividualDag errorr handling", () => {
  beforeEach(() => {
    const mockUser = { token: "mock-token" };
    localStorage.getItem = jest.fn().mockReturnValue(JSON.stringify(mockUser));
  });
  it("should call onError with response data when API fails with the response", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Error occurred", code: "INTERNAL_ERROR" };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply(500, errorResponse);
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should call onError with undefined when API  fails without response", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply(500); 
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(undefined);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should call onError with undefined when network error occurss", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .networkError();
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(undefined);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should call onError with undefined when request timeout", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .timeout();
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(undefined);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle 400 Bad Request error with response data", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Invalid parameters", code: "VALIDATION_ERROR" };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply(400, errorResponse);
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle  Not Found error with response", async () => {
    const dagId = "non-existent-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "DAG not found", code: "NOT_FOUND" };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply(404, errorResponse);
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle 401 Unauthorized error with response", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Unauthorized access", code: "AUTH_ERROR" };
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply(401, errorResponse);
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle error with empty response object", async () => {
    const dagId = "test-dag";
    const current = 1;
    const pageSize = 10;
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.individualDag}${dagId}`)
      .reply(500, {});
    await getIndividualDag({ dagId, current, pageSize, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith({});
    expect(onSuccess).not.toHaveBeenCalled();
  });
});
  describe("deleteSchedule", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { scheduleId: "test-schedule" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true };

      mock
        .onDelete(jobScheduleServiceConstants.delete)
        .reply(200, responseData);

      await deleteSchedule({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { scheduleId: "test-schedule" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onDelete(jobScheduleServiceConstants.delete)
        .reply(500, errorResponse);

      await deleteSchedule({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("runDag", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true };

      mock.onPost(jobScheduleServiceConstants.runDag).reply(200, responseData);

      await runDag({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock.onPost(jobScheduleServiceConstants.runDag).reply(500, errorResponse);

      await runDag({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("pauseDag", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const dagId = "test-dag";
      const payload = { is_paused: true };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true };

      mock
        .onPatch(`${jobScheduleServiceConstants.dag}/${dagId}`)
        .reply(200, responseData);

      await pauseDag({ dagId, payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const dagId = "test-dag";
      const payload = { is_paused: true };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPatch(`${jobScheduleServiceConstants.dag}/${dagId}`)
        .reply(500, errorResponse);

      await pauseDag({ dagId, payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getDagLogs", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { logs: ["log1", "log2"] };

      mock.onPost(jobScheduleServiceConstants.dagLogs).reply(200, responseData);

      await getDagLogs({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(jobScheduleServiceConstants.dagLogs)
        .reply(500, errorResponse);

      await getDagLogs({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("downloadDagInfo", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { info: "DAG info" };
      const contentType = "application/json";

      mock
        .onPost(jobScheduleServiceConstants.downloadDagInfo)
        .reply(200, responseData, { "content-type": contentType });

      await downloadDagInfo({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData, contentType);
      expect(onError).not.toHaveBeenCalled();
    });
    it("should call onError with error data when API call fails", async () => {
      const payload = { dagId: "test-dag" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(jobScheduleServiceConstants.downloadDagInfo)
        .reply(500, errorResponse);

      await downloadDagInfo({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getCode", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const chatId = "test-chat";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { code: "print('Hello, World!')" };

      mock
        .onGet(`${jobScheduleServiceConstants.codeConfig}/${chatId}`)
        .reply(200, responseData);

      await getCode({ chatId, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const chatId = "test-chat";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onGet(`${jobScheduleServiceConstants.codeConfig}/${chatId}`)
        .reply(500, errorResponse);

      await getCode({ chatId, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("updateCode", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const chatId = "test-chat";
      const payload = { code: "print('Updated code')" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true };

      mock
        .onPost(`${jobScheduleServiceConstants.codeConfig}/${chatId}`)
        .reply(200, responseData);

      await updateCode({ chatId, payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const chatId = "test-chat";
      const payload = { code: "print('Updated code')" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(`${jobScheduleServiceConstants.codeConfig}/${chatId}`)
        .reply(500, errorResponse);

      await updateCode({ chatId, payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("runCode", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { code: "print('Hello, World!')" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { output: "Hello, World!" };

      mock.onPost(jobScheduleServiceConstants.runCode).reply(200, responseData);

      await runCode({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { code: "print('Hello, World!')" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(jobScheduleServiceConstants.runCode)
        .reply(500, errorResponse);

      await runCode({ payload, onSuccess, onError });
    });
  });

  describe("triggerBot", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { botId: "test-bot", message: "Hello, bot!" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { reply: "Hello, human!" };

      mock.onPost(jobScheduleServiceConstants.pyspark).reply(200, responseData);

      await triggerBot({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { botId: "test-bot", message: "Hello, bot!" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred" };

      mock
        .onPost(jobScheduleServiceConstants.pyspark)
        .reply(500, errorResponse);

      await triggerBot({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });

    it("should send the correct payload in the request", async () => {
      const payload = { botId: "test-bot", message: "Hello, bot!" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      mock.onPost(jobScheduleServiceConstants.pyspark).reply((config) => {
        expect(JSON.parse(config.data)).toEqual(payload);
        return [200, { reply: "Hello, human!" }];
      });

      await triggerBot({ payload, onSuccess, onError });
    });
  });

  describe("resetBot", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { botId: "test-bot" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true, message: "Bot reset successfully" };

      mock
        .onPost(jobScheduleServiceConstants.pysparkReset)
        .reply(200, responseData);

      await resetBot({ payload, onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { botId: "test-bot" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Error occurred during reset" };

      mock
        .onPost(jobScheduleServiceConstants.pysparkReset)
        .reply(500, errorResponse);

      await resetBot({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });

    it("should send the correct payload in the request", async () => {
      const payload = { botId: "test-bot" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      mock.onPost(jobScheduleServiceConstants.pysparkReset).reply((config) => {
        expect(JSON.parse(config.data)).toEqual(payload);
        return [200, { success: true, message: "Bot reset successfully" }];
      });

      await resetBot({ payload, onSuccess, onError });
    });
  });
});
describe("getListTags", () => {
  const mockUserId = "user123";
  const mockResponse = {
    success: true,
    dag_search_filters: {
      schedule_names: ['la*', 's1ch3*', 'sch2*', 'te*', 'fgd', 'tr*', 'ex*', 'sch1*', 'st*', 'sc22*', 'sfwefw'],
      job_names: ['employee', 'tes']
    },
    msg: "Dag search filters retrieved successfully."
  };
  beforeEach(() => {
    mock.reset();
    const mockUser = { token: "mock-token" };
    localStorage.getItem = jest.fn().mockReturnValue(JSON.stringify(mockUser));
  });
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("should call onSuccess with response data when API call is successful", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, mockResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should make correct API call with user ID in URL", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, mockResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should include correct headers in the request", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply((config) => {
        expect(config.headers["Content-Type"]).toBe("application/json");
        expect(config.headers["Authorization"]).toBe("mock-token");
        return [200, mockResponse];
      });
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should call onError with error data when API call fails", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Error occurred" };
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(500, errorResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle network errors", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .networkError();
    await getListTags({ userId: mockUserId, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(undefined);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle timeout errors", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .timeout();
    await getListTags({ userId: mockUserId, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(undefined);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle 400 Bad Request error", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Invalid user ID", code: "VALIDATION_ERROR" };
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(400, errorResponse);

    await getListTags({ userId: mockUserId, onSuccess, onError });
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle 401 Unauthorizedd error", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Unauthorized access", code: "AUTH_ERROR" };
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(401, errorResponse);

    await getListTags({ userId: mockUserId, onSuccess, onError });
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle 404 Not Found errror", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "User not found", code: "NOT_FOUND" };
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(404, errorResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle empty response data", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const emptyResponse = {};
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, emptyResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should handle response with empty dag_search_filters", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseWithEmptyFilters = {
      success: true,
      dag_search_filters: {
        schedule_names: [],
        job_names: []
      },
      msg: "No filters available"
    };
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, responseWithEmptyFilters);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should handle response with missing dag_search_filters", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseWithoutFilters = {
      success: true,
      msg: "Success but no filters"
    };
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, responseWithoutFilters);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should handle missing user token", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    localStorage.getItem = jest.fn().mockReturnValue(null);
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, mockResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should handle  user token", async () => {
    const onSuccess = jest.fn();
    const onError = jest.fn();
    localStorage.getItem = jest.fn().mockReturnValue("invalid-json");
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, mockResponse);
    await getListTags({ userId: mockUserId, onSuccess, onError });
  });

  it("should handle conccurrent API calls", async () => {
    const onSuccess1 = jest.fn();
    const onError1 = jest.fn();
    const onSuccess2 = jest.fn();
    const onError2 = jest.fn();
    mock
      .onGet(`${jobScheduleServiceConstants.listTags}/${mockUserId}`)
      .reply(200, mockResponse);
    await Promise.all([
      getListTags({ userId: mockUserId, onSuccess: onSuccess1, onError: onError1 }),
      getListTags({ userId: mockUserId, onSuccess: onSuccess2, onError: onError2 })
    ]);
  });
});
