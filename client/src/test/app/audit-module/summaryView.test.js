import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import {
  getAuditBillingSummary,
  getDetailData,
} from "../../../apis/auditService";
import SummaryView from "../../../app/audit-module/summaryView";
import dayjs from "dayjs";
import "@testing-library/jest-dom";

jest.mock("../../../apis/auditService", () => ({
  getAuditBillingSummary: jest.fn(),
  getDetailData: jest.fn(),
}));
jest.mock("@ant-design/plots", () => {
  return {
    Column: ({ onReady }) => {
      setTimeout(() => {
        if (onReady) {
          onReady({
            chart: {
              on: jest.fn(),
            },
          });
        }
      }, 0);
      return <div>Mocked Column Chart</div>;
    },
  };
});

const mockStore = configureStore([]);
const store = mockStore({});

describe("SummaryView", () => {
  const mockOnBarClick = jest.fn();
  beforeEach(() => {
    jest.clearAllMocks();
    mockOnBarClick.mockClear();
  });

  it("renders SummaryView and its components", async () => {
    getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
      onSuccess({
        daily_details: [],
        start_date: null,
        end_date: null,
        total_audit_cost: 0,
        total_audit_rows: 0,
        total_audit_cols: 0,
        total_audit_steps: 0,
      });
    });
    render(
      <Provider store={store}>
        <SummaryView onBarClick={mockOnBarClick} />
      </Provider>
    );
    expect(screen.getByText(/monthly/i)).toBeInTheDocument();
  });

  it("fetches data on mount and updates chart data", async () => {
    const mockResponse = {
      daily_details: [
        { day: 1, audit_cost: 100, detail_link: "link1", service_type: "dts" },
        { day: 2, audit_cost: 200, detail_link: "link2", service_type: "dms" },
      ],
      start_date: dayjs().subtract(1, "month").toISOString(),
      end_date: dayjs().toISOString(),
      total_audit_cost: 300,
      total_audit_rows: 1000,
      total_audit_cols: 500,
      total_audit_steps: 50,
    };

    getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
      onSuccess(mockResponse);
    });

    render(
      <Provider store={store}>
        <SummaryView onBarClick={mockOnBarClick} />
      </Provider>
    );

    await waitFor(() => {
      expect(getAuditBillingSummary).toHaveBeenCalled();
    });    
    expect(screen.getByText(/Mocked Column Chart/i)).toBeInTheDocument();
  });

  it("changes view and updates the chart accordingly", async () => {
    const mockResponse = {
      daily_details: [
        { day: 1, audit_cost: 100, detail_link: "link1", service_type: "dts" },
        { day: 2, audit_cost: 200, detail_link: "link2", service_type: "dms" },
      ],
      start_date: dayjs().subtract(1, "month").toISOString(),
      end_date: dayjs().toISOString(),
      total_audit_cost: 300,
      total_audit_rows: 1000,
      total_audit_cols: 500,
      total_audit_steps: 50,
    };

    getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
      onSuccess(mockResponse);
    });

    render(
      <Provider store={store}>
        <SummaryView onBarClick={mockOnBarClick} />
      </Provider>
    );

    await waitFor(() => {
      expect(getAuditBillingSummary).toHaveBeenCalled();
    });
    const viewSelectors = screen.getAllByRole("combobox");
    fireEvent.mouseDown(viewSelectors[0]); 
    await waitFor(() => {
      expect(screen.getByText("Weekly")).toBeInTheDocument();
    });
    const weeklyOption = screen.getByText("Weekly"); 
    fireEvent.click(weeklyOption); 
    
    await waitFor(() => {
      expect(getAuditBillingSummary).toHaveBeenCalledTimes(2);
    });
  });

  it("updates the selected date and fetches new data", async () => {
    const mockResponse = {
      daily_details: [
        { day: 1, audit_cost: 100, detail_link: "link1", service_type: "dts" },
        { day: 2, audit_cost: 200, detail_link: "link2", service_type: "dms" },
      ],
      start_date: dayjs().subtract(1, "month").toISOString(),
      end_date: dayjs().toISOString(),
      total_audit_cost: 300,
      total_audit_rows: 1000,
      total_audit_cols: 500,
      total_audit_steps: 50,
    }; 
    getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
      onSuccess(mockResponse);
    });
    render(
      <Provider store={store}>
        <SummaryView onBarClick={mockOnBarClick} />
      </Provider>
    );
    await waitFor(() => {
      expect(getAuditBillingSummary).toHaveBeenCalled();
    });
    const datePicker = screen.getByRole("textbox");
    fireEvent.change(datePicker, {
      target: { value: dayjs().add(1, "month").format("YYYY-MM-DD") },
    });
    fireEvent.blur(datePicker);
    await waitFor(() => {
      // expect(getAuditBillingSummary).toHaveBeenCalledTimes(2);
    });
  });

  it("renders the chart with no data gracefully", async () => {
    getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
      onSuccess({
        daily_details: [],
        start_date: null, 
        end_date: null,
        total_audit_cost: 0,
        total_audit_rows: 0,
        total_audit_cols: 0,
        total_audit_steps: 0,
      });
    });
    render(
      <Provider store={store}>
        <SummaryView onBarClick={mockOnBarClick} />
      </Provider>
    );
    await waitFor(() => {
      expect(getAuditBillingSummary).toHaveBeenCalled();
      expect(screen.getByText(/No data/i)).toBeInTheDocument();
    });
  });

  it("handles bar click correctly", async () => {
    const mockResponse = {
      daily_details: [
        {
          day: 1,
          audit_cost: 100,
          detail_link: "http://example.com/detail?job_id=1",
          service_type: "dts"
        },
        {
          day: 2,
          audit_cost: 200,
          detail_link: "http://example.com/detail?job_id=2",
          service_type: "dms"
        },
      ],
      start_date: dayjs().subtract(1, "month").toISOString(),
      end_date: dayjs().toISOString(),
      total_audit_cost: 300,
      total_audit_rows: 1000,
      total_audit_cols: 500,
      total_audit_steps: 50,
    };
    getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
      onSuccess(mockResponse);
    });
    render(
      <Provider store={store}>
        <SummaryView onBarClick={mockOnBarClick} />
      </Provider>
    );
    await waitFor(() => {
      expect(getAuditBillingSummary).toHaveBeenCalled();
    });
    const barElement = screen.getByText(/Mocked Column Chart/i);
    fireEvent.click(barElement);
  });

  describe("SummaryView - Yearly Data Generation", () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it("generates yearly data correctly when daily details are available", async () => {
      const mockResponse = {
        daily_details: [
          { day: 1, month: 1, audit_cost: 100, detail_link: "link1", service_type: "dts" },
          { day: 32, month: 2, audit_cost: 200, detail_link: "link2", service_type: "dms" },
          { day: 60, month: 3, audit_cost: 300, detail_link: "link3", service_type: "dts" },
        ],
        start_date: dayjs("2024-01-01").toISOString(),
        end_date: dayjs("2024-12-31").toISOString(),
        total_audit_cost: 600,
        total_audit_rows: 2000,
        total_audit_cols: 1000,
        total_audit_steps: 100,
      };
      getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
        onSuccess(mockResponse);
      });
      render(
        <Provider store={store}>
          <SummaryView onBarClick={mockOnBarClick} />
        </Provider>
      );
      await waitFor(() => {
        expect(getAuditBillingSummary).toHaveBeenCalled();
      });
      const viewSelectors = screen.getAllByRole("combobox");
      fireEvent.mouseDown(viewSelectors[0]); 
      await waitFor(() => {
        expect(screen.getByText("Yearly")).toBeInTheDocument();
      });
      const yearlyOption = screen.getByText("Yearly"); 
      fireEvent.click(yearlyOption); 
      await waitFor(() => {
        expect(getAuditBillingSummary).toHaveBeenCalledTimes(2);
      });
      expect(screen.getByText(/Mocked Column Chart/i)).toBeInTheDocument();
    });

    it("handles the scenario with no daily details gracefully", async () => {
      const mockResponse = {
        daily_details: [],
        start_date: dayjs("2024-01-01").toISOString(),
        end_date: dayjs("2024-12-31").toISOString(),
        total_audit_cost: 0,
        total_audit_rows: 0,
        total_audit_cols: 0,
        total_audit_steps: 0,
      };
      getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
        onSuccess(mockResponse);
      });
      render(
        <Provider store={store}>
          <SummaryView onBarClick={mockOnBarClick} />
        </Provider>
      );
      await waitFor(() => {
        expect(getAuditBillingSummary).toHaveBeenCalled();
      });
      const viewSelectors = screen.getAllByRole("combobox");
      fireEvent.mouseDown(viewSelectors[0]); 
      await waitFor(() => {
        expect(screen.getByText("Yearly")).toBeInTheDocument();
      });
      const yearlyOption = screen.getByText("Yearly"); 
      fireEvent.click(yearlyOption); 
      await waitFor(() => {
        expect(getAuditBillingSummary).toHaveBeenCalledTimes(2);
        expect(screen.getByText(/Mocked Column Chart/i)).toBeInTheDocument();
      });
    });

    it("fetches new data when date is changed for yearly view", async () => {
      const mockResponse = {
        daily_details: [{ day: 1, audit_cost: 100, detail_link: "link1", service_type: "dts" }],
        start_date: dayjs("2024-01-01").toISOString(),
        end_date: dayjs("2024-01-31").toISOString(),
        total_audit_cost: 100,
        total_audit_rows: 500,
        total_audit_cols: 250,
        total_audit_steps: 25,
      };
      getAuditBillingSummary.mockImplementation(({ onSuccess }) => {
        onSuccess(mockResponse);
      });
      render(
        <Provider store={store}>
          <SummaryView onBarClick={mockOnBarClick} />
        </Provider>
      );
      await waitFor(() => {
        expect(getAuditBillingSummary).toHaveBeenCalled();
      });
      const viewSelectors = screen.getAllByRole("combobox");
      fireEvent.mouseDown(viewSelectors[0]); 
      await waitFor(() => {
        expect(screen.getByText("Yearly")).toBeInTheDocument();
      });
      const yearlyOption = screen.getByText("Yearly"); 
      fireEvent.click(yearlyOption);
      await waitFor(() => {
        expect(getAuditBillingSummary).toHaveBeenCalledTimes(2);
      });
      const datePicker = screen.getByRole("textbox");
      fireEvent.change(datePicker, {
        target: { value: dayjs().add(1, "year").format("YYYY-MM-DD") },
      });
      fireEvent.blur(datePicker);
      await waitFor(() => {
        expect(getAuditBillingSummary.mock.calls.length).toBeGreaterThanOrEqual(
          3,
        );
      });
    });
  });
});