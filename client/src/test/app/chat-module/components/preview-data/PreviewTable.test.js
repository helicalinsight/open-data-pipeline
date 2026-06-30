import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import "@testing-library/jest-dom";
import "../../../../__mocks__/matchMedia";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import PreviewTable from "../../../../../app/chat-module/components/preview-data/PreviewTable";
const mockStore = configureStore([]);
// Include the getRowClassName function directly in the test file
const getRowClassName = (record, index) => {
  return index % 2 === 0 ? "even-row" : "odd-row";
};

const mockColumns = [
  {
    dataIndex: "sr_",
    width: 100,
    key: "sr_",
    ellipsis: true,
    title: "sr_",
    sorter: (a, b) => a["sr_"] - b["sr_"],
  },
];

const mockData = [
  {
    sr_: 1,
    key: "key1",
    name: "Dett",
    gender: "Male",
    age: 18,
    date_: "21/05/2015",
    country: "Great Britain",
  },
  {
    sr_: 2,
    key: "key2",
    name: "Matt",
    gender: "Male",
    age: 19,
    date_: "21/05/2015",
    country: "Great Britain",
  },
];
// component props
const mockProps = {
  previewTableData: { datasource: { data: [] }, columns: [] },
  loading: true,
  paginationData: { limit_by: 10 },
  currentPage: 1,
  setSorter: jest.fn(),
  activeTabData: { alias: "test", source_id: "11723617236" },
};

// reusable function for render
const renderComponent = (props, initialState) => {
  const store = mockStore(initialState);
  render(
    // <PreviewTable {...props} />
    <Provider store={store}>
      <PreviewTable {...props} />
    </Provider>
  );
};

describe("Preview Table component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the component without error", () => {
    // renderComponent(mockProps);
    renderComponent(mockProps, { chat: { yamlSave: false } });
  });

  it("should show loading skeleton when data is getting fetched", () => {
    renderComponent(mockProps, { chat: { yamlSave: false } });
    expect(screen.getByTestId("skeleton-element")).toBeInTheDocument();
  });

  it("should show table data when data is available", () => {
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: mockColumns,
          datasource: { data: mockData },
        },
      },
      { chat: { yamlSave: false } }
    );
    expect(screen.getByTestId("preview-table-id")).toBeInTheDocument();
  });

  it("should sort the data when user clicks on sorter", async () => {
    const setSorterSpy = jest.fn();
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: mockColumns,
          datasource: { data: mockData },
        },
        setSorter: setSorterSpy,
      },
      { chat: { yamlSave: false } }
    );
    const headerCells = screen.getAllByRole("columnheader");
    const headerCell = headerCells.find((cell) => cell.textContent === "sr_");
    expect(headerCell).toBeInTheDocument();
    // First click (ascending order)
    fireEvent.click(headerCell);
    // Second click (descending order)
    fireEvent.click(headerCell);
    const rows = screen.getAllByRole("row");
    expect(rows[1]).toHaveTextContent("2");
    expect(rows[2]).toHaveTextContent("1");
  });

  // it("should show no data message when table data is empty", () => {
  //   renderComponent({ ...mockProps, loading: false });
  //   expect(screen.getByText(/No data/i)).toBeInTheDocument();
  // });

  it("should display 'No data' when there are no columns and no data", () => {
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: [],
          datasource: { data: [] },
        },
      },
      { chat: { yamlSave: false } }
    );
    expect(screen.getByText(/No data/i)).toBeInTheDocument();
  });
  it("should check and uncheck columns and update checkedList accordingly", async () => {
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: mockColumns,
          datasource: { data: mockData },
        },
      },
      { chat: { yamlSave: false } }
    );
    const settingsButton = screen.getByRole("img", {
      name: /column settings/i,
    });
    fireEvent.click(settingsButton);
    const srCheckbox = screen.getByRole("checkbox", { name: /sr_/i });
    expect(srCheckbox).toBeChecked();
    fireEvent.click(srCheckbox);
    expect(srCheckbox).not.toBeChecked();
    fireEvent.click(srCheckbox);
    expect(srCheckbox).toBeChecked();
  });

  it("should apply changes when 'OK' button is clicked", async () => {
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: mockColumns,
          datasource: { data: mockData },
        },
      },
      { chat: { yamlSave: false } }
    );
    const settingsButton = screen.getByRole("img", {
      name: /column settings/i,
    });
    fireEvent.click(settingsButton);
    const okButton = screen.getByText("OK");
    fireEvent.click(okButton);
    expect(screen.getByTestId("preview-table-id")).toBeInTheDocument();
  });

  it("should all columns when 'Select All' checkbox is clicked", async () => {
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: mockColumns,
          datasource: { data: mockData },
        },
      },
      { chat: { yamlSave: false } }
    );
    const settingsButton = screen.getByRole("img", {
      name: /column settings/i,
    });
    fireEvent.click(settingsButton);
    const selectAllCheckbox = screen.getByRole("checkbox", {
      name: /select all/i,
    });
    fireEvent.click(selectAllCheckbox);
  });
  it("should filtered columns and show matches when search input ", () => {
    renderComponent(
      {
        ...mockProps,
        loading: false,
        previewTableData: {
          columns: mockColumns,
          datasource: { data: mockData },
        },
      },
      { chat: { yamlSave: false } }
    );
    const settingsButton = screen.getByRole("img", {
      name: /column settings/i,
    });
    fireEvent.click(settingsButton);

    const searchInput = screen.getByPlaceholderText("Search column");
    fireEvent.change(searchInput, { target: { value: "sr_" } });
    fireEvent.change(searchInput, { target: { value: "nonexistent" } });
    expect(screen.queryByText("sr_")).not.toBeInTheDocument();
    fireEvent.change(searchInput, { target: { value: "" } });
  });
});
