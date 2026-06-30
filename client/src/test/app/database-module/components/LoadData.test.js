import React from "react";
import configureStore from "redux-mock-store";
import LoadData from "../../../../app/database-module/components/LoadData.jsx";
import { BrowserRouter as Router } from "react-router-dom";
import { fireEvent, render, screen, act } from "@testing-library/react";
import * as reactRedux from "react-redux";
import "../../../__mocks__/matchMedia.js";
import "@testing-library/jest-dom";

const mockStore = configureStore();

// component props
const mockProps = {
  formData: [],
  socket: {},
  handleClose: jest.fn(),
};

// store mock
const store = mockStore({
  database: {
    selectedDatasource: {
      driver: "flat_files",
    },
    savedConnections: [
      {
        _id: "62cb179a-dd58-43fb-97de-c01526636b48",
        alias: "enrollments",
        fileType: ".csv",
        key: "62cb179a-dd58-43fb-97de-c01526636b48",
      },
      {
        _id: "0575afeb-8faa-4dbf-a3a3-c86734fc99a7",
        alias: "file_example_XLSX_100",
        fileType: ".xlsx",
        key: "0575afeb-8faa-4dbf-a3a3-c86734fc99a7",
      },
    ],
  },
  chat: {
    chatList: {
      "65f97e88403f6d5fa967ac69": {
        chat_id: "65f97e88403f6d5fa967ac69",
        chat_name: "Job 2",
        loadedFiles: [
          {
            source_id: "65fd3be778aa5af726d559cd",
            alias: "csv file",
            type: "csv",
          },
        ],
      },
    },
  },
  dms: {
    step: 2,
  },
});

// reusable function for render
const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <LoadData {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

afterEach(() => {
  jest.clearAllMocks();
});

describe("DB Stepper component", () => {
  it("should render the datasource name and image in the card header", () => {
    renderComponent(store, mockProps);
    expect(screen.getByTestId("datasource-img-id")).toBeInTheDocument();
    expect(screen.getByTestId("datasource-name-id")).toBeInTheDocument();
  });

  it("should update search term when search value changes", () => {
    renderComponent(store, mockProps);
    const searchInput = screen.getByPlaceholderText("Search name");
    fireEvent.change(searchInput, { target: { value: "test" } });
    expect(searchInput.value).toBe("test");
  });
});
