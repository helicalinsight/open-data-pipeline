import React from "react";
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
import Extensions from "../../../../app/settings-module/components/Extensions";
import "../../../__mocks__/matchMedia";

global.setImmediate = jest.useRealTimers;

const mockStore = configureStore();

const store = mockStore({
  app: {
    selectedExtensions: [],
  },
});

const renderComponent = (appStore) => {
  return render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <Extensions />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Flat files component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error", () => {
    renderComponent(store);
  });

  it("shoud trigger switch change", () => {
    renderComponent(store);
    const extensionSwitch = screen.getAllByTestId("extension-switch");
    act(() => {
      fireEvent.click(extensionSwitch[0]);
    });
  });
});
