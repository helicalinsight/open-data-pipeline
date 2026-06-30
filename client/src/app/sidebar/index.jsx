import { Layout } from "antd";
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import {
  setPreviewTableData,
  setSelectedChatAction,
} from "../../store/actions/chatAction";
import { getLocalStorageItem } from "../../utils/userData";
import { useSearchParams } from "react-router-dom";
import SideBarFooter from "./components/SidebarFooter";
import SidebarHeader from "./components/SidebarHeader";
import SidebarJobs from "./components/SidebarJobs";
import SidebarActions from "./components/SidebarActions";
import "./style.scss";
import { ADModal } from "../../components/ADModal";
import { setMessageParamsAction } from "../../store/actions/messageActions";
import ErrorFallback from "../error-boundry/ErrorFallback";
import { chatRoutes, isDmsRoute } from "../../router/uiRouteConstants";
import { getDmsList } from "../../apis/jobScheduleService";
import { getAllDmsJobsApi, getAllJobsApi } from "../../apis/chatService";
import {
  addsetDmsStepsAction,
  setDmsJobsAction,
  setDmsSelectedChatAction,
  setSelectPipelineModeAction,
} from "../../store/actions/dmsAction";

const { Sider } = Layout;

function Sidebar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParms] = useSearchParams();
  const { user } = getLocalStorageItem() || {};
  const [allJobs, setAllJobs] = useState([]);
  const [dmsJobs, setDmsJobs] = useState([]);
  const [searchValue, setSearchValue] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [clickedChatItem, setClickedChatItem] = useState(null);
  const isSidebarCollapsed = useSelector(
    (state) => state.app.isSidebarCollapsed,
  );
  const allChats = useSelector((state) => state.chat?.chatList) || {};
  const dmschats = useSelector((state) => state.dms?.dmsJobs) || {};
  const memoizedJobs = useMemo(() => allChats, [allChats]);
  const memoizedDmsJobs = useMemo(() => dmschats, [dmschats]);

  const chat_id = searchParms.get("chat");
  //dms list
  useEffect(() => {
    if (!isDmsRoute(location.pathname)) {
      dispatch(setDmsJobsAction([]));
      return;
    }
    if (!chat_id) {
      dispatch(setDmsSelectedChatAction({}));
    }
    if (Object.keys(dmschats).length > 0) return;
    getAllJobsApi({
      params: { service_mode: "DMS" },
      onSuccess: (res) => {
        const dmsJobsData = res.success && res.chats?.length ? res.chats : [];
        dispatch(setDmsJobsAction(dmsJobsData));
        if (chat_id && dmsJobsData.length > 0) {
          const selectedChat = dmsJobsData.find(
            (job) => job.chat_id === chat_id,
          );
          if (selectedChat) {
            dispatch(setDmsSelectedChatAction(selectedChat));
          }
        }
      },
      onError: () => {
        dispatch(setDmsJobsAction([]));
      },
    });
  }, [location.pathname, user?.id,  chat_id]);

  const apiCallsStatus =
    useSelector((state) => state.chat?.chatList[chat_id]?.apiCallsStatus) || [];

  useEffect(() => {
    if (Object.keys(memoizedJobs).length) {
      let chats = Object.values(memoizedJobs);
      setAllJobs(chats.reverse());
    }
  }, [memoizedJobs]);
  useEffect(() => {
    if (Object.keys(memoizedDmsJobs).length) {
      let chats = Object.values(memoizedDmsJobs);
      setDmsJobs(chats.reverse());
    }
  }, [memoizedDmsJobs]);

  const currentJobs = isDmsRoute(location.pathname) ? dmsJobs : allJobs;

  const switchChat = (item) => {
    if (!item) return null;
    dispatch(setMessageParamsAction({ offset: 0 }));
    dispatch(setPreviewTableData({ columns: [], datasource: {} }));
    if (isDmsRoute(location.pathname)) {
      dispatch(setDmsSelectedChatAction(item));
      dispatch(addsetDmsStepsAction(0));
      dispatch(setSelectPipelineModeAction("table"));
      dispatch({ type: "RESET_DMS_STATE" });
    } else {
      dispatch(setSelectedChatAction(item));
    }
    navigate(
      {
        search: `?chat=${item.chat_id}`,
      },
      { state: { chatId: item.chat_id } },
    );
    // }
  };

  const handleChatClick = (item) => {
    if (isDmsRoute(location.pathname)) {
      switchChat(item);
    } else {
      if (chat_id !== item.chat_id) {
        const inProgressAPI = apiCallsStatus.find(
          (eachAPI) => eachAPI.isFetching,
        );
        if (inProgressAPI) {
          setIsModalOpen(true);
          setClickedChatItem(item);
        } else {
          switchChat(item);
        }
      }
    }
  };

  const getSearchResults = () => {
    if (searchValue === "") {
      return currentJobs;
    } else {
      const filteredResults = currentJobs.filter((eachJob) =>
        eachJob.chat_name.toLowerCase().includes(searchValue.toLowerCase()),
      );
      return filteredResults;
    }
  };

  const handleOk = () => {
    switchChat(clickedChatItem);
    setIsModalOpen(false);
    setClickedChatItem(null);
    apiCallsStatus.forEach((eachAPI) => {
      if (eachAPI.abortController) {
        eachAPI.abortController.abort();
      }
    });
  };

  const handleCancel = () => {
    setIsModalOpen(false);
    setClickedChatItem(null);
  };

  const searchResults = getSearchResults();

  const sidebarComponents = {
    "/app-space": (
      <>
        <SidebarActions
          searchValue={searchValue}
          setSearchValue={setSearchValue}
          allJobs={allJobs}
        />
        <SidebarJobs
          searchResults={searchResults}
          handleChatClick={handleChatClick}
          allJobs={currentJobs}
          setAllJobs={setAllJobs}
          isSidebarCollapsed={isSidebarCollapsed}
          isDmsMode={false}
        />
      </>
    ),
    "/dms": (
      <>
        <SidebarActions
          searchValue={searchValue}
          setSearchValue={setSearchValue}
          allJobs={dmsJobs}
        />
        <SidebarJobs
          searchResults={searchResults}
          handleChatClick={handleChatClick}
          allJobs={currentJobs}
          setAllJobs={setDmsJobs}
          isSidebarCollapsed={isSidebarCollapsed}
          isDmsMode={true}
        />
      </>
    ),
    "/schedule": (
      <p
        style={{ color: "white", marginTop: "2rem", fontSize: "12px" }}
        className="items-center"
      >
        Job Schedules view
      </p>
    ),
    "/data-source": (
      <p
        style={{ color: "white", marginTop: "2rem", fontSize: "12px" }}
        className="items-center"
      >
        Data sources view
      </p>
    ),
    "/audit": (
      <p
        style={{ color: "white", marginTop: "2rem", fontSize: "12px" }}
        className="items-center"
      >
        Audit view
      </p>
    ),
  };
  const getSidebarContent = () => {
    const pathname = location?.pathname;
    if (isDmsRoute(pathname)) {
      return sidebarComponents[chatRoutes.dms];
    }
    return sidebarComponents[pathname] || null;
  };
  return (
    <ErrorFallback>
      <Sider
        width="275px"
        collapsed={isSidebarCollapsed}
        collapsedWidth="0px"
        className="sidebar-section overflowHidden"
        theme="dark"
        data-testid="sider-component"
      >
        <div className="dFlex h-100 flexColumn">
          <div style={{ height: "93%" }} className="overflowHidden">
            <SidebarHeader isSidebarCollapsed={isSidebarCollapsed} />
            {getSidebarContent()}
          </div>
          <SideBarFooter user={user} isSidebarCollapsed={isSidebarCollapsed} />
        </div>
      </Sider>
      <ADModal
        title="Switch Chat"
        description="Some data is still proccessing. Do you still wanna proceed ?"
        open={isModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}
        okText="Continue"
        cancelText="Cancel"
        showCancelButton={true}
        hideButtons={false}
      />
    </ErrorFallback>
  );
}

export default Sidebar;
