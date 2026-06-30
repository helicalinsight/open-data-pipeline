import React, { useEffect, useMemo, useRef, useState } from "react";
import { Select, Input, Typography, Tag, Tooltip } from "antd";
import { PlusOutlined, CloseOutlined } from "@ant-design/icons";

const { Text } = Typography;
const { Option } = Select;

const fieldStyle = { display: "flex", alignItems: "center" };
const labelStyle = { marginRight: 8, whiteSpace: "nowrap" };

const QueryField = ({ label, value, onChange, placeholder, size }) => (
  <div className="query-mode" style={fieldStyle}>
    <Text className="query-label" style={labelStyle}>{label}</Text>
    <Input
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      placeholder={placeholder}
      size={size}
      className="small-input"
      style={{ width: 180 }}
    />
  </div>
);

const toKeys = (val) =>
  Array.isArray(val) ? val : val ? [val] : [];

const toOutput = (arr) =>
  arr.length <= 1 ? arr[0] || "" : arr;

const containerStyle = {
  display: "flex",
  alignItems: "center",
  width: 180,
  border: "1px solid #d9d9d9",
  borderRadius: 6,
  padding: "0 4px 0 6px",
  background: "#fff",
  boxSizing: "border-box",
  cursor: "text",
  gap: 4,
};

const scrollStyle = {
  display: "flex",
  alignItems: "center",
  gap: 4,
  flex: 1,
  overflowX: "auto",
  whiteSpace: "nowrap",
  scrollbarWidth: "thin",
  padding: "3px 0",
};

const tagStyle = {
  margin: 0,
  padding: "0 4px",
  fontSize: 11,
  lineHeight: "16px",
  flexShrink: 0,
};
const iconStyle = {
  cursor: "pointer",
  fontSize: 11,
};

const actionStyle = {
  display: "flex",
  alignItems: "center",
  gap: 6,
  flexShrink: 0,
  paddingLeft: 4,
  borderLeft: "1px solid #f0f0f0",
};
const IncrementKeyField = ({
  value,
  onChange,
  label = "Increment Key",
}) => {
  const [inputVal, setInputVal] = useState("");
  const scrollRef = useRef(null);
  const keys = useMemo(() => toKeys(value), [value]);
   useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [keys]);

  const updateKeys = (updatedKeys) =>
    onChange?.(toOutput(updatedKeys));

  const addKey = () => {
    const key = inputVal.trim();
    if (!key || keys.includes(key)) {
      setInputVal("");
      return;
    }
    updateKeys([...keys, key]);
    setInputVal("");
  };

  const removeKey = (key) =>
    updateKeys(keys.filter((k) => k !== key));

  const clearAllKeys = () => {
    updateKeys([]);
    setInputVal("");
  };

  return (
    <div className="query-mode" style={fieldStyle}>
      <Text className="query-label" style={labelStyle}>
        {label}
      </Text>

      <div
        style={containerStyle}
        onClick={() =>
          document.getElementById("increment-key-input")?.focus()
        }
      >
        <div ref={scrollRef} style={scrollStyle}>
          {keys.map((key) => (
            <Tag
              key={key}
              closable
              onClose={() => removeKey(key)}
              closeIcon={<CloseOutlined style={{ fontSize: 9 }} />}
              style={tagStyle}
            >
              {key}
            </Tag>
          ))}

          <Input
            id="increment-key-input"
            value={inputVal}
            placeholder={ "Enter increment key(s)"}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === ",") {
                e.preventDefault();
                addKey();
              }
            }}
            onBlur={addKey}
            style={{
              border: "none",
              padding: 0,
              minWidth: 40,
              width: inputVal
                ? `${inputVal.length + 2}ch`
                : keys.length
                ? 45
                : 110,
              background: "transparent",
              flexShrink: 0,
            }}
          />
        </div>
        <div style={actionStyle}>
          <Tooltip title="Add key (Enter or ,)">
            <PlusOutlined
              style={iconStyle}
              onMouseDown={(e) => {
                e.preventDefault();
                addKey();
              }}
            />
          </Tooltip>
          {keys.length > 0 && (
            <Tooltip title="Clear all">
              <CloseOutlined
                style={iconStyle}
                onMouseDown={(e) => {
                  e.preventDefault();
                  clearAllKeys();
                }}
              />
            </Tooltip>
          )}
        </div>
      </div>
    </div>
  );
};

const QueryModeSelect = ({
  value,
  onChange,
  primaryKeyValue = "",
  incrementKeyValue = "",
  onPrimaryKeyChange,
  onIncrementKeyChange,
  queryModes = [],
  size = "small",
  showPrimaryKeyField = true,
  custom,
}) => {
  const showPrimaryKey = value === "merge" && showPrimaryKeyField;
  const showIncrementKey = ["append", "merge"].includes(value);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginRight: 10 }}>
      <div className="query-mode" style={fieldStyle}>
        <Text className="query-label" style={labelStyle}>Query Mode</Text>
        <Select
          value={value}
          onChange={onChange}
          className="small-select"
          size={size}
          style={{ marginRight: custom ? 10 : 0 }}
        >
          {queryModes.map(({ value, label }) => (
            <Option key={value} value={value}>{label}</Option>
          ))}
        </Select>
      </div>

      {showPrimaryKey && (
        <QueryField
          label="Primary Key"
          value={primaryKeyValue}
          onChange={onPrimaryKeyChange}
          placeholder="Enter primary key"
          // size={size}
        />
      )}

      {showIncrementKey && (
        <IncrementKeyField
          label="Increment Key"
          value={incrementKeyValue}
          onChange={onIncrementKeyChange}
          size={size}
        />
      )}
    </div>
  );
};

export default QueryModeSelect;
