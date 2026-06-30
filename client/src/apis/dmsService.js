import axios from "./axios.js";
import {  dmsConstants } from "./apiUrlConstants";

// dms-list currently we are  not using
export async function getDmsList({ userId, scheduleId, onSuccess, onError }) {
  try {
    const response = await axios.get(dmsConstants.dmsList, {
      params: { user_id: userId, schedule_id: scheduleId },
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
// dms-datasource api currently we're not using 
export async function getDmsDatasource({ onSuccess, onError }) {
  try {
    const response = await axios.get(dmsConstants.dmsDatasource, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

//dms-delete  currently we are not using 
export async function deleteDmsSchedule({ payload, onSuccess, onError }) {
  try {
    const response = await axios.delete(dmsConstants.deleteDmsSchedule, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
      data: JSON.stringify(payload),
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

// dmsschedule
export async function triggerDms({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(dmsConstants.dmsSchedule, payload, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    console.log("err", error);
    onError(error?.response?.data || error || "");
  }
}

// save the source & destination data
export async function saveProgressDms({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(dmsConstants.dmsPostProgress, payload, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    console.log("err", error);
    onError(error?.response?.data || error || "");
  }
}
// to get Progress Save data
export async function getProgressDms({ chatId, onSuccess, onError }) {
  try {
    const response = await axios.get(dmsConstants.dmsGetProgress, {
      params: { chat_id: chatId},
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}