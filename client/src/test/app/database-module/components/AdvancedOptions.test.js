import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";
import { fetchColumns } from "../../../../apis/databaseService";
import "@testing-library/jest-dom";
import "../../../__mocks__/matchMedia";

import * as reactRedux from "react-redux";
import configureStore from "redux-mock-store";
import AdvancedOptions from "../../../../app/database-module/components/AdvancedOptions";

jest.mock("../../../../apis/databaseService", () => ({
  fetchColumns: jest.fn(),
}));

const tableColumns = {
  "2017 Order Data.sample_sheet": [
    {
      key: "2017 Order Data.sample_sheet aaa",
      name: "aaa",
      parent: "2017 Order Data.sample_sheet",
    },
    {
      key: "2017 Order Data.sample_sheet bbb",
      name: "bbb",
      parent: "2017 Order Data.sample_sheet",
    },
  ],
};

const mockStore = configureStore();

const appStore1 = mockStore({
  database: {
    tableColumns: {},
  },
});

const appStore2 = mockStore({
  database: {
    tableColumns,
  },
});

const mockProps = {
  tables: [
    {
      name: "2017 Order Data.Order Data",
      value: "2017 Order Data.Order Data",
    },
    {
      name: "2017 Order Data.sample_sheet",
      value: "2017 Order Data.sample_sheet",
    },
  ],
  selectedConnection: {
    source: "flat_files",
    connection_id: "c4ba8d28-5cd2-430c-999a-6bc926d945f2",
    _id: "c4ba8d28-5cd2-430c-999a-6bc926d945f2",
    alias: "2017 Order Data",
    fileType: ".xlsx",
    key: "c4ba8d28-5cd2-430c-999a-6bc926d945f2",
  },
  selectedCols: {
    "2017 Order Data.Order Data": ["Customer ID", "Cookies Shipped"],
    "2017 Order Data.sample_sheet": [],
  },
  isCsvFile: false,
  setSelectedCols: jest.fn(),
};

const renderComponent = (appStore1, props) => {
  render(
    <reactRedux.Provider store={appStore1}>
      <Router>
        <AdvancedOptions {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

describe("Advanced Options", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without errrs", () => {
    renderComponent(appStore1, mockProps);
  });

  it("should render table on click of adavanced button", () => {
    renderComponent(appStore1, mockProps);
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
  });

  it("should render when type is csv", () => {
    renderComponent(appStore1, { ...mockProps, isCsvFile: true });
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
  });

  it("should tigger fetchColumns API:SUCCESS CASE when columns are empty", () => {
    fetchColumns.mockImplementationOnce(({ onSuccess }) => {
      onSuccess({ success: true, columns: ["col1", "col2"] });
    });
    renderComponent(appStore1, { ...mockProps });
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("Expand row"));
    });
  });

  it("should tigger fetchColumns API: FAILED CASE when columns are empty", () => {
    fetchColumns.mockImplementationOnce(({ onError }) => {
      onError("error");
    });
    renderComponent(appStore1, { ...mockProps });
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("Expand row"));
    });
  });

  it("should not tigger fetchColumns API on exapnd", () => {
    renderComponent(appStore2, { ...mockProps });
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("Expand row"));
    });
  });

  it("should tick check box on click of Row", () => {
    renderComponent(appStore2, { ...mockProps });
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("Expand row"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("aaa"));
    });
  });
  it("should filter column names based on search text", () => {
    renderComponent(appStore2, { ...mockProps });
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("Expand row"));
    });
    const columnsBeforeSearch = screen.getAllByText(/aaa|bbb/);
    expect(columnsBeforeSearch.length).toBeGreaterThan(0);
    const searchInput = screen.getByPlaceholderText("Search Column Names");
    fireEvent.change(searchInput, { target: { value: "aaa" } });
    const columnsAfterSearch = screen.getAllByText("aaa");
    expect(columnsAfterSearch.length).toBeGreaterThan(0);
    const columnsAfterSearchNotShown = screen.queryAllByText("bbb");
    expect(columnsAfterSearchNotShown.length).toBe(0);
  });
  it("should update selected columns when 'select all' checkbox is clicked", () => {
    const setSelectedCols = jest.fn();
    const mockPropsWithMockedSetSelectedCols = {
      ...mockProps,
      setSelectedCols,
    };
    renderComponent(appStore2, mockPropsWithMockedSetSelectedCols);
    act(() => {
      fireEvent.click(screen.getByTestId("advanced-button"));
    });
    act(() => {
      fireEvent.click(screen.getByLabelText("Expand row"));
    });
    const selectAllCheckbox = screen.getByRole("checkbox", { name: /2017 Order Data.sample_sheet/i });
    act(() => {
      fireEvent.click(selectAllCheckbox); 
    });
  });
});
