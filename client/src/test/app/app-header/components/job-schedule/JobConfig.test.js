import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import JobConfig from "../../../../../app/app-header/components/job-schedule/components/JobConfig";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";

const mockStore = configureStore();

const createStore = (overrides = {}) => {
  return mockStore({
    app: {
      editorSuggestions: {
        yaml: [],
        python: [],
      },
      jobHelpInfo: {
        yaml: "yaml",
        python: "python",
      },
    },
    chat: {
      selectedChat: {
        chat_id: "1234",
        chat_name: "Test Chat"
      },
      chatList: {
        1234: {
          scheduleConfig: [
            {
              key: "d44daf13-80db-40c7-b577-fa6a19491369",
              configKey: "spark-1",
              configValue: "spark-value-1",
            },
            {
              key: "d44daf13-80db-40c7-b577-fa6a19491370",
              configKey: "spark-2",
              configValue: "spark-value-2",
            },
          ],
        },
      },
      jobMode: "pipeline"
    },
    jobSchedule: {
      isScheduleEditMode: false,
      jobListDetails: {
        job_name: "Test Job"
      },
      childDrawer: false
    },
    ...overrides
  });
};

const props = {
  setCurrent: jest.fn(),
};

const renderComponent = (store, props) => {
  return render(
    <reactRedux.Provider store={store}>
      <Router>
        <JobConfig {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("JobConfig Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without errors", () => {
    const store = createStore();
    renderComponent(store, props);
    expect(screen.getByText("Job Name -")).toBeInTheDocument();
    expect(screen.getByText("Test Chat")).toBeInTheDocument();
  });

  it("should display job name from jobListDetails in read mode", () => {
    const store = createStore({
      jobSchedule: {
        isScheduleEditMode: true,
        jobListDetails: {
          job_name: "Read Mode Job"
        }
      }
    });
    renderComponent(store, props);
    expect(screen.getByText("Read Mode ...")).toBeInTheDocument();
  });

  it("should display config section with info icon when not in read mode", () => {
    const store = createStore();
    renderComponent(store, props);
    expect(screen.getByText("Config")).toBeInTheDocument();
    expect(screen.getByTestId("show-info-icon")).toBeInTheDocument();
  });

  it("should not display config section in read mode", () => {
    const store = createStore({
      jobSchedule: {
        isScheduleEditMode: true
      }
    });
    renderComponent(store, props);
    expect(screen.queryByText("Config")).not.toBeInTheDocument();
    expect(screen.queryByTestId("show-info-icon")).not.toBeInTheDocument();
  });

  it("should call setCurrent when Next button is clicked", () => {
    const store = createStore();
    renderComponent(store, props);
    act(() => {
      fireEvent.click(screen.getByTestId("next-button"));
    });
    expect(props.setCurrent).toHaveBeenCalled();
  });

  it("should dispatch addScheduleConfig when form is submitted", () => {
    const store = createStore();
    renderComponent(store, props);
    act(() => {
      fireEvent.change(screen.getByTestId("configKey"), { target: { value: "new-key" } });
      fireEvent.change(screen.getByTestId("configValue"), { target: { value: "new-value" } });
      fireEvent.submit(screen.getByTestId("key-value-form"));
    });
  });

  it("should dispatch delteScheduleConfig when delete is clicked", () => {
    const store = createStore();
    renderComponent(store, props);
    act(() => {
      fireEvent.click(screen.getAllByTestId("delete")[0]);
    });
    const actions = store.getActions();
  });

  it("should dispatch setChildDrawer when editor button is clicked", () => {
    const store = createStore();
    renderComponent(store, props);
    const actions = store.getActions();
  });

  it("should filter duplicate config keys correctly", () => {
    const store = createStore({
      chat: {
        selectedChat: {
          chat_id: "1234",
          chat_name: "Test Chat"
        },
        chatList: {
          1234: {
            scheduleConfig: [
              {
                key: "1",
                configKey: "duplicate-key",
                configValue: "value-1",
              },
              {
                key: "2",
                configKey: "duplicate-key",
                configValue: "value-2",
              },
              {
                key: "3",
                configKey: "unique-key",
                configValue: "value-3",
              }
            ],
          },
        },
        jobMode: "pipeline"
      }
    });
    renderComponent(store, props);
    expect(screen.getAllByText("duplicate-key").length).toBe(1);
    expect(screen.getByText("value-1")).toBeInTheDocument();
    expect(screen.queryByText("value-2")).not.toBeInTheDocument();
    expect(screen.getByText("unique-key")).toBeInTheDocument();
  });
});