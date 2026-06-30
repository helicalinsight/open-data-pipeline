import { Button } from "antd";
import { ADSpace } from "../../../components";
import { useDispatch, useSelector } from "react-redux";
import { createChat } from "../../../apis/chatService";
import genrateUniqueJobName from "../../../utils/genrateUniqueJobName";
import {
  addNewChatAction,
  setSelectedChatAction,
} from "../../../store/actions/chatAction";
import { useNavigate, useSearchParams } from "react-router-dom";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { useState } from "react";
import CustomMessage from "../../settings-module/CustomMessage";
import { useLocation } from "react-router-dom";
import { chatRoutes, dmsPath } from "../../../router/uiRouteConstants";
import {
  addNewDmsChatAction,
  addsetDmsStepsAction,
  setDmsSelectedChatAction,
  setSelectPipelineModeAction,
} from "../../../store/actions/dmsAction";

function DefaultJobView({ setShowDefaultPage }) {
  const user = useSelector((state) => state.app.user);
  const dispatch = useDispatch();
  const location = useLocation();

  const navigate = useNavigate();
  const [searchParms] = useSearchParams();
  const allChats = useSelector((state) => state.chat?.chatList || {});
  const allDmsJobs = useSelector((state) => state.dms?.dmsJobs || {});
  const isDmsRouteVar = location.pathname === chatRoutes.dms;
  const allJobs = isDmsRouteVar ? Object.values(allDmsJobs) : Object.values(allChats);
  const [jobLoading, setJobLoading] = useState(false);

  let firstName = user?.firstname?.split(" ")[0];

  async function handleCreateJobClick() {
    setJobLoading(true);
    let jobName = genrateUniqueJobName(allJobs);
    const payload = {
      user_id: user.id,
      chat_name: jobName,
    };
    if (isDmsRouteVar) {
      payload.service_mode = "DMS";
    }
    await createChat({
      payload,
      onSuccess: (response) => {
        setJobLoading(false);
        const { chat_id, chat_name } = response;
        if (isDmsRouteVar) {
          dispatch({ type: "RESET_DMS_STATE" });
          dispatch(addNewDmsChatAction(response));
          dispatch(setDmsSelectedChatAction({ chat_id, chat_name }));
          dispatch(setSelectPipelineModeAction("table"));
          dispatch(addsetDmsStepsAction(0)); 
        } else {
          dispatch(addNewChatAction(response));
          dispatch(setSelectedChatAction({ chat_id, chat_name }));
        }
        setShowDefaultPage((prev) => false);
        navigate(
          {
            search: `?chat=${chat_id}`,
          },
          { state: { chatId: chat_id } },
        );
        // navigate(
        //   {
        //     search: `?session=${sessionId}&chat=${chat_id}`,
        //   },
        //   { state: { chatId: chat_id, sessionId } }
        // );
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        setJobLoading(false);
      },
    });
  }
  return (
    <div
      style={{
        width: "100%",
        margin: "0 auto",
        maxWidth: "1200px",
      }}
    >
      <ADSpace
        justifyContent="center"
        alignItem="center"
        className="chat-section__default-view"
        data-testid="default-job-view-id"
        style={{ marginTop: "50px" }}
      >
        <ADSpace space="10" stack="vertical" style={{ width: "50%" }}>
          <ADSpace
            stack="vertical"
            alignItem="center"
            className="chat-section__default-view--title"
          >
            <div>Welcome ! {firstName}</div>
            <div>Ready? Set. Chat! Let's jump right into things</div>
          </ADSpace>
          <ADSpace justifyContent="space-between" space="10">
            <ADSpace
              stack="vertical"
              className="chat-section__default-view--image-section"
              alignItem="center"
            >
              <div>{isDmsRouteVar ? "D" : "A"}</div>
              <div>
                {isDmsRouteVar
                  ? "Data. Load data from variety of sources to your choice of destination"
                  : "Advance your data transformations with our NLP-powered ETL tool."}
              </div>
            </ADSpace>
            <ADSpace
              stack="vertical"
              alignItem="center"
              className="chat-section__default-view--image-section"
            >
              <div>{isDmsRouteVar ? "M" : "O"}</div>
              <div>
                {isDmsRouteVar
                  ? "Migration. Choose migration modes whether you want to replace data,merge data or execute custom commands."
                  : "Operate with natural language commands"}
              </div>
            </ADSpace>
            <ADSpace
              stack="vertical"
              alignItem="center"
              className="chat-section__default-view--image-section"
            >
              <div>{isDmsRouteVar ? "S" : "D"}</div>
              <div>
                {isDmsRouteVar
                  ? "Service. Manage multiple schedules to migrate your data."
                  : "Drive efficiency in your data processing tasks."}
              </div>
            </ADSpace>
          </ADSpace>
          <ADSpace justifyContent="center">
            <Button
              size="large"
              type="primary"
              loading={jobLoading}
              style={{ boxShadow: "none" }}
              onClick={handleCreateJobClick}
              data-testid="create-job-id"
            >
              Create Job
            </Button>
          </ADSpace>
        </ADSpace>
      </ADSpace>
    </div>
  );
}

export default DefaultJobView;
