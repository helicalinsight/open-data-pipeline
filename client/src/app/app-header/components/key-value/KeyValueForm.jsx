import { Button, Col, Form, Input, message, Row, Space, Tooltip } from "antd";
import { v4 as uuidv4 } from "uuid";
import { dispatchMessage } from "../../../../utils/handleClick";
import { useDispatch, useSelector } from "react-redux";
import { MoreOutlined } from "@ant-design/icons";
import { formatKeyValue, validateConfigKey, validateConfigValue } from "../../utils";
import { setHideMessageAction } from "../../../../store/actions/settingActions";

const KeyValueForm = ({ keyValueData, onAdd, handleOpenDrawer, isMode }) => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const [messageApi, contextHolder] = message.useMessage();


  const handleFinish = (e) => {
    dispatch(setHideMessageAction(true));
    const duplicate = keyValueData.find(
      (config) => config.configKey === e.configKey
    );

    if (duplicate) {
      dispatchMessage(
        dispatch,
        "warning",
        `${duplicate.configKey} already exits`
      );
      return;
    }
    const data = {
      key: uuidv4(),
      ...e,
    };
    const formattedData = {
      key: uuidv4(),
      configKey: formatKeyValue(e.configKey),
      configValue: formatKeyValue(e.configValue),
    };
    onAdd(formattedData, "single", () => form.resetFields());
    form.resetFields();
  };

  const handleAddButtonClick = () => {
    handleOpenDrawer();
  };

  return (
    <>
      {contextHolder}
      <Form
        layout="vertical"
        onFinish={handleFinish}
        form={form}
        hideRequiredMark
        data-testid="key-value-form"
        className="key-form-mar"
      >
        <Row gutter={16}>
          <Col span={9}>
            <Form.Item
              className="advance-table custom-form-item key-val-table"
              name="configKey"
              label="Key"
              rules={[
                {
                  validator: isMode
                    ? validateConfigKey
                    : (_, value) => {
                        if (!value)
                          return Promise.reject("This key is required");
                        return Promise.resolve();
                      },
                },
              ]}
            >
              <Input.TextArea
                placeholder="Please enter user name"
                data-testid="configKey"
                className="form-font"
                autoSize={{ minRows: 1, maxRows: 3.5 }}
              />
            </Form.Item>
          </Col>
          <Col span={10}>
            <Form.Item
              className="advance-table custom-form-item key-val-table"
              name="configValue"
              label="Value"
              rules={[
                {
                  validator: isMode
                    ? validateConfigValue
                    : (_, value) => {
                        if (!value)
                          return Promise.reject("This value is required");
                        return Promise.resolve();
                      },
                },
              ]}
            >
              <Input.TextArea
                placeholder="Please enter value"
                data-testid="configValue"
                className="form-font"
                autoSize={{ minRows: 1, maxRows: 3.5 }}
              />
            </Form.Item>
          </Col>
          <Col span={5}>
            <Form.Item label=" ">
              <Space style={{ marginRight: "10px" }}>
                <Button
                  style={{ height: "25px" }}
                  className="advance-add"
                  htmlType="submit"
                >
                  Add
                </Button>
                {isMode && (
                  <Tooltip title="Config Editor">
                    <MoreOutlined onClick={handleAddButtonClick} />
                  </Tooltip>
                )}
              </Space>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </>
  );
};

export default KeyValueForm;
