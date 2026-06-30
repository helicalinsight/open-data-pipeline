import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import EditorDrawer from "../../../../../app/app-header/components/job-schedule/components/EditorDrawer";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";

const mockStore = configureStore();

const initialState = {
  app: {
    editorSuggestions: {
      yaml: [],
      python: [],
    },
    jobHelpInfo: {
      yaml: "yaml help info",
      python: "python help info",
    },
  },
  chat: {
    chatList: {
      Job1: {
        isYamlSaved: true,
      },
    },
    selectedChat: {
      chat_id: "Job1",
    },
  },
  jobSchedule: {
    childDrawer: true,
  },
};

const defaultProps = {
  mode: "python",
  handleClose: jest.fn(),
  title: "Python",
  isJobConfig: true,
  keyValueData: {},
  onAdd: jest.fn(),
};

const renderComponent = (storeState = initialState, props = {}) => {
  const store = mockStore(storeState);
  return render(
    <reactRedux.Provider store={store}>
      <Router>
        <EditorDrawer {...defaultProps} {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("EditorDrawer Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders without errors", () => {
    renderComponent();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByTestId("help-info-icon")).toBeInTheDocument();
  });

  it("shows help info when info icon is clicked", () => {
    renderComponent();
    act(() => {
      fireEvent.click(screen.getByTestId("help-info-icon"));
    });
  });

  it("calls handleClose when drawer is closed", () => {
    renderComponent();
    act(() => {
      fireEvent.click(screen.getByLabelText("Close"));
    });
    expect(defaultProps.handleClose).toHaveBeenCalled();
  });

  it("toggles word wrap when checkbox is clicked", () => {
    renderComponent();
    
    // Click settings icon to show popover
    act(() => {
      fireEvent.click(screen.getByRole("img", { name: "setting" }));
    });
    
    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).not.toBeChecked();
    
    act(() => {
      fireEvent.click(checkbox);
    });
    expect(checkbox).toBeChecked();
    
    act(() => {
      fireEvent.click(checkbox);
    });
    expect(checkbox).not.toBeChecked();
  });

  it("doesn't show settings icon when isJobConfig is false", () => {
    renderComponent(initialState, { isJobConfig: false });
    expect(screen.queryByRole("img", { name: "setting" })).not.toBeInTheDocument();
  });

  it("renders CustomEditor component", () => {
    renderComponent();
    expect(screen.getByRole("button", { name: /save/i })).toBeInTheDocument();
  });

  it("matches snapshot when closed", () => {
    const store = mockStore({
      ...initialState,
      jobSchedule: { childDrawer: false }
    });
    const { asFragment } = render(
      <reactRedux.Provider store={store}>
        <Router>
          <EditorDrawer {...defaultProps} />
        </Router>
      </reactRedux.Provider>
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("dispatches setChildDrawer action when drawer is closed", () => {
    const store = mockStore(initialState);
    render(
      <reactRedux.Provider store={store}>
        <Router>
          <EditorDrawer {...defaultProps} />
        </Router>
      </reactRedux.Provider>
    );
    
    act(() => {
      fireEvent.click(screen.getByLabelText("Close"));
    });
    
    const actions = store.getActions();
    expect(actions).toContainEqual(expect.objectContaining({
      type: "SET_CHILD_DRAWER",
      payload: false
    }));
  });

  it("renders with correct title", () => {
    renderComponent(initialState, { title: "YAML Editor" });
    expect(screen.getByText("YAML Editor")).toBeInTheDocument();
  });
});