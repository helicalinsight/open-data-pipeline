import { useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useSearchParams } from "react-router-dom";
import { Button, Table, Tooltip, message, Skeleton, Space } from "antd";
import {
  EditOutlined,
  DeleteOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import {
  dataLoads,
  deleteConnection,
  getConnection,
  testConnection,
} from "../../../apis/databaseService";
import { ADModal } from "../../../components/ADModal";
import {
  deleteSavedConnection,
  setConnectionsStatus,
  setDataSourceConnectionName,
  setEditConnection,
  setSelectedConnection,
  setTestConnectionMessage,
} from "../../../store/actions/databaseActions";
import { addNewMessageAction } from "../../../store/actions/messageActions";
import { getEachConnStatus } from "./utils";
import { v4 as uuidv4 } from "uuid";
import { removeFirstDot } from "../utils/arrayOperations";
import { searchItemFilterData } from "../utils/searchItemFilterData";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../apis/commonAPIs";

import CustomIcon from "../../../components/ADIcons/custom-icon";
import getTimeStamp from "../../../utils/getCurrentTime";
import { setSidebarState } from "../../../store/actions/appActions";
import { dispatchMessage } from "../../../utils/handleClick";
import { setDestinationConnectionIdAction, setSourceConnectionIdAction } from "../../../store/actions/dmsAction";
import { isDmsRoute } from "../../../router/uiRouteConstants";

const SavedDbConnections = (props) => {
  const {
    module,
    selectedConnection,
    setActiveTab,
    setIsEdit,
    handleClose,
    searchTerm,
    mode,
    getConnectionId,
    savedList,
    getData,
  } = props;
  const dispatch = useDispatch();
  const location = useLocation();
  const [searchParams] = useSearchParams() || [];
  const [deleteModal, setDeleteModal] = useState({
    open: false,
    connectionId: null,
  });
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("");
  const [messageApi, contextHolder] = message.useMessage();
  const savedConnections = useSelector(
    (state) => state.database.savedConnections,
  );
  const savedConnApiStatus = useSelector(
    (state) => state.database.savedConnApiStatus,
  );

  const chatId = searchParams?.get("chat");
  const selectedDatasource = useSelector(
    (store) => store.database.selectedDatasource,
  );
  const loadedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.loadedFiles) || [];
  const step = useSelector((state) => state.dms.step);
  const isDms = isDmsRoute(location.pathname);
  const selectedPipelineMode = useSelector(
    (state) => state.dms.selectedPipelineMode,
  );
  const [asyncOperationsCompleted, setAsyncOperationsCompleted] =
    useState(false);

  const memoizedData = useMemo(() => {
    return (
      savedConnections?.map((connection) => ({
        ...connection,
        key: connection?._id,
      })) || []
    );
  }, [savedConnections]);

  const memoizedDataSource = useMemo(() => {
    return searchItemFilterData(memoizedData, searchTerm);
  }, [searchTerm, memoizedData]);
  const isFlatFile = selectedDatasource?.driver === "flat_files";
  const handleEdit = (record) => {
    getConnection({
      query: `connection_id=${record._id}`,
      onSuccess: (response) => {
        if (response.success) {
          dispatch(setEditConnection(response.connection_data));
          setActiveTab && setActiveTab("1");
          setIsEdit && setIsEdit(true);
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
      },
    });
  };

  const handleDelete = (record) => {
    setDeleteModal({ open: true, connectionId: record._id });
  };

  const handleDeleteConfirm = () => {
    const payload = { _id: deleteModal.connectionId };

    deleteConnection({
      payload,
      onSuccess: (response) => {
        dispatch(deleteSavedConnection(response.connection_id));
        dispatchMessage(
          dispatch,
          "success",
          response.msg || "Connection deleted successfully!!",
        );
        setDeleteModal({ open: false, connectionId: null });
        getData();
      },
      onError: (error) => {
        setDeleteModal({ open: false, connectionId: null });
        handleSessionExpiry(dispatch, error);
      },
    });
  };

  if (asyncOperationsCompleted) {
    handleClose();
  }
  const handleTest = (record, type) => {
    return new Promise((resolve, reject) => {
      const payload = {
        type: "test",
        connector: selectedDatasource.driver,
        details: {
          connection_id: record?._id,
        },
      };
      testConnection({
        payload,
        onSuccess: (response) => {
          if (typeof setConnectionsStatus === "function") {
            dispatch(setConnectionsStatus(true));
          }
          setConnectionStatus("success");
          dispatchMessage(
            dispatch,
            "success",
            response.msg || "Connection Tested successfully",
            true,
          );
          dispatch(setTestConnectionMessage(response.msg));
          resolve(response);
        },
        onError: (error) => {
          dispatchMessage(
            dispatch,
            "error",
            error?.message || "Test connection failed",
          );
          setConnectionStatus("failed");
          handleSessionExpiry(dispatch, error);
          reject(error);
        },
      });
    });
  };

  const handleLoad = (record) => {
    dispatch(
      setSelectedConnection({
        source: isFlatFile ? "flat_files" : "database",
        connection_id: record._id,
        ...record,
      }),
    );

    if (isFlatFile) {
      dispatch(setConnectionsStatus(true));
    } else {
      setConnectionStatus("fetching");
      handleTest(record, "connect");
    }
  };

  const handleConnect = async (record) => {
        if (isDms) {
          const isDestinationStep = step === 2;
          const isSourceCustomSql =
            step === 1 && selectedPipelineMode === "custom_sql";
          if (isDestinationStep || isSourceCustomSql) {
            const action = isDestinationStep
              ? setDestinationConnectionIdAction
              : setSourceConnectionIdAction;
            const message = isDestinationStep
              ? "Destination connection id saved"
              : "Source connection id saved";
            dispatch(action(record._id));
            dispatchMessage(dispatch, "success", message, true);
            handleClose();
            return;
          }
        }
    dispatch(setDataSourceConnectionName(record?.alias));
    if (mode === "schedule") {
      if (isFlatFile) {
        getConnectionId({
          ...record,
          driver: selectedDatasource.driver,
        });
        handleClose();
      } else {
        try {
          const response = await handleTest(record, "connect");
          if (response?.success) {
            getConnectionId({
              ...record,
              driver: selectedDatasource.driver,
            });
            handleClose();
          }
        } catch (error) {
          console.error("Connection failed:", error);
        }
      }
    } else {
      handleLoad(record);
    }
  };

  const dataSource = useMemo(() => {
    const sortedDataSource = (source) =>
      [...source]?.sort((a, b) =>
        a?.alias?.localeCompare(b?.alias, undefined, { sensitivity: "base" }),
      );
    if (module === "load") {
      return sortedDataSource(memoizedDataSource);
    }
    return sortedDataSource(savedList?.databases || []);
  }, [module, savedList, memoizedDataSource]);

  const columns = [
    {
      title: "S.No",
      key: "serialNum",
      render: (...args) => args[2] + 1,
      width: 100,
    },
    {
      title: "Connection Name",
      dataIndex: "alias",
      key: "alias",
      onHeaderCell: () => ({
        title: "",
      }),
      ellipsis: true,
      render: (text, record) => {
        const iconName = removeFirstDot(record.fileType);
        return (
          <Space>
            {iconName && (
              <CustomIcon name={iconName} style={{ fontSize: "20px" }} />
            )}
            <span>{text}</span>
          </Space>
        );
      },
    },
    ...(isFlatFile
      ? [
          {
            title: "File Type",
            dataIndex: "fileType",
            key: "fileType",
          },
        ]
      : []),
    {
      title: "Actions",
      dataIndex: "",
      key: "",
      render: (record) => {
        if (module === "load") {
          const eachConnStatus = getEachConnStatus(
            connectionStatus,
            selectedConnection,
            record,
          );
          if (eachConnStatus === "failed") {
            return (
              <Button type="primary" disabled size="small">
                Edit
              </Button>
            );
          }
          const tooltipText = isFlatFile
            ? record.fileType === ".xlsx"
              ? "Select sheet or columns for an Excel file"
              : "Select columns for a CSV file"
            : "";
          return (
            <>
              <Tooltip
                title={`Connection Id : ${record?._id}`}
                overlayClassName="custom-tooltip"
              >
                <InfoCircleOutlined className="info-icon-font connection " />
              </Tooltip>
              <Tooltip title={tooltipText} overlayClassName="custom-tooltip">
                <Button
                  type="primary"
                  onClick={() => {
                    handleConnect(record);
                  }}
                  size="small"
                  loading={eachConnStatus === "fetching"}
                  data-testid={`load-button-${record?.key}`}
                >
                  connect
                </Button>
              </Tooltip>
            </>
          );
        }
        return (
          <>
            <Tooltip
              title={`Connection Id : ${record?._id}`}
              overlayClassName="custom-tooltip"
            >
              <InfoCircleOutlined className="info-icon-font savedconnection" />
            </Tooltip>
            <Tooltip title="Edit" overlayClassName="custom-tooltip">
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
                data-testid="edit-conn-btn"
                className="action-icon-size"
              />
            </Tooltip>
            <Tooltip title="Delete" overlayClassName="custom-tooltip">
              <Button
                type="text"
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(record)}
                data-testid="delete-conn-btn"
                className="action-icon-size"
              />
            </Tooltip>
            <Tooltip title="Test connection" overlayClassName="custom-tooltip">
              <Button
                type="text"
                onClick={() => handleTest(record)}
                data-testid="test-conn-id"
                className="action-icon-size"
              >
                Test
              </Button>
            </Tooltip>
          </>
        );
      },
    },
  ];
  const tableProps = {
    columns,
    dataSource,
    virtual: false,
    size: "small",
    scroll: {
      x: 400,
      y: 340,
    },
    pagination: false,
  };

  if (isFlatFile) {
    tableProps.rowSelection = {
      type: "checkbox",
      selectedRowKeys,
      onChange: setSelectedRowKeys,
      getCheckboxProps: (record) => {
        return {
          disabled: mode === "schedule",
          name: record.alias,
        };
      },
    };
  }

  const handleDataLoad = () => {
    setConnectionStatus("fetching");
    let payload = [];
    memoizedDataSource.forEach((eachData) => {
      if (selectedRowKeys.includes(eachData._id)) {
        payload.push({
          source: "file",
          details: {
            connection_id: eachData._id,
            chat_id: chatId,
            type: eachData.fileType,
            file_name: eachData.alias,
          },
        });
      }
    });
    dataLoads({
      payload,
      onSuccess: async (response) => {
        setConnectionStatus("success");
        if (response?.files_uploaded?.length > 0) {
          const chatMessage = {
            isUser: true,
            text: "Initiating database load",
            message_id: uuidv4(),
            time: getTimeStamp(),
          };
          dispatch(addNewMessageAction({ chatId, data: [chatMessage] }));
          setSelectedRowKeys([]);
          setAsyncOperationsCompleted(true);
          triggerGetInfoAPI(dispatch, chatId, { showPreview: true });
          triggerPipelineHistory(dispatch, chatId);
          dispatch(setSidebarState(true));
        }

        if (response.message) {
          if (response.success) {
            messageApi.success({
              type: "success",
              content: response?.message || "",
            });
          } else {
            messageApi.error({
              type: "error",
              content: "Something went wrong",
            });
          }
        }
      },
      onError: (error) => {
        setConnectionStatus("error");
        messageApi.error({
          type: "error",
          content: error.message || "Failed to load the file",
        });
        handleSessionExpiry(dispatch, error);
      },
    });
  };
  const connectionToDelete = savedList?.databases?.find(
    (conn) => conn?._id === deleteModal?.connectionId,
  );
  const connectionName = connectionToDelete?.alias;
  return (
    <>
      {contextHolder}
      {savedConnApiStatus === "FETCHING" ? (
        <div data-testid="loading-id">
          <Skeleton loading paragraph={{ rows: 5 }} />
        </div>
      ) : (
        <>
          <Table
            className="flat-files-font"
            {...tableProps}
            data-testid="saved-connections-table"
          />
          {selectedRowKeys.length > 0 && (
            <Tooltip
              title="This will load all columns in selected files"
              placement="right"
            >
              <Button
                type="primary"
                onClick={handleDataLoad}
                data-testid="multi-file-load-btn"
                style={{ marginLeft: "10px" }}
                loading={connectionStatus === "fetching"}
              >
                Load {selectedRowKeys?.length}{" "}
                {selectedRowKeys?.length > 1 ? "files" : "file"}
              </Button>
            </Tooltip>
          )}
          <ADModal
            title="Delete Connection"
            description={`Are you sure to delete the connection ${connectionName}?`}
            open={deleteModal.open}
            onOk={handleDeleteConfirm}
            onCancel={() => setDeleteModal({ open: false, connectionId: null })}
            okText="Delete"
            cancelText="Cancel"
            showCancelButton
            hideButtons={false}
          />
        </>
      )}
    </>
  );
};

export default SavedDbConnections;
