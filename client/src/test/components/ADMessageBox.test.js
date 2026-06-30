import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import ADMessageBox from "../../components/ADMessageBox";
import { BrowserRouter as Router} from "react-router-dom";

const mockStore = configureStore();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useSearchParams: jest.fn(),
}));

const mockProps = {
  handleMessageSent: jest.fn(),
  botStatus: true,
  columns: [],
  loadedFiles: [],
  selectedFiles: [],
};

const store = mockStore({
  app: {
    previewState: false,
  },
});
// reusable function for render
const renderComponent = (props, appStore) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <ADMessageBox {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("ADMessage box component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render beat loader when bot is typing", () => {
    renderComponent(mockProps, store);
    expect(screen.getByTestId("beat-loader")).toBeInTheDocument();
  });

  it("should show abort button when bot is typing", () => {
    renderComponent(mockProps, store);
    expect(screen.getByTestId("bot-abort-btn")).toBeInTheDocument();
  });

  it("should stop all process when user clicks on abort button",()=>{
    renderComponent(mockProps, store);
    fireEvent.click(screen.getByTestId("bot-abort-btn"));
  })

  it("should render follow up prompts when bot is not typing", () => {
    renderComponent({ ...mockProps, botStatus: false }, store);
    expect(screen.getByTestId("follow-up-prompts")).toBeInTheDocument();
  });
});
