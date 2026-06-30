import axios from "./axios.js";
import { auditConstants } from "./apiUrlConstants.js";

export async function getAuditBillingSummary({ summary_type, target_date, onSuccess, onError }) {
  try {
    const response = await axios.get(`${auditConstants.auditBilling}?summary_type=${summary_type}&target_date=${target_date}`, 
        {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
export async function getDetailData({ detailLink, onSuccess, onError }) {
  try {
    const response = await axios.get(detailLink, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

