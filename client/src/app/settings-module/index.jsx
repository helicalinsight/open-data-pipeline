import React, { useState } from "react";
import { Divider, Tabs } from "antd";
import "./style.scss";
import Preferences from "./components/Preferences";
import Extensions from "./components/Extensions";
import CustomMessage from "./CustomMessage";
import { useSelector } from "react-redux";
import Profile from "./components/Profile";
import Documentation from "./components/Documentation";

const SettingsModule = () => {
  const [activeTab, setActiveTab] = useState("1");
  const messageData = useSelector((store) => store?.settings?.messageData);
  const items = [
    {
      key: "1",
      label: "Profile",
      children:<Profile/>,
    },
    {
      key: "2",
      label: "Preferences",
      children: <Preferences activeTab={activeTab} />,
    },
    {
      key: "3",
      label: "Extensions",
      children: <Extensions />,
    },
    {
      key: "4",
      label: "Documentation",
      children: <Documentation />,
    },
  ];
  return (
    <div className="settings-section">
      <div className="settings-section__header">
        {messageData && (
          <CustomMessage
            type={messageData.type}
            message={messageData.message}
          />
        )}
        <p className="f16 fw600">Settings</p>
        <span className="f14 settings-section__header-subhead">
          Manage your account settings and preferences
        </span>
        <Divider style={{ margin: "17px 0px" }} />
      </div>

      <div className="settings-section__tabs">
        <Tabs
          defaultActiveKey="1"
          items={items}
          activeKey={activeTab}
          onChange={(key) => setActiveTab(key)}
        />
      </div>
    </div>
  );
};

export default SettingsModule;
