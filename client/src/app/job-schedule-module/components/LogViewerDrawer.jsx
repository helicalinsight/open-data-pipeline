import { useState, useEffect } from "react";
import { Drawer, Button, Tooltip, message, Tag } from "antd";
import {
  VerticalAlignBottomOutlined,
  ExpandOutlined,
  CopyOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { LogViewer, LogViewerSearch } from "@patternfly/react-log-viewer";
import "@patternfly/react-core/dist/styles/base.css";
import {
  Toolbar,
  ToolbarContent,
  ToolbarGroup,
  ToolbarItem,
  Checkbox,
} from "@patternfly/react-core";
import { useDispatch, useSelector } from "react-redux";
import { downloadDagInfo } from "../../../apis/jobScheduleService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import {
  setJobDetails,
  setJobModal,
  setJobReadMode,
  setLogModal,
  setLogValue,
  setRunNowHistoryStatus,
  setRunNowLogValue,
  setRunNowStatus,
  setScheduleStatus,
} from "../../../store/actions/jobScheduleActions";
import { downloadFileErrorMessage } from "../../app-header/components/job-schedule/constants";
import { setHideMessageAction } from "../../../store/actions/settingActions";
import CustomMessage from "../../settings-module/CustomMessage";
import { handleFileBlobDownload } from "../../message-module/utils/listFiles.utils";
import {
  setRunNowHistoryEngineType,
  setRunNowHistoryFlag,
} from "../../../store/actions/chatAction";
import { capitalizeFirstLetter } from "../../database-module/components/utils";
import { getStatusTagColor } from "../../app-header/utils";
import { setDmsLogStatus, setDmsLogValue } from "../../../store/actions/dmsAction";

const LogViewerDrawer = ({
  loading,
  logs,
  isTextWrapped,
  setIsTextWrapped,
  isFullScreen,
  setIsFullScreen,
  logViewerRef,
  individualJob,
  runNowLocal,
  engineType,
  exportFileType,
  onClose,
  pollRef,
  setLoading,
  isDms,
  selectedRun
}) => {
  const dispatch = useDispatch();
  const logValue = useSelector((state) => state.jobSchedule?.logValue);
  const dmsLogValue = useSelector((state) => state.dms?.dmsLogValue);
  const runHistory = useSelector((state) => state.jobSchedule?.runHistory);
  console.log(runHistory,"gtg")
  const runnowLogValue = useSelector(
    (state) => state.jobSchedule?.runnowLogValue
  );
  const runNowStatus = useSelector((state) => state.jobSchedule?.runNowStatus);
  const runNowHistoryStatus = useSelector(
    (state) => state.jobSchedule?.runNowHistoryStatus
  );
  const scheduleStatus = useSelector(
    (state) => state.jobSchedule?.scheduleStatus
  );
  const dmsStatus = useSelector((state) => state.dms?.dmsStatus);
  const logDetails = useSelector((state) => state.jobSchedule?.logDetails);
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const runNowHistoryFlag = useSelector(
    (state) => state.chat?.runNowHistoryFlag
  );
  const runNowHistoryEngineType = useSelector(
    (state) => state.chat?.runNowHistoryEngineType
  );
  const messageData = useSelector((store) => store?.settings?.messageData);
  const logModal = useSelector((state) => state.jobSchedule?.logModal);
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );

  const downloadDagData = () => {
    const payload = {
      job_id: runNowHistoryFlag?selectedRun.schedule_id :logDetails.schedule_id,
      dag_run_id: runNowHistoryFlag?selectedRun.run_id: logDetails.run_id,
    };

    downloadDagInfo({
      payload,
      onSuccess: (blobData, contentType) => {
        try {
          handleFileBlobDownload({
            blobData,
            contentType,
            fallbackExtension: exportFileType || "xlsx",
            fallbackFileName: selectedChat?.chat_name || "dag_data",
            supportedTypes: ["xlsx", "csv", "json"],
          });
        } catch (error) {
          console.error("Error handling file download:", error);
          handleFileBlobDownload({
            blobData,
            fallbackExtension: exportFileType || "xlsx",
            fallbackFileName: selectedChat?.chat_name || "dag_data",
            supportedTypes: ["xlsx", "csv", "json"],
          });
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        message.open({ type: "error", content: downloadFileErrorMessage });
      },
    });
  };

  const FooterButton = (direction) => {
    if (direction === "top") {
      logViewerRef?.current?.scrollToTop();
    } else {
      logViewerRef?.current?.scrollToBottom();
    }
  };

  const onExpandClick = () => {
    const element = document.querySelector("#complex-toolbar-demo");
    if (!isFullScreen) {
      element.style.backgroundColor = "#fff";
      element.style.color = "#000";
      if (element.requestFullscreen) {
        element.requestFullscreen();
      } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
      } else if (element.webkitRequestFullScreen) {
        element.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
      }
      setIsFullScreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
      element.style.backgroundColor = "";
      element.style.color = "";
      setIsFullScreen(false);
    }
  };
  const copyLogsToClipboard = () => {
    const logsToCopy = isDms
      ? dmsLogValue
      : individualJob
      ? logs
      : runNowHistoryFlag
      ? runnowLogValue
      : logValue;

    navigator?.clipboard
      ?.writeText(logsToCopy)
      .then(() => {
        message.success("Logs copied to clipboard");
      })
      .catch(() => {
        message.error("Failed to copy logs");
      });
  };
  const shouldShow = ![logValue, runnowLogValue].some(
    (item) =>
      typeof item === "string" &&
      (item.includes("Marking task as SUCCESS") ||
        item.includes("Marking task as FAILED"))
  );
  const getCurrentStatus = () => {
    if (isDms) return dmsStatus || "";
    if (runNowHistoryFlag) return runNowHistoryStatus || "";
    if (individualJob) return scheduleStatus || "";
    return runNowStatus || "";
  };

  const getCurrentEngineType = () => {
    if (isDms) return capitalizeFirstLetter("Dlt");
    if (runNowHistoryFlag)
      return capitalizeFirstLetter(runNowHistoryEngineType);
    if (isScheduleEditMode && jobListDetails) {
      return capitalizeFirstLetter(
        jobListDetails?.job_details?.engine_type || "Spark"
      );
    }
    return engineType;
  };
  const leftAlignedToolbarGroup = (
    <>
      <ToolbarItem>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: "500" }}>
              Run Status :
            </span>
            <Tag color={getStatusTagColor(getCurrentStatus())}>
              {getCurrentStatus().toUpperCase()}
            </Tag>
          </div>
          <span style={{ fontSize: "12px" }}>
            Selected Engine Type : {getCurrentEngineType()}
          </span>
        </div>
      </ToolbarItem>
      <ToolbarItem>
        <LogViewerSearch placeholder="Search" />
      </ToolbarItem>
      <ToolbarItem alignSelf="center" style={{ fontSize: "10px" }}>
        <Checkbox
          label="Wrap text"
          isChecked={isTextWrapped}
          onChange={(_, value) => setIsTextWrapped(value)}
        />
      </ToolbarItem>
      <ToolbarItem>
        <Tooltip title="Copy Logs">
          <Button
            shape="square"
            icon={<CopyOutlined />}
            size="middle"
            onClick={copyLogsToClipboard}
          />
        </Tooltip>
      </ToolbarItem>
      <ToolbarItem>
        <Tooltip title="Scroll to bottom">
          <Button
            shape="square"
            icon={<VerticalAlignBottomOutlined />}
            size="middle"
            onClick={() => FooterButton("bottom")}
          />
        </Tooltip>
      </ToolbarItem>
      <ToolbarItem>
        <Tooltip title="Expand">
          <Button
            shape="square"
            icon={<ExpandOutlined />}
            size="middle"
            onClick={onExpandClick}
          />
        </Tooltip>
      </ToolbarItem>
      {!individualJob &&
        (logDetails?.local || runNowLocal) &&
        ((typeof logValue === "string" &&
          logValue?.includes("Marking task as SUCCESS")) ||
          (typeof runnowLogValue === "string" &&
            runnowLogValue?.includes("Marking task as SUCCESS"))) && (
          <ToolbarItem>
            <Tooltip title="Download Data">
              <Button
                shape="square"
                onClick={() => downloadDagData()}
                icon={<DownloadOutlined />}
                size="middle"
                data-testid="download_logs_id"
              />
            </Tooltip>
          </ToolbarItem>
        )}

      {loading && shouldShow && (
        <ToolbarItem>
          <Tooltip title="Loading">
            <Button
              shape="square"
              icon={<ReloadOutlined className="rotate" />}
              size="middle"
            />
          </Tooltip>
        </ToolbarItem>
      )}
    </>
  );

  const closeDrawer = (e) => {
      if (pollRef?.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
      if (onClose) {
        onClose();
        setLoading(false);
      }
    dispatch(setRunNowHistoryFlag(false));
    dispatch(setRunNowHistoryEngineType(null));
    dispatch(setHideMessageAction(false));
    dispatch(setLogModal(false));
    dispatch(setLogValue(""));
    dispatch(setRunNowLogValue(""));
    dispatch(setRunNowStatus(""));
    dispatch(setRunNowHistoryStatus(""));
    dispatch({ type: "RESET_LOG_VALUE" });
    dispatch({ type: "RESET_DMS_LOG_VALUE" });
    dispatch(setDmsLogValue(""));
    dispatch(setDmsLogStatus(""));
    if (individualJob) {
      dispatch(setLogModal(false));
      dispatch(setScheduleStatus(""));
    } else {
      e.stopPropagation();
      dispatch(setJobModal(false));
      dispatch(setJobReadMode(false));
      dispatch(setLogModal(false));
      dispatch(setLogValue(""));
      dispatch(setRunNowLogValue(""));
      dispatch({ type: "RESET_LOG_VALUE" });
      dispatch({ type: "RESET_DMS_LOG_VALUE" }); 
      dispatch(setJobDetails({}));
      dispatch(setRunNowStatus(""));
      dispatch(setRunNowHistoryStatus(""));
      dispatch(setDmsLogStatus(""));
      dispatch(setDmsLogValue(""));
    }
  };
  useEffect(() => {
    if (logValue || runnowLogValue || dmsLogValue) {
      FooterButton("bottom");
    }
  }, [logValue, runnowLogValue, dmsLogValue]);
  return (
    <Drawer
      rootClassName="log-viewer"
      title="View Logs"
      open={logModal}
      width="80vw"
      onClose={(e) => closeDrawer(e)}
    >
      <div className="logs">
        {messageData && (
          <div style={{ margin: "5px" }}>
            <CustomMessage
              type={messageData?.type}
              message={messageData?.message}
            />
          </div>
        )}
        <LogViewer
          data={
            isDms
              ? dmsLogValue
              : individualJob
              ? logs
              : runNowHistoryFlag
              ? runnowLogValue
              : logValue
          }
          id="complex-toolbar-demo"
          isTextWrapped={isTextWrapped}
          ref={logViewerRef}
          height={isFullScreen ? "100%" : 600}
          toolbar={
            <Toolbar>
              <ToolbarContent style={{ justifyContent: "flex-end" }}>
                <ToolbarGroup>{leftAlignedToolbarGroup}</ToolbarGroup>
              </ToolbarContent>
            </Toolbar>
          }
        />
      </div>
    </Drawer>
  );
};

export default LogViewerDrawer;
