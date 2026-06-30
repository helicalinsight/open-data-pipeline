import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import InfoSection from "../../../../app/chat-module/components/InfoSection";
import { updateJobMode } from "../../../../apis/chatService";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../../apis/commonAPIs";
import "@testing-library/jest-dom/extend-expect";
import { message } from "antd";

jest.mock("../../../../apis/chatService", () => ({
  updateJobMode: jest.fn(),
}));

jest.mock("../../../../apis/commonAPIs", () => ({
  triggerGetInfoAPI: jest.fn(),
  triggerPipelineHistory: jest.fn(),
}));

jest.mock("../../../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));

jest.mock("antd", () => {
  const antd = jest.requireActual("antd");
  return {
    ...antd,
    message: {
      useMessage: jest.fn(),
    },
  };
});

const mockStore = configureStore([]);

describe("InfoSection Component", () => {
  let store;
  let mockMessageApi;

  beforeEach(() => {
    store = mockStore({
      chat: {
        selectedChat: { chat_id: "12345" },
        jobMode: "python",
      },
    });
    mockMessageApi = { open: jest.fn() };
    message.useMessage.mockReturnValue([mockMessageApi, null]);
    jest.clearAllMocks();
  });

  const renderComponent = () =>
    render(
      <Provider store={store}>
        <InfoSection />
      </Provider>
    );

  it("renders correctly in Python mode", () => {
    const { getByText, getByRole, queryByText } = renderComponent();
    expect(getByText(/In this mode, you can write code with assistance/i)).toBeInTheDocument();
    expect(getByText(/ACE Editor/i)).toBeInTheDocument();
    expect(getByRole("button", { name: /Back/i })).toBeInTheDocument();
    expect(queryByText(/Change Your Mode/i)).not.toBeInTheDocument();
  });

  it("renders correctly in YAML mode", () => {
    store = mockStore({
      chat: {
        selectedChat: { chat_id: "12345" },
        jobMode: "yaml",
      },
    });
    const { getByText, queryByRole } = renderComponent();
    expect(getByText(/You are currently in/i)).toBeInTheDocument();
    expect(queryByRole("button", { name: /Back/i })).not.toBeInTheDocument();
  });

  it("opens the modal when Back button is clicked in Python mode", async () => {
    const { getByRole, findByText } = renderComponent();
    fireEvent.click(getByRole("button", { name: /Back/i }));
    expect(await findByText("Change Your Mode")).toBeInTheDocument();
  });

  it("dispatches actions and shows success message when mode changes", async () => {
    updateJobMode.mockImplementation(({ onSuccess }) => onSuccess({}));
    const { getByRole, findByText } = renderComponent();
    fireEvent.click(getByRole("button", { name: /Back/i }));
    fireEvent.click(await findByText("Change"));
    await waitFor(() => {
      expect(triggerGetInfoAPI).toHaveBeenCalledWith(store.dispatch, "12345");
      expect(triggerPipelineHistory).toHaveBeenCalledWith(store.dispatch, "12345");
    });
  });

  it("shows error message when updateJobMode fails", async () => {
    updateJobMode.mockImplementation(({ onError }) => onError({ message: "Job Mode failed" }));
    const { getByRole, findByText } = renderComponent();
    fireEvent.click(getByRole("button", { name: /Back/i }));
    fireEvent.click(await findByText("Change"));
  });

  it("opens modal when close link is clicked in YAML mode", async () => {
    store = mockStore({
      chat: {
        selectedChat: { chat_id: "12345" },
        jobMode: "yaml",
      },
    });
    const { getByText, findByText } = renderComponent();
    fireEvent.click(getByText("close"));
    expect(await findByText("Change Your Mode")).toBeInTheDocument();
  });
});
