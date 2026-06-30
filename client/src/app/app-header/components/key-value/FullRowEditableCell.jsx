import { Form, Input } from "antd";
import { validateConfigKey, validateConfigValue } from "../../utils";

const FullRowEditableCell = ({
  editing,
  dataIndex,
  title,
  inputType,
  record,
  index,
  children,
  visible,
  ...restProps
}) => {
  const inputNode = <Input.TextArea />;
  const getValidator = (field) => {
    if (field === "configKey") return validateConfigKey;
    if (field === "configValue") return validateConfigValue;
    return null;
  };

  return (
    <td {...restProps}>
      {editing ? (
        <Form.Item
          className="key-val-table"
          name={dataIndex}
          style={{
            margin: 0,
          }}
          rules={
            visible
              ? [
                  {
                    required: true,
                    message: `Please Input ${title}!`,
                  },
                ]
              : [
                  {
                    validator: getValidator(dataIndex),
                  },
                ]
          }
        >
          {inputNode}
        </Form.Item>
      ) : (
        children
      )}
    </td>
  );
};

export default FullRowEditableCell;
