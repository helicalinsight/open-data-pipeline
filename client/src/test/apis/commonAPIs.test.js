import { v4 as uuidv4 } from "uuid";
import { getInformationApi } from "../../apis/chatService";
import {
  addLoadedFilesAction,
  addScheduleConfig,
  setColumnListAction,
  setPreviewRefreshData,
  setSelectedFilesAction,
  setJobMode
} from "../../store/actions/chatAction";
import { setPreviewState } from "../../store/actions/appActions";
import { handleSessionExpiry } from "../../utils/handleSessionExpiry";
import { triggerGetInfoAPI } from "../../apis/commonAPIs";

jest.mock("../../apis/chatService", () => ({
  getInformationApi: jest.fn(),
}));

jest.mock("../../store/actions/appActions", () => ({
  setPreviewState: jest.fn(),
}));

jest.mock("../../store/actions/chatAction", () => ({
  addLoadedFilesAction: jest.fn(),
  setSelectedFilesAction: jest.fn(),
  setColumnListAction: jest.fn(),
  addScheduleConfig: jest.fn(),
  setPreviewRefreshData: jest.fn(),
  setJobMode: jest.fn(),
}));

jest.mock("../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

describe("triggerGetInfoAPI", () => {
  let dispatch;

  beforeEach(() => {
    dispatch = jest.fn();
  });

  it("should dispatch actions correctly when API call is successful", () => {
    const mockData = {
      success: true,
      chats: {
        job_mode: "llm",
        loaded_files: ["file1", "file2"],
        cwf: "file3",
        metadata: ["meta1", "meta2"],
        configurations: {
          config1: "value1",
          config2: "value2",
        },
      },
    };

    getInformationApi.mockImplementation(({ onSuccess }) =>
      onSuccess(mockData)
    );

    const chatId = "123";
    const rest = { refresh: true, showPreview: true };

    triggerGetInfoAPI(dispatch, chatId, rest);

    expect(getInformationApi).toHaveBeenCalledWith(expect.any(Object));
    expect(dispatch).toHaveBeenCalledWith(
      setJobMode(mockData.chats.job_mode)
    );

    expect(dispatch).toHaveBeenCalledWith(
      addLoadedFilesAction({
        chat_id: chatId,
        files: mockData.chats.loaded_files,
      })
    );

    expect(dispatch).toHaveBeenCalledWith(
      setSelectedFilesAction({
        chat_id: chatId,
        files: [mockData.chats.cwf],
      })
    );

    expect(dispatch).toHaveBeenCalledWith(
      setColumnListAction({
        chat_id: chatId,
        files: mockData.chats.metadata,
      })
    );

    const updatedConfigs = Object.entries(mockData.chats.configurations).map(
      ([configKey, configValue]) => ({
        configValue: String(configValue),
        configKey,
        key: expect.any(String), // uuidv4() will return a string, but we don't need to check the exact value here
      })
    );

    expect(dispatch).toHaveBeenCalledWith(
      addScheduleConfig({
        chat_id: chatId,
        data: updatedConfigs,
        event: "update",
      })
    );

    expect(dispatch).toHaveBeenCalledWith(
      setPreviewRefreshData({
        id: chatId,
        refresh: true,
      })
    );

    expect(dispatch).toHaveBeenCalledWith(setPreviewState(true));
  });

  it("should handle API errors by calling handleSessionExpiry", () => {
    const mockError = new Error("API call failed");
    getInformationApi.mockImplementation(({ onError }) => onError(mockError));

    const chatId = "123";
    const rest = {};

    triggerGetInfoAPI(dispatch, chatId, rest);

    expect(getInformationApi).toHaveBeenCalledWith(expect.any(Object));
    expect(handleSessionExpiry).toHaveBeenCalledWith(dispatch, mockError);
  });

  it("should handle cases with no `chats` data correctly", () => {
    const mockData = {
      success: true,
      chats: {},
    };

    getInformationApi.mockImplementation(({ onSuccess }) =>
      onSuccess(mockData)
    );

    const chatId = "123";
    const rest = {};

    triggerGetInfoAPI(dispatch, chatId, rest);

    expect(dispatch).not.toHaveBeenCalledWith(expect.any(Object));
  });
});
