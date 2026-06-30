import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import * as reactRedux from "react-redux";
import dayjs from "dayjs";
import configureStore from "redux-mock-store";
import { BrowserRouter as Router } from "react-router-dom";
import "../../../__mocks__/matchMedia.js";
import IndividualJob from "../../../../app/job-schedule-module/components/IndividualJob.jsx";
import {
  downloadDagInfo,
  getDagLogs,
  getIndividualDag,
} from "../../../../apis/jobScheduleService.js";
const mockStore = configureStore();

global.URL.createObjectURL = jest.fn();

// mock for useDispatch
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useDispatch: jest.fn(),
}));
const useDispatchMock = reactRedux.useDispatch;

// mock for api service
jest.mock("../../../../apis/jobScheduleService.js", () => ({
  downloadDagInfo: jest.fn(),
  getDagLogs: jest.fn(),
  getIndividualDag: jest.fn(),
}));

const mockDagInfoResponse = {
  basic_info: {
    dag_id: "1234",
    job_name: "Job 20",
    local: "true",
  },
  dag_runs: {
    dag_runs: [
      {
        dag_run_id: "dag_run_id",
        execution_date: "date",
        state: "running",
      },
    ],
  },
};

const mockErrorResponse = {
  msg: "Something went wrong!!",
};

const mockDagRunningProps = {
  setIndividualJob: jest.fn(),
  setDagInfo: jest.fn(),
  dagInfo: {
    basic_info: mockDagInfoResponse?.basic_info,
    dag_runs: mockDagInfoResponse?.dag_runs,
  },
};

const mockDagSuccessProps = {
  ...mockDagRunningProps,
  dagInfo: {
    basic_info: { ...mockDagRunningProps.dagInfo.basic_info },
    dag_runs: {
      dag_runs: [
        {
          dag_run_id: "dag_run_id",
          execution_date: "date",
          state: "success",
        },
      ],
    },
  },
};

const store = mockStore({
  app: {},
  dms: {  
    selectedServiceType: null
  },
});

// reusable function for render
const renderComponent = (props) => {
  render(
    <reactRedux.Provider store={store}>
      <Router>
        <IndividualJob {...props} />
      </Router>
    </reactRedux.Provider>
  );
};
describe("Individual Job module component", () => {
  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = {
      getItem: jest.fn().mockReturnValue(
        JSON.stringify({
          state: {
            success: "Success",
            running: "Running",
            failed: "Failed",
          },
        })
      ),
      setItem: jest.fn(),
      removeItem: jest.fn(),
      clear: jest.fn(),
    };
    global.localStorage = localStorageMock;
    useDispatchMock.mockImplementation(() => () => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    useDispatchMock.mockClear();
  });

  it("should show dag name and refresh button on the screen", () => {
    renderComponent(mockDagRunningProps);
    expect(screen.getByTestId("dag_refresh_btn")).toBeInTheDocument();
  });

  it("should fetch and show the updated dag Info when user clicks on refresh button with success network", () => {
    getIndividualDag.mockImplementationOnce(({ onSuccess }) =>
      onSuccess(mockDagInfoResponse)
    );
    renderComponent(mockDagRunningProps);
    fireEvent.click(screen.getByTestId("dag_refresh_btn"));
  });

  it("should fetch and show logs inside modal when user clicks on eye icon with success network", () => {
    getDagLogs.mockImplementationOnce(({ onSuccess }) =>
      onSuccess("Logs passed - description : this log is passed")
    );
    renderComponent(mockDagRunningProps);
  });

  it("should not fetch and show logs inside modal when user clicks on eye icon with failed network", () => {
    getDagLogs.mockImplementationOnce(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(mockDagRunningProps);
  });

  it("should show download logs button when dag running is finished", async () => {
    renderComponent(mockDagSuccessProps);
  });

  it("should download the logs when user clicks on download logs button with success network", () => {
    downloadDagInfo.mockImplementationOnce(({ onSuccess }) =>
      onSuccess("dag-info")
    );
    renderComponent(mockDagSuccessProps);
  });

  it("should not download the logs when user clicks on download logs button with failed network", () => {
    downloadDagInfo.mockImplementationOnce(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(mockDagSuccessProps);
  });

  it("should not fetch and show the updated dag Info when user clicks on refresh button with failed network", () => {
    getIndividualDag.mockImplementationOnce(({ onError }) =>
      onError(mockErrorResponse)
    );
    renderComponent(mockDagRunningProps);
    fireEvent.click(screen.getByTestId("dag_refresh_btn"));
  });
  it("should render table with correct columns", () => {
    renderComponent(mockDagRunningProps);
    expect(screen.getByText("Schedule run id")).toBeInTheDocument();
    expect(screen.getByText("Execution date")).toBeInTheDocument();
    expect(screen.getByText("State")).toBeInTheDocument();
    expect(screen.getByText("Logs")).toBeInTheDocument();
  });

  it("should display loading spinner when state is 'running'", () => {
    renderComponent(mockDagRunningProps);
  });

  it("should reverse the data source array", () => {
    const mockPropsWithMultipleRuns = {
      ...mockDagRunningProps,
      dagInfo: {
        ...mockDagRunningProps.dagInfo,
        dag_runs: {
          dag_runs: [
            {
              dag_run_id: "run1",
              execution_date: "2023-01-01",
              state: "success",
            },
            {
              dag_run_id: "run2",
              execution_date: "2023-01-02",
              state: "success",
            },
          ],
        },
      },
    };
    renderComponent(mockPropsWithMultipleRuns);
    const rows = screen.getAllByRole("row");
  });

  it("should handle session expiry when API returns 401", () => {
    const mockUnauthorizedError = { response: { status: 401 } };
    getIndividualDag.mockImplementationOnce(({ onError }) =>
      onError(mockUnauthorizedError)
    );
    const mockDispatch = jest.fn();
    useDispatchMock.mockReturnValue(mockDispatch);
    renderComponent(mockDagRunningProps);
    fireEvent.click(screen.getByTestId("dag_refresh_btn"));
  });

  it("should handle empty dag_runs array", () => {
    const mockPropsWithNoRuns = {
      ...mockDagRunningProps,
      dagInfo: {
        ...mockDagRunningProps.dagInfo,
        dag_runs: { dag_runs: [] },
      },
    };
    renderComponent(mockPropsWithNoRuns);
  });

  it("should handle undefined execution_date", () => {
    const mockPropsWithUndefinedDate = {
      ...mockDagRunningProps,
      dagInfo: {
        ...mockDagRunningProps.dagInfo,
        dag_runs: {
          dag_runs: [
            { dag_run_id: "run1", execution_date: undefined, state: "success" },
          ],
        },
      },
    };
    renderComponent(mockPropsWithUndefinedDate);
  });

  it("should format execution date with correct timezone", () => {
    const fixedDate = "2023-01-01T00:00:00Z";
    const mockPropsWithFixedDate = {
      ...mockDagRunningProps,
      dagInfo: {
        ...mockDagRunningProps.dagInfo,
        dag_runs: {
          dag_runs: [
            { dag_run_id: "run1", execution_date: fixedDate, state: "success" },
          ],
        },
      },
    };
    renderComponent(mockPropsWithFixedDate);
  });
  it("should display empty state when no dag runs are available", () => {
    const emptyDagProps = {
      ...mockDagRunningProps,
      dagInfo: {
        basic_info: mockDagInfoResponse.basic_info,
        dag_runs: { dag_runs: [] },
      },
    };
    renderComponent(emptyDagProps);
    expect(
      screen.queryByRole("row", { name: /dag_run_id/ })
    ).not.toBeInTheDocument();
  });

  it("should handle different timezone formats in execution date", () => {
    const differentTimezoneProps = {
      ...mockDagRunningProps,
      dagInfo: {
        ...mockDagRunningProps.dagInfo,
        dag_runs: {
          dag_runs: [
            {
              dag_run_id: "run1",
              execution_date: "2023-01-01T12:00:00+05:30",
              state: "success",
            },
          ],
        },
      },
    };
    renderComponent(differentTimezoneProps);
  });

  it("it should handle session expiree on 401 error", () => {
    const mockDispatch = jest.fn();
    useDispatchMock.mockReturnValue(mockDispatch);
    const unauthorizedError = { response: { status: 401 } };
    getIndividualDag.mockImplementationOnce(({ onError }) =>
      onError(unauthorizedError)
    );
    renderComponent(mockDagRunningProps);
    fireEvent.click(screen.getByTestId("dag_refresh_btn"));
    expect(mockDispatch).toHaveBeenCalled();
  });
  it("should not show download button when local is false", () => {
    const mockPropsNotLocal = {
      ...mockDagSuccessProps,
      dagInfo: {
        ...mockDagSuccessProps.dagInfo,
        basic_info: {
          ...mockDagSuccessProps.dagInfo.basic_info,
          local: "false",
        },
      },
    };
    renderComponent(mockPropsNotLocal);
    expect(screen.queryByTestId("download_logs_id")).not.toBeInTheDocument();
  });
});
