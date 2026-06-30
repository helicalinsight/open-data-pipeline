import { Form, Space, Table, Popconfirm, Typography, Button } from "antd";
import { useState } from "react";
import { CloseOutlined, CheckOutlined } from "@ant-design/icons";
import CustomIcon from "../../../../components/ADIcons/custom-icon";
import FullRowEditableCell from "./FullRowEditableCell";
import { useSelector } from "react-redux";
import { ADModal } from "../../../../components/ADModal";
import { formatKeyValue } from "../../utils";

const KeyValueTable = ({
  dataSource,
  onEdit,
  onDelete,
  handleFinish,
  loading,
  values,
  visible,
}) => {
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );

  const [form] = Form.useForm();
  const [editingKey, setEditingKey] = useState("");
  const [deleteRowModal, setDeleteRowModal] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);

  const isEditing = (record) => record.key === editingKey;

  const handleDeleteClick = (record) => {
    setRecordToDelete(record);
    setDeleteRowModal(true);
  };

  const confirmDelete = () => {
    if (!recordToDelete) return;
    if (isScheduleEditMode) {
      const currentConfig = [
        ...(jobListDetails?.job_details?.configuration || []),
      ];
      const updatedConfig = currentConfig.filter(
        (item, index) => index !== recordToDelete.key
      );
      onEdit(updatedConfig);
    } else {
      onDelete(recordToDelete);
    }
    setDeleteRowModal(false);
    setRecordToDelete(null);
  };

  const columns = [
    {
      title: "Key",
      dataIndex: "configKey",
      key: "userKey",
      editable: true,
      width: "38%",
    },
    {
      title: "Value",
      dataIndex: "configValue",
      key: "value",
      ellipsis: true,
      editable: true,
      width: "43%",
      onHeaderCell: () => ({
        title: "",
      }),
    },
    {
      title: "Actions",
      width: "18%",
      dataIndex: "actions",
      render: (_, record) => {
        const editable = isEditing(record);
        return editable ? (
          <span>
            <Typography.Link
              onClick={() => save(record.key)}
              style={{
                marginRight: 8,
              }}
            >
              <CheckOutlined
                data-testid="update-button"
                style={{ fontSize: "10px" }}
              />
            </Typography.Link>
            <Popconfirm
              title={<span>Sure to cancel?</span>}
              onConfirm={cancel}
              overlayClassName="config-table"
            >
              <CloseOutlined
                data-testid="cancel-button"
                style={{ fontSize: "10px" }}
              />
            </Popconfirm>
          </span>
        ) : (
          <Space>
            <CustomIcon
              name="edit"
              color="#000"
              className="cursor-pointer"
              onClick={() => edit(record)}
              data-testid="edit"
            />
            <CustomIcon
              name="delete"
              color="#000"
              className="cursor-pointer"
              onClick={() => handleDeleteClick(record)}
              data-testid="delete"
            />
          </Space>
        );
      },
    },
  ];

  const edit = (record) => {
    form.setFieldsValue({
      name: "",
      age: "",
      address: "",
      ...record,
    });
    setEditingKey(record.key);
  };

  const cancel = () => {
    setEditingKey("");
  };

  const save = async (key) => {
    try {
      const row = await form.validateFields();
      const formattedRow = {
        configKey: formatKeyValue(row.configKey),
        configValue: formatKeyValue(row.configValue),
      };
      const updatedTableData = [
        ...(jobListDetails?.job_details?.configuration || []),
      ].map((item, key) => ({ ...item, key }));
      const newData = isScheduleEditMode ? updatedTableData : [...dataSource];
      const index = newData.findIndex((item) => key === item.key);
      if (index > -1) {
        const item = newData[index];
        newData.splice(index, 1, {
          ...item,
          ...formattedRow,
        });
        onEdit(newData);
        setEditingKey("");
      } else {
        newData.push(formattedRow);
        onEdit(newData);
        setEditingKey("");
      }
    } catch (errInfo) {
      console.log("Validate Failed:", errInfo);
    }
  };

  const mergedColumns = columns.map((col) => {
    if (!col.editable) {
      return col;
    }
    return {
      ...col,
      onCell: (record) => ({
        record,
        dataIndex: col.dataIndex,
        title: col.title,
        editing: isEditing(record),
        visible,
      }),
    };
  });

  const tableData = isScheduleEditMode
    ? [...(jobListDetails?.job_details?.configuration || [])]
    : dataSource;

  const updatedTableData = tableData.map((item, key) => ({ ...item, key }));

  return (
    <Form form={form} component={false}>
      <Table
        dataSource={isScheduleEditMode ? updatedTableData : tableData}
        columns={mergedColumns}
        size="small"
        bordered
        components={{
          body: {
            cell: FullRowEditableCell,
          },
        }}
        scroll={{
          y: 200,
        }}
        pagination={false}
      />
      {visible && (
        <div className="advanced-key-value-pair">
          <Button
            type="primary"
            htmlType="submit"
            key={"test"}
            loading={loading}
            onClick={() =>
              handleFinish(values, dataSource.length ? dataSource : [], "child")
            }
            style={{
              backgroundColor: "rgb(242, 142, 30)",
              color: "#ffffff",
            }}
            data-testid="test-button"
          >
            Test Connection
          </Button>
        </div>
      )}
      <ADModal
        title="Delete Row"
        description={
          <>
            Are you sure you want to delete this{" "}
            <b>{recordToDelete?.configKey}</b> row?
          </>
        }
        open={deleteRowModal}
        onOk={confirmDelete}
        onCancel={() => setDeleteRowModal(false)}
        okText="Delete"
        cancelText="Cancel"
        showCancelButton
        hideButtons={false}
      />
    </Form>
  );
};

export default KeyValueTable;
