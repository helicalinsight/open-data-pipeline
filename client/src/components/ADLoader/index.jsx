import React from "react";
import { Spin } from "antd";
import { LoadingOutlined } from "@ant-design/icons";

function ADLoader() {
  return (
    <Spin
      size="large"
      indicator={<LoadingOutlined />}
      className="ad-loader items-center h-100-vh w-100"
    />
  );
}
export default ADLoader;
