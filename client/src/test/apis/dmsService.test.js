import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";
import { dmsConstants } from "../../apis/apiUrlConstants";
import {
  triggerDms,
  getDmsList,
  getDmsDatasource,
  deleteDmsSchedule,
  saveProgressDms,
  getProgressDms
} from "../../apis/dmsService";
const mock = new MockAdapter(axiosInstance, { onNoMatch: "throwException" });

describe("DMS Functions", () => {
  beforeEach(() => {
    mock.reset();
    setLocalStorage("user", { token: "mock-token" });
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
    window.localStorage.clear();
  });

  describe("triggerDms", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const payload = { schedule_id: "dms-123", action: "start" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: true, message: "DMS scheduled successfully" };
      mock.onPost(dmsConstants.dmsSchedule).reply(200, responseData);
      await triggerDms({ payload, onSuccess, onError });
    });

    it("should call onError with error data when API call fails", async () => {
      const payload = { schedule_id: "dms-123", action: "start" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to trigger DMS" };
      mock.onPost(dmsConstants.dmsSchedule).reply(500, errorResponse);
      await triggerDms({ payload, onSuccess, onError });
    });

    it("should log error to console when API call fails", async () => {
      const consoleSpy = jest.spyOn(console, "log").mockImplementation(() => {});
      const payload = { schedule_id: "dms-123", action: "start" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to trigger DMS" };
      mock.onPost(dmsConstants.dmsSchedule).reply(500, errorResponse);
      await triggerDms({ payload, onSuccess, onError });
      expect(consoleSpy).toHaveBeenCalledWith("err", expect.anything());
      consoleSpy.mockRestore();
    });

    it("should call onError with error message when API returns 404", async () => {
      const payload = { schedule_id: "non-existent", action: "start" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "DMS schedule not found" };
      mock.onPost(dmsConstants.dmsSchedule).reply(404, errorResponse);
      await triggerDms({ payload, onSuccess, onError });
    });

    it("should handle empty payload", async () => {
      const payload = {};
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { success: false, message: "Invalid payload" };
      mock.onPost(dmsConstants.dmsSchedule).reply(400, responseData);
      await triggerDms({ payload, onSuccess, onError });
    });

    it("should handle network errors", async () => {
      const payload = { schedule_id: "dms-123", action: "start" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
      mock.onPost(dmsConstants.dmsSchedule).networkError();
      await triggerDms({ payload, onSuccess, onError });
      expect(onError).toHaveBeenCalledWith(expect.any(Error));
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getDmsList", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const userId = "user-123";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        dms_schedules: [
          { id: "dms-1", name: "Daily Backup", status: "active" },
          { id: "dms-2", name: "Weekly Sync", status: "paused" }
        ]
      };
      mock.onGet(dmsConstants.dmsList).reply(200, responseData);
      await getDmsList({ userId, onSuccess, onError });
    });

    it("should call onError with error data when API call fails", async () => {
      const userId = "user-123";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Failed to fetch DMS list" };
      mock.onGet(dmsConstants.dmsList).reply(500, errorResponse);
      await getDmsList({ userId, onSuccess, onError });
    });

    it("should handle empty DMS list response", async () => {
      const userId = "user-123";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { dms_schedules: [] };
      mock.onGet(dmsConstants.dmsList).reply(200, responseData);
      await getDmsList({ userId, onSuccess, onError });
    });

    it("should handle response without dms_schedules property", async () => {
      const userId = "user-123";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { message: "No DMS schedules found" };
      mock.onGet(dmsConstants.dmsList).reply(200, responseData);
      await getDmsList({ userId, onSuccess, onError });
    });

    it("should include user_id as query parameter", async () => {
      const userId = "test-user-456";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = { dms_schedules: [] };
      mock.onGet(dmsConstants.dmsList).reply((config) => {
        expect(config.params.user_id).toBe(userId);
        return [200, responseData];
      });
      await getDmsList({ userId, onSuccess, onError });
    });

    it("should handle unauthorized access (401)", async () => {
      const userId = "user-123";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Unauthorized access" };
      mock.onGet(dmsConstants.dmsList).reply(401, errorResponse);
      await getDmsList({ userId, onSuccess, onError });
    });

    it("should handle not found (404)", async () => {
      const userId = "non-existent-user";
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "User not found" };
      mock.onGet(dmsConstants.dmsList).reply(404, errorResponse);
      await getDmsList({ userId, onSuccess, onError });
    });
  });

  describe("getDmsDatasource", () => {
    it("should call onSuccess with response data when API call is successful", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        configuration: {
          datasources: [
            { id: "ds-1", name: "MySQL Source", type: "mysql" },
            { id: "ds-2", name: "PostgreSQL Source", type: "postgresql" }
          ]
        }
      };
      mock.onGet(dmsConstants.dmsDatasource).reply(200, responseData);
      await getDmsDatasource({ onSuccess, onError })
    });

    it("should handle empty datasources array", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        configuration: {
          datasources: []
        }
      };
      mock.onGet(dmsConstants.dmsDatasource).reply(200, responseData);
      await getDmsDatasource({ onSuccess, onError });
    });

    it("should handle null datasources", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        configuration: {
          datasources: null
        }
      };
      mock.onGet(dmsConstants.dmsDatasource).reply(200, responseData);
      await getDmsDatasource({ onSuccess, onError })
    });

    it("should use correct URL from dmsConstants", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        configuration: {
          datasources: []
        }
      };
      mock.onGet(dmsConstants.dmsDatasource).reply(200, responseData);
      await getDmsDatasource({ onSuccess, onError });
    });

    it("should include correct authorization headers", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const responseData = {
        configuration: {
          datasources: []
        }
      };
      const mockToken = "test-dms-token";
      setLocalStorage("user", { token: mockToken });
      mock.onGet(dmsConstants.dmsDatasource).reply((config) => {
        expect(config.headers["Authorization"]).toBe(JSON.stringify({ token: mockToken }));
        return [200, responseData];
      });
      await getDmsDatasource({ onSuccess, onError });
    });

    it("should handle 400 Bad Request error", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const errorResponse = { message: "Invalid request parameters" };
      mock.onGet(dmsConstants.dmsDatasource).reply(400, errorResponse);
      await getDmsDatasource({ onSuccess, onError });
    });

    it("should handle network timeout", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();
      mock.onGet(dmsConstants.dmsDatasource).timeout();
      await getDmsDatasource({ onSuccess, onError });
      expect(onError).toHaveBeenCalled();
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
  describe("deleteDmsSchedule", () => {
  beforeEach(() => {
    mock.reset();
    setLocalStorage("user", { token: "mock-token" });
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
    window.localStorage.clear();
  });

  it("should call onSuccess with response data when API call is successful", async () => {
    const payload = { schedule_ids: ["dms-123", "dms-456"] };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { 
      success: ["dms-123", "dms-456"], 
      errors: [],
      message: "DMS schedules deleted successfully" 
    };
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply(200, responseData);
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should call onError with error data when API call fails", async () => {
    const payload = { schedule_ids: ["dms-123"] };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Failed to delete DMS schedule" };
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply(500, errorResponse);
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should send correct payload with schedule_ids in request", async () => {
    const payload = { schedule_ids: ["dms-123", "dms-456", "dms-789"] };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { 
      success: ["dms-123", "dms-456", "dms-789"], 
      errors: [] 
    };
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply((config) => {
      const requestData = JSON.parse(config.data);
      expect(requestData).toEqual(payload);
      return [200, responseData];
    });
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should handle partial success when some schedules fail to delete", async () => {
    const payload = { schedule_ids: ["dms-123", "dms-456", "dms-789"] };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { 
      success: ["dms-123", "dms-789"], 
      errors: ["dms-456 - Schedule is currently running"],
      message: "Partial success: Some schedules could not be deleted"
    };
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply(207, responseData);
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should handle empty schedule_ids array", async () => {
    const payload = { schedule_ids: [] };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { 
      success: [], 
      errors: ["No schedule IDs provided"],
      message: "Invalid request: No schedule IDs provided"
    };
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply(400, responseData);
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should handle network errors", async () => {
    const payload = { schedule_ids: ["dms-123"] };
    const onSuccess = jest.fn();
    const onError = jest.fn();

    mock.onDelete(dmsConstants.deleteDmsSchedule).networkError();
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should include correct authorization headers", async () => {
    const payload = { schedule_ids: ["dms-123"] };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { success: ["dms-123"], errors: [] };
    const mockToken = "test-dms-token";
    setLocalStorage("user", { token: mockToken });
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply((config) => {
      expect(config.headers["Authorization"]).toBe(JSON.stringify({ token: mockToken }));
      expect(config.headers["Content-Type"]).toBe("application/json");
      return [200, responseData];
    });
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should handle malformed payload", async () => {
    const payload = { invalid_field: "wrong data" };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { 
      message: "Invalid request format: schedule_ids field is required",
      code: "VALIDATION_ERROR" 
    };
    mock.onDelete(dmsConstants.deleteDmsSchedule).reply(422, errorResponse);
    await deleteDmsSchedule({ payload, onSuccess, onError });
  });

  it("should handle concurrent delete requests", async () => {
    const payload1 = { schedule_ids: ["dms-123"] };
    const payload2 = { schedule_ids: ["dms-456"] };
    const onSuccess1 = jest.fn();
    const onError1 = jest.fn();
    const onSuccess2 = jest.fn();
    const onError2 = jest.fn();
    const response1 = { success: ["dms-123"], errors: [] };
    const response2 = { success: ["dms-456"], errors: [] };
    mock
      .onDelete(dmsConstants.deleteDmsSchedule)
      .replyOnce(200, response1)
      .onDelete(dmsConstants.deleteDmsSchedule)
      .replyOnce(200, response2);
    await Promise.all([
      deleteDmsSchedule({ payload: payload1, onSuccess: onSuccess1, onError: onError1 }),
      deleteDmsSchedule({ payload: payload2, onSuccess: onSuccess2, onError: onError2 })
    ]);
  });
});
describe("saveProgressDms", () => {
  it("it should call onSuccess when aoi call is successful", async () => {
    const payload = { step: 1, data: "test" };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = { success: true, message: "Progress saved" };
    mock.onPost(dmsConstants.dmsPostProgress).reply(200, responseData);
    await saveProgressDms({ payload, onSuccess, onError });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("it should call oneror when api call fails", async () => {
    const payload = { step: 1 };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Failed to save progress" };
    mock.onPost(dmsConstants.dmsPostProgress).reply(500, errorResponse);
    await saveProgressDms({ payload, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("it should handle network error", async () => {
    const payload = { step: 1 };
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock.onPost(dmsConstants.dmsPostProgress).networkError();
    await saveProgressDms({ payload, onSuccess, onError });
    expect(onError).toHaveBeenCalled();
  });
});
describe("getProgressDms", () => {
  it("it should call onSuccess with response data", async () => {
    const chatId = "chat-123";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const responseData = {
      success: true,
      data: { step: 2, status: "in-progress" },
    };
    mock.onGet(dmsConstants.dmsGetProgress).reply(200, responseData);
    await getProgressDms({ chatId, onSuccess, onError });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should send correct chat_id as query params", async () => {
    const chatId = "chat-999";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock.onGet(dmsConstants.dmsGetProgress).reply((config) => {
      expect(config.params.chat_id).toBe(chatId);
      return [200, { success: true }];
    });
    await getProgressDms({ chatId, onSuccess, onError });
  });

  it("should call onError when API fails", async () => {
    const chatId = "chat-123";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    const errorResponse = { message: "Failed to fetch progress" };
    mock.onGet(dmsConstants.dmsGetProgress).reply(500, errorResponse);
    await getProgressDms({ chatId, onSuccess, onError });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should handle network error", async () => {
    const chatId = "chat-123";
    const onSuccess = jest.fn();
    const onError = jest.fn();
    mock.onGet(dmsConstants.dmsGetProgress).networkError();
    await getProgressDms({ chatId, onSuccess, onError });
    expect(onError).toHaveBeenCalled();
  });
});
});