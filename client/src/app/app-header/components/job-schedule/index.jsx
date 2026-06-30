import { useEffect, useState } from "react";
import { Drawer, Form, Steps, message } from "antd";
import { triggerSchedule } from "./components/scheduleAPI";
import { useSelector, useDispatch } from "react-redux";
import { initialValues } from "./constants";
import { useSearchParams } from "react-router-dom";
import JobData from "./components/JobData";
import JobConfig from "./components/JobConfig";
import CustomScheduling from "./components/CustomScheduling";
import ConnectionMapping from "./components/ConnectionMapping";
import {
  setJobModal,
  setJobReadMode,
  setJobValue,
} from "../../../../store/actions/jobScheduleActions";
import { triggerGetDatasources } from "../../../../apis/commonAPIs";
import CustomMessage from "../../../settings-module/CustomMessage";
import { setHideMessageAction } from "../../../../store/actions/settingActions";
import { compareCaseInsensitive, toDisplayCase } from "../../utils";
import { useLocation } from "react-router-dom";
import { isDmsRoute } from "../../../../router/uiRouteConstants";
import { handleSessionExpiry } from "../../../../utils/handleSessionExpiry";
import { getProgressDms } from "../../../../apis/dmsService";
import { setDmsProgessDetailsAction } from "../../../../store/actions/dmsAction";

const contentStyle = {
  marginTop: "20px",
  fontSize: "10px",
};

const JobScheduleWrapper = ({ messageApi, openJobModal, setOpenJobModal }) => {
  const [jobDataForm] = Form.useForm();
  const [scheduleForm] = Form.useForm();
  const [jobData, setJobData] = useState();
  const [mappedData, setMappedData] = useState({});
  const [loading, setLoading] = useState();
  const [current, setCurrent] = useState(0);
  const [openDbDrawer, setOpenDbDrawer] = useState(false);
  const [dataSource, setDataSource] = useState([]);
  const [searchParams] = useSearchParams();
  const chatId = searchParams.get("chat");
  const dispatch = useDispatch();
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const { loadedFiles, scheduleConfig } =
    useSelector((state) => state.chat?.chatList[selectedChat?.chat_id]) ?? {};
  const pipelineHistory =
    useSelector((state) => state.chat.chatList[chatId]?.pipelineHistory) || {};
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const jobMode = useSelector((state) => state.chat.jobMode);
  const jobModal = useSelector((state) => state.jobSchedule?.jobModal);
  const messageData = useSelector((store) => store?.settings?.messageData);
  const datasources = useSelector((state) => state?.database?.datasources);
  const location = useLocation();
  const selectedDmsChat = useSelector((state) => state.dms?.selectedDmsChat);
   const dmsScheduleConfig =
    useSelector(
      (state) => state?.dms?.dmsJobs[selectedDmsChat?.chat_id]
    ) ?? [];
  const dmsProgressDetails = useSelector(
  (state) => state.dms?.dmsProgressDetails
);
  const isDms = isDmsRoute(location.pathname)

  useEffect(() => {
    if (isScheduleEditMode && jobListDetails?.service_type !== "dms")
      triggerGetDatasources(dispatch);
    const processHistoryData = () => {
      const result = [];
      const seenIds = new Set();
      pipelineHistory?.history?.forEach((eachHistory) => {
        if (
          !["read_files", "read_tables", "read"].includes(eachHistory?.function)
        )
          return;
        if (!eachHistory?.parameters?.length) return;

        eachHistory?.parameters?.forEach((param) => {
          if (!param?._id || seenIds.has(param._id)) return;
          seenIds?.add(param._id);
          const originalDBAlias = eachHistory?.database_alias;
          if (compareCaseInsensitive(originalDBAlias, "flat_files")) return;
          const matchingConnection = pipelineHistory.connections?.find(
            (conn) => conn?._id === param._id
          );
          const alias =
            matchingConnection?.alias !== "na"
              ? matchingConnection.alias
              : param.alias || param.catalog;
          const matchingDatasource = datasources?.find((ds) =>
            compareCaseInsensitive(ds.driver, originalDBAlias)
          );
          result.push({
            key: param._id,
            pipeline: eachHistory.function,
            databaseAlias: toDisplayCase(
              matchingDatasource?.name || originalDBAlias
            ),
            fileName: alias,
            id: param._id,
          });
        });
      });
      return result;
    };
    setDataSource(processHistoryData());
  }, [pipelineHistory?.history, pipelineHistory?.connections]);
  useEffect(() => {
    if (isDms) {
      fetchDmsProgressDetails();
    }
  }, [isDms, selectedDmsChat]);
  const fetchDmsProgressDetails = async () => {
    try {
      getProgressDms({
        chatId: selectedDmsChat.chat_id,
        onSuccess: (res) => {
          dispatch(setDmsProgessDetailsAction(res.data));
        },
        onError: (err) => {
          handleSessionExpiry(dispatch, err);
        },
      });
    } catch (err) {
      console.error(err);
    }
  };
  const onClose = (e) => {
    // e.stopPropagation()
    // setOpenJobModal(false);
    jobDataForm.resetFields();
    scheduleForm.setFieldsValue(initialValues);
    setMappedData({});
    dispatch(setHideMessageAction(false));
    dispatch(setJobReadMode(false));
    // setCurrent(0);
  };
  const onCloseLogs = (e) => {
    // e.stopPropagation()
    // setOpenJobModal(false);
    dispatch(setJobModal(false));
    dispatch(setJobReadMode(false));
    dispatch(setHideMessageAction(false));
    // jobDataForm.resetFields();
    // scheduleForm.setFieldsValue(initialValues);
    // setMappedData({});
    // setCurrent(0);
  };

  const handleScheduleJob = (params) => {
    const args = {
      ...params,
      jobDataForm,
      selectedChat,
      messageApi,
      loadedFiles,
      scheduleConfig,
      jobData,
      onClose,
      setLoading,
      executionType: jobMode === "python" ? "code" : "pipeline",
      mappedData,
      isScheduleEditMode,
      jobListDetails,
      isDms,
      selectedDmsChat,
      dmsProgressDetails,
      pollRef: params.pollRef,
      dmsScheduleConfig
    };
    triggerSchedule(args);
  };

  const steps = [
    {
      title: "Job Config",
      content: <JobConfig setCurrent={setCurrent} />,
    },
    {
      title: "Job Data",
      content: (
        <JobData
          setCurrent={setCurrent}
          handleScheduleJob={handleScheduleJob}
          jobDataForm={jobDataForm}
          setJobData={setJobData}
          loading={loading}
          setLoading={setLoading}
          setOpenDbDrawer={setOpenDbDrawer}
          setOpenJobModal={setOpenJobModal}
          dataSource={dataSource}
        />
      ),
    },
    {
      title: "Schedule",
      content: (
        <CustomScheduling
          setCurrent={setCurrent}
          handleScheduleJob={handleScheduleJob}
          scheduleForm={scheduleForm}
          setOpenJobModal={setOpenJobModal}
          loading={loading}
        />
      ),
    },
  ];

  const items = steps.map((item) => ({
    key: item.title,
    title: item.title,
  }));

  return (
    <>
      <Drawer
        title="Job Scheduling"
        onClose={(e) => onCloseLogs(e)}
        open={jobModal}
        width={550}
        data-testid="schedule-drawer"
        destroyOnClose={true}
      >
        {messageData && (
          <div style={{ marginBottom: "10px" }}>
            <CustomMessage
              type={messageData.type}
              message={messageData.message}
            />
          </div>
        )}
        <Steps
          className="job-steps"
          current={current}
          items={items}
          size="small"
        />
        <div style={contentStyle}>{steps[current].content}</div>
        <ConnectionMapping
          openDbDrawer={openDbDrawer}
          setOpenDbDrawer={setOpenDbDrawer}
          mappedData={mappedData}
          setMappedData={setMappedData}
          dataSource={dataSource}
          setDataSource={setDataSource}
        />
      </Drawer>
    </>
  );
};

export default JobScheduleWrapper;
