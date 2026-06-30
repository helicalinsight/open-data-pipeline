import actionsTypes from "../../../store/actions/actionTypes";
import auditReducer from "../../../store/reducers/auditReducer";

const { 
  SET_AUDIT_BILLING_SUMMARY, 
  SET_DATE_RANGE, 
  SET_DETAIL_DATA, 
  SET_IS_DETAILED_VIEW 
} = actionsTypes.audits;

describe("auditReducer", () => {
  const initialState = {
    billingSummary: {},
    detailData: [],
    dateRange: {
      startTime: null,
      endTime: null,
    },
    isDetailedView: false,
  };

  it("should return the initial state", () => {
    expect(auditReducer(undefined, {})).toEqual(initialState);
  });

  describe("SET_AUDIT_BILLING_SUMMARY", () => {
    it("should handle SET_AUDIT_BILLING_SUMMARY", () => {
      const action = {
        type: SET_AUDIT_BILLING_SUMMARY,
        payload: { total: 1000, month: "October" },
      };
      const newState = auditReducer(initialState, action);
      expect(newState.billingSummary).toEqual({ total: 1000, month: "October" });
    });
  });

  describe("SET_DETAIL_DATA", () => {
    it("should handlee SET_DETAIL_DATA", () => {
      const action = {
        type: SET_DETAIL_DATA,
        payload: [{ id: 1, name: "Item 1" }, { id: 2, name: "Item 2" }],
      };
      const newState = auditReducer(initialState, action);
      expect(newState.detailData).toEqual([{ id: 1, name: "Item 1" }, { id: 2, name: "Item 2" }]);
    });
  });

  describe("SET_IS_DETAILED_VIEW", () => {
    it("shouldd handle SET_IS_DETAILED_VIEW", () => {
      const action = {
        type: SET_IS_DETAILED_VIEW,
        payload: true,
      };
      const newState = auditReducer(initialState, action);
      expect(newState.isDetailedView).toEqual(true);
    });
  });

  describe("SET_DATE_RANGE", () => {
    it("should handle SET_DATE_RANGE", () => {
      const action = {
        type: SET_DATE_RANGE,
        payload: { startTime: '2024-01-01', endTime: '2024-01-31' },
      };
      const newState = auditReducer(initialState, action);
      expect(newState.dateRange).toEqual({ startTime: '2024-01-01', endTime: '2024-01-31' });
    });
  });

  it("should handle RESET_STATE", () => {
    const state = {
      billingSummary: { total: 1000, month: "October" },
      detailData: [{ id: 1, name: "Item 1" }],
      dateRange: {
        startTime: '2024-01-01',
        endTime: '2024-01-31',
      },
      isDetailedView: true,
    };
    const action = { type: "RESET_STATE" };
    expect(auditReducer(state, action)).toEqual(initialState);
  });

  it("should return the current state for unknown action", () => {
    const state = {
      billingSummary: { total: 1000, month: "October" },
      detailData: [{ id: 1, name: "Item 1" }],
      dateRange: {
        startTime: '2024-01-01',
        endTime: '2024-01-31',
      },
      isDetailedView: true,
    };
    const action = { type: "UNKNOWN_ACTION" };
    expect(auditReducer(state, action)).toEqual(state);
  });
});