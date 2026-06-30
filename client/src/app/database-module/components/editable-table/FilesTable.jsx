import { useMemo, useRef, useState } from "react";
import { Skeleton, Space, Table, Tooltip, message } from "antd";
import CustomIcon from "../../../../components/ADIcons/custom-icon";
import {
  DeleteOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import EditableRow from "./EditableRow";
import EditableCell from "./EditableCell";
import { deleteFile, renameFile } from "../../../../apis/fileService";
import BeatLoader from "../../../../components/ADLoader/BeatLoader/BeatLoader";
import { useDispatch, useSelector } from "react-redux";
import { ADModal } from "../../../../components/ADModal";
import {
  deleteSavedConnection,
  updateSavedConnection,
} from "../../../../store/actions/databaseActions";
import { removeFirstDot } from "../../utils/arrayOperations";
import { searchItemFilterData } from "../../utils/searchItemFilterData";
import { handleSessionExpiry } from "../../../../utils/handleSessionExpiry";
import { dispatchMessage } from "../../../../utils/handleClick";

const FilesTable = (props) => {
  const {
    searchTerm,
    setSelectedRowKeys,
    selectedRowKeys,
    openDeleteModal,
    setOpenDeleteModal,
    deleteLoading,
    setDeleteFileIds,
    handleDeleteFiles,
    deleteFileIds,
    messageApi,
  } = props;
  console.log(deleteFileIds, "iyf");
  const dispatch = useDispatch();
  const [renameAPIid, setRenameAPIid] = useState("");
  const savedConnections = useSelector(
    (state) => state.database.savedConnections
  );
  const savedConnApiStatus = useSelector(
    (state) => state.database.savedConnApiStatus
  );

  const [isNameEditable, setIsNameEditable] = useState(false);
  const [activeEditableRowId, setActiveEditableRowId] = useState(null); // when user clicks on edit icon
  const [editingValue, setEditingValue] = useState("");

  const memoizedData = useMemo(() => {
    return (
      savedConnections?.map((connection) => ({
        ...connection,
        key: connection._id,
      })) || []
    );
  }, [savedConnections]);

  const memoizedTableDataSource = useMemo(() => {
    return searchItemFilterData(memoizedData, searchTerm);
  }, [searchTerm, memoizedData]);

  const onDeleteClick = (id) => {
    setDeleteFileIds([id]);
    setOpenDeleteModal(true);
  };

  const defaultColumns = [
    {
      title: "S No",
      key: "serialNumber",
      render: (...args) => {
        return args[2] + 1;
      },
    },
    {
      title: "Name",
      dataIndex: "alias",
      key: "name",
      editable: true,
      ellipsis: true,
      onHeaderCell: () => ({
        title: "",
      }),
      render: (text, record) => {
        if (renameAPIid === record._id) {
          return <BeatLoader color="#096DD9" />;
        }
        if (activeEditableRowId === record._id) {
          return (
            <input
              value={editingValue}
              onChange={(e) => setEditingValue(e.target.value)}
              style={{ width: "100%" }}
            />
          );
        }
        const iconName = removeFirstDot(record?.fileType);
        return (
          <Space>
            {iconName && (
              <CustomIcon name={iconName} style={{ fontSize: "24px" }} />
            )}
            <Tooltip title={text} placement="topLeft">
              <span>{text}</span>
            </Tooltip>
          </Space>
        );
      },
    },

    {
      title: "Type",
      dataIndex: "fileType",
      key: "fileType",
    },
    {
      title: "Actions",
      key: "action",
      render: (_, record) => (
        <Space size="middle">
          <Tooltip
            title={`Connection Id : ${record?._id}`}
            overlayClassName="custom-tooltip"
          >
            <InfoCircleOutlined />
          </Tooltip>
          {activeEditableRowId === record._id ? (
            <>
              <Tooltip title="Save" overlayClassName="custom-tooltip">
                <CheckOutlined
                  style={{ color: "green", cursor: "pointer" }}
                  onClick={() => handleSave(record)}
                />
              </Tooltip>
              <Tooltip title="Cancel" overlayClassName="custom-tooltip">
                <CloseOutlined
                  style={{ color: "red", cursor: "pointer" }}
                  onClick={handleCancelEdit}
                />
              </Tooltip>
            </>
          ) : (
            <Tooltip title="Edit" overlayClassName="custom-tooltip">
              <EditOutlined
                onClick={() => {
                  setActiveEditableRowId(record._id);
                  setEditingValue(record.alias);
                }}
                style={{ cursor: "pointer" }}
              />
            </Tooltip>
          )}
          <Tooltip title="Delete" overlayClassName="custom-tooltip">
            <DeleteOutlined
              data-testid={`${record?._id}-delete`}
              onClick={() => onDeleteClick(record._id)}
              type="delete"
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const columns = defaultColumns.map((col) => {
    if (!col.editable) {
      return col;
    }
    return {
      ...col,
      onCell: (record) => {
        return {
          record,
          editable: col.editable,
          dataIndex: col.dataIndex,
          title: col.title,
          handleSave,
          activeEditableRowId,
        };
      },
    };
  });

  const handleSave = (record) => {
    setRenameAPIid(record._id);
    renameFile({
      payload: { ...record, alias: editingValue },
      onSuccess: (res) => {
        if (res.success) {
          dispatch(
            updateSavedConnection({
              connection_id: record._id,
              connection_alias: editingValue,
            })
          );
          dispatchMessage(
            dispatch,
            "success",
            res.message || "File name updated successfully."
          );
        } else {
          dispatchMessage(
            dispatch,
            "error",
            res.message || "Failed to update file name."
          );
        }
        setRenameAPIid("");
        setActiveEditableRowId(null);
      },
      onError: (err) => {
        setRenameAPIid("");
        setActiveEditableRowId(null);
        dispatchMessage(
          dispatch,
          "error",
          err.message || "Failed to update file name."
        );
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  const handleCancelEdit = () => {
    setActiveEditableRowId(null);
  };

  const components = {
    body: {
      row: EditableRow,
      cell: EditableCell,
    },
  };

  const onSelectChange = (...args) => {
    setSelectedRowKeys(args[0]);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
  };
  const isMultipleFiles = deleteFileIds.length > 1;
  return (
    <>
      {savedConnApiStatus === "FETCHING" ? (
        <Skeleton
          data-testid="skeleton"
          loading
          paragraph={{
            rows: 5,
          }}
        />
      ) : (
        <Table
          className="flat-files-font"
          data-testid="flat-files-table"
          dataSource={memoizedTableDataSource}
          columns={defaultColumns}
          rowSelection={rowSelection}
          size="small"
          expandable={{
            rowExpandable: false,
            expandIcon: () => null,
          }}
          pagination={false}
          virtual={false}
          scroll={{
            y: 400,
          }}
          components={components}
          rowClassName={(record) =>
            record.type === "folder" ? "cursor-pointer" : ""
          }
        />
      )}
      <ADModal
        title={`Delete File${deleteFileIds.length > 1 ? "s" : ""}`}
        description={
          isMultipleFiles
            ? `Are you sure you want to delete these files?`
            : `Are you sure you want to delete this file: ${
                memoizedData?.find((file) => file._id === deleteFileIds[0])
                  ?.alias || ""
              }?`
        }
        open={openDeleteModal}
        onOk={() => handleDeleteFiles()}
        onCancel={() => {
          setDeleteFileIds([]);
          setOpenDeleteModal(false);
        }}
        okText="Delete"
        cancelText="Cancel"
        showCancelButton={true}
        hideButtons={false}
        loading={deleteLoading}
      />
    </>
  );
};

export default FilesTable;
