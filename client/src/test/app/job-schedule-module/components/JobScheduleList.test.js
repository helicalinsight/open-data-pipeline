import React from "react";
import {
  fireEvent,
  render,
  screen,
  act,
  waitFor,
  within,
} from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter as Router } from "react-router-dom";
import {
  deleteSchedule,
  getIndividualDag,
  pauseDag,
  runDag,
  getListTags,
} from "../../../../apis/jobScheduleService.js";
import configureStore from "redux-mock-store";
import JobScheduleList from "../../../../app/job-schedule-module/components/JobScheduleList";
import * as reactRedux from "react-redux";
import "../../../__mocks__/matchMedia.js";
import dayjs from "dayjs";

jest.mock("../../../../utils/userData", () => ({
  getLocalStorageItem: jest.fn(),
}));
jest.mock("../../../../utils/handleSessionExpiry", () => ({
  handleSessionExpiry: jest.fn(),
}));
jest.mock("../../../../utils/handleClick", () => ({
  dispatchMessage: jest.fn(),
}));
const mockStore = configureStore();
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
  useSelector: jest.fn(),
}));
jest.mock("../../../../apis/jobScheduleService.js", () => ({
  deleteSchedule: jest.fn(),
  getIndividualDag: jest.fn(),
  runDag: jest.fn(),
  pauseDag: jest.fn(),
  getListTags: jest.fn(),
}));
jest.mock("../../../../store/actions/jobScheduleActions", () => ({
  setDagInfo: jest.fn(),
  setDagsListAction: jest.fn(),
  setIndividualJob: jest.fn(),
  setJobListDetails: jest.fn(),
  setJobModal: jest.fn(),
  setJobReadMode: jest.fn(),
}));

import { getLocalStorageItem } from "../../../../utils/userData";
import { handleSessionExpiry } from "../../../../utils/handleSessionExpiry";
import { dispatchMessage } from "../../../../utils/handleClick";
import {
  setDagInfo,
  setDagsListAction,
  setIndividualJob,
  setJobListDetails,
  setJobModal,
  setJobReadMode,
} from "../../../../store/actions/jobScheduleActions";

const mockUser = {
  id: "66c2e364bba59ea44e4451a6",
  name: "Test User",
  email: "test@example.com",
};

const mockDagList = [
  {
    dag_id: "dag_1",
    job_name: "Test Job 1",
    schedule_name: "Schedule 1",
    timetable_description: "At 00:00 every day",
    next_dagrun: "2024-08-25T00:00:00+00:00",
    next_dagrun_data_interval_start: "2024-08-24T00:00:00+00:00",
    next_dagrun_data_interval_end: "2024-08-25T00:00:00+00:00",
    next_dagrun_create_after: "2024-08-25T00:00:00+00:00",
    is_paused: false,
    starts_on: dayjs().add(2, "minute").toISOString(), 
    configuration: { param1: "value1" },
    files_list: ["file1.txt"],
  },
  {
    dag_id: "dag_2",
    job_name: "Test Job 2",
    schedule_name: "Schedule 2",
    timetable_description: "At 12:00 every day",
    next_dagrun: "2024-08-26T12:00:00+00:00",
    next_dagrun_data_interval_start: "2024-08-25T12:00:00+00:00",
    next_dagrun_data_interval_end: "2024-08-26T12:00:00+00:00",
    next_dagrun_create_after: "2024-08-26T12:00:00+00:00",
    is_paused: true,
    starts_on: dayjs().subtract(1, "minute").toISOString(), 
    configuration: { param2: "value2" },
    files_list: ["file2.txt", "file3.csv"],
  },
  {
    dag_id: "dag_3",
    job_name: "Test Job 3",
    schedule_name: "Schedule 3",
    timetable_description: "Weekly on Monday",
    next_dagrun: null,
    next_dagrun_data_interval_start: null,
    next_dagrun_data_interval_end: null,
    next_dagrun_create_after: null,
    is_paused: false,
    starts_on: null, 
    configuration: null,
    files_list: [],
  },
];

const mockDagSearchFilters = {
  success: true,
  dag_search_filters: {
    schedule_names: ["Schedule 1", "Schedule 2", "Schedule 3", "Schedule 4"],
    job_names: ["Test Job 1", "Test Job 2", "Test Job 3", "Test Job 4"],
  },
};

const mockDagInfoResponse = {
  basic_info: {
    dag_id: "dag_1",
    job_name: "Test Job 1",
    owners: ["user1"],
    description: "Test description",
  },
  dag_runs: {
    dag_runs: [
      {
        dag_run_id: "run_1",
        execution_date: "2024-08-25T00:00:00+00:00",
        state: "success",
        start_date: "2024-08-25T00:00:00+00:00",
        end_date: "2024-08-25T01:00:00+00:00",
      },
    ],
    total_entries: 1,
  },
};

const mockPaginationData = {
  current: 1,
  pageSize: 10,
  total: 3,
  showSizeChanger: true,
  showQuickJumper: true,
};

const mockProps = {
  loading: false,
  paginationData: mockPaginationData,
  fetchDagList: jest.fn(),
  onFilterChange: jest.fn(),
};

const createStore = (overrides = {}) =>
  mockStore({
    app: {},
    jobSchedule: {
      dagList: mockDagList,
      currentPageInfo: 1,
      pageSizeInfo: 10,
      ...overrides.jobSchedule,
    },
    settings: {
      messageData: null,
      hideMessage: false,
      ...overrides.settings,
    },
  });

const renderComponent = (props = {}, storeOverrides = {}) => {
  const store = createStore(storeOverrides);
  const mergedProps = { ...mockProps, ...props };

  return render(
    <reactRedux.Provider store={store}>
      <Router>
        <JobScheduleList {...mergedProps} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("JobScheduleList Component", () => {
  let mockDispatch;
  let useSelectorMock;

  beforeEach(() => {
    mockDispatch = jest.fn();
    useSelectorMock = jest.spyOn(reactRedux, "useSelector")
    jest.spyOn(reactRedux, "useDispatch").mockReturnValue(mockDispatch);
    useSelectorMock.mockImplementation((selector) => {
      const state = {
        jobSchedule: {
          dagList: mockDagList,
          currentPageInfo: 1,
          pageSizeInfo: 10,
        },
        settings: {
          messageData: null,
          hideMessage: false,
        },
      };
      return selector(state);
    });
    getLocalStorageItem.mockReturnValue({ user: mockUser });
    getListTags.mockImplementation(({ onSuccess }) =>
      onSuccess(mockDagSearchFilters)
    );
    getIndividualDag.mockImplementation(({ onSuccess }) =>
      onSuccess(mockDagInfoResponse)
    );
    deleteSchedule.mockImplementation(({ onSuccess }) =>
      onSuccess({ success: [], errors: [] })
    );
    runDag.mockImplementation(({ onSuccess }) =>
      onSuccess({ success: true, message: "DAG triggered" })
    );
    pauseDag.mockImplementation(({ onSuccess }) =>
      onSuccess({ success: true, message: "DAG paused" })
    );
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  describe("Initialization and Mount", () => {
    it("should render without crashing", () => {
      renderComponent();
      expect(
        screen.getByText("Latest schedules will be available shortly")
      ).toBeInTheDocument();
    });

    it("should fetch search filters on mount", async () => {
      renderComponent();
      await waitFor(() => {
        expect(getListTags).toHaveBeenCalledWith({
          userId: mockUser.id,
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        });
      });
    });

    it("should handle missing user data gracefully", () => {
      getLocalStorageItem.mockReturnValueOnce({ user: null });
      expect(() => renderComponent()).not.toThrow();
    });

    it("should initialize with correct default states", () => {
      renderComponent();
      expect(screen.getByTestId("refresh")).toBeInTheDocument();
      expect(screen.getByRole("table")).toBeInTheDocument();
    });
  });

  describe("UI Elements Rendering", () => {
    it("should display the info alert message", () => {
      renderComponent();
      expect(
        screen.getByText("Latest schedules will be available shortly")
      ).toBeInTheDocument();
    });

    it("should display refresh button", () => {
      renderComponent();
      expect(screen.getByTestId("refresh")).toBeInTheDocument();
    });

    it("should show loading skeleton when loading prop is true", () => {
      renderComponent({ loading: true });
      expect(screen.getByTestId("loading-spinner-id")).toBeInTheDocument();
    });

    it("should not show loading skeleton when loading prop is false", () => {
      renderComponent({ loading: false });
      expect(
        screen.queryByTestId("loading-spinner-id")
      ).not.toBeInTheDocument();
    });

    it("should display all table columns", () => {
      renderComponent();
      expect(screen.getByText("Schedule Name")).toBeInTheDocument();
      expect(screen.getByText("Job Name")).toBeInTheDocument();
      expect(screen.getByText("Schedule")).toBeInTheDocument();
      expect(screen.getByText("Next Run")).toBeInTheDocument();
      expect(screen.getByText("Actions")).toBeInTheDocument();
    });

    it("should display all DAG data in the table", () => {
      renderComponent();
      expect(screen.getByText("Schedule 1")).toBeInTheDocument();
      expect(screen.getByText("Schedule 2")).toBeInTheDocument();
      expect(screen.getByText("Schedule 3")).toBeInTheDocument();
      expect(screen.getByText("Test Job 1")).toBeInTheDocument();
      expect(screen.getByText("Test Job 2")).toBeInTheDocument();
      expect(screen.getByText("Test Job 3")).toBeInTheDocument();
    });

    it("should display filter icons for schedule and job names", async () => {
      renderComponent();
      await waitFor(() => {
        expect(
          screen.getByTestId("schedule_name-filter-icon")
        ).toBeInTheDocument();
        expect(screen.getByTestId("job_name-filter-icon")).toBeInTheDocument();
      });
    });
  });

  describe("Data Display and Formatting", () => {
    it("should format next run dates correctly", () => {
      renderComponent();
      const nextRunCells = screen.getAllByText(/2024-08-25|2024-08-26/);
      expect(nextRunCells.length).toBeGreaterThan(0);
    });

    it("should handle null next run dates", () => {
      renderComponent()
      expect(screen.getByText("Test Job 3")).toBeInTheDocument(); 
    });

    it("should display info tooltips for next run dates", () => {
      renderComponent();
      const infoIcons = screen.getAllByRole("img", { name: /info-circle/i });
      expect(infoIcons.length).toBeGreaterThan(0);
    });
  });

  describe("Row Selection Functionality", () => {
    it("should handle row selection", () => {
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      expect(checkboxes[1]).toBeChecked();
    });

    it("should show multi-delete button when rows are selected", () => {
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      expect(screen.getByTestId("multi-file-delete-btn")).toBeInTheDocument();
      expect(screen.getByText("Delete 1 schedule")).toBeInTheDocument();
    });

    it("should update multi delete button text with countt", () => {
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      fireEvent.click(checkboxes[2]);
      expect(screen.getByText("Delete 2 schedules")).toBeInTheDocument();
    });

    it("should hide multi delete button when no rows are selected", () => {
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      fireEvent.click(checkboxes[1]);
      expect(
        screen.queryByTestId("multi-file-delete-btn")
      ).not.toBeInTheDocument();
    });
  });

  describe("Action Buttons Functionality", () => {
    describe("Trigger Button", () => {
      it("should enable trigger button when start time has passed", () => {
        renderComponent();
        const triggerButton = screen.getByTestId("trigger-btn-id_dag_2");
        expect(triggerButton).not.toBeDisabled();
      });

      it("should disable trigger button when start time is in future", () => {
        renderComponent();
        const triggerButton = screen.getByTestId("trigger-btn-id_dag_1");
        expect(triggerButton).toBeDisabled();
      });

      it("should call runDag API when trigger button is clicked", async () => {
        renderComponent();
        const triggerButton = screen.getByTestId("trigger-btn-id_dag_2");
        await act(async () => {
          fireEvent.click(triggerButton);
        });
        expect(runDag).toHaveBeenCalledWith({
          payload: { dag_id: "dag_2" },
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        });
      });

      it("should handle runDag API success", async () => {
        runDag.mockImplementation(({ onSuccess }) =>
          onSuccess({ success: true, message: "DAG triggered successfully" })
        );
        renderComponent();
        const triggerButton = screen.getByTestId("trigger-btn-id_dag_2");
        await act(async () => {
          fireEvent.click(triggerButton);
        });
        expect(dispatchMessage).toHaveBeenCalled();
      });

      it("should handle runDag API failure", async () => {
        runDag.mockImplementation(({ onError }) =>
          onError({ message: "Trigger failed" })
        );
        renderComponent();
        const triggerButton = screen.getByTestId("trigger-btn-id_dag_2");
        await act(async () => {
          fireEvent.click(triggerButton);
        });
        expect(dispatchMessage).toHaveBeenCalled();
      });
    });

    describe("Pause/Resume Switch", () => {
      it("should display correct switch state based on is_paused", () => {
        renderComponent();
        const switches = screen.getAllByRole("switch");
        expect(switches[0]).toBeChecked();
        expect(switches[1]).not.toBeChecked();
      });

      it("should call pauseDag API when switch is toggledd", async () => {
        renderComponent();
        const switches = screen.getAllByRole("switch");
        await act(async () => {
          fireEvent.click(switches[0]);
        });
        expect(pauseDag).toHaveBeenCalledWith({
          dagId: "dag_1",
          payload: { is_paused: true },
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        });
      });

      it("should show loading state during pause API call", async () => {
        let resolveApi;
        const pausePromise = new Promise((resolve) => {
          resolveApi = resolve;
        });
        pauseDag.mockImplementation(({ onSuccess }) => {
          return pausePromise;
        });
        renderComponent();
        const switches = screen.getAllByRole("switch");
        fireEvent.click(switches[0]);
        expect(pauseDag).toHaveBeenCalled();
        await act(async () => {
          resolveApi();
        });
      });

      it("should handle pauseDag API error", async () => {
        pauseDag.mockImplementation(({ onError }) =>
          onError({ message: "Pause failed" })
        );
        renderComponent();
        const switches = screen.getAllByRole("switch");
        await act(async () => {
          fireEvent.click(switches[0]);
        });
        expect(handleSessionExpiry).toHaveBeenCalled();
      });
    });

    describe("Delete Button", () => {
      it("should open delete confirmation modal", () => {
        renderComponent();
        const deleteButtons = screen.getAllByTestId(/delete-btn-id_/);
        fireEvent.click(deleteButtons[0]);
        expect(screen.getByText("Delete schedule")).toBeInTheDocument();
        expect(screen.getByText("Schedule 1")).toBeInTheDocument();
      });

      it("should call deleteSchedule API when confirmed", async () => {
        deleteSchedule.mockImplementation(({ onSuccess }) =>
          onSuccess({ success: ["dag_1"], errors: [] })
        );
        renderComponent();
        const deleteButton = screen.getByTestId("delete-btn-id_dag_1");
        fireEvent.click(deleteButton);
        const confirmButton = screen.getByTestId("modal-ok-button");
        await act(async () => {
          fireEvent.click(confirmButton);
        });
        expect(deleteSchedule).toHaveBeenCalledWith({
          payload: { schedule_ids: ["dag_1"] },
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        });
      });

      it("should handle deleteSchedule API success with mixed results", async () => {
        deleteSchedule.mockImplementation(({ onSuccess }) =>
          onSuccess({
            success: ["dag_1"],
            errors: ["dag_2"],
          })
        );
        renderComponent();
        const deleteButton = screen.getByTestId("delete-btn-id_dag_1");
        fireEvent.click(deleteButton);
        const confirmButton = screen.getByTestId("modal-ok-button");
        await act(async () => {
          fireEvent.click(confirmButton);
        });
        expect(dispatchMessage).toHaveBeenCalled();
      });

      it("should handle deleteSchedule API error", async () => {
        deleteSchedule.mockImplementation(({ onError }) =>
          onError({ message: "Delete failed" })
        );
        renderComponent();
        const deleteButton = screen.getByTestId("delete-btn-id_dag_1");
        fireEvent.click(deleteButton);
        const confirmButton = screen.getByTestId("modal-ok-button");
        await act(async () => {
          fireEvent.click(confirmButton);
        });
        expect(handleSessionExpiry).toHaveBeenCalled();
      });

      it("should close delete modal when cancel is clicked", () => {
        renderComponent();
        const deleteButton = screen.getByTestId("delete-btn-id_dag_1");
        fireEvent.click(deleteButton);
        expect(screen.getByText("Delete schedule")).toBeInTheDocument();
        const cancelButton = screen.getByTestId("modal-cancel-button");
        fireEvent.click(cancelButton);
        expect(screen.queryByText("Delete schedule")).not.toBeInTheDocument();
      });
    });

    describe("More Actions Button", () => {
      it("should open job modal when more actions button is clicked", () => {
        renderComponent();
        const moreButtons = screen.getAllByRole("button", {
          name: /ellipsis/i,
        });
        fireEvent.click(moreButtons[0]);
        expect(setJobModal).toHaveBeenCalledWith(true);
        expect(setJobReadMode).toHaveBeenCalledWith(true);
        expect(setJobListDetails).toHaveBeenCalled();
      });
    });
  });

  describe("Row Click Functionality", () => {
    it("should fetch individual DAG details when row is clicked", async () => {
      renderComponent();
      const rows = screen.getAllByRole("row");
      await act(async () => {
        fireEvent.click(rows[1]);
      });
      expect(getIndividualDag).toHaveBeenCalledWith({
        dagId: "dag_1",
        current: 1,
        pageSize: 10,
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
    });

    it("should set individual job state on successful DAG fetch", async () => {
      renderComponent();
      const rows = screen.getAllByRole("row");
      await act(async () => {
        fireEvent.click(rows[1]);
      });
      expect(setIndividualJob).toHaveBeenCalledWith(true);
      expect(setDagInfo).toHaveBeenCalledWith(mockDagInfoResponse);
      expect(setJobListDetails).toHaveBeenCalled();
      expect(setJobReadMode).toHaveBeenCalledWith(true);
    });

    it("should handle individual DAG fetch error", async () => {
      getIndividualDag.mockImplementation(({ onError }) =>
        onError({ message: "Fetch failed" })
      );
      renderComponent();
      const rows = screen.getAllByRole("row");
      await act(async () => {
        fireEvent.click(rows[1]);
      });
      expect(handleSessionExpiry).toHaveBeenCalled();
    });
  });

  describe("Filtering Functionality", () => {
    it("should open filter dropdown when filter icon is clicked", async () => {
      renderComponent();
      const filterIcon = screen.getByTestId("schedule_name-filter-icon");
      fireEvent.click(filterIcon);
      await waitFor(() => {
        expect(
          screen.getByPlaceholderText("Select schedule name")
        ).toBeInTheDocument();
      });
    });

    it("should apply filters when search is confirmed", async () => {
      renderComponent();
      const filterIcon = screen.getByTestId("schedule_name-filter-icon");
      fireEvent.click(filterIcon);
      const selectInput = await screen.findByPlaceholderText(
        "Select schedule name"
      );
      expect(selectInput).toBeInTheDocument();
    });

    it("should reset filters when reset is clicked", async () => {
      renderComponent();
      const filterIcon = screen.getByTestId("schedule_name-filter-icon");
      fireEvent.click(filterIcon);
      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /reset/i })
        ).toBeInTheDocument();
      });
    });
  });

  describe("Refresh Functionality", () => {
    it("should call fetchDagList and reset filters on refresh", async () => {
      renderComponent();
      const refreshButton = screen.getByTestId("refresh");
      await act(async () => {
        fireEvent.click(refreshButton);
      });
      expect(mockProps.fetchDagList).toHaveBeenCalledWith(true, {});
      expect(mockProps.onFilterChange).toHaveBeenCalledWith({});
    });

    it("should reset selection on refresh time", async () => {
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      const refreshButton = screen.getByTestId("refresh");
      await act(async () => {
        fireEvent.click(refreshButton);
      });
      expect(
        screen.queryByTestId("multi-file-delete-btn")
      ).not.toBeInTheDocument();
    });
  });

  describe("Timer and Real Time Updates", () => {
    it("should set up timers for trigger state updates", () => {
      renderComponent();
      act(() => {
        jest.advanceTimersByTime(30000);
      });
      expect(screen.getByTestId("refresh")).toBeInTheDocument();
    });

    it("should cleanup timers on unmounted", () => {
      const { unmount } = renderComponent();
      expect(() => unmount()).not.toThrow();
    });
  });

  describe("Error Handling and Edge Cases", () => {
    it("should handle empty DAG list", () => {
      useSelectorMock.mockImplementation((selector) => {
        const state = {
          jobSchedule: {
            dagList: [],
            currentPageInfo: 1,
            pageSizeInfo: 10,
          },
          settings: {
            messageData: null,
            hideMessage: false,
          },
        };
        return selector(state);
      });
      renderComponent();
      expect(screen.getByRole("table")).toBeInTheDocument();
    });

    it("should handle API errors", async () => {
      getListTags.mockImplementation(({ onError }) =>
        onError({ message: "Failed to fetch filters" })
      );
      expect(() => renderComponent()).not.toThrow();
    });

    it("should handle DAG data", () => {
      useSelectorMock.mockImplementation((selector) => {
        const state = {
          jobSchedule: {
            dagList: [{ dag_id: "dag1" }, { invalid: "data" }, null],
            currentPageInfo: 1,
            pageSizeInfo: 10,
          },
          settings: {
            messageData: null,
            hideMessage: false,
          },
        };
        return selector(state);
      });
      expect(() => renderComponent()).not.toThrow();
    });

    it("should display custom messages when it available", () => {
      useSelectorMock.mockImplementation((selector) => {
        const state = {
          jobSchedule: {
            dagList: mockDagList,
            currentPageInfo: 1,
            pageSizeInfo: 10,
          },
          settings: {
            messageData: {
              type: "success",
              message: "Test success message",
            },
            hideMessage: false,
          },
        };
        return selector(state);
      });
      renderComponent();
      expect(screen.getByText("Test success message")).toBeInTheDocument();
    });

    it("should not display message when hideMessagee is true", () => {
      useSelectorMock.mockImplementation((selector) => {
        const state = {
          jobSchedule: {
            dagList: mockDagList,
            currentPageInfo: 1,
            pageSizeInfo: 10,
          },
          settings: {
            messageData: {
              type: "success",
              message: "Test success message",
            },
            hideMessage: true,
          },
        };
        return selector(state);
      });
      renderComponent();
      expect(
        screen.queryByText("Test success message")
      ).not.toBeInTheDocument();
    });
  });

  describe("Multi Delete Functionality", () => {
    it("should open multi delete modal with correct scheduled names", () => {
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      fireEvent.click(checkboxes[2]);
      const multiDeleteButton = screen.getByTestId("multi-file-delete-btn");
      fireEvent.click(multiDeleteButton);

      expect(screen.getByText("Delete schedules")).toBeInTheDocument();
      expect(screen.getByText("Schedule 1")).toBeInTheDocument();
      expect(screen.getByText("Schedule 2")).toBeInTheDocument();
    });

    it("should call delete with multiple Ids", async () => {
      deleteSchedule.mockImplementation(({ onSuccess }) =>
        onSuccess({ success: ["dag_1", "dag_2"], errors: [] })
      );
      renderComponent();
      const checkboxes = screen.getAllByRole("checkbox");
      fireEvent.click(checkboxes[1]);
      fireEvent.click(checkboxes[2]);
      const multiDeleteButton = screen.getByTestId("multi-file-delete-btn");
      fireEvent.click(multiDeleteButton);
      const confirmButton = screen.getByTestId("modal-ok-button");
      await act(async () => {
        fireEvent.click(confirmButton);
      });
      expect(deleteSchedule).toHaveBeenCalledWith({
        payload: { schedule_ids: ["dag_1", "dag_2"] },
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
    });
  });
});

describe("Integrationnn Tests", () => {
  let mockDispatch;
  beforeEach(() => {
    mockDispatch = jest.fn();
    jest.spyOn(reactRedux, "useDispatch").mockReturnValue(mockDispatch);
    getLocalStorageItem.mockReturnValue({ user: mockUser });
    getListTags.mockImplementation(({ onSuccess }) =>
      onSuccess(mockDagSearchFilters)
    );
    jest.useFakeTimers();
  });
  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it("should complete full workflow select, trigger, and delete", async () => {
    renderComponent();
    expect(screen.getByText("Schedule 1")).toBeInTheDocument();
    const checkboxes = screen.getAllByRole("checkbox");
    fireEvent.click(checkboxes[1]);
    expect(screen.getByTestId("multi-file-delete-btn")).toBeInTheDocument();
    const triggerButton = screen.getByTestId("trigger-btn-id_dag_2");
    await act(async () => {
      fireEvent.click(triggerButton);
    });
    const rows = screen.getAllByRole("row");
    await act(async () => {
      fireEvent.click(rows[1]);
    });
    const refreshButton = screen.getByTestId("refresh");
    await act(async () => {
      fireEvent.click(refreshButton);
    });
    expect(mockProps.fetchDagList).toHaveBeenCalled();
  });

  it("should handle concurrent API calls", async () => {
    renderComponent();
    const triggerButton = screen.getByTestId("trigger-btn-id_dag_2");
    const deleteButton = screen.getByTestId("delete-btn-id_dag_1");
    await act(async () => {
      fireEvent.click(triggerButton);
      fireEvent.click(deleteButton);
    });
    expect(runDag).toHaveBeenCalled();
    expect(deleteSchedule).not.toHaveBeenCalled();
  });
});
describe("Service type column", () => {
  it("should display service type column in table headers", () => {
    renderComponent();
    expect(screen.getByText("Service Type")).toBeInTheDocument();
  });

  it("should show DTS and DMS service types in uppercase", () => {
    const dagsWithServiceTypes = [
      {
        ...mockDagList[0],
        service_type: "dts",
      },
      {
        ...mockDagList[1],
        service_type: "dms",
      },
      {
        ...mockDagList[2],
        service_type: null,
      },
    ];
    useSelectorMock.mockImplementation((selector) => {
      const state = {
        jobSchedule: {
          dagList: dagsWithServiceTypes,
          currentPageInfo: 1,
          pageSizeInfo: 10,
        },
        settings: {
          messageData: null,
          hideMessage: false,
        },
      };
      return selector(state);
    });
    renderComponent();
    const serviceTypeCells = screen.getAllByText(/DTS|DMS/);
    expect(serviceTypeCells.length).toBeGreaterThan(0);
    expect(screen.getByText("DTS")).toBeInTheDocument();
    expect(screen.getByText("DMS")).toBeInTheDocument();
  });

  it("should filter icon for service type column", async () => {
    renderComponent();
    await waitFor(() => {
      expect(screen.getByTestId("service_type-filter-icon")).toBeInTheDocument();
    });
  });
});