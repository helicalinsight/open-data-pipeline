import { Button, Input, Tooltip } from "antd";
import React, { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addNewChatAction,
  setPreviewTableData,
  setSelectedChatAction,
} from "../../../store/actions/chatAction";
import { PlusCircleOutlined } from "@ant-design/icons";
import { createChat } from "../../../apis/chatService";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { getLocalStorageItem } from "../../../utils/userData";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import genrateUniqueJobName from "../../../utils/genrateUniqueJobName";
import DataBaseModule from "../../database-module";
import { ADSpace } from "../../../components";
import { setMessageParamsAction } from "../../../store/actions/messageActions";
import {
  chatRoutes,
  dmsPath,
  isDmsRoute,
} from "../../../router/uiRouteConstants";
import {
  addNewDmsChatAction,
  addsetDmsStepsAction,
  setDmsSelectedChatAction,
  setSelectPipelineModeAction,
} from "../../../store/actions/dmsAction";

export default function SidebarActions({
  searchValue,
  setSearchValue,
  allJobs,
  socket,
}) {
  const inputRef = useRef();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = getLocalStorageItem() || {};
  const [searchParms] = useSearchParams();
  const [isMouseEntered, setIsMouseEntered] = useState(false);
  const [createJobLoading, setCreateJobLoading] = useState(false);
  const isSidebarCollapsed = useSelector(
    (state) => state.app.isSidebarCollapsed,
  );
  const [openSourcesDrawer, setOpenSourcesDrawer] = useState(false);
  const isDms = isDmsRoute(location.pathname);

  useEffect(() => {
    if (isMouseEntered && inputRef?.current) {
      inputRef.current.focus();
    }
  }, [isMouseEntered]);

  async function handleCreateChat() {
    setCreateJobLoading(true);
    let jobName = genrateUniqueJobName(allJobs);
    const payload = {
      user_id: user.id,
      chat_name: jobName, 
    };
    if (isDms) {
      payload.service_mode = "DMS";
    }
    await createChat({
      payload,
      onSuccess: (response) => {
        const { chat_id, chat_name } = response;
        setCreateJobLoading(false);
        dispatch(setPreviewTableData({ columns: [], datasource: {} }));
        dispatch(setMessageParamsAction({ offset: 0 }));
        if (isDms) {
          dispatch({ type: "RESET_DMS_STATE" });
          dispatch(addNewDmsChatAction(response));
          dispatch(setDmsSelectedChatAction({ chat_id, chat_name }));
          dispatch(addsetDmsStepsAction(0)); 
          dispatch(setSelectPipelineModeAction("table"));
        } else {
          dispatch(addNewChatAction(response));
          dispatch(setSelectedChatAction({ chat_id, chat_name }));
        }
        navigate(
          {
            search: `?chat=${chat_id}`,
          },
          { state: { chatId: chat_id } },
        );
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        setCreateJobLoading(false);
      },
    });
  }


  const getCreateButtonText = () => {
    if (isSidebarCollapsed || isMouseEntered || searchValue !== "") return "";
    return "Create a new Job";
  };

  return (
    <>
      <div className="actions-container dFlex justifyCenter alignCenter w-100">
        {!isSidebarCollapsed && (
          <div
            onMouseLeave={() => {
              setIsMouseEntered(false);
            }}
            style={{
              width: !isMouseEntered && searchValue === "" ? "15%" : "auto",
            }}
            className="search-container dFlex"
            data-testid="search-container-id"
          >
            <Button
              type="text"
              className="search-button"
              icon={<CustomIcon name={"search"} />}
              data-testid="search-button-id"
              onMouseEnter={() => {
                if (!isMouseEntered) setIsMouseEntered(true);
              }}
            />
            {(isMouseEntered || searchValue !== "") && (
              <Input
                ref={inputRef}
                onChange={(e) => setSearchValue(e.target.value)}
                bordered={false}
                value={searchValue}
                placeholder="Search"
                data-testid="search-id"
                allowClear
              />
            )}
          </div>
        )}
        <ADSpace flexWrap="wrap" alignItem="center">
          <Tooltip title={isSidebarCollapsed ? "Create a new job" : ""}>
            <Button
              type="primary"
              data-testid="create-chat-id"
              icon={<PlusCircleOutlined style={{ fontSize: "19.364px" }} />}
              onClick={handleCreateChat}
              loading={createJobLoading}
              className="create-job-button dFlex alignCenter flex-1"
              style={{
                backgroundColor: "#F28E1E",
                width: isSidebarCollapsed ? "30px" : "auto",
                border: isSidebarCollapsed && "none",
                justifyContent:
                  isMouseEntered || isSidebarCollapsed || searchValue !== ""
                    ? "center"
                    : "flex-start",
                fontSize: "12px",
              }}
            >
              {getCreateButtonText()}
            </Button>
          </Tooltip>
        </ADSpace>
      </div>
      {openSourcesDrawer && (
        <DataBaseModule
          // socket={socket}
          setOpenDbModal={setOpenSourcesDrawer}
          openDbModal={openSourcesDrawer}
          haveLoad={false}
        />
      )}
    </>
  );
}
