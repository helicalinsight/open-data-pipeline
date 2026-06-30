import React from "react";
import { Steps, Select, Button } from "antd";
import "./style.scss";
import DataBaseModule from "../database-module";

const { Option } = Select;
const { Step } = Steps;
const STEPS = ["Migration Mode", "Source", "Destination"];
export const CommonPipelineSteps = ({ current = 0 }) => {
  return (
    <div className="common-steps-wrapper">
      <Steps current={current} responsive={false}>
        {STEPS.map((title) => (
          <Step key={title} title={title} />
        ))}
      </Steps>
    </div>
  );
};
export const PipelinePageWrapper = ({ children }) => {
  return <div className="pipeline-page">{children}</div>;
};

export const CommonSelectWithLabel = ({
  label,
  value,
  onChange,
  options = [],
  placeholder,
  error,
}) => {
  return (
    <div className="pm-row">
      <div className="pm-label">{label} :</div>

      <div className="pm-field">
        <Select
          allowClear
          showSearch
          value={value}
          onChange={onChange}
          size="middle"
          className="pm-select"
          placeholder={placeholder}
          virtual={false}
          status={error ? "error" : ""}
        >
          {(options || []).map((item) => (
            <Option key={item.driver} value={item.driver}>
              {item.name}
            </Option>
          ))}
        </Select>
        {error && <div className="pm-error">{error}</div>}
      </div>
    </div>
  );
};

export const ConnectDataSource = ({
  openDbModal,
  setOpenDbModal,
  onClick,
  selectedSourceType,
  selectedDestinationType,
}) => {
  return (
    <>
      <div className="connect-btn-wrapper">
        <Button type="primary" onClick={onClick}>
          Connect Datasource
        </Button>
      </div>

      {openDbModal && (
        <DataBaseModule
          setOpenDbModal={setOpenDbModal}
          openDbModal={openDbModal}
          haveLoad={true}
          selectedSourceType={selectedSourceType}
          selectedDestinationType={selectedDestinationType}
        />
      )}
    </>
  );
};

export const validateTableName = (name) => {
  if (!name.trim()) {
    return "Target table name is required";
  }
  return "";
};

export const SQL_QUERY_ERROR = "A valid custom SQL query is required to proceed.";
export const PRIMARY_KEY_ERROR = "A Primary Key is required to proceed.";
export const SOURCE_DATASOURCE_ERROR = "A source datasource connection is required to proceed.";
export const DESTINATION_DATASOURCE_ERROR = "A destination datasource connection is required before saving.";