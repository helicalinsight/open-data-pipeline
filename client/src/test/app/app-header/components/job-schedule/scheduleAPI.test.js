import {
  exportConfig,
  getStreamLogs,
  dagRunStatus,
  triggerDag,
  updateScheduleDetails,
} from "../../../../../apis/jobScheduleService";
import {
  triggerSchedule,
  handleTriggerDag,
  handleUpdateSchedule,
} from "../../../../../app/app-header/components/job-schedule/components/scheduleAPI";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry";
import { getLocalStorageItem } from "../../../../../utils/userData";

jest.mock("../../../../../apis/jobScheduleService", () => ({
  exportConfig: jest.fn(),
  triggerDag: jest.fn(),
  getStreamLogs: jest.fn(),
  dagRunStatus:jest.fn(),
  updateScheduleDetails: jest.fn(),
}));

jest.mock("../../../../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));

jest.mock("../../../../../utils/userData", () => ({
  getLocalStorageItem: jest.fn(),
}));
jest.mock("../../../../../utils/appUtils", () => ({
  fetchDagListUtil: jest.fn(),
}));

jest.mock("../../../../../utils/handleClick", () => ({
  dispatchMessage: jest.fn(),
}));

jest.mock("../../../../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));

describe("triggerSchedule", () => {
  const mockParams = {
    jobData: {
      destination: "db",
      database: "test_db",
      catalog: "catalog",
      files: ["file1"],
    },
    jobDataForm: {
      getFieldsValue: jest.fn().mockReturnValue({
        destination: "db",
        database: "test_db",
        catalog: "catalog",
        files: ["file1"],
      }),
    },
    scheduleConfig: [{ configKey: "key1", configValue: "value1" }],
    selectedChat: { chat_id: "123", chat_name: "test_chat" },
    messageApi: { open: jest.fn() },
    dispatch: jest.fn(),
    loadedFiles: [{ source_id: "file1" }],
    frequency: true,
    setLoading: jest.fn(),
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should call exportConfig and trigger handleTriggerDag on success", async () => {
    exportConfig.mockImplementation(({ onSuccess }) => onSuccess({}));

    await triggerSchedule(mockParams);

    expect(exportConfig).toHaveBeenCalled();
    expect(mockParams.setLoading).toHaveBeenCalledWith(true);
    expect(mockParams.messageApi.open).not.toHaveBeenCalled();
  });

  it("should handle exportConfig error", async () => {
    const errorMessage = { msg: "Export config error" };
    exportConfig.mockImplementation(({ onError }) => onError(errorMessage));

    await triggerSchedule(mockParams);

    expect(mockParams.setLoading).toHaveBeenCalledWith(false);
    expect(mockParams.messageApi.open).toHaveBeenCalledWith({
      type: "error",
      content: errorMessage.msg,
    });
    expect(handleSessionExpiry).toHaveBeenCalledWith(
      mockParams.dispatch,
      errorMessage
    );
  });
});
const mockPollRef = { current: null };
describe("handleTriggerDag", () => {
  const mockParams = {
    frequency: "daily",
    messageApi: { open: jest.fn() },
    selectedChat: { chat_id: "123", chat_name: "test_chat" },
    dispatch: jest.fn(),
    mode: "run",
    customFormData: {},
    onClose: jest.fn(),
    setLoading: jest.fn(),
    job_details: {},
    schedule_name: "test_schedule",
    executionType: "normal",
    mappedData: {},
    notification: {},
    jobData: { notification: {} },
    isImmediateExecution: true,
    pollRef: mockPollRef,
  };

  beforeEach(() => {
    getLocalStorageItem.mockReturnValue({ user: { id: "user_id" } });
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  it("should call triggerDag and show success message on success", async () => {
    triggerDag.mockImplementation(({ onSuccess }) =>
      onSuccess({
        message: "Job scheduled successfully",
        job_id: "1",
        run_id: "2",
        local: true,
        schedule_id: "schedule_1",
        engine_type: "spark",
      })
    );
    dagRunStatus.mockImplementation(({ onSuccess }) =>
      onSuccess({ success: true, state: "success" })
    );
    getStreamLogs.mockImplementation(({ onSuccess }) =>
      onSuccess({ logs: "log data" })
    );
    const mockDispatchMessage = jest.spyOn(
      require("../../../../../utils/handleClick"),
      "dispatchMessage"
    );
    await handleTriggerDag(mockParams);
    expect(triggerDag).toHaveBeenCalled();
    expect(mockParams.setLoading).toHaveBeenCalledWith(false);
    expect(mockParams.onClose).toHaveBeenCalled();
    expect(mockDispatchMessage).toHaveBeenCalledWith(
      mockParams.dispatch,
      "success",
      "Job scheduled successfully"
    );
    jest.advanceTimersByTime(1000);
    expect(dagRunStatus).toHaveBeenCalled();
    expect(getStreamLogs).toHaveBeenCalled();
  });

  it("should handle triggerDag error", async () => {
    const errorMessage = { message: "Trigger DAG error" };
    triggerDag.mockImplementation(({ onError }) => onError(errorMessage));
    await handleTriggerDag(mockParams);
    expect(mockParams.setLoading).toHaveBeenCalledWith(false);
    expect(mockParams.messageApi.open).toHaveBeenCalledWith({
      type: "error",
      content: errorMessage.message,
    });
    expect(handleSessionExpiry).toHaveBeenCalledWith(
      mockParams.dispatch,
      errorMessage
    );
  });

  it("should not fetch logs when isImmediateExecution is false", async () => {
    const paramsWithoutImmediateExecution = {
      ...mockParams,
      isImmediateExecution: false,
      pollRef: { current: null }
    };
    triggerDag.mockImplementation(({ onSuccess }) =>
      onSuccess({
        message: "Job scheduled successfully",
        job_id: "1",
        run_id: "2",
        local: true,
        schedule_id: "schedule_1",
        engine_type: "spark",
      })
    );
    await handleTriggerDag(paramsWithoutImmediateExecution);
    expect(triggerDag).toHaveBeenCalled();
    expect(mockParams.setLoading).toHaveBeenCalledWith(false);
    jest.advanceTimersByTime(1000);
    expect(dagRunStatus).not.toHaveBeenCalled();
    expect(getStreamLogs).not.toHaveBeenCalled();
  });
});

describe("handleUpdateSchedule", () => {
  const mockParams = {
    frequency: "daily",
    dispatch: jest.fn(),
    customFormData: { start_date: "2023-01-01", end_date: "2023-12-31" },
    onClose: jest.fn(),
    setLoading: jest.fn(),
    job_details: {
      files_list: [{ source_id: "file1" }],
      type: "db",
      database: "test_db",
      connection_id: "test_db",
      catalog: "catalog",
    },
    schedule_name: "test_schedule",
    mappedData: { old_connection: "new_connection" },
    notification: true,
    jobData: {
      engineType: "spark",
      isEditExecutiontype: "normal",
      notification: true,
    },
    configurations: { key1: "value1" },
    jobListDetails: {
      schedule_id: "schedule_123",
      meta_schedule_version: 1,
      job_details: {
        configuration: [{ configKey: "key1", configValue: "value1" }],
      },
    },
    isScheduleEditMode: true,
  };
  const mockUser = { id: "user_123", name: "Test User" };
  beforeEach(() => {
    jest.clearAllMocks();
    getLocalStorageItem.mockReturnValue({ user: mockUser });
  });

  it("should successfully update schedule with meta_schedule_version 1", () => {
    updateScheduleDetails.mockImplementation(({ onSuccess }) =>
      onSuccess({ msg: "Schedule updated successfully" })
    );
    handleUpdateSchedule(mockParams);
    expect(updateScheduleDetails).toHaveBeenCalledWith({
      payload: expect.objectContaining({
        schedule_id: mockParams.jobListDetails.schedule_id,
        configurations: mockParams.configurations,
        schedule_interval: mockParams.frequency,
        job_details: mockParams.job_details,
        schedule_name: mockParams.schedule_name,
        engine_type: mockParams.jobData.engineType,
        replace_connections: mockParams.mappedData,
        notification: {
          active: mockParams.jobData.notification,
          type: "email",
          details: { to: null, subject: null, body: null },
        },
        advanced_scheduling: mockParams.customFormData,
        execution_type: mockParams.jobData.isEditExecutiontype,
        upgrade_schedule_version: 2,
      }),
      onSuccess: expect.any(Function),
      onError: expect.any(Function),
    });
    const call = updateScheduleDetails.mock.calls[0][0];
    call.onSuccess({ msg: "Schedule updated successfully" });
    expect(mockParams.setLoading).toHaveBeenCalledWith(false);
    expect(mockParams.onClose).toHaveBeenCalled();
  });

  it("should successfully update schedule with meta_schedule_version 2 (no version upgrade)", () => {
    const paramsWithVersion2 = {
      ...mockParams,
      jobListDetails: {
        ...mockParams.jobListDetails,
        meta_schedule_version: 2,
      },
    };
    updateScheduleDetails.mockImplementation(({ onSuccess }) =>
      onSuccess({ msg: "Schedule updated successfully" })
    );
    handleUpdateSchedule(paramsWithVersion2);
    const call = updateScheduleDetails.mock.calls[0][0];
    expect(call.payload).not.toHaveProperty("execution_type");
    expect(call.payload).not.toHaveProperty("meta_schedule_version");
  });

  it("should handle update schedule error", () => {
    const error = { message: "Failed to update schedule" };
    updateScheduleDetails.mockImplementation(({ onError }) => onError(error));
    handleUpdateSchedule(mockParams);
    const call = updateScheduleDetails.mock.calls[0][0];
    call.onError(error);
    expect(mockParams.setLoading).toHaveBeenCalledWith(false);
    expect(handleSessionExpiry).toHaveBeenCalledWith(
      mockParams.dispatch,
      error
    );
  });

  it("should handle update schedule error with default message", () => {
    const error = {};
    updateScheduleDetails.mockImplementation(({ onError }) => onError(error));
    handleUpdateSchedule(mockParams);
    const call = updateScheduleDetails.mock.calls[0][0];
    call.onError(error);
  });

  it("should use notification from params when frequency is falsy", () => {
    const paramsWithoutFrequency = {
      ...mockParams,
      frequency: null,
      jobData: { ...mockParams.jobData, notification: false },
    };
    handleUpdateSchedule(paramsWithoutFrequency);
    const call = updateScheduleDetails.mock.calls[0][0];
    expect(call.payload.notification.active).toBe(mockParams.notification);
  });

  it("should handle missing user data gracefully", () => {
    getLocalStorageItem.mockReturnValue({});
    updateScheduleDetails.mockImplementation(({ onSuccess }) =>
      onSuccess({ msg: "Schedule updated" })
    );
    handleUpdateSchedule(mockParams);
    const call = updateScheduleDetails.mock.calls[0][0];
    call.onSuccess({ msg: "Schedule updated" });
  });

  it("should handle non-edit mode correctly", () => {
    const paramsNonEditMode = {
      ...mockParams,
      isScheduleEditMode: false,
    };
    handleUpdateSchedule(paramsNonEditMode);
    const call = updateScheduleDetails.mock.calls[0][0];
    expect(call.payload).not.toHaveProperty("execution_type");
    expect(call.payload).not.toHaveProperty("meta_schedule_version");
  });
});
