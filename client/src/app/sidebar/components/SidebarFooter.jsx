import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { removeLocalStorageData } from "../../../utils/userData";
import { Avatar, Popover, Space } from "antd";
import { DashOutlined, MoreOutlined } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { resetRedux } from "../../../store/actions/sessionActions";
import { ADModal } from "../../../components/ADModal";

const SideBarFooter = ({ user, isSidebarCollapsed }) => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();
 const getAppVersion = () => {
    try {
      const storedVersion = localStorage.getItem("app_version");
      if (!storedVersion) return "Unknown";
      const parsed = JSON.parse(storedVersion);
      if (typeof parsed === 'object' && parsed !== null) {
        return parsed.version || parsed.state || JSON.stringify(parsed);
      }
      return parsed || "Unknown";
    } catch (error) {
      const storedVersion = localStorage.getItem("app_version");
      return storedVersion || "Unknown";
    }
  };
  
  const appVersion = getAppVersion();
  const [signoutModal, setSignoutModal] = useState(false);
  function handleLogout() {
    dispatch(resetRedux());
    removeLocalStorageData();
    navigate("/login");
  }

  function handleSettings() {
    navigate("/setting");
    setOpen(false);
  }

  const handleOpenChange = (newOpen) => {
    setOpen(newOpen);
  };
  const content = (
    <div style={{ fontSize: "12px" }}>
      <p className=" cursor-pointer" style={{ marginBottom: "10px" }}>
        Version - {appVersion}
      </p>
      <p
        onClick={handleSettings}
        className="cursor-pointer"
        style={{ marginBottom: "10px" }}
        data-testid="settings-id"
      >
        Settings
      </p>
      <p
        onClick={() => {
          setSignoutModal(true);
          setOpen(false);
        }}
        className="cursor-pointer"
        data-testid="logout"
      >
        Sign out
      </p>
    </div>
  );
  let classNames = "sidebar-footer-container dFlex justifyBetween alignCenter";
  if (isSidebarCollapsed) classNames += " items-center";

  return (
    <>
      <div className={classNames}>
        <Space>
          <Avatar src={user?.picture} className="profile-avtar items-center" />
          {!isSidebarCollapsed && (
            <>
              <span className="user-name f14">
                {`Welcome ${
                  user?.given_name?.charAt(0)?.toUpperCase() +
                  user?.given_name?.slice(1)
                } !`}
              </span>
            </>
          )}
        </Space>

        <Popover
          content={content}
          trigger="click"
          data-testid="signout-popover"
          open={open}
          onOpenChange={handleOpenChange}
        >
          {!isSidebarCollapsed ? (
            <DashOutlined
              style={{ color: "#ffffff" }}
              data-testid="dash-icon"
            />
          ) : (
            <MoreOutlined
              style={{ color: "#ffffff" }}
              data-testid="more-icon"
            />
          )}
        </Popover>
        <ADModal
          title="Sign out"
          description="Are you sure you want to sign out?"
          open={signoutModal}
          onOk={handleLogout}
          onCancel={() => setSignoutModal(false)}
          okText="Sign out"
          cancelText="Cancel"
          showCancelButton
          hideButtons={false}
        />
      </div>
    </>
  );
};

export default SideBarFooter;
