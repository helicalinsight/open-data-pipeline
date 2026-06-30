import actionsTypes from "./actionTypes";

export const setAuditBillingSummaryAction = (payload) => {
  return {
    type: actionsTypes.audits.SET_AUDIT_BILLING_SUMMARY,
    payload,
  };
};
export const setIsDetailedView = (payload) => {
  return {
    type: actionsTypes.audits.SET_IS_DETAILED_VIEW,
    payload,
  };
};
export const setDetailDataAction = (data) => ({
  type: actionsTypes.audits.SET_DETAIL_DATA,
  payload: data,
});
export const setDateRange = (startTime, endTime) => ({
  type: actionsTypes.audits.SET_DATE_RANGE,
  payload: { startTime, endTime },
});
