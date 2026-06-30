import actionsTypes from "../actions/actionTypes";

const initialState = {
  billingSummary: {},
  detailData: [],
  dateRange: {
    startTime: null,
    endTime: null,
  },
  isDetailedView: false,
};

const {
  SET_AUDIT_BILLING_SUMMARY,
  SET_DETAIL_DATA,
  SET_DATE_RANGE,
  SET_IS_DETAILED_VIEW,
} = actionsTypes.audits;

function auditReducer(state = initialState, action) {
  switch (action.type) {
    case SET_AUDIT_BILLING_SUMMARY: {
      return {
        ...state,
        billingSummary: action.payload,
      };
    }
    case SET_DETAIL_DATA:
      return {
        ...state,
        detailData: action.payload,
      };
    case SET_IS_DETAILED_VIEW:
      return {
        ...state,
        isDetailedView: action.payload,
      };
    case SET_DATE_RANGE:
      return {
        ...state,
        dateRange: {
          startTime: action.payload.startTime,
          endTime: action.payload.endTime,
        },
      };
    case "RESET_STATE":
      return initialState;
    default: {
      return { ...state };
    }
  }
}

export default auditReducer;
