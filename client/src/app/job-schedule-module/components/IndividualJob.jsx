import { useEffect, useState, useRef } from "react";
import React from "react";
import { Drawer } from "antd";
import {
  Button,
  Tooltip,
  Space,
  DatePicker,
  Spin,
  Table,
  Checkbox,
} from "antd";
import {
  DownloadOutlined,
  EyeOutlined,
  SearchOutlined,
  InfoCircleOutlined,
  FilterFilled,
} from "@ant-design/icons";
import {
  dagRunStatus,
  downloadDagInfo,
  getDagLogs,
  getIndividualDag,
} from "../../../apis/jobScheduleService";
import ADSpace from "../../../components/ADSpace";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { useDispatch, useSelector } from "react-redux";
import {
  dagStateFilters,
  dateFormat,
  scheduleRunId,
  userTimezone,
} from "../../app-header/components/job-schedule/constants";
import dayjs from "dayjs";
import LogViewerDrawer from "./LogViewerDrawer";
import OverviewModule from "../../dms-module/OverView";
import {
  setCurrentPage,
  setDagInfo,
  setIndividualJob,
  setLogModal,
  setPageSize,
  setScheduleStatus,
} from "../../../store/actions/jobScheduleActions";
import { handleFileBlobDownload } from "../../message-module/utils/listFiles.utils";
const { RangePicker } = DatePicker;

function IndividualJob({ paginationInfoData }) {
  const [logs, setLogs] = useState("");
  const [loading, setLoading] = useState(true);
  const [dataSource, setDataSource] = useState([]);
  const [filterDateRange, setFilterDateRange] = useState([]);
  const [selectedStates, setSelectedStates] = useState([]);
  const [sortField, setSortField] = useState("");
  const [sortOrder, setSortOrder] = useState("");
  const [isFilterActive, setIsFilterActive] = useState(false);
  const [tempDateRange, setTempDateRange] = useState([]);
  const [tempSelectedStates, setTempSelectedStates] = useState([]);
  const [showOverview, setShowOverview] = useState(false);
  const savedScheduleConfig = JSON.parse(
    localStorage.getItem("schedule_configuration") || '{"state": {}}'
  );
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );
  const serviceTypes = useSelector((state) => state.dms.selectedServiceType);
  const dagInfo = useSelector((state) => state.jobSchedule?.dagInfo);
  const dispatch = useDispatch();
  // logvieweee
  const [isTextWrapped, setIsTextWrapped] = React.useState(false);
  const logViewerRef = React.useRef();
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [isFullScreen, setIsFullScreen] = React.useState(false);
  const changeSource = useRef(null);
  const [sortedInfo, setSortedInfo] = useState({
    columnKey: "",
    order: null,
  });
  const pollRef = useRef(null);
  useEffect(() => {
    const hasActiveFilters =
      filterDateRange?.length > 0 || selectedStates?.length > 0;
    setIsFilterActive(hasActiveFilters);
  }, [filterDateRange, selectedStates]);

  useEffect(() => {
    // setting the table datasource
    const data = dagInfo?.dag_runs?.dag_runs?.map((dag, i) => ({
      key: String(i + 1),
      dag_run_id: dag?.dag_run_id,
      execution_date: dag?.execution_date,
      state: dag?.state,
    }));
    setDataSource(data || []);
  }, [dagInfo?.dag_runs?.dag_runs]);

  const handlePaginationChange = (page, pageSize) => {
    changeSource.current = "pagination";
    dispatch(setCurrentPage(page));
    dispatch(setPageSize(pageSize));
    fetchDagData(
      page,
      pageSize,
      selectedStates,
      filterDateRange,
      sortField,
      sortOrder
    );
  };

  const fetchDagData = (
    page,
    pageSize,
    states,
    dateRange,
    sortField,
    sortOrder
  ) => {
    getIndividualDag({
      dagId: dagInfo?.basic_info?.dag_id,
      current: page,
      pageSize: pageSize,
      stateFilters: states,
      dateRange: dateRange,
      sortField: sortField,
      sortOrder: sortOrder,
      onSuccess: (response) => {
        dispatch(setDagInfo(response));
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        console.log(error, "error");
      },
    });
  };

  const updatedPaginationInfoData = {
    ...paginationInfoData,
    onChange: handlePaginationChange,
    onShowSizeChange: (current, newPageSize) => {
      handlePaginationChange(1, newPageSize);
    },
  };

  const getColumnSearchProps = (dataIndex) => ({
    filterDropdown: ({ confirm, clearFilters, setSelectedKeys }) => (
      <div
        style={{
          padding: 8,
        }}
      >
        <Space direction="vertical">
          <RangePicker
            showTime={{
              format: "HH:mm:ss",
            }}
            format="YYYY-MM-DD HH:mm:ss"
            value={
              tempDateRange.length === 2
                ? [
                    tempDateRange[0] ? dayjs(tempDateRange[0]) : null,
                    tempDateRange[1] ? dayjs(tempDateRange[1]) : null,
                  ]
                : []
            }
            onChange={(dates, dateStrings) => {
              setTempDateRange(dateStrings);
            }}
          />
          <Space>
            <Button
              type="primary"
              size="small"
              onClick={() => {
                if (tempDateRange.length === 2) {
                  setFilterDateRange(tempDateRange);
                  confirm();
                  fetchDagData(
                    paginationInfoData.current,
                    paginationInfoData.pageSize,
                    selectedStates,
                    tempDateRange,
                    sortField,
                    sortOrder
                  );
                }
              }}
              disabled={tempDateRange.length !== 2}
            >
              OK
            </Button>
            <Button
              size="small"
              onClick={() => {
                setTempDateRange([]);
                setFilterDateRange([]);
                clearFilters();
                confirm();
                fetchDagData(
                  paginationInfoData.current,
                  paginationInfoData.pageSize,
                  selectedStates,
                  [],
                  sortField,
                  sortOrder
                );
              }}
              disabled={tempDateRange.length === 0}
            >
              Reset
            </Button>
          </Space>
        </Space>
      </div>
    ),
    filterIcon: (filtered) => (
      <SearchOutlined
        style={{
          color:
            filtered || filterDateRange?.length > 0 ? "#152A4F" : undefined,
          padding: "0 5px",
        }}
      />
    ),
    onFilterDropdownOpenChange: (visible) => {
      if (visible) {
        setTempDateRange(filterDateRange);
      }
    },
    render: (text) => text,
  });

  const getStateFilterProps = () => ({
    filterDropdown: ({ confirm, clearFilters }) => (
      <div
        style={{
          padding: 8,
        }}
        className="schedule-state "
      >
        <Space direction="vertical">
          {Object?.entries(savedScheduleConfig?.state)?.map(([key, value]) => (
            <Checkbox
              key={key}
              checked={tempSelectedStates?.includes(key)}
              onChange={(e) => {
                const newSelectedStates = e?.target?.checked
                  ? [...tempSelectedStates, key]
                  : tempSelectedStates?.filter((state) => state !== key);
                setTempSelectedStates(newSelectedStates);
              }}
            >
              {value}
            </Checkbox>
          ))}
          <Space>
            <Button
              type="primary"
              size="small"
              onClick={() => {
                setSelectedStates(tempSelectedStates);
                confirm();
                fetchDagData(
                  paginationInfoData.current,
                  paginationInfoData.pageSize,
                  tempSelectedStates,
                  filterDateRange,
                  sortField,
                  sortOrder
                );
              }}
              disabled={tempSelectedStates?.length === 0}
            >
              OK
            </Button>
            <Button
              size="small"
              onClick={() => {
                setTempSelectedStates([]);
                setSelectedStates([]);
                clearFilters();
                confirm();
                fetchDagData(
                  paginationInfoData.current,
                  paginationInfoData.pageSize,
                  [],
                  filterDateRange,
                  sortField,
                  sortOrder
                );
              }}
              disabled={tempSelectedStates?.length === 0}
            >
              Reset
            </Button>
          </Space>
        </Space>
      </div>
    ),
    filterIcon: (filtered) => (
      <FilterFilled
        style={{
          color: filtered || selectedStates.length > 0 ? "#152A4F" : undefined,
        }}
      />
    ),
    onFilterDropdownOpenChange: (visible) => {
      if (visible) {
        setTempSelectedStates(selectedStates);
      } else {
        setTempSelectedStates([]);
      }
    },
  });

  // table headers for dag info list
  const columns = [
    {
      title: (
        <span>
          Schedule run id
          <Tooltip title={scheduleRunId} overlayClassName="custom-tooltip">
            <InfoCircleOutlined
              style={{ fontSize: "10px", marginLeft: "5px" }}
            />
          </Tooltip>
        </span>
      ),
      dataIndex: "dag_run_id",
      key: "dag_run_id",
    },
    {
      title: "Execution date",
      dataIndex: "execution_date",
      key: "execution_date",
      sorter: true,
      sortOrder:
        sortedInfo.columnKey === "execution_date" ? sortedInfo.order : null,

      ...getColumnSearchProps("execution_date"),
      render: (text) => {
        if (text) {
          return `${dayjs(text)
            .tz(userTimezone)
            .format(dateFormat)} (${userTimezone})`;
        }
        return null;
      },
    },
    {
      title: "State",
      dataIndex: "state",
      key: "state",
      ...getStateFilterProps(),
      render: (state) => savedScheduleConfig?.state?.[state] || state,
    },
    {
      title: "Logs",
      dataIndex: "logs",
      render: (a, record) => {
        return (
          <>
            <Tooltip title="View Logs">
              <Button
                type="text"
                onClick={() => {
                  getLogs(record);
                  dispatch(setLogModal(true));
                }}
                data-testid="view_logs_id"
                icon={<EyeOutlined />}
                size="middle"
              />
            </Tooltip>
            {record?.state === "success" && dagInfo?.basic_info?.local && serviceTypes !=="dms" && (
              <Tooltip title="Download Data">
                <Button
                  type="text"
                  onClick={() => downloadDagData(record)}
                  icon={<DownloadOutlined />}
                  size="middle"
                  data-testid="download_logs_id"
                />
              </Tooltip>
            )}
          </>
        );
      },
    },
  ];

  const handleTableChange = (pagination, filters, sorter) => {
    if (changeSource.current === "pagination") {
      changeSource.current = null;
      return;
    }
    changeSource.current = null;
    let newSortField = "";
    let newSortOrder = "";
    if (sorter.field && sorter.order) {
      newSortField = sorter.field;
      newSortOrder = sorter.order === "ascend" ? "asc" : "desc";
    }
    setSortField(newSortField);
    setSortOrder(newSortOrder);
    setSortedInfo({
      columnKey: sorter.field,
      order: sorter.order,
    });
    fetchDagData(
      paginationInfoData.current,
      paginationInfoData.pageSize,
      selectedStates,
      filterDateRange,
      newSortField,
      newSortOrder
    );
  };
  // onclick handler for download button
  const downloadDagData = (record) => {
    const payload = {
      job_id: dagInfo?.basic_info?.dag_id,
      dag_run_id: record?.dag_run_id,
    };
    downloadDagInfo({
      payload,
      onSuccess: (blobData, contentType) => {
        try {
          handleFileBlobDownload({
            blobData,
            contentType,
            fallbackFileName: dagInfo?.basic_info?.job_name || "dag_data",
            supportedTypes: ["xlsx", "csv", "json"],
          });
        } catch (error) {
          console.error("Error handling file download:", error);
          handleFileBlobDownload({
            blobData,
            fallbackFileName: dagInfo?.basic_info?.job_name || "dag_data",
            supportedTypes: ["xlsx", "csv", "json"],
          });
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        console.log(error, "log error");
      },
    });
  };

  //on Click handler for getting the logs
  const getLogs = (record) => {
    setLoading(true);
    const payload = {
      job_id: dagInfo?.basic_info?.dag_id,
      dag_run_id: record.dag_run_id,
      engine_type: jobListDetails?.job_details?.engine_type || "spark",
    };
    if (pollRef.current) {
      clearInterval(pollRef.current);
    }
     pollRef.current = setInterval(() => {
      dagRunStatus({
        payload: {
          dag_id: dagInfo?.basic_info?.dag_id,
          dag_run_id: record.dag_run_id,
        },
        onSuccess: (res) => {
          if (res.success) {
            dispatch(setScheduleStatus(res.state));
            if (res.state === "success" || res.state === "failed") {
              clearInterval(pollRef.current);
            }
          }
        },
        onError: (err) => {
          clearInterval(pollRef.current);
          handleSessionExpiry(dispatch, err);
        },
      });
    }, 1000);
    getDagLogs({
      payload,
      onSuccess: (response) => {
        setLogs(response);
        setLoading(false);
      },
      onError: (error) => {
        setLoading(false);
        handleSessionExpiry(dispatch, error);
        console.log(error, "log error");
      },
    });
  };

  // calling logs api after clicking refresh button
  const refreshLogs = () => {
    dispatch(setCurrentPage(1));
    dispatch(setPageSize(10));
    setSelectedStates([]);
    setFilterDateRange([]);
    setSortField("");
    setSortOrder("");
    setSortedInfo({
      columnKey: "",
      order: null,
    });
    fetchDagData(1, 10, [], [], "", "");
  };

  return (
    <>
      <div className="individual-job">
        <ADSpace justifyContent="space-between" alignItem="center">
          <h4 className="dag-name">{dagInfo?.basic_info?.job_name}</h4>
          <div style={{ display: "flex", gap: "8px" }}>
            {serviceTypes === "dms" && (
              <Button onClick={() => setShowOverview(true)}>
                DMS Overview
              </Button>
            )}
            <Button onClick={refreshLogs} data-testid="dag_refresh_btn">
              Refresh
            </Button>
          </div>
        </ADSpace>
        <Table
          data-testid="individual-job-pagination"
          className="schedule-jobs individual-jobs"
          columns={columns}
          dataSource={dataSource}
          size="small"
          virtual={false}
          pagination={updatedPaginationInfoData}
          onChange={handleTableChange}
          scroll={{
            x: 400,
            y: 360,
          }}
        />
        <Drawer
          title="DMS Overview"
          placement="right"
          width={"80%"}
          onClose={() => setShowOverview(false)}
          open={showOverview}
          destroyOnClose
        >
          <OverviewModule />
        </Drawer>
      </div>
      <LogViewerDrawer
        loading={loading}
        logs={logs}
        isTextWrapped={isTextWrapped}
        setIsTextWrapped={setIsTextWrapped}
        isFullScreen={isFullScreen}
        setIsFullScreen={setIsFullScreen}
        logViewerRef={logViewerRef}
        getLogs={getLogs}
        loadingLogs={loadingLogs}
        dagInfo={dagInfo}
        individualJob="true"
        pollRef={pollRef}
      />
    </>
  );
}

export default IndividualJob;
