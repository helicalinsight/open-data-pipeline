import { Form, Input } from "antd";
import { useContext, useEffect, useRef, useState } from "react";
import { EditableContext } from "./EditableRow";

const EditableCell = (props) => {
  const {
    title,
    editable,
    children,
    dataIndex,
    record,
    handleSave,
    activeEditableRowId,
    ...restProps
  } = props;

  const [editing, setEditing] = useState(false);
  const inputRef = useRef(null);
  const form = useContext(EditableContext);

  useEffect(() => {
    if (editing) {
      inputRef.current.focus();
    }
  }, [editing]);

  useEffect(() => {
    if (activeEditableRowId && record._id === activeEditableRowId) {
      setEditing(true);
      form.setFieldsValue({
        [dataIndex]: record[dataIndex],
      });
    }
  }, [activeEditableRowId]);

  const toggleEdit = () => {
    setEditing(!editing);
    form.setFieldsValue({
      [dataIndex]: record[dataIndex],
    });
  };

  const save = async () => {
    try {
      const values = await form.validateFields();
      toggleEdit();

      handleSave({
        ...record,
        ...values,
      });
    } catch (errInfo) {
      console.log("Save failed:", errInfo);
    }
  };

  let childNode = children;
  if (editable) {
    childNode = editing ? (
      <Form.Item
        style={{
          margin: 0,
        }}
        name={dataIndex}
        rules={[
          {
            required: true,
            message: `${title} is required.`,
          },
        ]}
        onClick={(e) => e.stopPropagation()}
      >
        <Input
          className="form-font"
          ref={inputRef}
          data-testid={`${record._id}-input`}
          onPressEnter={(e) => {
            e.stopPropagation();
            save();
          }}
          onBlur={(e) => {
            e.stopPropagation();
            save();
          }}
          onChange={(e) => e.stopPropagation()}
          placeholder={`Please enter ${title}`}
        />
      </Form.Item>
    ) : (
      <div onClick={(e) => e.stopPropagation()}>{children}</div>
    );
  }
  return <td {...restProps}>{childNode}</td>;
};

export default EditableCell;
