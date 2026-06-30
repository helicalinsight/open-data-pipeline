import { Layout, Spin, Space, message } from "antd";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getLocalStorageItem } from "../../utils/userData";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { chatRoutes, userRoutes } from "../../router/uiRouteConstants";
import { ADSpace } from "../../components";
import { chatHistoryApi, getAllJobsApi } from "../../apis/chatService";
import { transformChatHistoryData } from "./utils";
import { handleSessionExpiry } from "../../utils/handleSessionExpiry";
import { ADModal } from "../../components/ADModal";
import { setSelectedDatasourceAction } from "../../store/actions/databaseActions";
import { resetRedux } from "../../store/actions/sessionActions";
import {
  addNewMessageAction,
  setMessageParamsAction,
} from "../../store/actions/messageActions";
import {
  setFetchChatHistoryAction,
  addNewChatAction,
  setSelectedChatAction,
} from "../../store/actions/chatAction";
import {
  triggerGetApplication,
  triggerGetDatasources,
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../apis/commonAPIs";

import Sidebar from "../sidebar";
import ChatWindow from "./components/ChatWindow";
import ADPreview from "./components/PreviewSection";
import JobViewHeader from "../app-header";
import SettingsModule from "../settings-module";
import ErrorFallback from "../error-boundry/ErrorFallback";
import DataBaseModule from "../database-module";
import JobScheduleModule from "../job-schedule-module";
import DefaultJobView from "./components/DefaultJobView";
import InfoSection from "./components/InfoSection";
import AuditModule from "../audit-module";
import CustomMessage from "../settings-module/CustomMessage";

const ChatModule = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loader, setLoader] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();
  const showPreview = useSelector((state) => state.app?.previewState);
  const [searchParms] = useSearchParams();
  const chat_id = searchParms.get("chat");
  const params = useSelector((state) => state.messages.params);
  const activeViewState = useSelector((state) => state.app.activeViewState);
  const selectedDatasource = useSelector(
    (state) => state.database.selectedDatasource
  );
  const selectedChat = useSelector((state) => state.chat?.selectedChat) || {};
  const statusMessage = useSelector((state) => state.chat.statusMessage);
  const jobMode = useSelector((state) => state.chat.jobMode);
  const yamlSave = useSelector((state) => state.chat.yamlSave);
  const [showDefaultPage, setShowDefaultPage] = useState(false);
  const dispatch = useDispatch();
  const { token } = getLocalStorageItem() || "";
  const messageData = useSelector((store) => store?.settings?.messageData);
  const hideMessage = useSelector((store) => store?.settings?.hideMessage);
  // page refresh issue fix
  useEffect(() => {
    const reloadFromApi = localStorage.getItem("reloadFromApi");
    if (!token) {
      navigate(userRoutes.login);
    } else if (reloadFromApi) {
      localStorage.removeItem("reloadFromApi");
    } else {
      getAllJobsApi({
        onSuccess: (jobData) => {
          const chats = jobData.chats.map((chat) => {
            let newChat = {
              ...chat,
            };
            dispatch(addNewChatAction(newChat));
            return newChat;
          });
          chats.reverse();
          const selectedChat = chats.filter((obj) => obj.chat_id === chat_id);
          dispatch(setSelectedChatAction(selectedChat[0]));
        },
        onError: (e) => {
          handleSessionExpiry(dispatch, e);
        },
      });
      triggerGetDatasources(dispatch);
      triggerGetApplication(dispatch);
      // triggerPipelineHistory(dispatch, chat_id);
    }
  }, []);

  useEffect(() => {
    setShowDefaultPage(false);

    if (selectedChat?.chat_id && location.search !== "") {
      setLoader(true);
      fetchHistory();
      triggerGetInfoAPI(dispatch, selectedChat?.chat_id);
      setShowDefaultPage(false);
    } else {
      setShowDefaultPage(true);
    }
  }, [selectedChat?.chat_id]);

  function fetchHistory() {
    chatHistoryApi({
      chatId: chat_id,
      params,
      onSuccess: (data) => {
        setLoader(false);
        if (!data.status && data.message) {
          messageApi.open({
            type: "error",
            content: data.message,
          });
        } else {
          const chatMessages = transformChatHistoryData(data.chat_history);

          triggerPipelineHistory(dispatch, chat_id);

          dispatch(
            setMessageParamsAction({
              offset: params.offset + 30,
            })
          );

          dispatch(
            setFetchChatHistoryAction({
              chat_id,
              value: data.has_more,
            })
          );

          dispatch(
            addNewMessageAction({
              chatId: chat_id,
              data: chatMessages,
              status: "update",
            })
          );
        }

        // setLoader(false);
      },
      onError: (error) => {
        setLoader(false);
        handleSessionExpiry(dispatch, error);
        // messageApi.open({
        //   type: "error",
        //   content: "This is an error message",
        // });
      },
    });
  }


  return (
    <ErrorFallback>
      {messageData && !hideMessage && (
        <div style={{ margin: "15px" }}>
          <CustomMessage
            type={messageData.type}
            message={messageData.message}
          />
        </div>
      )}
      {contextHolder}
      {jobMode === "python" ? (
        <InfoSection />
      ) : location.search === "" ? (
        <DefaultJobView setShowDefaultPage={setShowDefaultPage} />
      ) : (
        location?.pathname === chatRoutes?.chat && (
          <ADSpace className="overflowHidden flex-1 chat-preview-stack">
            {showPreview && jobMode !== "yaml" && <ADPreview />}
            {loader ? (
              <div
                className="items-center"
                style={{ width: showPreview ? "30%" : "100%" }}
              >
                <Space>
                  <Spin />
                  <span>Loading chat...</span>
                </Space>
              </div>
            ) : jobMode !== "yaml" ? (
              <ChatWindow showPreview={showPreview} />
            ) : jobMode === "yaml" ? (
              <>
                <ADPreview />
                <div className="info-section-wrapper">
                  <InfoSection />
                </div>
              </>
            ) : null}
          </ADSpace>
        )
      )}

    </ErrorFallback>
  );
};
export default ChatModule;
