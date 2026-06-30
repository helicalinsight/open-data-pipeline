import { setSessionExpiry } from "../store/actions/appActions";

const invalidErrList = ["Token is invalid", "Token expired", "Invalid token"];

export const handleSessionExpiry = async (dispatch, error) => {
  if (invalidErrList.includes(error?.msg || error?.message)) {
    await dispatch(setSessionExpiry(true));
  }
};
