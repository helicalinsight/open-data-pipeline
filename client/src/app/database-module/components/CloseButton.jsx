import { Space, Tooltip } from "antd";
import { CloseOutlined } from "@ant-design/icons";
import PropTypes from "prop-types";

const CloseButton = ({ handleClose, tooltipTitle, testId }) => {
  return (
    <div className="close-button-wrapper">
    <Tooltip title={tooltipTitle} placement="topRight">
      <Space
        onClick={handleClose}
        className="cursor-pointer close-button"
        data-testid="back-btn-id"
        style={{ cursor: "pointer" }}
      >
        Close
        <CloseOutlined />
      </Space>
    </Tooltip>
    </div>
  );
};

CloseButton.propTypes = {
  handleClose: PropTypes.func.isRequired,
  tooltipTitle: PropTypes.string,
  testId: PropTypes.string,
};

CloseButton.defaultProps = {
  tooltipTitle: "Close this section to return to the main datasource section",
  testId: "back-btn-id",
};

export default CloseButton;
