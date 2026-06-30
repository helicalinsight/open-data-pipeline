import axiosInstance from "../../apis/axios";
import MockAdapter from "axios-mock-adapter";
import { cleanup } from "@testing-library/react";
import {
  chatServiceConstants,
  completionAPIURL,
  previewFileConstants,
} from "../../apis/apiUrlConstants";
import {
  createChat,
  deleteChat,
  getAllJobsApi,
  updateChat,
  sendMessage,
  dataPreview,
  chatHistoryApi,
  getInformationApi,
  pipelineHistoryApi,
  clearChatMessageHistory,
  undoPipelineHistory,
  redoPipelineHistory,
  completionApi,
  updateJobMode
} from "../../apis/chatService";
import { setLocalStorage } from "../__mocks__/mockLocalStorage";

describe("Chat Service", () => {
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

  describe("createChat", () => {
    it("should call onSuccess when createChat is successful", async () => {
      const payload = { name: "Test Chat" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, id: "123" };
      mock.onPost(chatServiceConstants.chat).reply(200, responseData);

      await createChat({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when createChat fails", async () => {
      const payload = { name: "Test Chat" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to create chat" };
      mock.onPost(chatServiceConstants.chat).reply(500, errorResponse);

      await createChat({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getAllJobsApi", () => {
    it("should call onSuccess when getAllJobsApi is successful", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, jobs: [] };
      mock.onGet(chatServiceConstants.chat).reply(200, responseData);

      await getAllJobsApi({ onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when getAllJobsApi fails", async () => {
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to get jobs" };
      mock.onGet(chatServiceConstants.chat).reply(500, errorResponse);

      await getAllJobsApi({ onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("updateChat", () => {
    it("should call onSuccess when updateChat is successful", async () => {
      const payload = { name: "Updated Chat", chat_id: "123" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true };
      mock
        .onPatch(`${chatServiceConstants.chat}/${payload.chat_id}`)
        .reply(200, responseData);

      await updateChat({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when updateChat fails", async () => {
      const payload = { name: "Updated Chat", chat_id: "123" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to update chat" };
      mock
        .onPatch(`${chatServiceConstants.chat}/${payload.chat_id}`)
        .reply(500, errorResponse);

      await updateChat({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("deleteChat", () => {
    it("should call onSuccess when deleteChat is successful", async () => {
      const chatId = "123";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true };
      mock
        .onDelete(`${chatServiceConstants.chat}/${chatId}`)
        .reply(200, responseData);

      await deleteChat({ chatId, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when deleteChat fails", async () => {
      const chatId = "123";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to delete chat" };
      mock
        .onDelete(`${chatServiceConstants.chat}/${chatId}`)
        .reply(500, errorResponse);

      await deleteChat({ chatId, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("sendMessage", () => {
    it("should call onSuccess when sendMessage is successful", async () => {
      const payload = { message: "Hello, world!" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true, messageId: "456" };
      mock.onPost(chatServiceConstants.sendMessage).reply(200, responseData);

      await sendMessage({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when sendMessage fails", async () => {
      const payload = { message: "Hello, world!" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to send message" };
      mock.onPost(chatServiceConstants.sendMessage).reply(500, errorResponse);

      await sendMessage({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("dataPreview", () => {
    it("should call onSuccess with preview data when dataPreview is successful", async () => {
      const payload = { fileId: "789" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { preview: "File preview content" };
      mock.onPost(previewFileConstants.previewFile).reply(200, responseData);

      await dataPreview({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData.preview);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when dataPreview fails", async () => {
      const payload = { fileId: "789" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to preview file" };
      mock.onPost(previewFileConstants.previewFile).reply(500, errorResponse);

      await dataPreview({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("chatHistoryApi", () => {
    it("should call onSuccess with chat history when chatHistoryApi is successful", async () => {
      const chatId = "123";
      const params = { page: 1, limit: 20 };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { messages: [{ id: "1", content: "Hello" }] };
      mock
        .onGet(`${chatServiceConstants.chatHistory}/${chatId}`)
        .reply(200, responseData);

      await chatHistoryApi({ chatId, params, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when chatHistoryApi fails", async () => {
      const chatId = "123";
      const params = { page: 1, limit: 20 };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to fetch chat history" };
      mock
        .onGet(`${chatServiceConstants.chatHistory}/${chatId}`)
        .reply(500, errorResponse);

      await chatHistoryApi({ chatId, params, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("getInformationApi", () => {
    it("should call onSuccess with information data when getInformationApi is successful", async () => {
      const query = "type=user&id=123";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { user: { id: "123", name: "John Doe" } };
      mock
        .onGet(`${chatServiceConstants.getInformation}?${query}`)
        .reply(200, responseData);

      await getInformationApi({ query, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when getInformationApi fails", async () => {
      const query = "type=user&id=123";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to fetch information" };
      mock
        .onGet(`${chatServiceConstants.getInformation}?${query}`)
        .reply(500, errorResponse);

      await getInformationApi({ query, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("pipelineHistoryApi", () => {
    it("should call onSuccess with pipeline history data when pipelineHistoryApi is successful", async () => {
      const query = "jobId=456";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { history: [{ id: "1", status: "completed" }] };
      mock
        .onGet(`${chatServiceConstants.pipelineHistory}?${query}`)
        .reply(200, responseData);

      await pipelineHistoryApi({ query, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when pipelineHistoryApi fails", async () => {
      const query = "jobId=456";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to fetch pipeline history" };
      mock
        .onGet(`${chatServiceConstants.pipelineHistory}?${query}`)
        .reply(500, errorResponse);

      await pipelineHistoryApi({ query, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("clearChatMessageHistory", () => {
    it("should call onSuccess when clearChatMessageHistory is successful", async () => {
      const chatId = "789";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { success: true };
      mock
        .onDelete(`${chatServiceConstants.chatHistory}/${chatId}`)
        .reply(200, responseData);

      await clearChatMessageHistory({ chatId, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when clearChatMessageHistory fails", async () => {
      const chatId = "789";
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to clear chat history" };
      mock
        .onDelete(`${chatServiceConstants.chatHistory}/${chatId}`)
        .reply(500, errorResponse);

      await clearChatMessageHistory({ chatId, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("undoPipelineHistory", () => {
    it("should call onSuccess when undoPipelineHistory is successful", async () => {
      const payload = { historyId: "123" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = {
        success: true,
        message: "Pipeline history undone",
      };
      mock
        .onPost(chatServiceConstants.undoPipelineHistory)
        .reply(200, responseData);

      await undoPipelineHistory({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when undoPipelineHistory fails", async () => {
      const payload = { historyId: "123" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to undo pipeline history" };
      mock
        .onPost(chatServiceConstants.undoPipelineHistory)
        .reply(500, errorResponse);

      await undoPipelineHistory({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("redoPipelineHistory", () => {
    it("should call onSuccess when redoPipelineHistory is successful", async () => {
      const payload = { historyId: "456" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = {
        success: true,
        message: "Pipeline history redone",
      };
      mock
        .onPost(chatServiceConstants.redoPipelineHistory)
        .reply(200, responseData);

      await redoPipelineHistory({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when redoPipelineHistory fails", async () => {
      const payload = { historyId: "456" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to redo pipeline history" };
      mock
        .onPost(chatServiceConstants.redoPipelineHistory)
        .reply(500, errorResponse);

      await redoPipelineHistory({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe("completionApi", () => {
    it("should call onSuccess when completionApi is successful", async () => {
      const payload = { prompt: "Complete this sentence" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const responseData = { completion: "This is a completed sentence." };
      mock.onPost(completionAPIURL).reply(200, responseData);

      await completionApi({ payload, onError, onSuccess });

      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });

    it("should call onError when completionApi fails", async () => {
      const payload = { prompt: "Complete this sentence" };
      const onSuccess = jest.fn();
      const onError = jest.fn();

      const errorResponse = { message: "Failed to get completion" };
      mock.onPost(completionAPIURL).reply(500, errorResponse);

      await completionApi({ payload, onSuccess, onError });

      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
  describe("updateJobMode", () => {
    it("should call onSuccess when updateJobMode is successful", async () => {
      const payload = { name: "batch", chatId: "123" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
  
      const responseData = { success: true };
      mock
        .onPatch(`${chatServiceConstants.jobMode}/${payload.chatId}`)
        .reply(200, responseData);
  
      await updateJobMode({ payload, onError, onSuccess });
  
      expect(onSuccess).toHaveBeenCalledWith(responseData);
      expect(onError).not.toHaveBeenCalled();
    });
  
    it("should call onError when updateJobMode fails", async () => {
      const payload = { name: "batch", chatId: "123" };
      const onSuccess = jest.fn();
      const onError = jest.fn();
  
      const errorResponse = { message: "Failed to update job mode" };
      mock
        .onPatch(`${chatServiceConstants.jobMode}/${payload.chatId}`)
        .reply(500, errorResponse);
  
      await updateJobMode({ payload, onSuccess, onError });
  
      expect(onError).toHaveBeenCalledWith(errorResponse);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
  
});
