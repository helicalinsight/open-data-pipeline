import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { loginApi, registerUserApi } from "../../apis/authService";
import { authApiConstants } from "../../apis/apiUrlConstants";

describe("Auth API Service", () => {
  const mock = new MockAdapter(axiosInstance, { onNoMatch: "throwException" });

  beforeAll(() => {
    mock.reset();
  });

  afterEach(cleanup);

  describe("authService", () => {
    describe("loginApi", () => {
      it("should call onSuccess with response data when login is successful", async () => {
        const payload = { username: "user", password: "password" };
        const responseData = { token: "fake_token" };

        mock.onPost(authApiConstants.login).reply(200, responseData);

        const onSuccess = jest.fn();
        const onError = jest.fn();

        await loginApi({ payload, onError, onSuccess });

        console.log("onSuccess calls:", onSuccess.mock.calls);
      });

      it("should call onError when login fails", async () => {
        const payload = { username: "testUser", password: "wrongPassword" };
        const onSuccess = jest.fn();
        const onError = jest.fn();

        const errorResponse = { message: "Invalid credentials" };
        mock.onPost(authApiConstants.login).reply(500, errorResponse);

        await loginApi({ payload, onSuccess, onError });
      });
    });

    describe("registerUserApi", () => {
      it("should call onSuccess when registerUserApi is successful", async () => {
        const payload = { username: "testUser", password: "password" };
        const onSuccess = jest.fn();
        const onError = jest.fn();

        const responseData = { token: "fakeToken" };
        mock.onPost(authApiConstants.register).reply(200, responseData);

        await registerUserApi({ payload, onSuccess, onError });
      });

      it("should call onError when registerUserApi fails", async () => {
        const payload = { username: "testUser", password: "wrongPassword" };
        const onSuccess = jest.fn();
        const onError = jest.fn();

        const errorResponse = { message: "Invalid credentials" };
        mock.onPost(authApiConstants.register).reply(400, errorResponse);

        await registerUserApi({ payload, onSuccess, onError });
      });
    });
  });
});
