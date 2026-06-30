import React, { useEffect } from "react";
import { Space } from "antd";
import {
  InfoCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined 
} from "@ant-design/icons";
import "./CustomMessage.css"; 

const CustomMessage = ({ type, message, onClose }) => {
  const renderIcon = () => {
    switch (type) {
      case "success":
        return <CheckCircleOutlined />;
      case "error":
        return <CloseCircleOutlined />;
      case "info":
        return <InfoCircleOutlined />;
      case "warning": 
        return <WarningOutlined />;
      default:
        return <InfoCircleOutlined />;
    }
  };
  useEffect(() => {
    const timer = setTimeout(() => {
      if (onClose) onClose();
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);
  return (
    <Space className={`msgs-text ${type}`}>
      {renderIcon()}
      {message}
    </Space>
  );
};

export default CustomMessage;
