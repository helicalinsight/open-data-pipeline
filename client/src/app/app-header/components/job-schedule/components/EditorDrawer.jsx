import { useState } from "react";
import { useSelector } from "react-redux";
import { Drawer, Space, Popover, Checkbox } from "antd";
import { InfoCircleOutlined, SettingOutlined } from "@ant-design/icons";
import CustomEditor from "./CustomEditor";
import JobInfoDrawer from "./JobInfoDrawer";
import { useDispatch } from "react-redux";
import { setChildDrawer } from "../../../../../store/actions/jobScheduleActions";
const EditorDrawer = ({
  mode,
  childrenDrawer,
  setChildrenDrawer,
  handleClose,
  title,
  keyValueData,
  onAdd,
  isJobConfig,
}) => {
  const [open, setOpenInfo] = useState(false);
  const [wordWrap, setWordWrap] = useState("off");
  const [settingsVisible, setSettingsVisible] = useState(false);
  const dispatch = useDispatch();
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const { isYamlSaved } =
    useSelector((state) => state.chat?.chatList[selectedChat?.chat_id]) ?? {};
  const childDrawer = useSelector((state) => state.jobSchedule?.childDrawer);

  const onChildrenDrawerClose = () => {
    dispatch(setChildDrawer(false));
    handleClose();
    setWordWrap("off");
  };

  const handleWordWrapToggle = (e) => {
    setWordWrap(e.target.checked ? "on" : "off");
  };

  const handleSettingsVisibleChange = (visible) => {
    setSettingsVisible(visible);
  };
  const settingsContent = (
    <div>
      <Checkbox
        checked={wordWrap === "on"}
        onChange={handleWordWrapToggle}
        style={{ fontSize: "10px" }}
      >
        Wrap lines
      </Checkbox>
    </div>
  );

  return (
    <>
      <Drawer
        title={
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Space>
              <span>{title}</span>
              <InfoCircleOutlined
                onClick={() => setOpenInfo(true)}
                style={{ fontSize: "12px", marginTop: "4px" }}
                data-testid="help-info-icon"
              />
            </Space>
            {isJobConfig && (
              <Popover
                content={settingsContent}
                trigger="click"
                placement="bottomRight"
                visible={settingsVisible}
                onVisibleChange={handleSettingsVisibleChange}
              >
                <SettingOutlined
                  style={{
                    fontSize: "14px",
                    cursor: "pointer",
                  }}
                />
              </Popover>
            )}
          </div>
        }
        width={"80%"}
        onClose={onChildrenDrawerClose}
        open={childDrawer}
        destroyOnClose={true}
      >
        <CustomEditor
          open={childDrawer}
          onChildrenDrawerClose={onChildrenDrawerClose}
          selectedChat={selectedChat}
          mode={mode}
          keyValueData={keyValueData}
          onAdd={onAdd}
          isJobConfig={isJobConfig}
          wordWrap={wordWrap}
        />
        <JobInfoDrawer open={open} setOpenInfo={setOpenInfo} mode={mode} />
      </Drawer>
    </>
  );
};

export default EditorDrawer;
