import React from "react";
import { fireEvent, render, screen, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";
import ChatModule from "../../../app/chat-module";
import "@testing-library/jest-dom";
import "../../__mocks__/matchMedia";
import { chatHistoryApi, getAllJobsApi } from "../../../apis/chatService";

import { getLocalStorageItem } from "../../../utils/userData";

jest.mock("../../../apis/chatService", () => ({
  getInformationApi: jest.fn(),
  getAllJobsApi: jest.fn(),
  chatHistoryApi: jest.fn(),
  pipelineHistoryApi: jest.fn(),
}));

jest.mock("../../../apis/databaseService", () => ({
  getDataSources: jest.fn(),
}));

jest.mock("../../../apis/featureService", () => ({
  getApplication: jest.fn(),
}));

jest.mock("../../../utils/userData", () => ({
  getLocalStorageItem: jest.fn(),
}));

const mockStore = configureStore();

window.HTMLElement.prototype.scrollIntoView = function () {};

const getStore = ({ isSessionExpired, activeViewState }) => {
  return mockStore({
    app: {
      showPreview: true,
      activeViewState,
      isSessionExpired,
    },
    jobSchedule: {
      dagList: [],
    },
    database: {
      selectedDatasource: {
        driver: "test_driver",
      },
    },
    chat: {
      chatList: {
        "65d303abc6619e0b2bf7f114": {
          chat_id: "65d303abc6619e0b2bf7f114",
          chat_name: "Job 14",
          columnList: ["index", "customer_id", "first_name", "last_name"],
          selectedFiles: [
            {
              source_id: "662ba55788e28e8af8679eb1",
              alias: "customers-100",
              type: "csv",
            },
          ],
          loadedFiles: [
            {
              source_id: "662ba40f88e28e8af8679eb0",
              alias: "free-test-data",
              type: "csv",
            },
          ],
          fetchChatHistory: false,
        },
      },
      selectedChat: {
        chat_id: "65d303abc6619e0b2bf7f114",
        chat_name: "Job 14",
      },
    },
    messages: {
      params: { offset: 0, limit: 30 },
      allMessages: {
        "65d303abc6619e0b2bf7f114": [
          {
            isUser: false,
            text: "Final Output: Renamed column(s) city with current_city.",
            timestamp: 1714136590.032909,
            message_id: "6298256c-b588-4b33-82dc-e4b18141a910",
            time: "6:33 PM",
            id: "6298256c-b588-4b33-82dc-e4b18141a910",
          },
        ],
      },
    },
  });
};

let dynamicProps = {
  isSessionExpired: true,
  showPreview: false,
  activeViewState: "job-scheduling-view",
};

const appStore = getStore(dynamicProps);

// reusable function for render
const renderComponent = (appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <MemoryRouter initialEntries={["?chat=123"]}>
        <ChatModule />
      </MemoryRouter>
    </reactRedux.Provider>
  );
};

const renderComponentWithoutChatId = (appStore) => {
  return render(
    <reactRedux.Provider store={appStore} initialEntries={["?chat=undefined"]}>
      <MemoryRouter>
        <ChatModule />
      </MemoryRouter>
    </reactRedux.Provider>
  );
};

describe("ChatModule component", () => {
  it("should render the component without erros", () => {
    renderComponent(appStore);
  });

  it("should render the component without erros", () => {
    getLocalStorageItem.mockReturnValue({ token: "mockToken" });

    getAllJobsApi.mockImplementationOnce(({ onSuccess }) => {
      onSuccess({ chats: [{ name: "chat" }] });
    });

    chatHistoryApi.mockImplementationOnce(({ onSuccess }) => {
      onSuccess({
        status: false,
        message: "message",
      });
    });

    renderComponentWithoutChatId(appStore);
  });

  it("chatHistoryApi : SUCCESS", () => {
    chatHistoryApi.mockImplementationOnce(({ onSuccess }) => {
      onSuccess({
        status: true,
        chat_history: [],
        has_more: true,
      });
    });

    renderComponentWithoutChatId(appStore);
  });

  it("chatHistoryApi : Error", () => {
    chatHistoryApi.mockImplementationOnce(({ onError }) => {
      onError("erro");
    });
    renderComponentWithoutChatId(appStore);
  });

  it("show showPreview when true", () => {
    const updatedStore = getStore({
      isSessionExpired: false,
      activeViewState: "job-listing-view",
    });
    renderComponent(updatedStore);
  });

  it("show datasources when true", () => {
    dynamicProps = { ...dynamicProps, activeViewState: "datasources-view" };
    const updatedStore = getStore(dynamicProps);
    renderComponent(updatedStore);
  });

  it("show job lisiting when true", () => {
    dynamicProps = { ...dynamicProps, activeViewState: "job-listing-view" };
    const updatedStore = getStore(dynamicProps);
    renderComponentWithoutChatId(updatedStore);
  });

  it("show job setting when true", () => {
    dynamicProps = { ...dynamicProps, activeViewState: "settings-view" };
    const updatedStore = getStore(dynamicProps);
    renderComponent(updatedStore);
  });
});
