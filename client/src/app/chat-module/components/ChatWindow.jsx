import { Spin } from "antd";
import { useEffect, useRef, useState } from "react";
import { getLocalStorageItem } from "../../../utils/userData";
import { ChatContext } from "./ChatContext";
import { useDispatch, useSelector } from "react-redux";
import { useSearchParams } from "react-router-dom";
import { ADSpace } from "../../../components";
import { addNewMessageAction } from "../../../store/actions/messageActions";
import { chatHistoryApi, completionApi } from "../../../apis/chatService";
import { transformChatHistoryData } from "../utils";
import { LoadingOutlined } from "@ant-design/icons";
import { v4 as uuidv4 } from "uuid";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../apis/commonAPIs";
import {
  setFetchChatHistoryAction,
  setAPICallStatus,
} from "../../../store/actions/chatAction";

import MessageLayout from "../../message-module";
import InfiniteScroll from "react-infinite-scroll-component";
import ADMessageBox from "../../../components/ADMessageBox";
import getTimeStamp from "../../../utils/getCurrentTime";

import "../style.scss";
import { dispatchMessage } from "../../../utils/handleClick";

function ChatWindow({ showPreview }) {
  const { user } = getLocalStorageItem() || {};
  const [searchParms] = useSearchParams();
  const [botStatus, setBotStatus] = useState(false);

  const dispatch = useDispatch();
  const chatId = searchParms.get("chat");
  const userConfig = useSelector((state) => state?.app?.userConfig);
  const previewState = useSelector((state) => state.app.previewState);
  const messages =
    useSelector((state) => state.messages?.allMessages[chatId]) || [];
  const selectedChat = useSelector((state) => state.chat?.selectedChat) || {};
  const columnList =
    useSelector((state) => state.chat?.chatList[chatId]?.columnList) || [];
  const selectedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.selectedFiles) || [];
  const fetchChatHistory = useSelector(
    (state) => state.chat?.chatList[chatId]?.fetchChatHistory
  );
  const loadedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.loadedFiles) || [];

  const messagesEndRef = useRef(null);
  const scrollToBottom = () => {
    messagesEndRef?.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  function handleLoadMore() {
    const filteredMessages = messages.filter(
      (eachMessage) =>
        eachMessage.type !== "connected" || eachMessage.type !== "disconnected"
    );
    chatHistoryApi({
      chatId: selectedChat.chat_id,
      params: {
        offset: filteredMessages.length,
        limit: 30,
      },
      onSuccess: (data) => {
        const chatMessages = transformChatHistoryData(data.chat_history);
        dispatch(
          setFetchChatHistoryAction({
            chat_id: chatId,
            value: data.has_more,
          })
        );

        dispatch(
          addNewMessageAction({
            chatId: selectedChat?.chat_id,
            data: chatMessages,
            isHistory: true,
          })
        );
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
      },
    });
  }

  useEffect(() => {
    const apiData = {
      name: "bot",
      isFetching: botStatus === "Ask On Data is typing" ? true : false,
    };
    dispatch(setAPICallStatus({ chat_id: chatId, apiData }));
  }, [botStatus]);

  const handleSendMessage = async (data) => {
    setBotStatus("Ask On Data is typing");
    dispatch(
      addNewMessageAction({
        chatId,
        data: [
          {
            isUser: true,
            text: data?.title,
            message_id: uuidv4(),
            time: getTimeStamp(),
          },
        ],
      })
    );
    const payload = {
      input_text: data?.title,
      chat_id: chatId,
      user_id: user?.id,
    };

    completionApi({
      payload,
      onSuccess: (response) => {
        setBotStatus(false);
        const { messages } = response.event || {};
        if (messages[0]?.message !== "") {
          const { message, message_id, details } = messages[0];
          const data = {
            isUser: false,
            text: message,
            message_id,
            time: getTimeStamp(),
          };
          if (messages[0]?.export && details?.export_details) {
            data["shipment"] = {
              download_files: [details.export_details],
            };
          }
          dispatch(
            addNewMessageAction({
              chatId,
              data: [data],
            })
          );
        }
        if (messages[0]?.details?.refresh) {
          triggerGetInfoAPI(dispatch, chatId, { refresh: true });
          triggerPipelineHistory(dispatch, chatId);
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        dispatchMessage(
          dispatch,
          "error",
          error?.msg || "Something went wrong. Please try again."
        );
        setBotStatus(false);
      },
    });
  };
  function handlePromtBtnClick(data) {
    // handleSendMessage(data);
    handleSendMessage(data);
  }
  return (
    <ChatContext.Provider value={{ handleMessage: handlePromtBtnClick }}>
      <ADSpace
        stack="vertical"
        className={`chat-section overflowHidden flex-1 ${
          showPreview ? "chat-preview" : "no-preview"
        }`}
      >
        <ADSpace
          id="scrollableDiv"
          className={`chat-section__content flex-1 ${
            previewState && "hide-job"
          }`}
        >
          <InfiniteScroll
            dataLength={messages.length}
            next={handleLoadMore}
            hasMore={fetchChatHistory}
            style={{
              display: "flex",
              flexDirection: "column-reverse",
              overflow: "hidden",
              margin: "0px 10px 10px 10px ",
            }}
            loader={
              <ADSpace
                alignItem="center"
                justifyContent="center"
                style={{ padding: "5px" }}
              >
                <Spin
                  tip="Loading"
                  size="large"
                  indicator={<LoadingOutlined />}
                />
              </ADSpace>
            }
            inverse={true}
            scrollableTarget="scrollableDiv"
            // endMessage={}
          >
            {messages &&
              messages.map((item, index) => (
                <MessageLayout
                  chatItem={item}
                  key={item.message_id + "-" + index}
                  index={index}
                />
              ))}
          </InfiniteScroll>
        </ADSpace>
        <div ref={messagesEndRef} />
        <ADSpace stack="vertical">
          <ADMessageBox
            botStatus={botStatus}
            handleMessageSent={handleSendMessage}
            columns={columnList}
            loadedFiles={loadedFiles}
            selectedFiles={selectedFiles}
            chatId={chatId}
          />
          {userConfig?.role === "free" && (
            <div className="chat-section__content-beta-message text-ellipsis">
              **This is the free edition. Please contact us to learn more about
              our Enterprise Edition and its comprehensive capabilities. Feel
              free to inquire now.
            </div>
          )}
        </ADSpace>
      </ADSpace>
    </ChatContext.Provider>
  );
}

export default ChatWindow;
