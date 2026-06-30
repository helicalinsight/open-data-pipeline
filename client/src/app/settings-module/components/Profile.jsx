import React, { useEffect, useState } from "react";
import {
  Table,
  Card,
  Button,
  Input,
  DatePicker,
  Form,
  message,
  Tooltip,
} from "antd";
import { DeleteOutlined, CopyOutlined } from "@ant-design/icons";
import "../style.scss";
import {
  createGenerateKey,
  getGenerateKey,
  deleteGenerateKey,
} from "../../../apis/settingsService";
import { getLocalStorageItem } from "../../../utils/userData";
import dayjs from "dayjs";
import { dispatchMessage } from "../../../utils/handleClick";
import { useDispatch, useSelector } from "react-redux";
import { setApiKeys } from "../../../store/actions/settingActions";
import { ADModal } from "../../../components/ADModal";

const Profile = () => {
  const [isAdding, setIsAdding] = useState(false);
  const { user } = getLocalStorageItem() || {};
  const dispatch = useDispatch();
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [selectedToken, setSelectedToken] = useState(null);
  const keyData = useSelector((state) => state?.settings?.apiKeys);

  const disabledDate = (current) => {
    return current && current <= dayjs().startOf("day");
  };

  useEffect(() => {
    togetGenerateKey();
  }, []);

  const togetGenerateKey = () => {
    const payload = {
      user_id: user?.id,
    };
    getGenerateKey({
      payload,
      onSuccess: (response) => {
        if (response) {
          const formatted = [
            {
              tokenname: response.token_name || "-",
              apikey: response.api_key || "-",
              expirydate: response.expiry_date
                ? dayjs(response.expiry_date).format("YYYY-MM-DD")
                : "-",
            },
          ];
          dispatch(setApiKeys(formatted));
        }
      },
      onError: (error) => {
        dispatchMessage(dispatch, "error", "Failed to fetch API key");
      },
    });
  };

  const handleSave = (values) => {
    const payload = {
      email: user.email,
      token_name: values.tokenName,
    };
    if (values.expires) {
      payload.expiry_date = values.expires.format("YYYY-MM-DD");
    }
    createGenerateKey({
      payload,
      onSuccess: (response) => {
        dispatchMessage(dispatch, "success", "Token Created Successfully");
        setIsAdding(false);
        togetGenerateKey();
      },
      onError: (error) => {
        dispatchMessage(dispatch, "error", "Error Creating Token");
        setIsAdding(false);
      },
    });
  };

  const handleDeleteClick = (record) => {
    setSelectedToken(record);
    setDeleteModal(true);
  };

  const deleteGenerateApiKey = () => {
    setDeleteLoading(true);
    const payload = {
      user_id: user?.id,
    };
    deleteGenerateKey({
      payload,
      onSuccess: (response) => {
        dispatchMessage(dispatch, "success", "Token deleted Successfully");
        togetGenerateKey();
        setDeleteLoading(false);
        setDeleteModal(false);
        setSelectedToken(null);
      },
      onError: (error) => {
        dispatchMessage(dispatch, "error", "Error deleted Token");
        setDeleteLoading(false);
        setDeleteModal(false);
        setSelectedToken(null);
      },
    });
  };

  const handleCancelDelete = () => {
    setDeleteModal(false);
    setSelectedToken(null);
  };

  const copyToClipboard = (apiKey) => {
    if (apiKey && apiKey !== "-") {
      navigator.clipboard
        .writeText(apiKey)
        .then(() => {
          dispatchMessage(dispatch, "success", "API key copied to clipboard!");
        })
        .catch((err) => {
          dispatchMessage(dispatch, "error", "Failed to copy API key");
        });
    }
  };

  const columns = [
    {
      title: "Token Name",
      dataIndex: "tokenname",
      key: "tokenname",
    },
    {
      title: "Api Key",
      dataIndex: "apikey",
      key: "apikey",
      onHeaderCell: () => ({
        title: "",
      }),
      ellipsis: true,
    },
    {
      title: "Expiry Date",
      dataIndex: "expirydate",
      key: "expirydate",
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => {
        const shouldShowActions =
          record.tokenname !== "-" ||
          record.apikey !== "-" ||
          record.expirydate !== "-";

        return shouldShowActions ? (
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Tooltip title="Copy API Key" overlayClassName="custom-tooltip">
              <CopyOutlined
                style={{
                  cursor: "pointer",
                }}
                onClick={() => copyToClipboard(record.apikey)}
              />
            </Tooltip>
            <Tooltip title="Delete Token" overlayClassName="custom-tooltip">
              <DeleteOutlined
                className="delete-icon"
                data-testid="delete-icon"
                onClick={() => handleDeleteClick(record)}
              />
            </Tooltip>
          </div>
        ) : null;
      },
    },
  ];

  return (
    <Card>
      <div className="header">
        <Button type="primary" onClick={() => setIsAdding(true)}>
          Add new token
        </Button>
      </div>
      {isAdding && (
        <Form
          onFinish={handleSave}
          layout="vertical"
          className="form-container"
        >
          <div className="form-fields">
            <Form.Item
              label="Token Name"
              name="tokenName"
              rules={[{ required: true, message: "Token name is required!" }]}
              className="form-item"
            >
              <Input
                allowClear
                placeholder="Enter token name"
                className="full-width"
              />
            </Form.Item>

            <Form.Item
              label="Expiration Date"
              name="expires"
              className="form-item"
            >
              <DatePicker
                className="full-width"
                disabledDate={disabledDate}
                getPopupContainer={(trigger) => trigger.parentElement}
                placement="top"
              />
            </Form.Item>
          </div>
          <div className="button-group">
            <Button type="primary" htmlType="submit">
              Save
            </Button>
            <Button onClick={() => setIsAdding(false)}>Cancel</Button>
          </div>
        </Form>
      )}
      <div className="table-container">
        <Table
          dataSource={keyData}
          columns={columns}
          pagination={false}
          size="small"
          rowKey="apikey"
        />
      </div>
      <ADModal
        title="Delete Token"
        description={`Are you sure you want to delete the token ${selectedToken?.tokenname} ?`}
        open={deleteModal}
        onOk={deleteGenerateApiKey}
        onCancel={handleCancelDelete}
        okText="Delete"
        cancelText="Cancel"
        loading={deleteLoading}
        showCancelButton
        hideButtons={false}
      />
    </Card>
  );
};

export default Profile;
