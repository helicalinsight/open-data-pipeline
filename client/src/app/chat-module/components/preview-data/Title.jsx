import { Tooltip } from "antd";
import { ADSpace } from "../../../../components";
import { ClockCircleOutlined, CheckSquareOutlined } from "@ant-design/icons";

export const Title = ({ columnName, dataType }) => {
  const isNumeric = /^int|^float/i.test(dataType);
  const dataTypeIndicator = isNumeric ? (
    "123"
  ) : dataType?.includes("datetime64") ? (
    <ClockCircleOutlined />
  ) : dataType === "bool" ? (
    <CheckSquareOutlined />
  ) : (
    "A-Z"
  );
  return (
    <Tooltip title={`${columnName} (${dataType})`}>
      <div className="fw600 title-container">
        <div
          className="fw600 title-container"
          style={{ display: "flex", alignItems: "center" }}
        >
          <span className="data-type">{dataTypeIndicator}</span>
          <span className="title-text">{columnName}</span>
        </div>
      </div>
    </Tooltip>
  );
};

export const Text = ({ text }) => {
  return (
    <Tooltip placement="topLeft">
      <span className="text-content">{text}</span>
    </Tooltip>
  );
};
