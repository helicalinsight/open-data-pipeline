import React from "react";
import { Button, Modal, Space } from "antd";
import CustomIcon from "../ADIcons/custom-icon";
import "./index.scss";
import ADSpace from "../ADSpace";

export const ModalButtons = ({
  onOk,
  onCancel,
  okText,
  okType,
  cancelText,
  showCancelButton,
  loading,
}) => {
  const handleOk = () => {
    if (typeof onOk === "function") onOk();
  };

  const handleCancel = () => {
    if (typeof onCancel === "function") onCancel();
  };

  return (
    <Space className="buttons-container">
      <Button
        className="modal-button items-center f14"
        data-testid="modal-ok-button"
        onClick={handleOk}
        htmlType={okType ? "submit" : "button"}
        loading={loading && loading}
      >
        {okText}
      </Button>
      {showCancelButton && (
        <Button
          className="modal-button items-center f14"
          onClick={handleCancel}
          data-testid="modal-cancel-button"
        >
          {cancelText}
        </Button>
      )}
    </Space>
  );
};

export const ADModal = (props) => {
  const {
    title,
    open,
    onOk,
    onCancel,
    description,
    okText,
    cancelText,
    iconName,
    showCancelButton,
    hideButtons,
    element,
    logs,
    loading,
    width,
  } = props;

  const bodyStyle = {
    // height: element ? "auto" : "120px",
    // height: element ? "auto" : logs ? "250" : "120px",
    padding: "0px 15px 8px ",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-around",
    alignItems: "center",
    fontFamily: "Ubuntu",
  };
  const descriptionStyle = {
    maxHeight: '200px',
    overflowY: 'auto',
    width: '100%',
  };

  return (
    <Modal
      title={
        <ADSpace className="modal-header justifyCenter alignCenter fw600">
          <Space>
            {iconName && (
              <span>
                <CustomIcon name={iconName} />
              </span>
            )}
            <span>{title}</span>
          </Space>
        </ADSpace>
      }
      centered
      closeIcon={null}
      footer={null}
      open={open}
      width={width ? width : logs ? 1000 : 420}
      bodyStyle={bodyStyle}
      data-testid="ad-modal"
    >
      <ADSpace
        stack="vertical"
        alignItem="center"
        justifyContent="space-between"
        className="modal-content flex-1"
      >
        {description && <div className="description f14" style={descriptionStyle}>{description}</div>}
        {logs && <>{logs}</>}
        {element && <div className="radio-btns">{element}</div>}
        {hideButtons === false && (
          <ModalButtons
            onOk={onOk}
            onCancel={onCancel}
            okText={okText}
            cancelText={cancelText}
            showCancelButton={showCancelButton}
            loading={loading}
          />
        )}
      </ADSpace>
    </Modal>
  );
};
