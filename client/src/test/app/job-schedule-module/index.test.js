import React from "react";
import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";
import { BrowserRouter as Router } from "react-router-dom";
import JobScheduleModule from "../../../app/job-schedule-module/index.jsx";
import { getLocalStorageItem } from "../../../utils/userData.js";
import { fetchDagListUtil } from "../../../utils/appUtils.js";

jest.mock("../../../utils/userData.js");
jest.mock("../../../utils/appUtils.js");

const mockStore = configureStore();

import "../../__mocks__/matchMedia.js";

describe("Job Schedule module component", () => {
  let store;
  const initialState = {
    jobSchedule: {
      dagList: [],
      dagTotal: 0,
      individualJob: false,
      dagInfo: null,
      currentPageInfo: 1,
      pageSizeInfo: 10,
    },
  };

  beforeEach(() => {
    store = mockStore(initialState);
    getLocalStorageItem.mockReturnValue({ user: { id: 1 } });
    fetchDagListUtil.mockImplementation(() => Promise.resolve());
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without crashing", () => {
    render(
      <reactRedux.Provider store={store}>
        <Router>
          <JobScheduleModule />
        </Router>
      </reactRedux.Provider>
    );
  });

  it("should render IndividualJob when individualJob is true", () => {
    const customState = {
      ...initialState,
      jobSchedule: {
        ...initialState.jobSchedule,
        individualJob: true,
      },
    };
    const customStore = mockStore(customState);
    render(
      <reactRedux.Provider store={customStore}>
        <Router>
          <JobScheduleModule />
        </Router>
      </reactRedux.Provider>
    );
  });

  it("should call fetchDagList on mount", async () => {
    render(
      <reactRedux.Provider store={store}>
        <Router>
          <JobScheduleModule />
        </Router>
      </reactRedux.Provider>
    );
    await waitFor(() => {
      expect(fetchDagListUtil).toHaveBeenCalledTimes(1);
      expect(fetchDagListUtil).toHaveBeenCalledWith({
        dispatch: expect.any(Function),
        setLoading: expect.any(Function),
        user: { id: 1 },
        current: 1,
        pageSize: 10,
        filters: {},
      });
    });
  });

  it("should show loading state", async () => {
    fetchDagListUtil.mockImplementationOnce(({ setLoading }) => {
      setLoading(true);
      return Promise.resolve();
    });
    render(
      <reactRedux.Provider store={store}>
        <Router>
          <JobScheduleModule />
        </Router>
      </reactRedux.Provider>
    );
  });
});
