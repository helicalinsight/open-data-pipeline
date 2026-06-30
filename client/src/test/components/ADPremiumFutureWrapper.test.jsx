import React, { useState } from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../__mocks__/matchMedia";
import PremiumFeatureWrapper from "../../components/ADPremiumFutureWrapper";

const mockStore = configureStore();

const appStore = mockStore({
  app: {
    userConfig: {
      chat: ["jobs", "create"],
      job: ["histroy", "dataPreview", "reset", "load"],
      datasources: ["flat_files"],
      settings: ["file_size"]
    },
  },
});

// reusable function for render
const renderComponent = (props, appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <PremiumFeatureWrapper {...props}>
          <div>children</div>
        </PremiumFeatureWrapper>
      </Router>
    </reactRedux.Provider>
  );
};

describe("Premium Feature Wrapper component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error", () => {
    const mockProps = {
      module: "chat",
      feature: "jobs",
      tooltip: {
        title: "Jobs",
      },
    };
    renderComponent(mockProps, appStore);
  });

  it("should return the children when it is available", () => {
    const mockProps = {
      module: "chat",
      feature: "create",
      tooltip: {
        title: "Create",
      },
    };
    renderComponent(mockProps, appStore);
    expect(screen.getByTestId("children")).toBeInTheDocument();
  });

  it("should return the premium when it is premium", () => {
    const props = {
      module: "chat",
      feature: "schedule",
      tooltip: {
        title: "Create",
      },
    };
    renderComponent(props, appStore);
    expect(screen.getByTestId("premium")).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("premium"));
  });
});
