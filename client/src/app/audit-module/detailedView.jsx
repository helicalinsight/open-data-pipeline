import React, { useState, useEffect } from "react";
import { Table, Space, Tooltip, DatePicker } from "antd";
import "./style.scss";
import { CloseOutlined } from "@ant-design/icons";
import { useSelector, useDispatch } from "react-redux";
import { getDetailData } from "../../apis/auditService";
import { setDetailDataAction } from "../../store/actions/auditAction";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

// Load plugins
dayjs.extend(utc);
dayjs.extend(timezone);
const { RangePicker } = DatePicker;

const DetailedView = ({ onBack }) => {
  const dispatch = useDispatch();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [dateRange, setDateRange] = useState([null, null]);
  const detailData = useSelector((state) => state.audit.detailData);
  const dateRanges = useSelector((state) => state.audit.dateRange);
  useEffect(() => {
    setDateRange([dayjs(dateRanges.startTime), dayjs(dateRanges.endTime)]);
  }, []);

  const columns = [
    {
      title: "Chat Id ",
      dataIndex: "Chat_id",
      key: "Chat_id",
    },
    {
      title: "Run Id",
      dataIndex: "Run_id",
      key: "Run_id",
    },
    {
      title: "Schedule Id",
      dataIndex: "Schedule_id",
      key: "Schedule_id",
    },
    {
      title: "Start Time",
      dataIndex: "run_start_time",
      key: "run_start_time",
    },
    {
      title: "End Time",
      dataIndex: "run_end_time",
      key: "run_end_time",
    },
    {
      title: "Execution Mode",
      dataIndex: "mode",
      key: "mode",
    },

    {
      title: "Total Columns",
      dataIndex: "Total_cols",
      key: "Total_cols",
      render: (text) => new Intl.NumberFormat().format(text),
    },
    {
      title: "Total Rows",
      dataIndex: "Total_rows",
      key: "Total_rows",
      render: (text) => new Intl.NumberFormat().format(text),
    },
    {
      title: "Total Steps",
      dataIndex: "Total_steps",
      key: "Total_steps",
      render: (text) => new Intl.NumberFormat().format(text),
    },
    {
      title: "Total Run Cost",
      dataIndex: "Total_run_cost",
      key: "Total_run_cost",
      render: (text) => new Intl.NumberFormat().format(text),
    },
  ];
  const transformedData = detailData.Audits.map((item) => ({
    Chat_id: item.Chat_id || "-",
    Run_id: item.Run_id || "-",
    Schedule_id: item.Schedule_id || "-",
    mode: item.mode,
    Total_cols: item.Total_cols,
    Total_rows: item.Total_rows,
    Total_steps: item.Total_steps,
    Total_run_cost: item.Total_run_cost,
    run_start_time: item.run_start_time
      ? dayjs(item.run_start_time)
          .tz("Asia/Calcutta")
          .format("DD/MM/YYYY hh:mm A") + " (Asia/Calcutta)"
      : "-",
    run_end_time: item.run_end_time
      ? dayjs(item.run_end_time)
          .tz("Asia/Calcutta")
          .format("DD/MM/YYYY hh:mm A") + " (Asia/Calcutta)"
      : "-",
  }));
  console.log(dayjs().tz("Asia/Kolkata").format("DD/MM/YYYY hh:mm A"));
  const handlePaginationChange = (page, pageSize) => {
    setCurrentPage(page);
    setPageSize(pageSize);
  };

  const handleDateChange = async (dates) => {
    setDateRange(dates);
    if (dates && dates[0] && dates[1]) {
      const startDate = dates[0].format("YYYY-MM-DDT00:00");
      const endDate = dates[1].format("YYYY-MM-DDT23:59");
      await getDetailData({
        detailLink: `/audit/billing/explore?start_time=${startDate}&end_time=${endDate}`,
        onSuccess: (data) => {
          dispatch(setDetailDataAction(data));
        },
        onError: (error) => {
          console.error("Error fetching detail data:", error);
        },
      });
    }
  };
  const totalRunCost = detailData.Audits.reduce(
    (acc, audit) => acc + audit.Total_run_cost,
    0
  );
  const formattedTotalRunCost = new Intl.NumberFormat().format(totalRunCost);
  return (
    <div className="order-details-container">
      <div className="filter-actions">
        <div className="content">
          <RangePicker
            value={dateRange}
            onChange={handleDateChange}
            style={{ marginLeft: 8 }}
            placeholder={["Start date", "End date"]}
          />
        </div>
      </div>
      <Table
        className="audit-table individual-jobs"
        columns={columns}
        dataSource={transformedData}
        scroll={{
          x: 400,
          y: 300,
        }}
        size="small"
        pagination={{
          current: currentPage,
          pageSize: pageSize,
          showSizeChanger: true,
          pageSizeOptions: ["10", "20", "50", "100"],
          onChange: handlePaginationChange,
          style: { marginRight: "10px" },
          showTitle: false,
        }}
        footer={() => (
          <div className="pagination-cost-container">
            <span>Total of Run Cost: {formattedTotalRunCost}</span>
          </div>
        )}
      />
    </div>
  );
};
export default DetailedView;
