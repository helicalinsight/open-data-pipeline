import React, { useState, useEffect } from "react";
import { Column } from "@ant-design/plots";
import { Card, Select, DatePicker, Tooltip } from "antd";
import dayjs from "dayjs";
import "./style.scss";
import { summaryTypeOptions, summaryTypeTooltips } from "../app-header/components/job-schedule/constants";
import { useDispatch } from "react-redux";
import { getAuditBillingSummary, getDetailData } from "../../apis/auditService";
import {
  setAuditBillingSummaryAction,
  setDateRange,
  setDetailDataAction,
} from "../../store/actions/auditAction";
import { metricConfig, totalMetricsOptions } from "../app-header/utils";
import { InfoCircleOutlined } from "@ant-design/icons";

const { Option } = Select;
const SERVICE_TYPES = ["dts", "dms"];
const isValidServiceType = (serviceType) => {
  return serviceType && SERVICE_TYPES.includes(serviceType.toLowerCase());
};
const SummaryView = ({ onBarClick }) => {
  const dispatch = useDispatch();
  const [view, setView] = useState("monthly");
  const [selectedMetric, setSelectedMetric] = useState("total_audit_cost");
  const [data, setData] = useState({
    daily_details: [],
    start_date: null,
    end_date: null,
    total_audit_cost: 0,
    total_audit_rows: 0,
    total_audit_cols: 0,
    total_audit_steps: 0,
  });
  const [selectedDate, setSelectedDate] = useState(dayjs());
  const [chartData, setChartData] = useState([]);
  const currentTooltip = summaryTypeTooltips[view];
  useEffect(() => {
    document.addEventListener("mouseover", (e) => {
      if (e.target?.title) e.target.removeAttribute("title");
    });
  }, []);
  const fetchData = async (summaryType, date) => {
    const formattedDate = date.format("YYYY-MM-DD");
    await getAuditBillingSummary({
      summary_type: summaryType,
      target_date: formattedDate,
      onSuccess: (response) => {
        dispatch(setAuditBillingSummaryAction(response));
        setData(response);
      },
      onError: (error) => {
        console.error(error);
      },
    });
  };

  useEffect(() => {
    const summaryType = view;
    fetchData(summaryType, selectedDate);
  }, [view, selectedDate]);

  const generateChartData = () => {
    if (!data.start_date || !data.end_date) return [];
    const startDate = dayjs(data.start_date);
    const endDate = dayjs(data.end_date);
    const detailKey = metricConfig[selectedMetric]?.detailKey || "audit_cost";
    const isYearly = view === "yearly";
    const aggregatedData = {};
    if (isYearly) {
      const startYear = startDate.year();
      const endYear = endDate.year();
      for (let month = 1; month <= 12; month++) {
        aggregatedData[month] = {
          dts: 0,
          dms: 0,
          detailLinks: {
            dts: "",
            dms: ""
          }
        };
      }
      data.daily_details.forEach((detail) => {
        const month = detail.month;
        const serviceType = (detail.service_type || "").toLowerCase();
        const value = detail[detailKey] || 0;
        const detailLink = detail.detail_link || "";
        if (month && isValidServiceType(serviceType)) {
          if (!aggregatedData[month]) {
            aggregatedData[month] = {
              dts: 0,
              dms: 0,
              detailLinks: {
                dts: "",
                dms: ""
              }
            };
          }
          aggregatedData[month][serviceType] += value;
          if (detailLink && !aggregatedData[month].detailLinks[serviceType]) {
            aggregatedData[month].detailLinks[serviceType] = detailLink;
          }
        }
      });
    } else {
      const daysInRange = endDate.diff(startDate, "day") + 1;     
      for (let i = 0; i < daysInRange; i++) {
        const currentDate = startDate.add(i, "day");
        const dayOfMonth = currentDate.date();
        aggregatedData[dayOfMonth] = {
          dts: 0,
          dms: 0,
          detailLinks: {
            dts: "",
            dms: ""
          }
        };
      }
      data.daily_details.forEach((detail) => {
        const day = detail.day;
        const serviceType = (detail.service_type || "").toLowerCase();
        const value = detail[detailKey] || 0;
        const detailLink = detail.detail_link || "";
        if (day && isValidServiceType(serviceType)) {
          if (!aggregatedData[day]) {
            aggregatedData[day] = {
              dts: 0,
              dms: 0,
              detailLinks: {
                dts: "",
                dms: ""
              }
            };
          }
          aggregatedData[day][serviceType] += value;   
          if (detailLink && !aggregatedData[day].detailLinks[serviceType]) {
            aggregatedData[day].detailLinks[serviceType] = detailLink;
          }
        }
      });
    }
    const result = [];
    const periods = Object.keys(aggregatedData)
      .map(Number)
      .sort((a, b) => a - b);
    periods.forEach(period => {
      const periodData = aggregatedData[period];
      SERVICE_TYPES.forEach(serviceType => {
        result.push({
          [isYearly ? "month" : "date"]: period,
          usage: periodData[serviceType] || 0,
          category: serviceType.toUpperCase(),
          detailLink: periodData.detailLinks[serviceType] || "",
          serviceType: serviceType
        });
      });
    });
    return result;
  };

  useEffect(() => {
    const chartData = generateChartData();
    setChartData(chartData);    
    if (view === "yearly") {
      const monthlyTotals = {};
      chartData.forEach(item => {
        const month = item.month;
        if (!monthlyTotals[month]) {
          const initialTotals = {};
          SERVICE_TYPES.forEach(type => {
            initialTotals[type] = 0;
          });
          monthlyTotals[month] = initialTotals;
        }
        monthlyTotals[month][item.serviceType] = item.usage;
      });
    }
  }, [data, view, selectedMetric]);

  const handleBarClick = async (ev) => {
    const data = ev?.data?.data;
    if (!data) return console.error("Invalid event data:", ev);
    const { detailLink, usage, date, month, category } = data;
    if (!detailLink) {
      const metricName = metricConfig[selectedMetric]?.tooltipName || "Usage";
      const xLabel = view === "yearly" ? `Month ${month}` : `Day ${date}`;
      return console.error(
        `No detail link found for ${category} on ${xLabel} with ${metricName}: ${usage}`
      );
    }
    const [basePath, queryParams] = detailLink.split("?");
    const validParams = queryParams
      ? [...new URLSearchParams(queryParams)]
          .filter(([_, value]) => value !== "None")
          .map(([key, value]) => `${key}=${value}`)
          .join("&")
      : "";

    const finalUrl = validParams ? `${basePath}?${validParams}` : `${basePath}`;
    const urlParams = new URLSearchParams(finalUrl.split("?")[1]);
    const start_time = urlParams.get("start_time");
    const end_time = urlParams.get("end_time");
    const startDate = start_time?.slice(0, 10);
    const endDate = end_time?.slice(0, 10);
    await getDetailData({
      detailLink: finalUrl,
      onSuccess: (detailData) => {
        dispatch(setDetailDataAction(detailData));
        if (startDate && endDate) {
          dispatch(setDateRange(startDate, endDate));
        }
      },
      onError: (error) => {
        console.error("Error fetching detail data:", error);
      },
    });
    onBarClick();
  };

  const config = {
    data: chartData,
    xField: view === "yearly" ? "month" : "date",
    yField: "usage",
    colorField: "category",
    stack: true,
    scale: {
      color: {
        range: ["#F28E1E", "#152A4F"], 
      },
    },
    legend: {
      position: "top-left",
    },
    style: {
      cursor: "pointer",
    },
    responsive: true,
    tooltip: {
      shared: true,
      showMarkers: false,
      items: [
        (datum) => {
          const metricName = metricConfig[selectedMetric]?.tooltipName || "Usage";
          const xLabel = view === "yearly" 
            ? `Month ${datum.month}` 
            : `Day ${datum.date}`;
          return {
            name: `${datum.category} - ${metricName} (${xLabel})`,
            value: datum.usage,
          };
        },
      ],
    },
    onReady: ({ chart }) => {
      chart.on("element:click", handleBarClick);
    },
    interactions: [{ type: "element-active" }],
    height: 420,
  };

  return (
    <div>
      <div className="select-container">
        <Select
          defaultValue="monthly"
          className="select-view"
          onChange={(value) => setView(value)}
        >
          {summaryTypeOptions.map((option) => (
            <Option key={option.value} value={option.value}>
              {option.label}
            </Option>
          ))}
        </Select>
        <Select
          value={selectedMetric}
          style={{ width: "170px" }}
          onChange={(value) => {
            setSelectedMetric(value);
          }}
        >
          {totalMetricsOptions?.map((option) => (
            <Option key={option.value} value={option.value}>
              {option.label}
            </Option>
          ))}
        </Select>
        <div>
          <Tooltip title={currentTooltip} overlayClassName="custom-tooltip" placement="left">
            <InfoCircleOutlined
              style={{ fontSize: 10, cursor: "pointer", marginRight: "10px" }}
            />
          </Tooltip>
          <DatePicker
            defaultValue={selectedDate}
            onChange={(date) => setSelectedDate(date)}
            className="date-picker"
          />
        </div>
      </div>

      {data?.daily_details?.length === 0 && !data.start_date ? (
        <div className="items-center">No data</div>
      ) : (
        <div className="chart-container">
          <Column {...config} />
        </div>
      )}
    </div>
  );
};
export default SummaryView;