import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";
import SettingsModule from "../../../app/settings-module";
const mockStore = configureStore();
if (!window.matchMedia) {
  window.matchMedia = function() {
    return {
      matches: false,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    };
  };
}
const store = mockStore({
  settings: {
    allPreferences: {
      files: {
        file_size: 5,
        num_records: 100,
      },
    },
  },
  app: {
    userConfig: {
      role: "admin",
      chat: ["jobs", "create", "schedule"],
      job: [
        "histroy",
        "dataPreview",
        "reset",
        "load",
        "trigger",
        "undo",
        "redo",
      ],
      datasources: [
        "flat_files",
        "redshift",
        "mysql",
        "snowflake",
        "postgres",
        "astra",
        "cassandra",
        "firebird",
      ],
    },
  },
});

const renderComponent = () => {
  return render(
    <reactRedux.Provider store={store}>
      <SettingsModule />
    </reactRedux.Provider>
  );
};

describe("Settings component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render component without error", () => {
    renderComponent();
    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(
      screen.getByText("Manage your account settings and preferences")
    ).toBeInTheDocument();
  });

  it("should by default render contents of Profile tab", () => {
    renderComponent();
  });

  it("should show contents of Preferences tab when user clicks on preferences", () => {
    renderComponent();
    const preferencesTab = screen.getByText("Preferences");
    fireEvent.click(preferencesTab);
    expect(screen.getByText("Save Preferences")).toBeInTheDocument();
  });

  it("should show contents of Extensions tab when user clicks on extensions", () => {
    renderComponent();
    const extensionsTab = screen.getByText("Extensions");
    fireEvent.click(extensionsTab);
    expect(screen.getByText("/expression")).toBeInTheDocument();
    expect(screen.getByText("/sql")).toBeInTheDocument();
    expect(screen.getByText("/bi")).toBeInTheDocument();
  });
  it("should show contents of Documentation tab when user clicks on documentation", () => {
  renderComponent();
  const documentationTab = screen.getByText("Documentation");
  fireEvent.click(documentationTab);
  const documentationLinks = screen.getAllByRole('link');
  expect(documentationLinks.length).toBeGreaterThan(0);
});
});
