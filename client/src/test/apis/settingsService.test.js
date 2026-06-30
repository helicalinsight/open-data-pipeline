import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { preferencesConstants } from "../../apis/apiUrlConstants";
import {
  getPreferences,
  postPreferences,
  createGenerateKey,
  getGenerateKey,
  deleteGenerateKey,
} from "../../apis/settingsService";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";

describe("Settings Service", () => {
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

  describe("getPreferences", () => {
    it("should call onSuccess with response data when request is successful", async () => {
      const responseData = { success: true };
      mock.onGet(preferencesConstants.preferences).reply(200, responseData);

      const onSuccess = jest.fn();
      const onError = jest.fn();

      await getPreferences({ onSuccess, onError });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when request fails", async () => {
      const errorResponse = { message: "Error fetching preferences" };
      mock.onGet(preferencesConstants.preferences).reply(500, errorResponse);

      const onSuccess = jest.fn();
      const onError = jest.fn();

      await getPreferences({ onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("postPreferences", () => {
    it("should call onSuccess with response data when request is successful", async () => {
      const responseData = { success: true };
      const payload = { preference: "value" };
      mock
        .onPost(preferencesConstants.preferences, payload)
        .reply(200, responseData);
      const onSuccess = jest.fn();
      const onError = jest.fn();
      await postPreferences({ onSuccess, onError, payload });
      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when request fails", async () => {
      const errorResponse = { message: "Error updating preferences" };
      const payload = { preference: "value" };
      mock
        .onPost(preferencesConstants.preferences, payload)
        .reply(500, errorResponse);
      const onSuccess = jest.fn();
      const onError = jest.fn();
      await postPreferences({ onSuccess, onError, payload });
      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  it("should call onSuccess with response data when request is successful", async () => {
    const responseData = { success: true, token: "generated-token" };
    const payload = {
      email: "test@example.com",
      token_name: "TestToken",
      expiry_in_days: "2024-12-31",
    };
    mock
      .onPost(preferencesConstants.generateKey, payload)
      .reply(200, responseData);
    const onSuccess = jest.fn();
    const onError = jest.fn();
    await createGenerateKey({ onSuccess, onError, payload });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should call onError when request fails", async () => {
    const errorResponse = { message: "Error generating key" };
    const payload = {
      email: "test@example.com",
      token_name: "TestToken",
      expiry_in_days: "2024-12-31",
    };

    mock
      .onPost(preferencesConstants.generateKey, payload)
      .reply(500, errorResponse);

    const onSuccess = jest.fn();
    const onError = jest.fn();

    await createGenerateKey({ onSuccess, onError, payload });

    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should call onSuccess with response data when request is successful", async () => {
    const responseData = { success: true };
    const payload = { key_id: "12345" };
    mock
      .onDelete(preferencesConstants.generateKey, { params: payload })
      .reply(200, responseData);
    const onSuccess = jest.fn();
    const onError = jest.fn();
    await deleteGenerateKey({ onSuccess, onError, payload });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should call onError when request fails", async () => {
    const errorResponse = { message: "Error deleting key" };
    const payload = { key_id: "12345" };
    mock
      .onDelete(preferencesConstants.generateKey, { params: payload })
      .reply(500, errorResponse);
    const onSuccess = jest.fn();
    const onError = jest.fn();
    await deleteGenerateKey({ onSuccess, onError, payload });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("should call onSuccess with response data when request is successful", async () => {
    const responseData = { success: true, keys: ["key1", "key2"] };
    const payload = { email: "test@example.com" };
    mock
      .onGet(preferencesConstants.generateKey, { params: payload })
      .reply(200, responseData);
    const onSuccess = jest.fn();
    const onError = jest.fn();
    await getGenerateKey({ onSuccess, onError, payload });
    expect(onSuccess).toHaveBeenCalledWith(responseData);
    expect(onError).not.toHaveBeenCalled();
  });

  it("should call onError when request fails", async () => {
    const errorResponse = { message: "Error fetching keys" };
    const payload = { email: "test@example.com" };
    mock
      .onGet(preferencesConstants.generateKey, { params: payload })
      .reply(500, errorResponse);
    const onSuccess = jest.fn();
    const onError = jest.fn();
    await getGenerateKey({ onSuccess, onError, payload });
    expect(onError).toHaveBeenCalledWith(errorResponse);
    expect(onSuccess).not.toHaveBeenCalled();
  });
});
