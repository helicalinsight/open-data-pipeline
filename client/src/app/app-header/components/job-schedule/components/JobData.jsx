import { useEffect, useState, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry";
import { ArrowLeftOutlined, InfoCircleOutlined } from "@ant-design/icons";
import {
  destinationOptions,
  engineType,
  executionTypeOpt,
  initialFormValue,
  TOOLTIPS_INFO,
  engineTypeInfo,
  chooseExportType,
} from "../constants";
import { getOptions } from "../../../../database-module/components/utils";
import {
  fecthDbsAndTables,
  getSavedConnections,
} from "../../../../../apis/databaseService";
import {
  Select,
  Form,
  Space,
  TreeSelect,
  Button,
  Input,
  Switch,
  Tooltip,
  Skeleton,
} from "antd";
import {
  disableNodesBasedOnAlias,
  toApiCase,
  toDisplayCase,
} from "../../../utils";
import LogViewerDrawer from "../../../../job-schedule-module/components/LogViewerDrawer";
import { setHideMessageAction } from "../../../../../store/actions/settingActions";
import { setLogModal } from "../../../../../store/actions/jobScheduleActions";
import { dagRunStatus } from "../../../../../apis/jobScheduleService";
import { useLocation } from "react-router-dom";
import { isDmsRoute } from "../../../../../router/uiRouteConstants";

const InfoTooltip = ({ title, style = {} }) => {
  const defaultStyle = {
    marginLeft: 5,
    fontSize: 11,
    cursor: "pointer",
    ...style,
  };

  return (
    <Tooltip title={title} overlayClassName="custom-tooltip">
      <InfoCircleOutlined style={defaultStyle} />
    </Tooltip>
  );
};

function JobData(props) {
  const {
    jobDataForm,
    handleScheduleJob,
    setCurrent,
    setJobData,
    loading,
    setLoading,
    setOpenDbDrawer,
    dataSource,
    setOpenJobModal,
  } = props;
  const dispatch = useDispatch();
  const location = useLocation();
  const [formData, setFormData] = useState(initialFormValue);
  const [notification, setNotification] = useState(false);
  const [treeLoadedKeys, setTreeLoadedKeys] = useState([]);
  const [catalogList, setCatalogList] = useState([]);
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const chatId = selectedChat?.chat_id;
  const { loadedFiles } =
    useSelector((state) => state.chat?.chatList[chatId]) ?? {};
  const [treeData, setTreeData] = useState([]);
  const yamlSave = useSelector((state) => state.chat.yamlSave);
  const [isTextWrapped, setIsTextWrapped] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const logViewerRef = useRef(null);
  const jobMode = useSelector((state) => state.chat.jobMode);
  const [searchValue, setSearchValue] = useState("");
  const [currentEngineType, setCurrentEngineType] = useState("spark");
  const [exportFileType, setExportFileType] = useState("csv");
  const [currentEngineTypeLabel, setCurrentEngineTypeLabel] = useState("Spark");
  const [isEditExecutionType, setIseditExecutionType] = useState("pipeline");
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const isDms = isDmsRoute(location.pathname)
  const serviceTypes = useSelector((state) => state.dms.selectedServiceType);
  const pollRef = useRef(null);
  const [localFormValues, setLocalFormValues] = useState({
    schedule_name: "",
    files: [],
    destination: "localstorage",
    database: "",
    catalog: "",
    engineType: "spark",
    exportFile: "csv",
    isEditExecutiontype: "pipeline",
  });
  const [currentDestination, setCurrentDestination] = useState("localstorage");

  useEffect(() => {
    const savedFormValues = JSON.parse(
      localStorage.getItem("jobFormValues") || "{}"
    );
    if (Object.keys(savedFormValues).length > 0) {
      const updatedValues = {
        ...localFormValues,
        ...savedFormValues,
        engineType: savedFormValues.engineType || "spark",
        exportFile: savedFormValues.exportFile || "csv",
        isEditExecutiontype: savedFormValues.isEditExecutiontype || "pipeline",
        destination: savedFormValues.destination || "localstorage",
      };
      setLocalFormValues(updatedValues);
      setCurrentDestination(updatedValues.destination || "localstorage");
      if (savedFormValues.exportFile) {
        setExportFileType(savedFormValues.exportFile);
      }
      if (savedFormValues.engineType) {
        setCurrentEngineType(savedFormValues.engineType);
        const engineLabel = engineType?.find(
          (e) => e.value === savedFormValues.engineType
        )?.label;
        setCurrentEngineTypeLabel(engineLabel || "Spark");
      }
      if (savedFormValues.isEditExecutiontype) {
        setIseditExecutionType(savedFormValues.isEditExecutiontype);
      }
    } else {
      setExportFileType("csv");
      setCurrentDestination("localstorage");
    }
  }, []);

  useEffect(() => {
    if (isScheduleEditMode && jobListDetails) {
      const jobDetails = jobListDetails?.job_details;
      setNotification(jobDetails?.notification?.active || false);
      setCurrentEngineType(jobDetails?.engine_type || "spark");
      setIseditExecutionType(jobDetails?.execution_type || "pipeline");
      const editFormValues = {
        schedule_name: jobListDetails?.schedule_name || "",
        files: jobDetails?.export_files_list?.map((f) => f.alias) || [],
        destination: jobDetails?.destination?.[0]?.destination || "",
        database: jobDetails?.destination?.[0]?.connection_name || "",
        catalog: jobDetails?.destination?.[0]?.catalog || "",
        engineType: jobDetails?.engine_type || "spark",
        exportFile: jobDetails?.export_format || "csv",
        isEditExecutiontype: jobDetails?.execution_type || "pipeline",
      };
      setLocalFormValues(editFormValues);
      setCurrentDestination(editFormValues.destination || "");
      jobDataForm.setFieldsValue(editFormValues);
    } else {
      const formValues = {
        ...localFormValues,
        engineType: localFormValues.engineType || "spark",
        exportFile: localFormValues.exportFile || "csv",
        isEditExecutiontype: localFormValues.isEditExecutiontype || "pipeline",
        destination: localFormValues.destination || "localstorage",
      };
      setCurrentDestination(formValues.destination);
      jobDataForm.setFieldsValue(formValues);
    }
  }, [isScheduleEditMode, jobListDetails]);

  useEffect(() => {
    if (!isScheduleEditMode) {
      localStorage.setItem("jobFormValues", JSON.stringify(localFormValues));
    }
  }, [localFormValues, isScheduleEditMode]);

  useEffect(() => {
    const updatedOptions = [];
    jobDataForm.setFieldValue("database", "");
    const seenValues = new Set();
    dataSource?.forEach((ds) => {
      const displayAlias = toDisplayCase(ds.databaseAlias);
      const apiAlias = toApiCase(ds.databaseAlias);
      if (apiAlias === "flat_files" || seenValues.has(apiAlias)) return;
      seenValues.add(apiAlias);
      const alias = ds.mappedName ? toDisplayCase(ds.mappedName) : displayAlias;
      updatedOptions.push({
        id: alias,
        pId: 0,
        value: alias,
        title: alias,
        selectable: false,
        isLeaf: false,
      });
    });

    setTreeData(updatedOptions);
    setTreeLoadedKeys([]);
  }, [dataSource]);

  const onValuesChange = (changedValues, allValues) => {
    const updatedValues = {
      ...localFormValues,
      ...changedValues,
    };
    setLocalFormValues(updatedValues);
    if (changedValues.destination !== undefined) {
      setCurrentDestination(changedValues.destination);
    }
    if (changedValues.exportFile) {
      setExportFileType(changedValues.exportFile);
    }
    if (changedValues.engineType) {
      setCurrentEngineType(changedValues.engineType);
      const engineLabel = engineType?.find(
        (e) => e.value === changedValues.engineType
      )?.label;
      setCurrentEngineTypeLabel(engineLabel || "Spark");
    }
    if (changedValues.isEditExecutiontype) {
      setIseditExecutionType(changedValues.isEditExecutiontype);
    }
    if (
      changedValues.database &&
      localFormValues.database !== changedValues.database
    ) {
      setCatalogList([]);
    }
    if (
      changedValues.destination &&
      changedValues.destination !== "localstorage"
    ) {
      jobDataForm.setFieldValue("exportFile", undefined);
      setLocalFormValues((prev) => ({ ...prev, exportFile: undefined }));
    }
    if (
      changedValues.destination &&
      changedValues.destination === "localstorage"
    ) {
      jobDataForm.setFieldValue(
        "exportFile",
        localFormValues.exportFile || "csv"
      );
    }
  };
useEffect(() => {
  if (!isScheduleEditMode) {
    if (isDms) {
      jobDataForm.setFieldsValue({ engineType: "dlt" });
      setCurrentEngineType("dlt");
      setCurrentEngineTypeLabel("Dlt");
    } else {
      jobDataForm.setFieldsValue({ engineType: "spark" });
      setCurrentEngineType("spark");
      setCurrentEngineTypeLabel("Spark");
    }
  }
}, [isDms, isScheduleEditMode,jobDataForm]);
  const handleSchedule = async () => {
    dispatch(setHideMessageAction(true));
    try {
      await jobDataForm?.validateFields();
      const currentFormValues = jobDataForm?.getFieldsValue();
      const scheduleName = currentFormValues?.schedule_name || "";
      setLocalFormValues(currentFormValues);
      setCurrentDestination(currentFormValues.destination || "localstorage");
      let selectedFiles;
      if (isScheduleEditMode && jobListDetails?.job_details?.files_list) {
        const fileSource = jobListDetails?.job_details?.files_list;
        selectedFiles =
          currentFormValues?.files
            ?.map((alias) => fileSource?.find((file) => file?.alias === alias))
            .filter(Boolean) || [];
      } else {
        selectedFiles =
          loadedFiles?.filter((file) =>
            currentFormValues?.files?.includes(file?.source_id)
          ) || [];
      }
      const args = {
        setFormData,
        dispatch,
        mode: "skipAndRun",
        notification,
        isImmediateExecution: true,
        engineType: currentEngineType,
        exportFile: exportFileType,
        isEditExecutiontype: isEditExecutionType,
        files: selectedFiles,
        schedule_name: scheduleName,
        destination: currentFormValues?.destination,
        database: currentFormValues?.database,
        catalog: currentFormValues?.catalog,
        formValues: currentFormValues,
        pollRef
      };
      await handleScheduleJob(args);
      dispatch(setLogModal(true));
    } catch (e) {
      console.log(e);
    }
  };

  const handleFinish = async () => {
    const currentFormValues = jobDataForm?.getFieldsValue();
    setLocalFormValues(currentFormValues);
    setCurrentDestination(currentFormValues.destination || "localstorage");
    const {
      schedule_name,
      files: formFiles,
      destination,
      database,
      catalog,
      engineType,
      exportFile,
      isEditExecutiontype,
    } = currentFormValues;

    let selectedFiles;
    if (isScheduleEditMode && jobListDetails?.job_details?.files_list) {
      const fileSource = jobListDetails?.job_details?.files_list;
      selectedFiles =
        formFiles
          ?.map((alias) => fileSource?.find((file) => file?.alias === alias))
          .filter(Boolean) || [];
    } else {
      selectedFiles =
        loadedFiles?.filter((file) => formFiles?.includes(file?.source_id)) ||
        [];
    }

    const args = {
      setFormData,
      dispatch,
      mode: "skipAndRun",
      notification,
      isImmediateExecution: true,
      engineType: engineType || currentEngineType,
      exportFile: exportFile || exportFileType,
      isEditExecutiontype: isEditExecutiontype || isEditExecutionType,
      schedule_name: schedule_name,
      destination: destination,
      database: database,
      catalog: catalog,
      files: selectedFiles,
      formValues: currentFormValues,
    };
    await handleScheduleJob(args);
    dispatch(setLogModal(true));
  };
  const onNext = () => {
    jobDataForm
      .validateFields()
      .then(() => {
        const data = jobDataForm.getFieldsValue() || {};
        data.notification = notification;
        data.exportFile = exportFileType;
        data.engineType = currentEngineType;
        data.isEditExecutiontype = isEditExecutionType;
        setLocalFormValues(data);
        setCurrentDestination(data.destination || "localstorage");
        setJobData(data);
        setCurrent((prev) => prev + 1);
      })
      .catch((e) => console.log(e));
  };

  const layout = {
    labelCol: {
      span: 10,
    },
    wrapperCol: {
      span: 14,
    },
  };
  useEffect(() => {
    document.addEventListener("mouseover", (e) => {
      if (e.target?.title) e.target.removeAttribute("title");
    });
  }, []);

  const genTreeNode = (parentId, isLeaf = false, eachDb, selectable = true) => {
    return {
      id: eachDb._id,
      pId: parentId,
      value: eachDb._id,
      title: eachDb.alias,
      isLeaf,
      selectable,
    };
  };

  const onLoadData = ({ id }) => {
    return new Promise((resolve) => {
      getSavedConnections({
        query: toApiCase(id),
        onSuccess: (response) => {
          if (response?.databases) {
            const updatedDBs = response.databases.map((eachDb) =>
              genTreeNode(id, true, eachDb)
            );
            setTreeData((prev) => [...prev, ...updatedDBs]);
            setTreeLoadedKeys((prev) => [...prev, id]);
          }
          resolve();
        },
        onError: (error) => {
          handleSessionExpiry(dispatch, error);
          resolve();
        },
      });
    });
  };

  const getDatabase = (payload) => {
    fecthDbsAndTables({
      payload,
      onSuccess: (res) => {
        if (res.success) {
          setCatalogList(res?.dataCatalog);
        }
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  const finalCatalogList = disableNodesBasedOnAlias(catalogList);
  const filteredTreeData = treeData?.filter((node) =>
    node?.title?.toLowerCase()?.includes(searchValue?.toLowerCase())
  );

  useEffect(() => {
    if (isScheduleEditMode && jobListDetails) {
      const catalogValue = jobListDetails?.job_details?.destination[0]?.catalog;
      const splitCatalog = catalogValue?.split(".")?.pop();
      const editValues = {
        destination:
          jobListDetails?.job_details?.destination[0]?.destination || "",
        database:
          jobListDetails?.job_details?.destination[0]?.connection_name || "",
        catalog: splitCatalog || catalogValue || "",
      };
      setLocalFormValues((prev) => ({ ...prev, ...editValues }));
      setCurrentDestination(editValues.destination || "");
      jobDataForm.setFieldsValue(editValues);
    }
  }, [isScheduleEditMode, jobListDetails]);
  const handleLogDrawerClose = () => {
    if (!isScheduleEditMode) {
      jobDataForm.setFieldsValue(localFormValues);
      setCurrentDestination(localFormValues.destination || "localstorage");
    }
  };

  const selectedEngineType = jobDataForm.getFieldValue("engineType");
  const engineLabel = engineType?.find(
    (e) => e.value === selectedEngineType
  )?.label;

  const renderFormItems = () => {
    const isLocalStorageDestination = currentDestination === "localstorage";
    return (
      <>
        <Form
          {...layout}
          form={jobDataForm}
          requiredMark={false}
          onValuesChange={onValuesChange}
          onFinish={handleFinish}
          data-testid="job-data-form"
          layout="horizontal"
          labelAlign="left"
          preserve={true}
        >
          <Form.Item
            label={[
              " Notification",
              <InfoTooltip title={TOOLTIPS_INFO.notification} />,
            ]}
          >
            <Tooltip title={notification ? "Disable" : "Enable"}>
              <Switch
                checked={notification}
                onChange={(value) => setNotification(value)}
              />
            </Tooltip>
          </Form.Item>
          <Form.Item
            label={[
              "Engine Type",
              <InfoTooltip title={TOOLTIPS_INFO.engineTypeInfo} />,
            ]}
            name="engineType"
            key="engineType"
            initialValue="spark"
          >
            <Select
              className="select-dropdown"
              style={{ width: 120 }}
              showSearch
              virtual={false}
              options={engineType}
              value={localFormValues.engineType || "spark"}
              disabled={isDms || serviceTypes == "dms"}
              onChange={(value, option) => {
                setCurrentEngineType(value);
                setCurrentEngineTypeLabel(option.label);
                setLocalFormValues((prev) => ({ ...prev, engineType: value }));
              }}
            />
          </Form.Item>

          <Form.Item
            name="schedule_name"
            className="custom-form-item"
            label={[
              " Schedule Name",
              <InfoTooltip title={TOOLTIPS_INFO.scheduleName} />,
            ]}
          >
            <Input
              style={{ width: "100%" }}
              data-testid="scheduleName"
              placeholder="Schedule Name"
              maxLength={80}
              className="fieldval-font"
              value={localFormValues.schedule_name}
              onChange={(e) => {
                const value = e.target.value;
                jobDataForm.setFieldValue("schedule_name", value);
                setLocalFormValues((prev) => ({
                  ...prev,
                  schedule_name: value,
                }));
              }}
            />
          </Form.Item>
          {(jobMode !== "python" || yamlSave) && !isDms && serviceTypes !== "dms" && (
            <>
              <Form.Item
                name="files"
                className="custom-form-item"
                label={[
                  "Files to Export",
                  <InfoTooltip title={TOOLTIPS_INFO.filesToExport} />,
                ]}
              >
                <Select
                  showSearch
                  className="select-dropdown"
                  data-testid="select-files"
                  style={{ width: "100%" }}
                  placeholder="Select Files..."
                  mode="multiple"
                  allowClear
                  maxTagCount="responsive"
                  virtual={false}
                  options={getOptions(
                    isScheduleEditMode
                      ? jobListDetails?.job_details?.files_list
                      : loadedFiles,
                    "alias",
                    isScheduleEditMode ? "alias" : "source_id"
                  )}
                  filterOption={(input, option) =>
                    (option?.label ?? "")
                      .toLowerCase()
                      .includes(input.toLowerCase())
                  }
                  value={localFormValues.files}
                  onChange={(value) => {
                    setLocalFormValues((prev) => ({ ...prev, files: value }));
                  }}
                />
              </Form.Item>
              {isScheduleEditMode &&
                jobListDetails?.meta_schedule_version === 1 && (
                  <Form.Item
                    label={[
                      "Execution Type",
                      <InfoTooltip title={TOOLTIPS_INFO.executionTypeInfo} />,
                    ]}
                    name="isEditExecutiontype"
                    key="isEditExecutiontype"
                  >
                    <Select
                      className="select-dropdown"
                      style={{ width: 120 }}
                      showSearch
                      virtual={false}
                      options={executionTypeOpt}
                      value={localFormValues.isEditExecutiontype}
                      onChange={(value) => {
                        setIseditExecutionType(value);
                        setLocalFormValues((prev) => ({
                          ...prev,
                          isEditExecutiontype: value,
                        }));
                      }}
                    />
                  </Form.Item>
                )}
              <Form.Item
                className="custom-form-item"
                data-testid="select-destination"
                name="destination"
                label={[
                  "Destination",
                  <InfoTooltip title={TOOLTIPS_INFO.destination} />,
                ]}
              >
                <Select
                  className="select-dropdown"
                  style={{ width: "100%" }}
                  placeholder={"Select Destination..."}
                  onChange={(value) => {
                    setFormData({ ...formData, destination: value });
                    setCurrentDestination(value);
                    setLocalFormValues((prev) => ({
                      ...prev,
                      destination: value,
                    }));
                  }}
                  options={destinationOptions}
                  disabled={isScheduleEditMode}
                  value={localFormValues.destination || "localstorage"}
                />
              </Form.Item>
              {isLocalStorageDestination && !isScheduleEditMode && (
                <Form.Item
                  label={[
                    "Export File",
                    <InfoTooltip title={TOOLTIPS_INFO.exportFileInfo} />,
                  ]}
                  name="exportFile"
                  key="exportFile"
                >
                  <Select
                    className="select-dropdown"
                    style={{ width: 120 }}
                    showSearch
                    virtual={false}
                    options={chooseExportType}
                    value={localFormValues.exportFile || "csv"}
                    onChange={(value, option) => {
                      setExportFileType(value);
                      setLocalFormValues((prev) => ({
                        ...prev,
                        exportFile: value,
                      }));
                    }}
                  />
                </Form.Item>
              )}
              {currentDestination === "database" && (
                <>
                  <Form.Item
                    className="custom-form-item"
                    name="database"
                    label={[
                      "Database",
                      <InfoTooltip title={TOOLTIPS_INFO.database} />,
                    ]}
                    rules={
                      !isScheduleEditMode
                        ? [
                            {
                              required: true,
                              message: "Please select database",
                            },
                          ]
                        : []
                    }
                  >
                    <TreeSelect
                      allowClear
                      className="select-dropdown"
                      treeDataSimpleMode
                      treeLoadedKeys={treeLoadedKeys}
                      onTreeLoad={setTreeLoadedKeys}
                      loadData={onLoadData}
                      onChange={(value) => {
                        setCatalogList([]);
                        setLocalFormValues((prev) => ({
                          ...prev,
                          database: value,
                        }));
                        if (value) {
                          getDatabase({
                            source: "database",
                            connection_id: value,
                          });
                        }
                      }}
                      treeData={filteredTreeData}
                      placeholder="Please select"
                      virtual={false}
                      value={localFormValues.database}
                      dropdownStyle={{
                        maxHeight: 400,
                        minHeight: 200,
                        overflow: "auto",
                      }}
                      dropdownRender={(menu) => (
                        <>
                          <div style={{ padding: 6 }}>
                            <Input
                              allowClear
                              placeholder="Search database"
                              value={searchValue}
                              onChange={(e) => setSearchValue(e?.target?.value)}
                            />
                          </div>
                          {menu}
                        </>
                      )}
                      disabled={isScheduleEditMode}
                    />
                  </Form.Item>
                </>
              )}

              {jobDataForm.getFieldValue("database") &&
                currentDestination === "database" && (
                  <Form.Item
                    className="custom-form-item"
                    name="catalog"
                    label={[
                      "Catalog",
                      <InfoTooltip title={TOOLTIPS_INFO.catalog} />,
                    ]}
                    rules={[
                      {
                        required: true,
                        message: "Please select catalog",
                      },
                    ]}
                  >
                    {finalCatalogList?.length > 0 || isScheduleEditMode ? (
                      <TreeSelect
                        showSearch
                        allowClear
                        className="select-dropdown"
                        treeData={finalCatalogList}
                        placeholder="Select Catalog"
                        virtual={false}
                        style={{ width: "100%" }}
                        value={localFormValues.catalog}
                        onChange={(value) => {
                          setLocalFormValues((prev) => ({
                            ...prev,
                            catalog: value,
                          }));
                        }}
                        dropdownStyle={{
                          maxHeight: 400,
                          minHeight: 200,
                          overflow: "auto",
                        }}
                        disabled={isScheduleEditMode}
                      />
                    ) : (
                      <Skeleton.Button active={true} block={true} />
                    )}
                  </Form.Item>
                )}
            </>
          )}
        </Form>
      </>
    );
  };

  const renderButtons = () => {
    return (
      <Space className="next-button">
        <Tooltip title={TOOLTIPS_INFO.backButton}>
          <Button
            onClick={() => setCurrent((prev) => prev - 1)}
            data-testid="back-btn"
          >
            <ArrowLeftOutlined />
          </Button>
        </Tooltip>
        {!isScheduleEditMode && (
          <Tooltip title={TOOLTIPS_INFO.runNow}>
            <Button
              onClick={handleSchedule}
              className="run-btn "
              loading={loading}
              data-testid="run-now-button"
            >
              Run Now
            </Button>
          </Tooltip>
        )}
        <Tooltip title={TOOLTIPS_INFO.nextButton} placement="topRight">
          <Button
            type="primary"
            onClick={onNext}
            disabled={loading}
            data-testid="next-button"
          >
            Next
          </Button>
        </Tooltip>
      </Space>
    );
  };

  return (
    <>
    {!isDms && serviceTypes !== "dms" &&
      <div className="mode">
        <Space>
          <Tooltip
            overlayClassName="custom-tooltip"
            title={
              isScheduleEditMode
                ? TOOLTIPS_INFO.datasourceUsage
                : TOOLTIPS_INFO.updateConnections
            }
          >
            <Button
              onClick={() => setOpenDbDrawer(true)}
              data-testid="update-connections-btn"
              className="fields-font"
            >
              {isScheduleEditMode ? "Datasource Usage" : "Update Connections"}
            </Button>
          </Tooltip>
          {!isScheduleEditMode && (
            <Tooltip title={jobMode} overlayClassName="custom-tooltip">
              <InfoCircleOutlined
                style={{ marginRight: 25, fontSize: "14px", cursor: "pointer" }}
              />
            </Tooltip>
          )}
        </Space>
      </div>}
      {renderFormItems()}
      {renderButtons()}
      <LogViewerDrawer
        loading={loading}
        setLoading={setLoading}
        isTextWrapped={isTextWrapped}
        setIsTextWrapped={setIsTextWrapped}
        isFullScreen={isFullScreen}
        setIsFullScreen={setIsFullScreen}
        logViewerRef={logViewerRef}
        engineType={currentEngineTypeLabel}
        exportFileType={exportFileType}
        onClose={handleLogDrawerClose}
        pollRef={pollRef}
        isDms={isDms}
      />
    </>
  );
}

export default JobData;
