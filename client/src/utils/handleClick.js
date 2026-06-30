import {
  setEditConnection,
  setSelectedDatasourceAction,
} from "../store/actions/databaseActions";
import { setMessageAction } from "../store/actions/settingActions";

const handleBackClick = (dispatch, editConnection, setCurrent, current) => {
  dispatch(setSelectedDatasourceAction({}));
  if (Object.keys(editConnection).length > 0) {
    dispatch(setEditConnection({}));
  }
  setCurrent(current - 1);
};

export default handleBackClick;

export const dispatchMessage = (
  dispatch,
  type,
  message,
  isConnectionTest = false
) => {
  dispatch(
    setMessageAction({
      type,
      message,
    })
  );
  const timeoutDuration = isConnectionTest ? 700 : 3000;

  setTimeout(() => {
    dispatch(setMessageAction(null));
  }, timeoutDuration);
};
