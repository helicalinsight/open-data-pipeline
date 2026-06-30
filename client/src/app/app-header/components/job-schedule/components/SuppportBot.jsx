import {
  SendOutlined,
  UndoOutlined,
  LoadingOutlined,
  InfoCircleOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import { Button, Card, Input, message, Space, Tooltip } from "antd";
import { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { resetBot, triggerBot } from "../../../../../apis/jobScheduleService";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry";
import { useDispatch } from "react-redux";
import { imagePath } from "../../../../../constants/appConstants";

import BeatLoader from "../../../../../components/ADLoader/BeatLoader/BeatLoader";
import { ACEHelpInfo } from "../constants";
import RenderMarkDown from "../../../../database-module/components/RenderMarkDown";
import { dispatchMessage } from "../../../../../utils/handleClick";

const SuppportBot = (props) => {
  const inputRef = useRef();
  const { messages, setMessages, selectedChat, setEditorValue } = props;
  const [messageApi, contextHolder] = message.useMessage();
  const [showHelpInfo, setShowHelpInfo] = useState(false);

  const dispatch = useDispatch();
  const botMessagesContainerRef = useRef(null);

  const [loading, setLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [userText, setUserText] = useState("");

  const handleReset = () => {
    setResetLoading(true);
    resetBot({
      payload: {
        chat_id: selectedChat?.chat_id,
      },
      onSuccess: (res) => {
        if (res.success) {
          setMessages([]);
          setEditorValue("");
          // messageApi.open({
          //   type: "success",
          //   content: res.message || "Reset successful",
          // });
          dispatchMessage(
            dispatch,
            "success",
            res.message || "Reset successful"
          );
        } else {
          // messageApi.open({
          //   type: "error",
          //   content: res?.message || "Reset failed",
          // });
          dispatchMessage(dispatch, "error", res?.message || "Reset failed");
        }
        setResetLoading(false);
      },
      onError: (err) => {
        setLoading(false);
        handleSessionExpiry(dispatch, err);
        setResetLoading(false);
        // messageApi.open({
        //   type: "error",
        //   content: err?.message || "Reset failed",
        // });
        dispatchMessage(dispatch, "error", err?.message || "Reset failed");
      },
    });
  };

  const handleSend = () => {
    if (!userText) return;

    setMessages((prev) => [
      ...prev,
      { id: uuidv4(), text: userText, isUser: true },
    ]);

    setLoading(true);
    setUserText("");

    triggerBot({
      payload: {
        user_text: userText,
        chat_id: selectedChat?.chat_id,
      },
      onSuccess: (res) => {
        setLoading(false);

        if (res.success) {
          if (res.code) {
            setEditorValue(res.code);
          }
        }
        if (res?.message) {
          setMessages((prev) => [
            ...prev,
            { id: uuidv4(), text: res.message, isUser: false },
          ]);
        }
      },
      onError: (err) => {
        setLoading(false);
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  useEffect(() => {
    if (inputRef?.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (botMessagesContainerRef.current) {
      botMessagesContainerRef.current.scrollTop =
        botMessagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const actions = [
    <div
      className={`dFlex justifyBetween prompt-container ${
        showHelpInfo && "disabled-cursor"
      }`}
    >
      <Input
        style={{ width: "300px", fontSize: "10px" }}
        onChange={(e) => setUserText(e.target.value)}
        value={userText}
        onPressEnter={handleSend}
        ref={inputRef}
        disabled={loading}
        data-testid="user-test-input"
        className="user-test-input"
        placeholder="Enter prompt"
      />
      <SendOutlined
        style={{
          fontSize: "18px",
          color: "#152A4F",
        }}
        data-testid="send-message-button"
        onClick={handleSend}
        className={`${loading !== false ? "disabled-cursor" : ""}`}
      />
    </div>,
  ];

  const hanldeHelpInfo = () => {
    setShowHelpInfo((prev) => !prev);
  };

  return (
    <>
      {contextHolder}
      <Card
        title={
          <div className="dFlex alignCenter">
            <img
              src={`${imagePath}/favicon.svg`}
              style={{
                height: "18px",
                marginRight: "5px",
              }}
              alt="logo"
            />
            <span
              style={{
                marginRight: "5px",
              }}
            >
              ACE Assistant
            </span>
            <Tooltip title={showHelpInfo ? "Hide Info" : "Show Info"}>
              {showHelpInfo ? (
                <CloseOutlined
                  style={{ color: "#ffffff" }}
                  onClick={hanldeHelpInfo}
                />
              ) : (
                <InfoCircleOutlined onClick={hanldeHelpInfo} />
              )}
            </Tooltip>
          </div>
        }
        actions={actions}
        size="small"
        className="pyspark-card"
        extra={
          !showHelpInfo && (
            <Tooltip title="Reset">
              {!resetLoading ? (
                <UndoOutlined
                  style={{ color: "#ffffff", transform: "rotate(90deg)" }}
                  onClick={handleReset}
                  data-testid="reset-messages-button"
                />
              ) : (
                <LoadingOutlined style={{ color: "#ffffff" }} />
              )}
            </Tooltip>
          )
        }
      >
        <div id="botMessagesContainer" ref={botMessagesContainerRef}>
          {loading && (
            <p className="loader">
              <BeatLoader color="#096DD9" />
            </p>
          )}
          {showHelpInfo ? (
            <div className="p-10">
              <RenderMarkDown description={ACEHelpInfo} />
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((message) => {
                const { isUser, text } = message;
                return (
                  <span
                    key={uuidv4()}
                    className={isUser ? "message user" : "message bot"}
                  >
                    {text}
                  </span>
                );
              })}
            </div>
          )}
        </div>
      </Card>
    </>
  );
};

export default SuppportBot;
