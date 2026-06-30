import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setSidebarState } from "../../store/actions/appActions";
import { DoubleRightOutlined, DoubleLeftOutlined } from "@ant-design/icons";
import { message, Tooltip, Breadcrumb } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import ADSpace from "../../components/ADSpace";
import DataBaseModule from "../database-module";
import HeaderFileList from "./components/HeaderFileList";
import HeaderActions from "./components/HeaderActions";
import ErrorFallback from "../error-boundry/ErrorFallback";
import JobScheduleWrapper from "./components/job-schedule";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import "./style.scss";
import {
  chatRoutes,
  dmsPath,
  isDmsRoute,
  userRoutes,
} from "../../router/uiRouteConstants";
import {
  setCurrentPage,
  setIndividualJob,
} from "../../store/actions/jobScheduleActions";
import { setIsDetailedView } from "../../store/actions/auditAction";
import {
  addsetDmsStepsAction,
  setSelectPipelineModeAction,
} from "../../store/actions/dmsAction";

const JobViewHeader = () => {
  const dispatch = useDispatch();
  const location = useLocation();
  const isDms = isDmsRoute(location.pathname);
  const navigate = useNavigate();
  const { id } = useParams();
  const [openDbModal, setOpenDbModal] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();
  const isSidebarCollapsed = useSelector(
    (state) => state.app.isSidebarCollapsed,
  );
  const datasources = useSelector((state) => state.database.datasources);
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const selectedDmsChat = useSelector((state) => state.dms?.selectedDmsChat);
  const step = useSelector((state) => state.dms.step);
  const chatId = selectedChat?.chat_id;
  const loadedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.loadedFiles) ?? [];
  const selectedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.selectedFiles) ?? [];
  const activeViewState = useSelector((state) => state.app.activeViewState);
  const yamlSave = useSelector((state) => state.chat.yamlSave);
  const breadcrumbMap = {
    [chatRoutes.chat]: "Home",
    [chatRoutes.datasource]: "Data Sources",
    [chatRoutes.schedule]: "Job Schedules",
    [chatRoutes.audit]: "Audit",
    [chatRoutes.setting]: "Settings",
    [chatRoutes.dms]: "DMS",
    [chatRoutes.sourceType]: "Source Type",
    [chatRoutes.overview]: "Overview",
    [chatRoutes.destinationType]: "Destination Type",
    [chatRoutes.createPipeline]: "Create Pipeline",
    [chatRoutes.configureSource]: "Configure Source",
    [chatRoutes.configureDestination]: "Configure Destination",
    [chatRoutes.destinationObjectSelect]: "Destination Object Select",
    [chatRoutes.finalSetting]: "Final Setting",
    [chatRoutes.directFinalSetting]: "Final Setting",
    [chatRoutes.objectSelect]: "Object Select",
    [userRoutes.userSetup]: "User Setup",
  };
  const breadcrumbLabel = breadcrumbMap[location?.pathname] || "Unknown";
  const dagInfo = useSelector((state) => state.jobSchedule?.dagInfo);
  const individualJob = useSelector(
    (state) => state.jobSchedule?.individualJob,
  );
  const jobMode = useSelector((state) => state.chat.jobMode);
  const jobModal = useSelector((state) => state.jobSchedule?.jobModal);
  const isDetailedView = useSelector((state) => state.audit.isDetailedView);

  // Detect if the page was refreshed
  useEffect(() => {
    const isPageRefresh = sessionStorage.getItem("isRefreshed") === "true";
    if (id && isPageRefresh) {
      sessionStorage.removeItem("isRefreshed"); // Clear after detecting
      navigate(chatRoutes.datasource, { replace: true });
    }
  }, [navigate]);

  // Set sessionStorage on refresh
  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem("isRefreshed", "true");
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);
  const renderBreadcrumbItems = () => {
    const items = [
      <Breadcrumb.Item key="home" onClick={() => navigate(chatRoutes.chat)}>
        <span className="hover-underline">Home</span>
      </Breadcrumb.Item>,
    ];
    const breadcrumbConfigs = (() => {
     const fullName = selectedDmsChat?.chat_name;
     const isEllipsis = fullName?.length > 10;
     const chatName = isEllipsis ? fullName.slice(0, 10) + "..." : fullName;
     const chatLabel = isEllipsis ? (
         <Tooltip title={fullName}>
           <span>{chatName}</span>
         </Tooltip>
       ) : (
         chatName
       );
      const base = [
        ["dms", "DMS"],
        ["chat", chatLabel],
      ];
      if (step === 0) {
        return base;
      }
      if (step === 1) {
        return [...base, ["source", "Source"]];
      }
      if (step === 2) {
        return [...base, ["source", "Source"], ["destination", "Destination"]];
      }
      return base;
    })();
    const renderBreadcrumbItem = ([key, label], index) => {
      return (
        <Breadcrumb.Item
          key={key}
          onClick={() => {
            if (!isDms) return;
            if (index === 0) {
              navigate(chatRoutes.dms);
              dispatch(addsetDmsStepsAction(0));
            }
            if (index === 1) dispatch(addsetDmsStepsAction(0));
            if (index === 2) dispatch(addsetDmsStepsAction(1));
            if (index === 3) dispatch(addsetDmsStepsAction(2));
          }}
        >
          <span className="hover-underline">{label}</span>
        </Breadcrumb.Item>
      );
    };

    if (isDms) {
      breadcrumbConfigs
        .filter(([, label]) => label)
        .forEach((itemConfig, index) =>
          items.push(renderBreadcrumbItem(itemConfig, index)),
        );
    } else if (location?.pathname.includes(`${chatRoutes.datasource}/`) && id) {
      items.push(
        <Breadcrumb.Item
          key="datasources"
          onClick={() => navigate(chatRoutes.datasource)}
        >
          <span className="hover-underline">Data Sources</span>
        </Breadcrumb.Item>,
        <Breadcrumb.Item key="datasource-detail">
          <span className="hover-underline">
            {datasources?.find((ds) => ds?.driver === id)?.name}
          </span>
        </Breadcrumb.Item>,
      );
    } else if (location?.pathname === chatRoutes.schedule && individualJob) {
      items.push(
        <Breadcrumb.Item
          key="schedules"
          onClick={() => {
            dispatch(setIndividualJob(false));
            dispatch(setCurrentPage(1));
          }}
        >
          <span className="hover-underline">Job Schedules</span>
        </Breadcrumb.Item>,
        <Breadcrumb.Item key="job-detail">
          <span className="hover-underline">
            {dagInfo?.basic_info?.job_name}
          </span>
        </Breadcrumb.Item>,
      );
    } else if (location?.pathname === chatRoutes.audit && isDetailedView) {
      items.push(
        <Breadcrumb.Item
          key="audit"
          onClick={() => dispatch(setIsDetailedView(false))}
        >
          <span className="hover-underline">{breadcrumbLabel}</span>
        </Breadcrumb.Item>,
        <Breadcrumb.Item key="audit-detail">
          <span className="hover-underline">Summary</span>
        </Breadcrumb.Item>,
      );
    } else {
      items.push(
        <Breadcrumb.Item key="current">
          <span className="hover-underline">{breadcrumbLabel}</span>
        </Breadcrumb.Item>,
      );
    }

    return items;
  };

  return (
    <>
      {contextHolder}
      <ErrorFallback>
        <div className="ad-header dFlex alignCenter justifyBetween w-100">
          <ADSpace space="4" alignItem="center">
            {isSidebarCollapsed && (
              <Tooltip title="Maximize Sidebar" placement="bottomRight">
                <DoubleRightOutlined
                  className="cursor-pointer"
                  data-testid="menu-unfold-id"
                  onClick={() => {
                    dispatch(setSidebarState(false));
                  }}
                />
              </Tooltip>
            )}
            {location?.pathname !== chatRoutes?.chat &&
              location?.pathname !== userRoutes?.userSetup && (
                <Breadcrumb style={{ fontSize: "12px", margin: "10px" }}>
                  {renderBreadcrumbItems()}
                </Breadcrumb>
              )}

            {location?.pathname === chatRoutes?.chat &&
              location.search !== "" && (
                <>
                  <div className="ad-header__job-name f14 fw600 mw-fitcontent">
                    <Tooltip title={selectedChat?.chat_name}>
                      <span>
                        {selectedChat?.chat_name?.length > 10
                          ? `${selectedChat?.chat_name?.slice(0, 10)}...`
                          : selectedChat?.chat_name}
                      </span>
                    </Tooltip>
                    {selectedChat?.chat_name && (
                      <Tooltip title={`Job Type: ${jobMode}`}>
                        <InfoCircleOutlined
                          style={{ marginLeft: 8, cursor: "pointer" }}
                        />
                      </Tooltip>
                    )}
                  </div>
                  {location.search !== "" && (
                    <HeaderFileList
                      loadedFiles={loadedFiles}
                      selectedFiles={selectedFiles}
                    />
                  )}
                </>
              )}
          </ADSpace>
          {(location?.pathname === chatRoutes?.chat || isDms) && (
            <HeaderActions message={message} setOpenDbModal={setOpenDbModal} />
          )}
        </div>
        {openDbModal && (
          <DataBaseModule
            setOpenDbModal={setOpenDbModal}
            openDbModal={openDbModal}
            haveLoad={true}
          />
        )}
        {jobModal && <JobScheduleWrapper messageApi={messageApi} />}
      </ErrorFallback>
    </>
  );
};

export default JobViewHeader;
