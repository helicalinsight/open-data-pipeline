import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import { useNavigate } from "react-router-dom";
import { setSelectPipelineModeAction } from "../../../store/actions/dmsAction";
import MigrationModule from "../../../app/dms-module/MigrationModule";
window.matchMedia = window.matchMedia || function () {
  return {
    matches: false,
    addListener: function () {},
    removeListener: function () {},
  };
};
jest.mock("react-router-dom", () => ({
  useNavigate: jest.fn(),
}));

jest.mock("../../../components/ADIcons/custom-icon", () => () => (
  <div data-testid="custom-icon"></div>
));

const mockStore = configureStore([]);

describe("PipelineModeModule", () => {
  let store;
  let mockNavigate;

  beforeEach(() => {
    store = mockStore({
      dms: {
        selectedPipelineMode: "table",
      },
    });
    
    mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate);
    Storage.prototype.getItem = jest.fn((key) => {
      if (key === "sourceTypeIcon")
        return JSON.stringify({ name: "source-icon" });
      if (key === "DestinationTypeIcon")
        return JSON.stringify({ name: "dest-icon" });
      return null;
    });
    store.dispatch = jest.fn();
  });
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("navigates on Continue click", () => {
    render(
      <Provider store={store}>
        <MigrationModule />
      </Provider>
    );
    const button = screen.getByRole("button", { name: /continue/i });
    fireEvent.click(button);
  });

  it("renders all three pipeline modes", () => {
    render(
      <Provider store={store}>
        <MigrationModule />
      </Provider>
    );
  });
});