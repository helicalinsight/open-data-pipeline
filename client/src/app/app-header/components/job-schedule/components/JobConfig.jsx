import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { InfoCircleOutlined } from "@ant-design/icons";
import { Space, Button, Tooltip } from "antd";
import {
  addScheduleConfig,
  delteScheduleConfig,
  updateScheduleConfig,
  addScheduleConfigBulk,
  addJobConfig,
  deleteJobConfig,
  updateJobConfig,
} from "../../../../../store/actions/chatAction";
import {
  addDmsScheduleConfig,
  deleteDmsScheduleConfig,
  updateDmsScheduleConfig,
  addDmsScheduleConfigBulk,
} from "../../../../../store/actions/dmsAction";
import JobInfoDrawer from "./JobInfoDrawer";
import KeyValueForm from "../../key-value/KeyValueForm";
import KeyValueTable from "../../key-value/KeyValueTable";
import { TOOLTIPS_INFO } from "../constants";
import EditorDrawer from "./EditorDrawer";
import {
  setChildDrawer,
  setJobListDetails,
  updateJobListDetails,
} from "../../../../../store/actions/jobScheduleActions";
import { dispatchMessage } from "../../../../../utils/handleClick";
import { setHideMessageAction } from "../../../../../store/actions/settingActions";
import { isDmsRoute } from "../../../../../router/uiRouteConstants";
import { useLocation } from "react-router-dom";

const JobConfig = ({ setCurrent }) => {
  const [openInfo, setOpenInfo] = useState(false);
  const location = useLocation();
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const selectedDmsChat = useSelector((state) => state.dms?.selectedDmsChat);
  const dispatch = useDispatch();
  const isDms = isDmsRoute(location.pathname);
  const scheduleConfig =
    useSelector(
      (state) => state?.chat?.chatList[selectedChat?.chat_id]?.scheduleConfig
    ) ?? [];
  const dmsScheduleConfig =
    useSelector(
      (state) => state?.dms?.dmsJobs[selectedDmsChat?.chat_id]?.dmsScheduleConfig
    ) ?? [];
  const activeConfig = isDms ? dmsScheduleConfig : scheduleConfig;
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );

  const filteredScheduleConfig = Object?.values(
    activeConfig?.reduce((acc, item) => {
      if (!acc[item?.configKey]) {
        acc[item?.configKey] = item;
      }
      return acc;
    }, {})
  );
  const onDelete = (record) => {
    const chatId = isDms ? selectedDmsChat.chat_id : selectedChat.chat_id;
    const payload = {
      chat_id: chatId,
      key: record.key,
    };
    if (isDms) {
      dispatch(deleteDmsScheduleConfig(payload));
    } else {
      dispatch(delteScheduleConfig(payload));
    }
  };

  const onAdd = (data, type = "single", resetForm) => {
    if (isScheduleEditMode) {
      dispatch(setHideMessageAction(true));
      delete data?.key;
    }
    const duplicate = jobListDetails?.job_details?.configuration.find(
      (config) => config.configKey === data.configKey
    );
    if (duplicate) {
      dispatchMessage(
        dispatch,
        "warning",
        `${duplicate.configKey} already exits`
      );
      return;
    }
    const chatId = isDms ? selectedDmsChat.chat_id : selectedChat.chat_id;
    const payload = isScheduleEditMode
      ? {
          data,
          type: "new",
        }
      : { chat_id: chatId, data };
    if (isScheduleEditMode) {
      if (type === "bulk") {
        onEdit(data);
      } else {
        dispatch(setJobListDetails(payload));
      }
      if (resetForm) resetForm();
    }
    if (Array.isArray(data)) {
      if (isDms) {
        dispatch(addDmsScheduleConfigBulk(payload));
      } else {
        dispatch(addScheduleConfigBulk(payload));
      }
    } else if (typeof data === "object" && data !== null) {
      if (isDms) {
        dispatch(addDmsScheduleConfig(payload));
      } else {
        dispatch(addScheduleConfig(payload));
      }
    }
  };

  const onEdit = (data) => {
    const chatId = isDms ? selectedDmsChat.chat_id : selectedChat.chat_id;
    const payload = isScheduleEditMode
      ? { job_id: jobListDetails.job_id, data }
      : { chat_id: chatId, data };
    if (isDms) {
      dispatch(
        isScheduleEditMode
          ? updateJobListDetails(payload)
          : updateDmsScheduleConfig(payload)
      );
    } else {
      dispatch(
        isScheduleEditMode
          ? updateJobListDetails(payload)
          : updateScheduleConfig(payload)
      );
    }
  };
  const handleOpenDrawer = () => {
    dispatch(setChildDrawer(true));
  };
const text = isDmsRoute(location.pathname)
  ? selectedDmsChat?.chat_name
  : isScheduleEditMode
  ? jobListDetails?.job_name
  : selectedChat?.chat_name;
  return (
    <>
      <div className="h-100">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            width: "100%",
          }}
        >
          <div className="job-heading dFlex justifyBetween">
            <div>
              <span>Job Name - </span>
              <span>
                <Tooltip title={text}>
                  {text?.length > 10 ? text.slice(0, 10) + "..." : text}
                </Tooltip>
              </span>
            </div>
          </div>
          <div
            className="dFlex justifyBetween alignCenter"
            style={{ marginLeft: "auto" }}
          >
            {!isScheduleEditMode && !isDms && (
              <Space>
                <span className="job-heading ">Config</span>
                <InfoCircleOutlined
                  onClick={() => setOpenInfo(true)}
                  data-testid="show-info-icon"
                />
              </Space>
            )}
          </div>
        </div>
        <KeyValueForm
          keyValueData={activeConfig}
          onAdd={onAdd}
          handleOpenDrawer={handleOpenDrawer}
          isMode={true}
        />
        <EditorDrawer
          keyValueData={activeConfig}
          onAdd={onAdd}
          handleClose={() => {
            dispatch(setChildDrawer(false));
          }}
          title=" Job Config Editor"
          mode="job_arguments"
          isJobConfig={true}
        />
        <KeyValueTable
          dataSource={filteredScheduleConfig}
          onDelete={onDelete}
          onEdit={onEdit}
        />
        <Tooltip title={TOOLTIPS_INFO.nextButton} placement="topRight">
          <Button
            className="next-button"
            type="primary"
            onClick={() => setCurrent((prev) => prev + 1)}
            data-testid="next-button"
          >
            Next
          </Button>
        </Tooltip>
      </div>
      <JobInfoDrawer
        open={openInfo}
        setOpenInfo={setOpenInfo}
        mode="job_arguments"
      />
    </>
  );
};

export default JobConfig;
