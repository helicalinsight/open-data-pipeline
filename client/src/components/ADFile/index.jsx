import React, { useEffect, useRef, useState } from "react";
import { Input, Tooltip, message } from "antd";
import CustomIcon from "../ADIcons/custom-icon";
import "./style.scss";
import {
  addLoadedFilesAction,
  setOpenInfo,
  setPreviewTableData,
  setSelectedFilesAction,
} from "../../store/actions/chatAction";
import { useSearchParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { handleSessionExpiry } from "../../utils/handleSessionExpiry";
import {
  deleteDataPreviewFile,
  switchSelectedFile,
  updateName,
} from "../../apis/fileService";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../apis/commonAPIs";
import { ADModal } from "../ADModal";
import { dispatchMessage } from "../../utils/handleClick";
import { CheckOutlined, CloseOutlined } from "@ant-design/icons";

const ADFile = (props) => {
  const { name, style, type, source_id, onClick, fileId } = props;
  const inputRef = useRef(null);
  const dispatch = useDispatch();
  const [edit, setEdit] = useState(false);
  const [value, setValue] = useState();
  const [onHover, setOnHover] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();
  const [searchParms] = useSearchParams();
  const chatId = searchParms.get("chat");
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const loadedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.loadedFiles) || [];
  const pipelineHistory =
    useSelector((state) => state.chat.chatList[chatId]?.pipelineHistory) || {};
  const onEdit = (e) => {
    e.stopPropagation();
    setEdit(true);
    setValue(value);
  };

  useEffect(() => {
    if (edit && inputRef?.current) {
      inputRef.current.focus();
    }
  }, [edit]);

  useEffect(() => {
    setValue(name);
  }, [name]);

  const handleEdit = (e) => {
    e.stopPropagation();
    setEdit(false);

    if (!value) return;
    const isDuplicateName = loadedFiles.find(
      (file) => file?.alias?.toLowerCase() === value?.toLowerCase()
    );
    if (isDuplicateName) {
      setValue(name);
      // messageApi.open({
      //   type: "warning",
      //   content: "File name can not be same",
      // });
      dispatchMessage(dispatch, "warning", "File name can not be same");
      return;
    }
    const payload = {
      source_id,
      new_file_name: value,
      chat_id: chatId,
    };
    updateName({
      payload,
      onSuccess: (res) => {
        if (!res.success) return;
        // messageApi.open({
        //   type: "success",
        //   content: res?.message || "File renamed successfully.",
        // });
        dispatchMessage(
          dispatch,
          "success",
          res?.message || "File renamed successfully."
        );
        dispatch(
          addLoadedFilesAction({
            chat_id: chatId,
            payload,
          })
        );
      },
      onError: (e) => {
        handleSessionExpiry(dispatch, e);
        setValue(name);
        // messageApi.open({
        //   type: "error",
        //   content: "Failed to rename the file.",
        // });
        dispatchMessage(dispatch, "error", "Failed to rename the file.");
      },
    });
  };

  const handleCancel = (e) => {
    e.stopPropagation();
    setEdit(false);
    setValue(name);
  };
  const handleClick = () => {
    dispatch(setOpenInfo(false));
    if (deleteModal) return;
    if (typeof onClick === "function") {
      onClick({
        source_id,
        alias: name,
      });
    }
  };
  const handleDelete = () => {
    setDeleteLoading(true);
    deleteDataPreviewFile({
      payload: {
        chat_id: chatId,
        source_id: source_id,
      },
      onSuccess: (res) => {
        messageApi.open({
          type: "success",
          content: res?.message,
        });
        dispatch(setPreviewTableData({ columns: [], datasource: {} }));
        const updatedFiles = loadedFiles?.filter(
          (file) => file?.source_id !== source_id
        );
        if (updatedFiles?.length > 0) {
          const firstFile = updatedFiles[0];
          switchSelectedFile({
            payload: {
              chat_id: chatId,
              source_id: firstFile.source_id,
            },
            onSuccess: (res) => {
              if (res.success) {
                dispatch(
                  setSelectedFilesAction({
                    chat_id: chatId,
                    files: [firstFile],
                  })
                );
                triggerGetInfoAPI(dispatch, chatId);
                triggerPipelineHistory(dispatch, chatId);
              }
            },
            onError: (err) => {
              handleSessionExpiry(dispatch, err);
            },
          });
        } else {
          dispatch(setSelectedFilesAction({ chat_id: chatId, files: [] }));
          triggerGetInfoAPI(dispatch, chatId);
          triggerPipelineHistory(dispatch, chatId);
        }
        setDeleteModal(false);
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
        messageApi.open({
          type: "error",
          content: "Failed to delete the file.",
        });
      },
      finally: () => setDeleteLoading(false),
    });
  };
  const matchingConnection = pipelineHistory?.connections?.find(
    (conn) => conn?._id === fileId
  );
  const displayName = type === "table" ? "Table name" : "File name";
  const infoItems = matchingConnection
    ? [
        [displayName, name],
        ["Datasource name", matchingConnection.type || ""],
        ["Connection name", matchingConnection.alias || ""],
        ["Connection Id", matchingConnection._id || ""],
      ]
    : [[displayName, name]];

  const tooltipTitle = (
    <div style={{ fontSize: "10px", whiteSpace: "pre-line" }}>
      {infoItems?.map(([label, value]) => (
        <div key={label}>
          <strong>{label} :</strong> {value}
        </div>
      ))}
    </div>
  );

  return (
    <>
      {contextHolder}
      <Tooltip title={tooltipTitle}>
        <div
          style={style || {}}
          className="file-button-container cursor-pointer"
          onMouseEnter={() => setOnHover(true)}
          onMouseLeave={() => setOnHover(false)}
          data-testid={`ad-file-${source_id}`}
          onClick={handleClick}
        >
          {type === "table" ? (
            <CustomIcon
              name="table"
              data-testid="file-image-id"
              style={{ fontSize: "15px", marginRight: "4px" }}
            />
          ) : (
            <CustomIcon
              data-testid="file-image-id"
              name="csv"
              style={{ fontSize: "15px", marginRight: "4px" }}
            />
          )}
          {edit ? (
            <>
              <Input
                onChange={(e) => {
                  e.stopPropagation();
                  setValue(e.target.value);
                }}
                onClick={(e) => e.stopPropagation()}
                ref={inputRef}
                className="file-name-input"
                value={value}
                data-testid="file-name-input-id"
              />
              <CheckOutlined
                name="check"
                // style={{ cursor: "pointer", marginLeft: "5px" }}
                onClick={handleEdit}
                className="icon-size"
                style={{
                  cursor: "pointer",
                  marginLeft: "5px",
                  color: "green",
                }}
                data-testid="check-icon-id"
              />
              <CloseOutlined
                name="close"
                style={{
                  cursor: "pointer",
                  marginLeft: "5px",
                  color: "red",
                }}
                onClick={handleCancel}
                className="icon-size"
                data-testid="close-icon-id"
              />
            </>
          ) : (
            <span className="text-ellipsis" data-testid="file-name-id">
              {value}
            </span>
          )}
          {onHover && !edit && (
            <>
              <CustomIcon
                name="edit"
                style={{ cursor: "pointer" }}
                onClick={onEdit}
                className="edit-icon icon-size"
                color="#000"
                data-testid="edit-icon-id"
              />
              <CustomIcon
                name="delete"
                className="edit-icon icon-size"
                color="#000"
                onClick={(e) => {
                  e.stopPropagation();
                  setDeleteModal(true);
                }}
                data-testid="delete-icon-id"
              />
            </>
          )}
          <ADModal
            title="Delete File"
            description={
              <>
                Are you sure you want to delete File: <strong>{name}</strong>?
              </>
            }
            open={deleteModal}
            onOk={handleDelete}
            onCancel={() => setDeleteModal(false)}
            okText="Delete"
            cancelText="Cancel"
            loading={deleteLoading}
            showCancelButton
            hideButtons={false}
          />
        </div>
      </Tooltip>
    </>
  );
};

export default ADFile;
