import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { featureConstants } from "../../apis/apiUrlConstants";
import { getApplication } from "../../apis/featureService";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";

describe("Feauture Service", () => {
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

  describe("feature service", () => {
    describe("getApplication API", () => {
      it("should call onSuccess with response data when getApplication is successful", async () => {
        const responseData = { success: true };

        mock.onGet(featureConstants.getApplication).reply(200, responseData);

        const onSuccess = jest.fn();
        const onError = jest.fn();

        await getApplication({ onError, onSuccess });
      });

      it("should call onError when getApplication fails", async () => {
        const onSuccess = jest.fn();
        const onError = jest.fn();

        const errorResponse = { message: "Invalid credentials" };
        mock.onGet(featureConstants.getApplication).reply(500, errorResponse);

        await getApplication({ onSuccess, onError });
      });
    });
  });
});
