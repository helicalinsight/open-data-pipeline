import { Button, Input, Popover, Space, message } from "antd";
import React, { useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import UploadItem from "../../message-module/components/UploadItem";
import { ADSpace } from "../../../components";
import { setAPICallStatus } from "../../../store/actions/chatAction";
import { useDispatch, useSelector } from "react-redux";
import { deleteFile, uploadFileApi } from "../../../apis/fileService";
import { useSearchParams } from "react-router-dom";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { SearchOutlined, UploadOutlined } from "@ant-design/icons";
import FilesTable from "./editable-table/FilesTable";
import {
  deleteSavedConnection,
  setSavedConnections,
} from "../../../store/actions/databaseActions";
import CloseButton from "./CloseButton";
import handleBackClick, { dispatchMessage } from "../../../utils/handleClick";

export const FlatFiles = ({ current, setCurrent }) => {
  const dispatch = useDispatch();
  const inputRef = useRef();
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [messageApi, contextHolder] = message.useMessage();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchParms] = useSearchParams();
  const [fileList, setFileList] = useState({});
  const [open, setOpen] = useState(false);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteFileIds, setDeleteFileIds] = useState([]);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const chat_id = searchParms.get("chat");
  const savedConnections = useSelector(
    (state) => state.database.savedConnections
  );
  const allPreferences = useSelector(
    (store) => store?.settings?.allPreferences
  );

  const uploadFileSizeLimit = allPreferences?.files?.file_size || 5;

  const editConnection = useSelector((store) => store.database.editConnection);
  const handleFileUpload = async (allFiles) => {
    let apiCallsList = [];

    for (const fileId in allFiles) {
      const abortController = new AbortController();
      const signal = abortController.signal;
      const file = allFiles[fileId];

      apiCallsList.push(
        uploadFileApi({
          formdata: { file: file },
          onSuccess: (res) => {
            const { success, filesUploaded } = res;
            setFileList((prev) => {
              let files = { ...prev };
              files[file.id].progress = 100;
              files[file.id].status = success ? "uploaded" : "failed";
              return { ...files };
            });

            const isExists = savedConnections.some(
              (connection) => connection._id === filesUploaded?._id
            );

            if (success && filesUploaded && !isExists) {
              // messageApi.open({
              //   type: "success",
              //   content: `${file.name} uploaded successfully`,
              // });
              dispatchMessage(
                dispatch,
                "success",
                `${file.name} uploaded successfully`
              );
              dispatch(
                setSavedConnections({
                  key: "insert",
                  data: [filesUploaded],
                })
              );
            } else if (isExists) {
              // messageApi.open({
              //   type: "success",
              //   content: `${file.name} overwritten successfully`,
              // });
              dispatchMessage(
                dispatch,
                "success",
                `${file.name} overwritten successfully`
              );
            }
          },
          signal, // to abort API
          progressEvent: (event) => {
            let progress = Math.floor(event.progress * 100);
            setFileList((prev) => {
              let files = { ...prev };
              files[file.id].progress = progress - 1;
              files[file.id].status = "uploading";
              return { ...files };
            });
            const apiData = {
              name: "upload",
              isFetching: true,
              abortController,
            };
            dispatch(setAPICallStatus({ chat_id, apiData }));
          },
          onError: (error) => {
            setFileList((prev) => {
              let files = { ...prev };
              files[file.id].progress = 0;
              files[file.id].status = "failed";
              return files;
            });
            // messageApi.open({
            //   type: "error",
            //   content:
            //     error?.message || `Failed to upload the file. Please try again`,
            // });
            dispatchMessage(
              dispatch,
              "error",
              error?.message || `Failed to upload the file. Please try again`
            );
            handleSessionExpiry(dispatch, error);
          },
        })
      );
    }

    Promise.allSettled(apiCallsList).then(() => {
      const apiData = {
        name: "upload",
        isFetching: false,
        abortController: null,
      };
      setFileList({});
      dispatch(setAPICallStatus({ chat_id, apiData }));
    });
  };

  const handleFileChange = (event) => {
    const files = event?.target?.files;
    let allFiles = {};
    const allowedExtensions = [".csv", ".xlsx"];

    for (let i = 0; i < files?.length; i++) {
      const fileName = files[i]?.name?.toLowerCase();
      const isAllowed = allowedExtensions?.some((ext) =>
        fileName?.endsWith(ext)
      );
      if (!isAllowed) {
        dispatchMessage(
          dispatch,
          "warning",
          `${files[i].name} is not a valid file type.`
        );
        continue;
      }
      if (files[i].size > uploadFileSizeLimit * 1000000) {
        dispatchMessage(
          dispatch,
          "warning",
          `Cannot upload ${files[i].name} as size is greater than ${uploadFileSizeLimit}MB`
        );
      } else {
        let id = uuidv4();
        files[i].id = id;
        files[i].progress = 0;
        files[i].status = null;
        allFiles = {
          ...allFiles,
          [id]: files[i],
        };
      }
    }
    if (Object.keys(allFiles)?.length > 0) {
      setFileList((prevFiles) => ({
        ...prevFiles,
        ...allFiles,
      }));
      handleFileUpload(allFiles);
    }
    event.target.value = "";
  };

  const handleFileRemove = (file) => {
    setFileList((prev) => {
      let files = { ...prev };
      delete files[file.id];
      return files;
    });
  };

  const renderPopoverContent = () => {
    return (
      <div style={{ width: "300px" }}>
        <ADSpace stack="vertical" space="4">
          {Object.values(fileList)?.map((file, i) => {
            return (
              <UploadItem
                file={file}
                handleFileRemove={handleFileRemove}
                key={file.id}
                index={i + 1}
                uploadFileSizeLimit={uploadFileSizeLimit}
              />
            );
          })}
        </ADSpace>
      </div>
    );
  };

  const handleDeleteFiles = () => {
    setDeleteLoading(true);

    deleteFile({
      fileIds: deleteFileIds,
      onSuccess: (res) => {
        let keys = deleteFileIds;
        if (res?.failed_file_ids?.length) {
          keys = keys.filter((key) => !res.failed_file_ids.includes(key));
          const deletedNum =
            selectedRowKeys.length - res.failed_file_ids.length;
          // messageApi.open({
          //   type: "success",
          //   content: `Deleted ${deletedNum} Files`,
          // });
          dispatchMessage(dispatch, "success", `Deleted ${deletedNum} Files`);
        } else {
          // messageApi.open({
          //   type: "success",
          //   content: `Deleted Succesfully`,
          // });
          dispatchMessage(dispatch, "success", `Deleted Succesfully`);
        }
        setSelectedRowKeys([]);
        dispatch(deleteSavedConnection(keys));
        setDeleteLoading(false);
        setOpenDeleteModal(false);
        setDeleteFileIds([]);
      },
      onError: (error) => {
        setDeleteLoading(false);
        messageApi.open({
          type: "error",
          content: `Failed to delete`,
        });
        handleSessionExpiry(dispatch, error);
      },
    });
  };

  return (
    <>
      {contextHolder}
      <div className="flat-files-container dFlex flexColumn h-100">
        <div className="files-header-container dFlex alignCenter justifyBetween">
          <Space>
            <Button
              style={{ marginLeft: "7px" }}
              onClick={() => {
                inputRef.current.click();
              }}
              disabled={selectedRowKeys.length}
              type="primary"
              data-testid="upload-files-btn"
            >
              Upload Files
            </Button>
            {selectedRowKeys?.length > 0 && (
              <Button
                type="primary"
                data-testid="multi-file-delete-btn"
                onClick={() => {
                  setDeleteFileIds(selectedRowKeys);
                  setOpenDeleteModal(true);
                }}
              >
                {`Delete ${selectedRowKeys?.length} ${
                  selectedRowKeys?.length > 1 ? "files" : "file"
                }`}
              </Button>
            )}
          </Space>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Input
              allowClear
              placeholder="Search name"
              enterButton
              // suffix={<SearchOutlined />}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: "200px" }}
              data-testid="search-name-id"
            />
            {/* <CloseButton
              handleClose={() =>
                handleBackClick(dispatch, editConnection, setCurrent, current)
              }
            /> */}
          </div>
        </div>
        <div className="files-table-container flex-1">
          <FilesTable
            searchTerm={searchTerm}
            selectedRowKeys={selectedRowKeys}
            setSelectedRowKeys={setSelectedRowKeys}
            handleDeleteFiles={handleDeleteFiles}
            openDeleteModal={openDeleteModal}
            setOpenDeleteModal={setOpenDeleteModal}
            deleteLoading={deleteLoading}
            deleteFileIds={deleteFileIds}
            setDeleteFileIds={setDeleteFileIds}
            messageApi={messageApi}
          />
        </div>
        {Object.values(fileList).length > 0 && (
          <Space className="uploading-files-conatiner items-center">
            <span> Uploading {Object.values(fileList).length} files</span>
            <Popover
              content={renderPopoverContent()}
              data-testid="popover"
              trigger="click"
              open={open}
              onOpenChange={(newOpen) => setOpen(newOpen)}
            >
              <div className="rainbow">
                <Button
                  type="primary"
                  shape="circle"
                  size="small"
                  icon={<UploadOutlined className="anticon-upload-outlined" />}
                  className="button"
                />
              </div>
            </Popover>
          </Space>
        )}
        <input
          ref={inputRef}
          style={{ display: "none" }}
          type="file"
          onChange={handleFileChange}
          data-testid="upload-input"
          multiple
          accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
        />
      </div>
    </>
  );
};
