import { Button, message } from "antd";
import React, { useState } from "react";
import { ADSpace } from "../../../components";
import { useDispatch, useSelector } from "react-redux";
import { updateJobMode } from "../../../apis/chatService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../apis/commonAPIs";
import { ADModal } from "../../../components/ADModal";
import { dispatchMessage } from "../../../utils/handleClick";

const InfoSection = () => {
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const chatId = selectedChat?.chat_id;
  const [messageApi, contextHolder] = message.useMessage();
  const dispatch = useDispatch();
  const jobMode = useSelector((state) => state.chat.jobMode);
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const handleBackClick = () => {
    setDeleteLoading(true);
    const payload = {
      name: "llm",
      chatId,
    };
    updateJobMode({
      payload,
      onSuccess: (response) => {
        dispatchMessage(dispatch, "success", "Job Mode: LLM");
        triggerGetInfoAPI(dispatch, chatId);
        triggerPipelineHistory(dispatch, chatId);
        setDeleteModal(false);
        setDeleteLoading(false);
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);

        dispatchMessage(dispatch, "error", "Job Mode failed");
        setDeleteModal(false);
        setDeleteLoading(false);
      },
    });
  };

  return (
    <>
      {contextHolder}
      <div className="info-section">
        <div className="content">
          {jobMode === "python" ? (
            <p>
            In this mode, you can write code with assistance. Click the
              <strong> ACE Editor </strong>
              icon to access the editor. You won't be able to view or interact
              with your AI-prepared data pipeline in this mode. Switch back to
              interactive mode to do so.
            </p>
          ) : (
            <p>
              You are currently in <strong> YAML</strong> mode, where
              interactive functionality is unavailable. Please click{" "}
              <a
                onClick={(e) => {
                  e?.preventDefault();
                  setDeleteModal(true);
                }}
                className="link"
              >
                close
              </a>{" "}
              to switch to interactive mode.
            </p>
          )}
        </div>
        {jobMode === "python" && (
          <ADSpace justifyContent="center">
            <Button
              className="back-button"
              size="large"
              type="primary"
              onClick={() => setDeleteModal(true)}
              style={{ boxShadow: "none" }}
              data-testid="back-mode"
            >
              Back
            </Button>
          </ADSpace>
        )}
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
      </div>
    </>
  );
};

export default InfoSection;
