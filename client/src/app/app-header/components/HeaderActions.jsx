import {
  ClearOutlined,
  DatabaseOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  InfoCircleOutlined,
  ScheduleOutlined,
  LoadingOutlined,
  UnorderedListOutlined,
  CodeOutlined,
  PythonOutlined,
  HistoryOutlined,
} from "@ant-design/icons";
import {
  Popconfirm,
  Popover,
  Space,
  Spin,
  message,
  Tooltip,
  Dropdown,
  Menu,
} from "antd";
import { useState, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addNewMessageAction,
  clearChatMessagesHistoryAction,
} from "../../../store/actions/messageActions";
import {
  setActiveView,
  setPreviewState,
  setSidebarState,
} from "../../../store/actions/appActions";
import {
  setFetchChatHistoryAction,
  setFollowUpPromptAction,
  setPreviewTableData,
  setRunNowHistoryEngineType,
  setRunNowHistoryFlag,
} from "../../../store/actions/chatAction";
import {
  chatHistoryApi,
  clearChatMessageHistory,
  redoPipelineHistory,
  undoPipelineHistory,
  updateJobMode,
} from "../../../apis/chatService";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../apis/commonAPIs";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import OutsideClickHandler from "react-outside-click-handler";
import PipelineExecution from "../../chat-module/components/PipelineExecution";
import PremiumFeatureWrapper from "../../../components/ADPremiumFutureWrapper";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import EditorDrawer from "./job-schedule/components/EditorDrawer";
import ExecuteModal from "./job-schedule/components/ExecuteModal";
import { transformChatHistoryData } from "../../chat-module/utils";
import { dispatchMessage } from "../../../utils/handleClick";
import { ADModal } from "../../../components/ADModal";
import { useLocation } from "react-router-dom";
import {
  setChildDrawer,
  setJobModal,
  setJobReadMode,
  setRunNowHistoryStatus,
  setRunNowLogValue,
} from "../../../store/actions/jobScheduleActions";
import LogViewerDrawer from "../../job-schedule-module/components/LogViewerDrawer";
import {
  setLogModal,
  setLogValue,
} from "../../../store/actions/jobScheduleActions";
import { dagRunStatus, getStreamLogs } from "../../../apis/jobScheduleService";
import { Collapse, Divider, Timeline, Button } from "antd";
import ADSpace from "../../../components/ADSpace";
import getTimeStamp from "../../../utils/getCurrentTime";
import { runnowLogsMessage, TOOLTIPS_INFO } from "./job-schedule/constants";
import { chatRoutes, isDmsRoute } from "../../../router/uiRouteConstants";
import { setSelectedServiceType } from "../../../store/actions/dmsAction";

const color = "#919191";
const { Panel } = Collapse;
const HeaderActions = (props) => {
  const { setOpenDbModal, message } = props;
  const dispatch = useDispatch();
  const [messageApi, contextHolder] = message.useMessage();
  const [showMenu, setShowMenu] = useState(false);
  const [isPopover, setIsPopover] = useState(false);
  const [undoLoading, setUndoLoading] = useState(false);
  const [redoLoading, setRedoLoading] = useState(false);
  const [editorMode, setEditorMode] = useState(null);
  const [open, setOpen] = useState(false);
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const selectedDmsChat = useSelector((state) => state.dms?.selectedDmsChat);
  const { isYamlSaved } =
    useSelector((state) => state.chat?.chatList[selectedChat?.chat_id]) ?? {};
  const chatId = selectedChat?.chat_id;
  const dmsChatId = selectedDmsChat?.chat_id;
  const params = useSelector((state) => state.messages.params);
  const previewState = useSelector((state) => state.app.previewState);
  const pipelineHistory =
    useSelector((state) => state.chat.chatList[chatId]?.pipelineHistory) || {};
  const isUndoDisabled =
    !pipelineHistory?.history || pipelineHistory?.history.length === 0;
  const jobMode = useSelector((state) => state.chat.jobMode);
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const runHistory = useSelector((state) => state.jobSchedule?.runHistory);
  const dmsRunHistory = useSelector((state) => state.dms?.dmsRunHistory);
  const [isTextWrapped, setIsTextWrapped] = useState(false);
  const logViewerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [selectedRunLocal, setSelectedRunLocal] = useState(false);
  const [selectedRun, setSelectedRun] = useState(null); 
  const [runLogsPopoverOpen, setRunLogsPopoverOpen] = useState(false);
  const location = useLocation();
  const isDms = isDmsRoute(location.pathname);
  const pollRef = useRef(null);
  const handlePreview = () => {
    resetMenu();
    if (selectedChat?.chat_id) {
      dispatch(setPreviewState(!previewState));
      dispatch(setSidebarState(!previewState));
    }
  };

  function handleClearChatHistory() {
    resetMenu();
    clearChatMessageHistory({
      chatId,
      onSuccess: () => {
        dispatch(clearChatMessagesHistoryAction({ chatId }));
        dispatch(setFollowUpPromptAction({ chat_id: chatId, prompts: [] }));
        triggerGetInfoAPI(dispatch, chatId);
        triggerPipelineHistory(dispatch, chatId);
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
      },
    });
  }

  const resetMenu = () => {
    if (showMenu) {
      setShowMenu(false);
    }
  };

  const handleDsConnect = () => {
    resetMenu();
    if (selectedChat?.chat_id) {
      dispatch(setActiveView("job-listing-view"));
      // dispatch(setActiveView("create-report-view"));
      setOpenDbModal(true);
    }
  };
  const activeChat = isDms ? selectedDmsChat : selectedChat;

  const triggerJob = () => {
    dispatch(setJobReadMode(false));
    dispatch(setSelectedServiceType(""))
    resetMenu();
    if (activeChat?.chat_id) {
      dispatch(setJobModal(true));
    }
  };

  const resetLoading = () => {
    setUndoLoading(false);
    setRedoLoading(false);
  };

  const handleUndoRedoAction = (actionType) => {
    if (isUndoDisabled || !selectedChat?.chat_id) return;

    const payload = {
      chat_id: chatId,
    };

    let pipelineMethod;
    let type;

    if (actionType === "undo") {
      setUndoLoading(true);
      pipelineMethod = undoPipelineHistory;
      type = "Undo";
    } else {
      setRedoLoading(true);
      pipelineMethod = redoPipelineHistory;
      type = "Redo";
    }

    pipelineMethod({
      payload,
      onSuccess: (res) => {
        triggerGetInfoAPI(dispatch, chatId, { refresh: true });
        triggerPipelineHistory(dispatch, chatId);
        dispatchMessage(
          dispatch,
          "success",
          res?.msg || res?.message || `${type} done successfully`,
        );
        resetLoading();
      },
      onError: (error) => {
        resetLoading();
        dispatchMessage(
          dispatch,
          "error",
          error.msg || error.message || `Failed to ${type} transformation`,
        );
      },
    });
  };

  const cursor =
    !selectedChat?.chat_id || location.search == "" ? "not-allowed" : "pointer";

  const handleMenu = () => {
    setShowMenu((prev) => !prev);
  };

  const renderLoading = () => (
    <Spin
      indicator={
        <LoadingOutlined
          style={{
            fontSize: 18,
          }}
          spin
        />
      }
    />
  );

  const handleClose = () => {
    if (isYamlSaved) {
      setOpen(true); // show modal when user saves yaml
    }
  };

  const handleCode = (mode) => {
    setEditorMode(mode);
    // setChildrenDrawer(true);
    dispatch(setChildDrawer(true));
  };
  const handleBackClick = async () => {
    setDeleteLoading(true);
    const payload = {
      name: "llm",
      chatId,
    };
    try {
      await updateJobMode({
        payload,
        onSuccess: (response) => {
          dispatchMessage(dispatch, "success", "Job Mode : LLM");
        },
        onError: (error) => {
          handleSessionExpiry(dispatch, error);
          dispatchMessage(dispatch, "error", "Job Mode Failed");
          throw error;
        },
      });
      await triggerGetInfoAPI(dispatch, chatId);
      await triggerPipelineHistory(dispatch, chatId);
      setDeleteModal(false);
      setDeleteLoading(false);
    } catch (error) {
      console.error(error);
      setDeleteModal(false);
      setDeleteLoading(false);
    }
  };
  const handlePythonIconClick = () => {
    handleCode("python");
  };
    const currentRunHistory = isDms
      ? dmsRunHistory?.[dmsChatId] || []
      : runHistory?.[chatId] || [];
      console.log(currentRunHistory,"ityrf5")
    const handleRunHistoryClick = (runId, local, engine_type,schedule_id,runItem) => {
    dispatch(setRunNowHistoryFlag(true));
    dispatch(setRunNowHistoryEngineType(engine_type));
    setSelectedRunLocal(local);
    setSelectedRun(runItem); 
    dispatch(setLogModal(true));
    setRunLogsPopoverOpen(false);
    dispatch(setRunNowLogValue(""));
       if (pollRef.current) {
         clearInterval(pollRef.current);
       }
     pollRef.current = setInterval(() => {
      dagRunStatus({
        payload: {
          dag_id: "",
          dag_run_id: runId,
        },
        onSuccess: (res) => {
          if (res.success) {
            dispatch(setRunNowHistoryStatus(res.state));
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
    getStreamLogs({
      payload: {
        job_id: isDms ? dmsChatId : chatId,
        dag_run_id: runId,
        engine_type: engine_type,
      },
      onSuccess: (response) => {
        dispatch(setRunNowLogValue(response));
        setLoading(false);
      },
      onError: (error) => {
        console.error("Failed to fetch logs:", error);
        handleSessionExpiry(dispatch, error);
      },
    });
  };

  const renderRunLogsContent = () => {
    if (currentRunHistory.length === 0) {
      return (
        <div className="no-history text-center">No Run now logs found!</div>
      );
    }

    return (
      <div className="run-logs-container ">
        <Timeline mode="left" className="timeline-root">
          {currentRunHistory.map((item) => (
            <Timeline.Item
              key={item.run_id}
              color="green"
              style={{
                padding: "2px 0",
              }}
            >
              <div className="panel-header">{getTimeStamp(item.timestamp)}</div>
              <div className="run-id-text">
                <span
                  className="run-id-link"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRunHistoryClick(
                      item.run_id,
                      item.local,
                      item.engine_type,
                      item.schedule_id,  
                      item
                    );
                    // setRunLogsPopoverOpen(false);
                  }}
                >
                  Run ID : {item.run_id}
                </span>
              </div>
            </Timeline.Item>
          ))}
        </Timeline>
      </div>
    );
  };
  const isValidChat = isDms
    ? !!selectedDmsChat?.chat_id
    : !!selectedChat?.chat_id && location.search !== "";
  const isDisabled = !isValidChat;

  const getCursor = () => (isDisabled ? "not-allowed" : "pointer");
  const isYamlDisabled = (!isDms && jobMode === "python") || isDisabled;
  const handleSafeClick = (callback) => (e) => {
    if (isDisabled) {
      e.stopPropagation();
      return;
    }
    callback();
  };
  const renderItems = (direction, showPopoverControl = false) => {
    const placement = direction === "vertical" ? "left" : "bottom";
    return (
      <Space direction={direction} style={{ margin: "10px" }}>
        {!isDms && (
          <PremiumFeatureWrapper
            module="job"
            feature="load"
            tooltip={{ title: "Connect to datasources", placement }}
          >
            <DatabaseOutlined
              className="cursor-pointer"
              style={{
                fontSize: "16px",
                color,
                cursor,
              }}
              onClick={(e) => {
                if (!selectedChat?.chat_id || location.search == "") {
                  e.stopPropagation();
                } else {
                  handleDsConnect();
                }
              }}
              data-testid="connect-db-icon"
            />
          </PremiumFeatureWrapper>
        )}

        {previewState && !isDms ? (
          <PremiumFeatureWrapper
            module="job"
            feature="datapreview"
            tooltip={{ title: "Chat mode", placement }}
          >
            <EyeInvisibleOutlined
              data-testid="close-preview"
              className="cursor-pointer"
              onClick={(e) => {
                if (
                  jobMode === "yaml" ||
                  !selectedChat?.chat_id ||
                  location.search == ""
                ) {
                  e.stopPropagation();
                } else {
                  dispatch(
                    setPreviewTableData({ columns: [], datasource: {} }),
                  );
                  handlePreview();
                }
              }}
              style={{
                fontSize: "18px",
                color,
                cursor:
                  jobMode === "yaml" ||
                  !selectedChat?.chat_id ||
                  location.search == ""
                    ? "not-allowed"
                    : "pointer",
              }}
            />
          </PremiumFeatureWrapper>
        ) : (
          <>
            {!isDms && (
              <PremiumFeatureWrapper
                module="job"
                feature="datapreview"
                tooltip={{ title: "Preview mode", placement }}
              >
                <EyeOutlined
                  data-testid="open-preview"
                  onClick={(e) => {
                    if (
                      jobMode === "yaml" ||
                      !selectedChat?.chat_id ||
                      location.search == ""
                    ) {
                      e.stopPropagation();
                    } else {
                      handlePreview();
                    }
                  }}
                  style={{
                    fontSize: "17px",
                    color,
                    cursor:
                      jobMode === "yaml" ||
                      !selectedChat?.chat_id ||
                      location.search == ""
                        ? "not-allowed"
                        : "pointer",
                  }}
                />
              </PremiumFeatureWrapper>
            )}
          </>
        )}

        {!isDms && (
          <PremiumFeatureWrapper
            module="job"
            feature="undo"
            tooltip={{ title: "Undo Transformation", placement }}
          >
            {!undoLoading ? (
              <CustomIcon
                data-testid="undo-id"
                name="undo"
                onClick={(e) => {
                  if (!selectedChat?.chat_id || location.search == "") {
                    e.stopPropagation();
                  } else {
                    handleUndoRedoAction("undo");
                  }
                }}
                style={{
                  fontSize: "16px",
                  color,
                  cursor: isUndoDisabled ? "not-allowed" : cursor,
                }}
              />
            ) : (
              renderLoading()
            )}
          </PremiumFeatureWrapper>
        )}

        {!isDms && (
          <PremiumFeatureWrapper
            module="job"
            feature="redo"
            tooltip={{ title: "Redo Transformation", placement }}
          >
            {!redoLoading ? (
              <CustomIcon
                data-testid="redo-id"
                name="redo"
                onClick={() => handleUndoRedoAction("redo")}
                style={{ fontSize: "16px", color, cursor }}
              />
            ) : (
              renderLoading()
            )}
          </PremiumFeatureWrapper>
        )}

        <PremiumFeatureWrapper
          module="job"
          feature="history"
          tooltip={{ title: "Job History", placement }}
        >
          <Popover
            overlayClassName="popover-container"
            trigger={isDisabled ? "" : "click"}
            disabled={isDisabled}
            title="Job History"
            content={<PipelineExecution setIsPopover={setIsPopover} />}
            overlayStyle={{
              width: "360px",
            }}
            // disabled={!selectedChat?.chat_id}
            placement={placement}
            onOpenChange={(open) => setIsPopover(open ? true : false)}
          >
            <InfoCircleOutlined
              data-testid="pipeline-history-id"
              style={{ fontSize: "16px", color, cursor: getCursor() }}
            />
          </Popover>
        </PremiumFeatureWrapper>

        <PremiumFeatureWrapper
          module="job"
          feature="reset"
          tooltip={{ title: "Reset", placement }}
        >
          <Popconfirm
            title={<span className="popconfirm-title">Clear chat history</span>}
            description={
              <div className="popconfirm-description">
                <p>
                  Are you sure you want to clear the chat history for{" "}
                  <span className="chat-name-highlight">
                    {isDms
                      ? selectedDmsChat?.chat_name
                      : selectedChat?.chat_name}
                  </span>{" "}
                  ?
                </p>
                <p>This action cannot be undone.</p>
              </div>
            }
            onConfirm={(e) => {
              setIsPopover(false);
              e.stopPropagation();
              handleClearChatHistory();
            }}
            onClick={() => setIsPopover(true)}
            onCancel={(e) => {
              setIsPopover(false);
              e.stopPropagation();
            }}
            disabled={isDisabled}
            // disabled={!selectedChat?.chat_id || location.search == ""}
            placement="rightTop"
          >
            <ClearOutlined
              onClick={(e) => {
                if (isDisabled) {
                  e.stopPropagation();
                }
              }}
              data-testid="reset-chat-id"
              style={{
                fontSize: "16px",
                color,
                cursor: getCursor(),
              }}
            />
          </Popconfirm>
        </PremiumFeatureWrapper>
        <PremiumFeatureWrapper
          module="job"
          // feature="runnowlogs"
          tooltip={{
            title: <>{runnowLogsMessage}</>,
            placement,
          }}
        >
          <Popover
            overlayClassName="popover-container"
            // open={runLogsPopoverOpen}
            // trigger={
            //   !selectedChat?.chat_id || location.search == "" ? "" : "click"
            // }
            trigger={isDisabled ? "" : "click"}
            title={
              <div className="run-now-logs-header">
                <span>Run Now Logs</span>
                <Tooltip
                  title={TOOLTIPS_INFO.runNowLogsInfo}
                  overlayClassName="custom-tooltip"
                >
                  <InfoCircleOutlined className="run-now-logs-info-icon" />
                </Tooltip>
              </div>
            }
            content={renderRunLogsContent()}
            overlayStyle={{
              width: "360px",
            }}
            disabled={isDisabled}
            // disabled={!selectedChat?.chat_id}
            placement={placement}
            {...(showPopoverControl && {
              open: runLogsPopoverOpen,
              onOpenChange: (open) => setRunLogsPopoverOpen(open),
            })}
            getPopupContainer={(triggerNode) => triggerNode.parentNode}
          >
            <HistoryOutlined
              style={{ fontSize: "16px", color, cursor: getCursor() }}
              data-testid="run-now-logs-id"
            />
          </Popover>
        </PremiumFeatureWrapper>

        <PremiumFeatureWrapper
          module="job"
          feature="trigger"
          tooltip={{ title: "Trigger Job", placement: "left" }}
        >
          <ScheduleOutlined
            data-testid="trigger-job-id"
            onClick={handleSafeClick(triggerJob)}
            className="cursor-pointer"
            style={{
              fontSize: "17px",
              color,
              cursor: getCursor(),
            }}
          />
        </PremiumFeatureWrapper>
        <PremiumFeatureWrapper
          module="job"
          feature="yaml"
          tooltip={{ title: "YAML Editor", placement: "left" }}
        >
          <CodeOutlined
            // onClick={(e) => {
            //   if (
            //     jobMode === "python" ||
            //     !selectedChat?.chat_id ||
            //     location.search == ""
            //   ) {
            //     e.stopPropagation();
            //   } else {
            //     handleCode("yaml");
            //   }
            // }}
            onClick={(e) => {
              if ((!isDms && jobMode === "python") || isDisabled) {
                e.stopPropagation();
                return;
              }
              handleCode("yaml");
            }}
            className="cursor-pointer"
            style={{
              fontSize: "16px",
              color: jobMode === "yaml" ? " rgb(145, 145, 145)" : "#F28E1E",
              cursor: isYamlDisabled ? "not-allowed" : "pointer",
            }}
          />
        </PremiumFeatureWrapper>
        {!isDms && (
          <PremiumFeatureWrapper
            module="job"
            feature="ace"
            tooltip={{ title: "ACE Editor", placement: "left" }}
          >
            <PythonOutlined
              onClick={(e) => {
                if (
                  jobMode === "yaml" ||
                  !selectedChat?.chat_id ||
                  location.search == ""
                ) {
                  e.stopPropagation();
                } else {
                  handlePythonIconClick();
                }
              }}
              className="cursor-pointer"
              style={{
                fontSize: "16px",
                color: jobMode === "python" ? "rgb(145, 145, 145)" : "#F28E1E",
                cursor:
                  jobMode === "yaml" ||
                  !selectedChat?.chat_id ||
                  location.search == ""
                    ? "not-allowed"
                    : "pointer",
              }}
            />
          </PremiumFeatureWrapper>
        )}
        {jobMode === "yaml" && (
          <Tooltip title="Return to Pipeline Mode">
            <Space
              onClick={() => setDeleteModal(true)}
              className="cursor-pointer close-btn "
            >
              Close
            </Space>
          </Tooltip>
        )}
      </Space>
    );
  };
  return (
    <>
      {contextHolder}
      <div className="ad-header__info-container dFlex">
        <div className="icons-container w-100 dFlex justifyEnd alignCenter">
          <OutsideClickHandler
            onOutsideClick={() => {
              if (!isPopover && showMenu) {
                setShowMenu(false);
              }
            }}
          >
            <UnorderedListOutlined
              style={{ fontSize: "16px" }}
              onClick={() => handleMenu()}
              className="cursor-pointer more-icon"
              data-testid="menu-icon"
            />
            {showMenu && (
              <div
                className="vertical-menu menu-drop-down d-block"
                data-testid="vertical-menu-id"
              >
                {renderItems("vertical")}
              </div>
            )}
            <div className="horizontal-menu" data-testid="horizontal-menu">
              {renderItems("horizontal", true)}
            </div>
          </OutsideClickHandler>
        </div>
      </div>
      <EditorDrawer
        handleClose={() => {
          dispatch(setChildDrawer(false));
          setEditorMode(null);
        }}
        mode={editorMode}
        title={
          editorMode === "yaml"
            ? "YAML Editor"
            : "Ask On Data Code Editor (ACE)"
        }
      />
      <ExecuteModal open={open} setOpen={setOpen} />
      <ADModal
        title="Change Your Mode"
        description={
          <>
            Are you sure you want to change your current mode{" "}
            <strong>{jobMode}</strong>?
          </>
        }
        open={deleteModal}
        onOk={handleBackClick}
        onCancel={() => setDeleteModal(false)}
        okText="Change"
        cancelText="Cancel"
        loading={deleteLoading}
        showCancelButton
        hideButtons={false}
      />
      <LogViewerDrawer
        isTextWrapped={isTextWrapped}
        setIsTextWrapped={setIsTextWrapped}
        loading={loading}
        logViewerRef={logViewerRef}
        runNowLocal={selectedRunLocal}
        pollRef={pollRef}
        selectedRun={selectedRun}   
      />
    </>
  );
};

export default HeaderActions;
