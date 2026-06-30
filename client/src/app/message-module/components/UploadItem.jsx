import {
  DeleteOutlined,
  InfoCircleOutlined,
  LoadingOutlined,
} from "@ant-design/icons";
import { Progress } from "antd";
import { ADSpace } from "../../../components";

function UploadItem({ file, handleFileRemove, index, uploadFileSizeLimit }) {
  const { status, name, progress, size } = file;

  const isLimitExceeded = size > uploadFileSizeLimit * 1000000;
  // 5000000
  function sideIcon() {
    if (progress === 99) {
      return (
        <LoadingOutlined
          data-testid="loading-icon"
          style={{
            fontSize: "14px",
          }}
          spin
        />
      );
    }
    if (status && status === "failed") {
      return (
        <InfoCircleOutlined style={{ fontSize: "14px", color: "#FF0000" }} />
      );
    }
    if (!status) {
      return (
        <DeleteOutlined
          data-testid="remove-file"
          style={{ fontSize: "14px", color: isLimitExceeded && "red" }}
          onClick={() => handleFileRemove(file)}
        />
      );
    }
    return null;
  }

  const styles = {
    fontSize: status ? "11px" : "13px",
    color: status === "failed" || isLimitExceeded ? "red" : "",
    fontStyle: "italic",
  };

  return (
    <ADSpace space="6" justifyContent="space-between" alignItem="center">
      <ADSpace stack="vertical">
        <div style={styles}>{`${index}. ${name}`}</div>
        {status && status !== "failed" ? (
          <Progress
            data-testid="progress-bar"
            percent={progress}
            size="small"
            showInfo={progress === 99 ? false : true}
          />
        ) : (
          isLimitExceeded && (
            <span
              style={styles}
            >{`File size should not exceed ${uploadFileSizeLimit}Mb`}</span>
          )
        )}
      </ADSpace>
      <div>
        {/* add cancel icon here in place of null */}
        {sideIcon()}
      </div>
    </ADSpace>
  );
}

export default UploadItem;
