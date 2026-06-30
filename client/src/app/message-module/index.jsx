import { CopyOutlined, QuestionOutlined } from "@ant-design/icons";
import { Avatar, Space, Button, Tooltip } from "antd";
import CustomResponses from "./components/CustomResponses";
import "./style.scss";
import { ADSpace } from "../../components";
import { useSelector } from "react-redux";
import React, { useState } from "react";
import removeMd from "remove-markdown";

function MessageLayout({ chatItem, index }) {
  const [copied, setCopied] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleCopyText = () => {
    const plainText = removeMd(chatItem.text);
    navigator.clipboard.writeText(plainText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  const previewState = useSelector((state) => state.app.previewState);
  if (chatItem.type === "connected" || chatItem.type === "disconnected") {
    return (
      <div className="message-container__notification-text text-center">
        {chatItem.text}
      </div>
    );
  } else {
    return (
      <div
        className="message-container dFlex"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <ADSpace space="8">
          {!chatItem.isUser && (
            <div data-testid="bot-message">
              <Avatar
                size={30}
                icon={<QuestionOutlined />}
                style={{ background: "#F28E1E" }}
              />
            </div>
          )}
          <div className="message-content-wrapper">
            <ADSpace
              stack="vertical"
              alignItem={chatItem.isUser ? "end" : "start"}
              data-testid="message-id"
            >
              <div
                className={
                  chatItem.isUser
                    ? "message-container__chat-message message-container__chat-message-user"
                    : "message-container__chat-message message-container__chat-message-bot"
                }
                style={{
                  maxWidth: previewState ? "95%" : "60%",
                  position: "relative",
                }}
              >
                {isHovered && (
                  <div className="copy-action">
                    <Tooltip
                      title={!copied && "Copy"}
                      overlayClassName="custom-tooltip"
                    >
                      <button
                        onClick={handleCopyText}
                        className="chat-copy-btn"
                      >
                        {copied ? "Copied!" : <CopyOutlined />}
                      </button>
                    </Tooltip>
                  </div>
                )}
                <CustomResponses item={chatItem} index={index} />
                {isHovered && (
                  <div className="message-time">{chatItem.time}</div>
                )}
              </div>
            </ADSpace>
          </div>
        </ADSpace>
      </div>
    );
  }
}

export default MessageLayout;
