import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";
import {
  getAllFilesApi,
  deleteFile,
  renameFile,
  uploadFileApi,
  downloadFileApi,
  updateName,
  switchSelectedFile,
  deleteDataPreviewFile,
} from "../../apis/fileService";
import {
  fileConstants,
  filesServiceConstants,
} from "../../apis/apiUrlConstants";

describe("File Service", () => {
  const mock = new MockAdapter(axiosInstance, { onNoMatch: "throwException" });

  beforeEach(() => {
    setLocalStorage("user", { token: "mock-token" });
  });

  afterEach(() => {
    mock.reset();
  });

  afterAll(() => {
    cleanup();
    jest.restoreAllMocks();
    window.localStorage.clear();
  });

  describe("getAllFilesApi", () => {
    it("should call onSuccess with file data when getAllFilesApi is successful", async () => {
      const payload = {};
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { files: [{ id: "1", name: "file1.txt" }] };
      mock.onGet(filesServiceConstants.getAllFiles).reply(200, responseData);

      await getAllFilesApi({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when getAllFilesApi fails", async () => {
      const payload = {};
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to fetch files" };
      mock.onGet(filesServiceConstants.getAllFiles).reply(500, errorResponse);

      await getAllFilesApi({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("deleteFile", () => {
    it("should call onSuccess when deleteFile is successful", async () => {
      const fileIds = ["1", "2"];
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, message: "Files deleted" };
      mock.onDelete(filesServiceConstants.getAllFiles).reply(200, responseData);

      await deleteFile({ fileIds, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when deleteFile fails", async () => {
      const fileIds = ["1", "2"];
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to delete files" };
      mock
        .onDelete(filesServiceConstants.getAllFiles)
        .reply(500, errorResponse);

      await deleteFile({ fileIds, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("renameFile", () => {
    it("should call onSuccess when renameFile is successful", async () => {
      const payload = { id: "1", newName: "newfile.txt" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, message: "File renamed" };
      mock.onPatch(filesServiceConstants.getAllFiles).reply(200, responseData);

      await renameFile({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when renameFile fails", async () => {
      const payload = { id: "1", newName: "newfile.txt" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to rename file" };
      mock.onPatch(filesServiceConstants.getAllFiles).reply(500, errorResponse);

      await renameFile({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("uploadFileApi", () => {
    it("should call onSuccess when uploadFileApi is successful", async () => {
      const formdata = new FormData();
      formdata.append(
        "file",
        new Blob(["file content"], { type: "text/plain" }),
        "test.txt"
      );
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const progressEvent = jest.fn();

      const responseData = { success: true, message: "File uploaded" };
      mock.onPost(filesServiceConstants.getAllFiles).reply(200, responseData);

      await uploadFileApi({ formdata, onError, onSuccess, progressEvent });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when uploadFileApi fails", async () => {
      const formdata = new FormData();
      formdata.append(
        "file",
        new Blob(["file content"], { type: "text/plain" }),
        "test.txt"
      );
      const onSuccess = jest.fn();
      const onError = jest.fn();
      const progressEvent = jest.fn();

      const errorResponse = { message: "Failed to upload file" };
      mock.onPost(filesServiceConstants.getAllFiles).reply(500, errorResponse);

      await uploadFileApi({ formdata, onSuccess, onError, progressEvent });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("downloadFileApi", () => {
    let onSuccess, onError;
    const featherId = "123";
    const chat_id = "456";
    const responseData = "file content";
    const errorResponse = { message: "Failed to download file" };

    beforeEach(() => {
      onSuccess = jest.fn();
      onError = jest.fn();
      localStorage.setItem("user", JSON.stringify({ token: "mockToken" }));
    });

    afterEach(() => {
      mock.reset();
      localStorage.clear();
    });

    it("should call onSuccess when downloadFileApi is successful", async () => {
      // Mock successful response
      const contentType = "text/csv";
      mock
        .onGet(
          `${filesServiceConstants.download}/${featherId}?chat_id=${chat_id}`
        )
        .reply(200, responseData, { "content-type": contentType });

      await downloadFileApi({ featherId, chat_id, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledTimes(1);
      expect(onSuccess).toHaveBeenCalledWith(responseData, contentType);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when downloadFileApi fails", async () => {
      // Mock failure response
      mock
        .onGet(
          `${filesServiceConstants.download}/${featherId}?chat_id=${chat_id}`
        )
        .reply(500, errorResponse);

      await downloadFileApi({ featherId, chat_id, onSuccess, onError });

      expect(onError).toHaveBeenCalledTimes(1);
      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });

    it("should handle an error with an undefined response gracefully", async () => {
      // Simulating an error without a response body
      mock
        .onGet(
          `${filesServiceConstants.download}/${featherId}?chat_id=${chat_id}`
        )
        .reply(500);

      await downloadFileApi({ featherId, chat_id, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith("");
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("updateName", () => {
    it("should call onSuccess when updateName is successful", async () => {
      const payload = { id: "1", newName: "updatedfile.txt" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, message: "File name updated" };
      mock.onPost(fileConstants.rename).reply(200, responseData);

      await updateName({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when updateName fails", async () => {
      const payload = { id: "1", newName: "updatedfile.txt" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to update file name" };
      mock.onPost(fileConstants.rename).reply(500, errorResponse);

      await updateName({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("switchSelectedFile", () => {
    it("should call onSuccess when switchSelectedFile is successful", async () => {
      const payload = { fileId: "1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, message: "File switched" };
      mock.onPost(fileConstants.cwf).reply(200, responseData);

      await switchSelectedFile({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when switchSelectedFile fails", async () => {
      const payload = { fileId: "1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to switch file" };
      mock.onPost(fileConstants.cwf).reply(500, errorResponse);

      await switchSelectedFile({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
  describe("deleteDataPreviewFile", () => {
    it("should call onSuccess when deleteDataPreviewFile is successful", async () => {
      const payload = { fileId: "1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, message: "File preview deleted" };
      mock.onDelete(filesServiceConstants.deleteFile).reply(200, responseData);

      await deleteDataPreviewFile({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when deleteDataPreviewFile fails", async () => {
      const payload = { fileId: "1" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to delete file preview" };
      mock.onDelete(filesServiceConstants.deleteFile).reply(500, errorResponse);

      await deleteDataPreviewFile({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
});
