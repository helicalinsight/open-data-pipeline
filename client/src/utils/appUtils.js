import { getDagList } from "../apis/jobScheduleService";
import {
  setDagsListAction,
  setDagsTotalCount,
} from "../store/actions/jobScheduleActions";
import { handleSessionExpiry } from "./handleSessionExpiry";

export const convertToString = (value) => {
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
};

export const sortByName = (data) => {
  return data.sort((a, b) => a.name.localeCompare(b.name));
};

export const fetchDagListUtil = ({
  dispatch,
  setLoading,
  user,
  current,
  pageSize,
  filters = {},
}) => {
  const payload = {
    user_id: user?.id,
    page: current,
    per_page: pageSize,
  };
  Object.keys(filters).forEach(key => {
    if (filters[key]) {
      payload[key] = filters[key];
    }
  });
  if (setLoading) setLoading(true);

  getDagList({
    payload,
    onSuccess: (response) => {
      dispatch(setDagsListAction(response?.dags));
      dispatch(setDagsTotalCount(response?.total_records));
      if (setLoading) setLoading(false);
    },
    onError: (error) => {
      handleSessionExpiry(dispatch, error);
      if (setLoading) setLoading(false);
    },
  });
};
