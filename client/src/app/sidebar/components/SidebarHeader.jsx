import "../style.scss";
import { Divider, Tooltip, Popover } from "antd";
import { useDispatch } from "react-redux";
import { useState } from "react";
import { ADSpace } from "../../../components";
import {
  LoginOutlined,
  FieldTimeOutlined,
  CommentOutlined,
  AuditOutlined,
  MoreOutlined,
  DoubleLeftOutlined,
  // SyncOutlined,
  SwapOutlined,
} from "@ant-design/icons";
import { imagePath } from "../../../constants/appConstants";
import PremiumFeatureWrapper from "../../../components/ADPremiumFutureWrapper";
import { setSidebarState } from "../../../store/actions/appActions";
import { useNavigate } from "react-router-dom";
import {  setIndividualJob } from "../../../store/actions/jobScheduleActions";

function SidebarHeader({ isSidebarCollapsed }) {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [popoverVisible, setPopoverVisible] = useState(false);

  const handleIconClick = (route) => {
    navigate(route);
    setPopoverVisible(false);
    dispatch(setIndividualJob(false));
  };

  const renderIcons = () => (
    <>
      <PremiumFeatureWrapper
        module="chat"
        feature="jobs"
        tooltip={{ title: "Jobs" }}
      >
        <CommentOutlined
          data-testid="job-listing-view"
          className="cursor-pointer"
          style={{
            fontSize: isSidebarCollapsed ? "20px" : "20px",
            color: isSidebarCollapsed ? "black" : "white",
          }}
          onClick={() => handleIconClick("/app-space")}
        />
      </PremiumFeatureWrapper>

      <Divider type="vertical" />

      <PremiumFeatureWrapper
        module="chat"
        feature="create"
        tooltip={{ title: "Data Sources" }}
      >
        <LoginOutlined
          data-testid="datasources-view"
          className="cursor-pointer"
          style={{
            fontSize: isSidebarCollapsed ? "18px" : "18px",
            color: isSidebarCollapsed ? "black" : "white",
          }}
          onClick={() => handleIconClick("/data-source")}
        />
      </PremiumFeatureWrapper>

      <Divider type="vertical" />

      <PremiumFeatureWrapper
        module="chat"
        feature="schedule"
        tooltip={{ title: "Job Schedule" }}
      >
        <FieldTimeOutlined
          data-testid="job-scheduling-view"
          id="jobSchedule"
          className="cursor-pointer"
          style={{
            fontSize: isSidebarCollapsed ? "20px" : "20px",
            color: isSidebarCollapsed ? "black" : "white",
          }}
          onClick={() => handleIconClick("/schedule")}
        />
      </PremiumFeatureWrapper>

      <Divider type="vertical" />

      <PremiumFeatureWrapper
        module="chat"
        feature="schedule"
        tooltip={{ title: "Audit" }}
      >
        <AuditOutlined
          data-testid="audit-view"
          id="audit"
          className="cursor-pointer"
          style={{
            fontSize: isSidebarCollapsed ? "20px" : "20px",
            color: isSidebarCollapsed ? "black" : "white",
          }}
          onClick={() => handleIconClick("/audit")}
        />
      </PremiumFeatureWrapper>
      <Divider type="vertical" />

      <PremiumFeatureWrapper
        module="chat"
        feature="schedule"
        tooltip={{ title: "DMS" }}
      >
        <SwapOutlined
          data-testid="dms"
          id="dms"
          className="cursor-pointer"
          style={{
            fontSize: isSidebarCollapsed ? "20px" : "20px",
            color: isSidebarCollapsed ? "black" : "white",
          }}
          onClick={() => handleIconClick("/dms")}
        />
      </PremiumFeatureWrapper>
    </>
  );

  const popoverContent = (
    <ADSpace
      flexWrap="wrap"
      stack="vertical"
      justifyContent="flex-start"
      alignItem="center"
      className="more-icons-div-sidebar"
    >
      {renderIcons()}
    </ADSpace>
  );

  return (
    <div
      className={`sidebar-header items-center flexColumn w-100 ${
        isSidebarCollapsed && "sidebar-collapsed"
      }`}
    >
      <div className="minimize-menu">
        <span className="ad-title" data-testid="app-logo-title">
          Ask On Data
          <sup>
            <img
              src={`${imagePath}/favicon.svg`}
              style={{ height: "25px" }}
              alt="logo"
            />
          </sup>
        </span>
        <Tooltip title="Minimize Sidebar">
          <DoubleLeftOutlined
            data-testid="menufold-id"
            className="cursor-pointer double-left"
            onClick={() => {
              dispatch(setSidebarState(true));
            }}
          />
        </Tooltip>
      </div>
      <ADSpace
        flexWrap="wrap"
        stack={!isSidebarCollapsed ? "horizontal" : "vertical"}
        space={isSidebarCollapsed && "6"}
        justifyContent="center"
        alignItem="center"
        className="icons-div-sidebar"
      >
        {!isSidebarCollapsed && renderIcons()}
        {isSidebarCollapsed && (
          <Popover
            content={popoverContent}
            trigger="click"
            open={popoverVisible}
            onOpenChange={setPopoverVisible}
          >
            <MoreOutlined
              className="cursor-pointer"
              style={{ color: "#ffffff" }}
              data-testid="more-options"
              onClick={() => setPopoverVisible(true)}
            />
          </Popover>
        )}
      </ADSpace>
    </div>
  );
}

export default SidebarHeader;
