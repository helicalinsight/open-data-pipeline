import { useEffect } from "react";
import { Spin } from "antd";
import { useNavigate } from "react-router-dom";
import { getLocalStorageItem } from "../../utils/userData";
import { chatRoutes, userRoutes } from "../../router/uiRouteConstants";
import { useDispatch } from "react-redux";
import { getAllJobsApi } from "../../apis/chatService";
import {
  addNewChatAction,
  setSelectedChatAction,
} from "../../store/actions/chatAction";
import { setUserDataAction } from "../../store/actions/appActions";
import { handleSessionExpiry } from "../../utils/handleSessionExpiry";
import {
  triggerGetApplication,
  triggerGetDatasources
} from "../../apis/commonAPIs";

function CreateSession() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user, token } = getLocalStorageItem() || {};

  useEffect(() => {
    if (!token) {
      navigate(userRoutes.login);
    } else {
      dispatch(setUserDataAction(user));
      getDefaultSession();
    }
  }, []);

  const getDefaultSession = async () => {
    getAllJobsApi({
      onSuccess: (jobData) => {
        const chats = jobData?.chats?.map((chat) => {
          let newChat = {
            ...chat,
          };
          dispatch(addNewChatAction(newChat));
          return newChat;
        });
        chats?.reverse();
        localStorage.setItem("reloadFromApi", true);
        navigate ("/app-space")
        // if (chats?.length > 0) {
        //   const defaultChat = chats[0];
        //   dispatch(setSelectedChatAction(defaultChat));
        //   navigate(
        //     {
        //       pathname: chatRoutes.chat,
        //       search: `?chat=${defaultChat?.chat_id}`,
        //     },
        //     {
        //       state: {
        //         chatId: defaultChat?.chat_id,
        //       },
        //     }
        //   );
        // } else {
        //   navigate({
        //     pathname: chatRoutes.chat,
        //   });
        // }
      },
      onError: (e) => {
        handleSessionExpiry(dispatch, e);
      },
    });
    triggerGetDatasources(dispatch);
    triggerGetApplication(dispatch);
  };

  return (
    <div className="session-main-container">
      <Spin
        tip={<span>please wait. we are setting up your workspace.</span>}
        size="large"
        style={{
          width: "100%",
          height: "100vh",
        }}
        className="items-center"
      >
        <div />
      </Spin>
    </div>
  );
}

export default CreateSession;
