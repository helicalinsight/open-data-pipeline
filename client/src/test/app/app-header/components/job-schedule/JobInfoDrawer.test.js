import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";

import JobInfoDrawer from "../../../../../app/app-header/components/job-schedule/components/JobInfoDrawer";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";

const mockStore = configureStore();

const appStore = mockStore({
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
});

const props = {
  open: true,
  setOpenInfo: jest.fn(),
  mode: "yaml",
};

const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <JobInfoDrawer {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("JobInfo Drawer component", () => {
  it("render the component without erros", () => {
    renderComponent(appStore, props);
  });
  it("render the component without erros", () => {
    renderComponent(appStore, { ...props, mode: undefined });
  });

  it("close drawer", () => {
    renderComponent(appStore, props);
    act(() => {
      fireEvent.click(screen.getByLabelText("Close"));
    });
  });
});
