import {
  Button,
  Tooltip,
  Table,
  message,
  Skeleton,
  Space,
  DatePicker,
  Switch,
  Input,
  Select,
} from "antd";
import {
  CaretRightOutlined,
  DeleteOutlined,
  SearchOutlined,
  InfoCircleOutlined,
  EllipsisOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import { useEffect, useState, useRef, useCallback } from "react";
import {
  deleteSchedule,
  getIndividualDag,
  getListTags,
  pauseDag,
  runDag,
} from "../../../apis/jobScheduleService";
import { getLocalStorageItem } from "../../../utils/userData";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { useDispatch, useSelector } from "react-redux";
import {
  dateFormat,
  scheduleFilters,
  TOOLTIPS_INFO,
  userTimezone,
} from "../../app-header/components/job-schedule/constants";
import dayjs from "dayjs";
import {
  setDagInfo,
  setDagsListAction,
  setIndividualJob,
  setJobListDetails,
  setJobModal,
  setJobReadMode,
} from "../../../store/actions/jobScheduleActions";
import { ADModal } from "../../../components/ADModal";
import CustomMessage from "../../settings-module/CustomMessage";
import { dispatchMessage } from "../../../utils/handleClick";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import { setSelectedServiceType } from "../../../store/actions/dmsAction";
dayjs.extend(utc);
dayjs.extend(timezone);

const { RangePicker } = DatePicker;
const { Option } = Select;

function JobScheduleList({
  loading,
  paginationData,
  fetchDagList,
  onFilterChange = () => {},
}) {
  const [pauseAPIs, setPauseAPIs] = useState([]);
  const [dataSource, setDataSource] = useState([]);
  const [messageApi, contextHolder] = message.useMessage();
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [filterDateRange, setFilterDateRange] = useState([]);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteDagIds, setDeleteDagIds] = useState([]);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const dispatch = useDispatch();
  const [searchFilters, setSearchFilters] = useState({});
  const filterInputRefs = useRef({});
  const [currentTime, setCurrentTime] = useState(dayjs());
  const [triggerEnabledMap, setTriggerEnabledMap] = useState(new Map());
  const [dagSearchFilters, setDagSearchFilters] = useState({
    schedule_names: [],
    job_names: [],
    service_types: [],
  });
  const [allDags, setAllDags] = useState([]);
  const dagList = useSelector((state) => state.jobSchedule.dagList);
  const messageData = useSelector((store) => store?.settings?.messageData);
  const hideMessage = useSelector((store) => store?.settings?.hideMessage);
  const currentPageInfo = useSelector(
    (state) => state.jobSchedule?.currentPageInfo
  );
  const pageSizeInfo = useSelector((state) => state.jobSchedule?.pageSizeInfo);
  const { user } = getLocalStorageItem() || {};

  useEffect(() => {
    if (dagList.length > 0) {
      setAllDags((prevAllDags) => {
        const newDagsMap = new Map(prevAllDags.map((dag) => [dag.dag_id, dag]));
        dagList.forEach((dag) => newDagsMap.set(dag.dag_id, dag));
        return Array.from(newDagsMap.values());
      });
    }
  }, [dagList]);

  const fetchDagSearchFilters = useCallback(() => {
    getListTags({
      userId: user.id,
      onSuccess: (res) => {
        if (res.success && res.dag_search_filters) {
          setDagSearchFilters({
            schedule_names: res.dag_search_filters.schedule_names || [],
            job_names: res.dag_search_filters.job_names || [],
            service_types: (res.dag_search_filters.service_types || []).map(
              (type) => type?.toUpperCase(),
            ),
          });
        }
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
      },
    });
  }, [user.id, dispatch]);

  const isTriggerTime = useCallback(
    (startsOn, checkTime = currentTime) => {
      if (!startsOn) return false;
      const startTime = dayjs(startsOn);
      return (
        checkTime.isSame(startTime, "second") || checkTime.isAfter(startTime)
      );
    },
    [currentTime]
  );

  const updateTriggerEnabledStates = useCallback(() => {
    const now = dayjs();
    const newMap = new Map();
    dagList.forEach((dag) => {
      newMap.set(dag.dag_id, isTriggerTime(dag.starts_on, now));
    });
    setTriggerEnabledMap(newMap);
    setCurrentTime(now);
  }, [dagList, isTriggerTime]);

  useEffect(() => {
    updateTriggerEnabledStates();
    let intervalId;
    let timeoutId;
    const calculateNextCheck = () => {
      const now = dayjs();
      const upcomingStarts = dagList
        .map((dag) => ({
          startsOn: dag.starts_on,
          dagId: dag.dag_id,
        }))
        .filter((item) => item.startsOn && dayjs(item.startsOn).isAfter(now))
        .sort((a, b) => new Date(a.startsOn) - new Date(b.startsOn));
      if (upcomingStarts.length > 0) {
        const nextTrigger = dayjs(upcomingStarts[0].startsOn);
        const msUntilNext = nextTrigger.diff(now);
        if (msUntilNext <= 2 * 60 * 1000) {
          return 1000;
        } else if (msUntilNext <= 10 * 60 * 1000) {
          return 5000;
        } else if (msUntilNext <= 30 * 60 * 1000) {
          return 30000;
        } else {
          return 60000;
        }
      }
      return 30000;
    };

    const scheduleNextUpdate = () => {
      const now = dayjs();
      const upcomingStarts = dagList
        .map((dag) => dag.starts_on)
        .filter((startsOn) => startsOn && dayjs(startsOn).isAfter(now))
        .sort((a, b) => new Date(a) - new Date(b));
      if (upcomingStarts.length > 0) {
        const nextTrigger = dayjs(upcomingStarts[0]);
        const msUntilNext = nextTrigger.diff(now);
        if (msUntilNext <= 5000 && msUntilNext > 0) {
          timeoutId = setTimeout(() => {
            updateTriggerEnabledStates();
            scheduleNextUpdate();
          }, msUntilNext + 10);
          return;
        }
      }
      const intervalMs = calculateNextCheck();
      intervalId = setInterval(() => {
        updateTriggerEnabledStates();
      }, intervalMs);
    };

    const startUpdates = () => {
      if (intervalId) clearInterval(intervalId);
      if (timeoutId) clearTimeout(timeoutId);
      scheduleNextUpdate();
    };
    startUpdates();
    const restartUpdates = () => {
      startUpdates();
    };
    return () => {
      if (intervalId) clearInterval(intervalId);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [dagList, updateTriggerEnabledStates]);

  useEffect(() => {
    updateTriggerEnabledStates();
  }, [dagList, updateTriggerEnabledStates]);

  useEffect(() => {
    fetchDagSearchFilters();
  }, [fetchDagSearchFilters]);

  useEffect(() => {
    const now = dayjs();
    const hasUpcomingTriggers = dagList.some((dag) => {
      if (!dag.starts_on) return false;
      const startTime = dayjs(dag.starts_on);
      const timeDiff = startTime.diff(now, "second");
      return timeDiff > 0 && timeDiff <= 120;
    });
    if (hasUpcomingTriggers) {
      const secondInterval = setInterval(() => {
        updateTriggerEnabledStates();
      }, 1000);
      return () => clearInterval(secondInterval);
    }
  }, [dagList, updateTriggerEnabledStates]);

  useEffect(() => {
    const data = dagList.map((dag, i) => ({
      key: dag?.dag_id,
      serialNum: i + 1,
      job_id: dag?.dag_id,
      job_name: dag?.job_name,
      schedule: dag?.timetable_description,
      nextrun: dag?.next_dagrun,
      schedule_name: dag?.schedule_name,
      is_paused: dag?.is_paused,
      starts_on: dag?.starts_on,
      data_source_usage: dag?.files_list || [],
      job_arguments: dag?.configuration
        ? JSON?.stringify(dag?.configuration, null, 2)
        : "",
      service_type: dag?.service_type?.toUpperCase() || "",
    }));
    setDataSource(data);
  }, [dagList]);

  // get clicked dag info from the list
  const handleIndividualDag = (record) => {
    const selectedDag = dagList?.find((dag) => dag?.dag_id === record?.job_id);

    getIndividualDag({
      dagId: record.job_id,
      current: currentPageInfo,
      pageSize: pageSizeInfo,
      onSuccess: (response) => {
        dispatch(setIndividualJob(true));
        dispatch(setDagInfo(response));
        dispatch(setJobListDetails(selectedDag));
        dispatch(setJobReadMode(true));
        dispatch(setSelectedServiceType(selectedDag?.service_type))
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        console.log(error, "error");
      },
    });
  };

  const handleDelete = (schedule_ids) => {
    setDeleteLoading(true);
    deleteSchedule({
      payload: { schedule_ids },
      onSuccess: (res) => {
        if (res?.success?.length > 0) {
          const updatedDags = dagList.filter(
            (eachDag) => !res.success.includes(eachDag.dag_id)
          );
          dispatch(setDagsListAction(updatedDags));
          setAllDags((prevAllDags) =>
            prevAllDags?.filter((dag) => !res.success.includes(dag.dag_id))
          );
          res.success.forEach((id) => {
            dispatchMessage(
              dispatch,
              "success",
              `DAG ${id} deleted successfully`
            );
          });
          fetchDagList(true, {});
        }
        if (res?.errors?.length > 0) {
          res.errors.forEach((err) => {
            messageApi.open({
              type: "error",
              content: err || "Failed to delete",
            });
          });
        }
        setOpenDeleteModal(false);
        setSelectedRowKeys([]);
        setDeleteDagIds([]);
        setDeleteLoading(false);
        setTimeout(() => {
          updateTriggerEnabledStates();
        }, 100);
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        dispatchMessage(dispatch, "error", error.message || "Failed to delete");
        setDeleteLoading(false);
      },
    });
  };

  const handleRunDag = (record) => {
    runDag({
      payload: {
        dag_id: record?.job_id,
      },
      onSuccess: (res) => {
        if (res.success) {
          dispatchMessage(dispatch, "success", res.message);
        } else {
          dispatchMessage(dispatch, "error", res.message);
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        dispatchMessage(dispatch, "error", error.message);
      },
    });
  };

  const handlePause = (record, value) => {
    setPauseAPIs((prev) => [...prev, record.job_id]);
    pauseDag({
      dagId: record?.job_id,
      payload: {
        is_paused: !value,
      },
      onSuccess: (res) => {
        setPauseAPIs((prev) => prev.filter((id) => id !== record.job_id));
        if (res.success) {
          const updatedDags = dagList.map((eachDag) => {
            if (eachDag.dag_id === record.job_id) {
              return {
                ...eachDag,
                is_paused: !value,
              };
            }
            return eachDag;
          });
          dispatch(setDagsListAction(updatedDags));
          setAllDags((prevAllDags) =>
            prevAllDags?.map((dag) =>
              dag.dag_id === record.job_id ? { ...dag, is_paused: !value } : dag
            )
          );
          dispatchMessage(dispatch, "success", res.message);
        } else {
          dispatchMessage(dispatch, "error", res.message);
        }
      },
      onError: (error) => {
        setPauseAPIs((prev) => prev.filter((id) => id !== record.job_id));
        handleSessionExpiry(dispatch, error);
        messageApi.open({
          type: "error",
          content: error.message,
        });
      },
    });
  };

  const getColumnDropdownProps = (dataIndex, options) => {
    const displayOptions = options?.map((option) =>
      option === null ? "None" : option
    );
    return {
      filterDropdown: ({
        setSelectedKeys,
        selectedKeys,
        confirm,
        clearFilters,
      }) => {
        const displaySelectedKeys = (selectedKeys || [])?.map((key) =>
          key === null ? "None" : key
        );

        return (
          <div style={{ padding: 8, width: 250 }} className="schedule-filter">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <Select
                mode="multiple"
                showSearch
                allowClear
                virtual={false}
                placeholder={`Select ${dataIndex.replace("_", " ")}`}
                value={displaySelectedKeys}
                onChange={(displayValues) => {
                  const actualValues = (displayValues || [])?.map((value) =>
                    value === "None" ? null : value
                  );
                  setSelectedKeys(actualValues);
                }}
                style={{ flex: 1, fontSize: "10px" }}
                size="small"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
                maxTagCount="responsive"
              >
                {displayOptions?.map((displayOption, index) => (
                  <Option
                    key={displayOption}
                    value={displayOption === "None" ? "None" : displayOption}
                  >
                    {displayOption}
                  </Option>
                ))}
              </Select>
              <Space>
                <Tooltip title="Search" overlayClassName="custom-tooltip">
                  <Button
                    type="primary"
                    onClick={() => {
                      confirm();
                      handleSearch(dataIndex, selectedKeys);
                    }}
                    icon={<SearchOutlined />}
                    size="small"
                  />
                </Tooltip>
                <Tooltip title="Reset" overlayClassName="custom-tooltip">
                  <Button
                    onClick={() => {
                      clearFilters();
                      handleReset(dataIndex);
                    }}
                    icon={<CloseOutlined />}
                    size="small"
                  />
                </Tooltip>
              </Space>
            </div>
          </div>
        );
      },
      filterIcon: (filtered) => (
        <SearchOutlined
          style={{
            color: filtered ? "#152A4F" : undefined,
          }}
          data-testid={`${dataIndex}-filter-icon`}
        />
      ),
      filteredValue: searchFilters[dataIndex] ? searchFilters[dataIndex] : null,
      onFilterDropdownOpenChange: (open) => {
        if (open) {
          setTimeout(() => {
            const dropdown = filterInputRefs.current[dataIndex];
            if (dropdown) {
              dropdown.focus();
            }
          }, 100);
        }
      },
    };
  };
  const handleSearch = (field, values) => {
    const newFilters = { ...searchFilters };
    if (values && values.length > 0) {
      newFilters[field] = values;
    } else {
      delete newFilters[field];
    }

    setSearchFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = (field = null) => {
    if (field) {
      const newFilters = { ...searchFilters };
      delete newFilters[field];

      setSearchFilters(newFilters);
      onFilterChange(newFilters);
    } else {
      setSearchFilters({});
      onFilterChange({});
    }
  };

  const handleRefresh = () => {
    handleReset();
    setFilterDateRange([]);
    setSelectedRowKeys([]);
    setAllDags([]);
    fetchDagList(true, {});
    fetchDagSearchFilters();
    updateTriggerEnabledStates();
  };

  const getScheduleNamesByJobIds = (jobIds) => {
    const filteredJobs = allDags.filter((job) => jobIds.includes(job.dag_id));
    const scheduleNames = filteredJobs.map((job) => job.schedule_name);
    return scheduleNames;
  };

  const columns = [
    {
      title: () => (
        <Tooltip title="Pause/Resume" overlayClassName="custom-tooltip">
          <InfoCircleOutlined style={{ cursor: "pointer" }} />
        </Tooltip>
      ),
      dataIndex: "job_id",
      width: 80,
      ellipsis: true,
      render: (_, record) => {
        return (
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Tooltip
              title={record?.is_paused ? "Paused" : "Resumed"}
              overlayClassName="custom-tooltip"
            >
              <Switch
                size="small"
                loading={pauseAPIs.includes(record.job_id)}
                checked={!record.is_paused}
                onClick={(_, e) => e.stopPropagation()}
                onChange={(value, e) => {
                  e.stopPropagation();
                  handlePause(record, value);
                }}
                data-testid={`pause-btn-id_${record?.job_id}`}
              />
            </Tooltip>
            <Tooltip
              title={`Dag Id : ${record.job_id}`}
              overlayClassName="custom-tooltip"
            >
              <InfoCircleOutlined style={{ fontSize: "10px" }} />
            </Tooltip>
          </div>
        );
      },
    },

    {
      title: <span>Service Type</span>,
      dataIndex: "service_type",
      width: 100,
      ellipsis: {
        showTitle: false,
      },
      ...getColumnDropdownProps("service_type", dagSearchFilters.service_types),
      onFilter: (values, record) => {
        if (!values || values.length === 0) return true;
        return values.includes(record?.service_type);
      },
      render: (text) => (
        <Tooltip
          title={text}
          placement="topLeft"
          overlayClassName="custom-tooltip"
        >
          <span style={{ fontWeight: 500 }}>{text}</span>
        </Tooltip>
      ),
    },

    {
      title: <span>Schedule Name</span>,
      dataIndex: "schedule_name",
      ellipsis: {
        showTitle: false,
      },
      ...getColumnDropdownProps(
        "schedule_name",
        dagSearchFilters.schedule_names
      ),
      onFilter: (values, record) => {
        if (!values || values.length === 0) return true;
        return values.includes(record.schedule_name);
      },
      render: (text) => (
        <Tooltip
          title={text}
          placement="topLeft"
          overlayClassName="custom-tooltip"
        >
          {text}
        </Tooltip>
      ),
    },
    {
      title: <span>Job Name</span>,
      dataIndex: "job_name",
      ellipsis: {
        showTitle: false,
      },
      ...getColumnDropdownProps("job_name", dagSearchFilters.job_names),
      onFilter: (values, record) => {
        if (!values || values.length === 0) return true;
        return values.includes(record.job_name);
      },
      render: (text) => (
        <Tooltip
          title={text}
          placement="topLeft"
          overlayClassName="custom-tooltip"
        >
          {text}
        </Tooltip>
      ),
    },
    {
      title: "Schedule",
      dataIndex: "schedule",
      onFilter: (value, record) => record.schedule.indexOf(value) === 0,
    },
    {
      title: "Next Run",
      dataIndex: "nextrun",
      render: (text, record) => {
        const selectedDag = dagList?.find(
          (dag) => dag?.dag_id === record?.job_id
        );

        const formattedDate = text
          ? `${dayjs(text)
              .tz(userTimezone)
              .format(dateFormat)} (${userTimezone})`
          : null;
        const format_nextrundate = (value) =>
          value ? `${dayjs(value).tz(userTimezone).format(dateFormat)}` : "—";

        const tooltipContent = (
          <div style={{ fontSize: 10, lineHeight: 1.4 }}>
            <div>
              Data processing from :{" "}
              {format_nextrundate(selectedDag?.next_dagrun_data_interval_start)}
            </div>
            <div>
              Data processing to :{" "}
              {format_nextrundate(selectedDag?.next_dagrun_data_interval_end)}
            </div>
            <div>
              Upcoming run will start after :{" "}
              {format_nextrundate(selectedDag?.next_dagrun_create_after)}
            </div>
          </div>
        );
        return (
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {formattedDate}
            <Tooltip title={tooltipContent} overlayClassName="custom-tooltip">
              <InfoCircleOutlined style={{ fontSize: 10, cursor: "pointer" }} />
            </Tooltip>
          </div>
        );
      },
    },

    {
      title: "Actions",
      render: (record) => {
        const selectedDag = dagList?.find(
          (dag) => dag?.dag_id === record?.job_id
        );
        const isTriggerEnabled = triggerEnabledMap.get(record.job_id) || false;
        const startsOn = dagList.find(
          (dag) => dag.dag_id === record.job_id
        )?.starts_on;

        return (
          <>
            <Tooltip
              title={
                isTriggerEnabled
                  ? "Trigger"
                  : `Available at ${dayjs(startsOn).format(
                      "YYYY-MM-DD HH:mm:ss"
                    )}`
              }
              overlayClassName="custom-tooltip"
            >
              <Button
                type="text"
                icon={<CaretRightOutlined style={{ fontSize: "12px" }} />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleRunDag(record);
                }}
                disabled={!isTriggerEnabled}
                data-testid={`trigger-btn-id_${record?.job_id}`}
              />
            </Tooltip>
            <Tooltip title="Delete" overlayClassName="custom-tooltip">
              <Button
                type="text"
                icon={<DeleteOutlined style={{ fontSize: "12px" }} />}
                onClick={(e) => {
                  e.stopPropagation();
                  setDeleteDagIds([record?.job_id]);
                  setOpenDeleteModal(true);
                }}
                data-testid={`delete-btn-id_${record?.job_id}`}
              />
            </Tooltip>
            <Tooltip overlayClassName="custom-tooltip" title={"Show more"}>
              <Button
                type="text"
                icon={<EllipsisOutlined style={{ fontSize: "12px" }} />}
                onClick={(e) => {
                  e.stopPropagation();
                  dispatch(setJobModal(true));
                  dispatch(setJobReadMode(true));
                  dispatch(setSelectedServiceType(selectedDag?.service_type))
                  if (selectedDag) {
                    dispatch(setJobListDetails(selectedDag));
                  }
                }}
              />
            </Tooltip>
          </>
        );
      },
    },
  ];

  const onSelectChange = (newSelectedRowKeys) => {
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    columnWidth: 50,
    preserveSelectedRowKeys: true,
    getCheckboxProps: (record) => ({
      checked: selectedRowKeys.includes(record.key),
    }),
  };

  const getDataSource = () => {
    if (filterDateRange.length === 2) {
      const filterData = dataSource.filter((eachData) => {
        var date = new Date(eachData.nextrun);
        return (
          date >= new Date(filterDateRange[0]) &&
          date <= new Date(filterDateRange[1])
        );
      });
      return filterData;
    }
    return dataSource;
  };

  const scheduleNames = getScheduleNamesByJobIds(deleteDagIds);

  return (
    <>
      {contextHolder}
      {messageData && !hideMessage && (
        <div style={{ margin: "15px" }}>
          <CustomMessage
            type={messageData.type}
            message={messageData.message}
          />
        </div>
      )}
      <div className="job-schedule-list">
        <div className="alert-dags">
          <Space className="info-container ">
            <InfoCircleOutlined />
            Latest schedules will be available shortly
          </Space>

          <Space>
            {selectedRowKeys?.length > 0 && (
              <Button
                type="primary"
                data-testid="multi-file-delete-btn"
                onClick={() => {
                  setOpenDeleteModal(true);
                  setDeleteDagIds(selectedRowKeys);
                }}
              >{`Delete ${selectedRowKeys.length} schedule${
                selectedRowKeys.length > 1 ? "s" : ""
              }`}</Button>
            )}
            <Button
              data-testid="refresh"
              loading={loading}
              onClick={handleRefresh}
            >
              Refresh
            </Button>
          </Space>
        </div>
        {loading ? (
          <>
            <Skeleton
              className="w-100"
              size="large"
              data-testid="loading-spinner-id"
              active
            />
          </>
        ) : (
          <>
            <Table
              className="schedule-jobs individual-jobs"
              columns={columns}
              dataSource={getDataSource()}
              virtual={false}
              scroll={{
                x: 400,
                y: 360,
              }}
              size="small"
              pagination={paginationData}
              showSorterTooltip={false}
              onRow={(record) => {
                return {
                  onClick: () => handleIndividualDag(record),
                };
              }}
              rowSelection={rowSelection}
              rowClassName="cursor-pointer"
            />
          </>
        )}
      </div>
      <ADModal
        title={`Delete schedule${deleteDagIds.length > 1 ? "s" : ""}`}
        description={
          <>
            Are you sure you want to delete the following schedule
            {deleteDagIds.length > 1 ? "s" : ""}:
            <div>
              {scheduleNames.map((name, index) => (
                <div key={index} style={{ padding: "2px 0" }}>
                  {index + 1}. {name}
                </div>
              ))}
            </div>
          </>
        }
        open={openDeleteModal}
        onOk={() => handleDelete(deleteDagIds)}
        onCancel={() => {
          setDeleteDagIds([]);
          setOpenDeleteModal(false);
        }}
        okText="Delete"
        cancelText="Cancel"
        showCancelButton={true}
        hideButtons={false}
        loading={deleteLoading}
      />
    </>
  );
}

export default JobScheduleList;
