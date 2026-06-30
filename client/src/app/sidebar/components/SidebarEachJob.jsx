import { Avatar, Button, Input, Tooltip, message } from "antd";
import {
  CloseOutlined,
  CheckOutlined,
  QuestionOutlined,
} from "@ant-design/icons";
import { useEffect, useRef, useState } from "react";
import { deleteChat, updateChat } from "../../../apis/chatService";
import {
  deleteChatAction,
  setSelectedChatAction,
  updateChatName,
} from "../../../store/actions/chatAction";
import { useDispatch, useSelector } from "react-redux";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import BeatLoader from "../../../components/ADLoader/BeatLoader/BeatLoader";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { setPreviewState } from "../../../store/actions/appActions";
import { useNavigate, useLocation } from "react-router-dom";
import { chatRoutes } from "../../../router/uiRouteConstants";
import { ADModal } from "../../../components/ADModal";
import { getNameForAvtar } from "../utils";
import { dispatchMessage } from "../../../utils/handleClick";
import { deleteDmsSchedule } from "../../../apis/jobScheduleService";
import { getLocalStorageItem } from "../../../utils/userData";
import { deleteDmsChatAction, setDmsSelectedChatAction, updateDmsChatName } from "../../../store/actions/dmsAction";

const SidebarEachJob = ({
  eachJob,
  sessionId,
  allJobs,
  setAllJobs,
  isHovered,
  isDmsMode = false,
}) => {
  const inputRef = useRef();
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const [messageApi, contextHolder] = message.useMessage();
  const selectedChat = useSelector((state) => state.chat.selectedChat);
  const selectedDmsChat = useSelector((state) => state.dms.selectedDmsChat);

  const isSidebarCollapsed = useSelector(
    (state) => state.app.isSidebarCollapsed
  );
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteModal, setDeleteModal] = useState({ open: false });
  const [updateNameLoading, setUpdateNameLoading] = useState(false);
  const { user } = getLocalStorageItem() || {};
  const jobName = isDmsMode ? eachJob.chat_name : eachJob.chat_name;
  const jobId = isDmsMode ? eachJob.chat_id : eachJob.chat_id;
  const [editData, setEditData] = useState({
    edit: false,
    id: "",
    newName: jobName,
  });

  useEffect(() => {
    if (inputRef?.current) {
      inputRef.current.focus();
    }
  }, [inputRef?.current]);

  function handleEditChatName() {
    setEditData((prev) => {
      return {
        ...prev,
        edit: true,
        id: jobId,
        newName: jobName,
      };
    });
  }

  const resetEditData = () => {
    setEditData({
      edit: false,
      id: "",
      newName: jobName,
    });
  };

  const handleChatNameUpdate = () => {
    if (!editData?.newName) {
      resetEditData();
      return;
    }
    if (editData?.newName.trim() !== jobName) {
      setUpdateNameLoading(true);
      const payload = {
        name: editData.newName.trim(),
        chat_id: jobId,
        sessionId,
      };
     if (isDmsMode) {
       payload.service_mode = "DMS";
     }
      resetEditData();
      updateChat({
        payload,
        onSuccess: (response) => {
          const { chat_id, chat_name } = response;
          if (isDmsMode) {
            dispatch(updateDmsChatName({ chat_id, chat_name }));
          } else {
            dispatch(updateChatName({ chat_id, chat_name }));
          }    
          setUpdateNameLoading(false);
          dispatchMessage(
            dispatch,
            "success",
            "Chat name updated successfully"
          );
        },
        onError: (error) => {
          handleSessionExpiry(dispatch, error);
          setUpdateNameLoading(false);
          dispatchMessage(dispatch, "error", "Chat name update failed");
        },
      });
    }
    resetEditData();
  };

  const handleInputChange = (e) => {
    setEditData((prev) => {
      return {
        ...prev,
        newName: e.target.value,
      };
    });
  };

  function handleDeleteChat() {
    setDeleteLoading(true);
      deleteChat({
        chatId: jobId,
        onSuccess: () => {
          dispatchMessage(dispatch, "success", "Chat deleted succesfully");
          dispatch(setPreviewState(false));
          if (isDmsMode) {
            dispatch(setDmsSelectedChatAction({}));
          } else {
            dispatch(setSelectedChatAction({}));
          }
          setDeleteLoading(false);
          if (isDmsMode) {
            dispatch(
              deleteDmsChatAction({
                chat_id: jobId,
              }),
            );
          } else {
            dispatch(
              deleteChatAction({
                chat_id: jobId,
              }),
            );
          }
          const updatedJobs = allJobs.filter((job) => {
            const currentId = job.chat_id;
            return currentId !== jobId;
          });
          setAllJobs(updatedJobs.length ? updatedJobs : []);
          if (isDmsMode) {
            navigate({
              pathname: chatRoutes.dms,
            });
          } else {
            navigate({
              pathname: chatRoutes.chat,
            });
          }
          setDeleteModal({
            open: false,
            chatId: null,
          });
        },
        onError: (error) => {
          handleSessionExpiry(dispatch, error);
          setDeleteLoading(false);
          dispatchMessage(dispatch, "error", "Chat deleted failed");
          setDeleteModal({
            open: false,
            chatId: null,
          });
        },
      });
    }
  const isEditMode = editData.edit && editData.id === jobId;
  const isSelected =
    (selectedChat?.chat_id === jobId || selectedDmsChat?.chat_id === jobId);

  const avatarName = getNameForAvtar(jobName);

  return (
    <>
      {contextHolder}
      <div
        className="job-item-container cursor-pointer dFlex alignCenter"
        key={jobId}
        data-testid={`job-item-id-${isDmsMode ? 'dms' : 'chat'}-${jobId}`}
      >
        <div
          className={`not-selected-job ${isSelected && "selected-job"}`}
        ></div>
        <div
          className={`${
            isSelected && "selected-job-name"
          } cursor-pointer job-name-container dFlex alignCenter overflowHidden w-100`}
        >
          <div
            style={{ width: "13%", marginRight: "10px", height: "51px" }}
            className="items-center"
          >
            <Avatar
              size={26}
              icon={<QuestionOutlined />}
              style={{ background: "#F28E1E" }}
            />
          </div>
          <div
            style={{
              width: "81%",
              justifyContent: "flex-start",
            }}
            className="text-ellipsis dFlex alignCenter"
            data-testid="input-outer-id"
          >
            <Input
              ref={inputRef}
              onPressEnter={handleChatNameUpdate}
              size={"small"}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) => {
                e.stopPropagation();
                handleInputChange(e);
              }}
              value={editData?.newName || ""}
              style={{ display: !isEditMode && "none" }}
              data-testid="editable-input"
            />
            <div
              style={{ display: isEditMode && "none", color: "#ffffff" }}
              className="text-ellipsis"
            >
              {updateNameLoading ? (
                <BeatLoader color="#096DD9" />
              ) : (
                <Tooltip title={jobName} placement="topLeft">
                  <span className="text-ellipsis job-name">{jobName}</span>
                </Tooltip>
              )}
            </div>
          </div>
          {((isSelected && !isSidebarCollapsed) || isHovered) && (
            <div className="buttons-container dFlex alignCenter">
              <Tooltip title={isEditMode ? "Update" : "Edit"}>
                <Button
                  size="small"
                  type="text"
                  data-testid="edit-btn-id"
                  icon={
                    isEditMode ? (
                      <CheckOutlined
                        style={{ color: "#fff", fontSize: "10px" }}
                      />
                    ) : (
                      <CustomIcon name="edit" />
                    )
                  }
                  onClick={(e) => {
                    e.stopPropagation();
                    isEditMode ? handleChatNameUpdate() : handleEditChatName();
                  }}
                />
              </Tooltip>

              {isEditMode ? (
                <Tooltip title="Cancel">
                  <Button
                    size="small"
                    type="text"
                    icon={
                      <CloseOutlined
                        style={{ color: "#fff", fontSize: "10px" }}
                      />
                    }
                    onClick={(e) => {
                      e.stopPropagation();
                      resetEditData();
                    }}
                    data-testid="close-btn-id"
                  />
                </Tooltip>
              ) : (
                <div data-testid="delete-confirm-id">
                  <Tooltip title="Delete">
                    <Button
                      type="text"
                      size="small"
                      icon={<CustomIcon name="delete" />}
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteModal({
                          open: true,
                          chatId: jobId,
                        });
                      }}
                      data-testid="delete-btn-id"
                    />
                  </Tooltip>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <ADModal
        title="Delete Job"
        description={
          <>
            Are you sure you want to delete Job: <b>{jobName}</b>? <br />
            {isDmsMode ? (
              <>Deleting this schedule will remove all associated data.<br />This action cannot be undone.</>
            ) : (
              <>Deleting this job will also remove all associated schedules.<br />This action cannot be undone.</>
            )}
          </>
        }
        open={deleteModal.open}
        onOk={handleDeleteChat}
        onCancel={() => setDeleteModal({ open: false, chatId: null })}
        okText="Delete"
        cancelText="Cancel"
        loading={deleteLoading}
        showCancelButton
        hideButtons={false}
      />
    </>
  );
};

export default SidebarEachJob;
