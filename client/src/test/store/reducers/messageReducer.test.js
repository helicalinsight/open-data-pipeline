import actionsTypes from "../../../store/actions/actionTypes";
import { messageReducer } from "../../../store/reducers";

const {
  ADD_NEW_MESSAGE,
  SET_MESSAGE_HISTORY_PARAMS,
  CLEAR_CHAT_MESSAGES_HISTORY,
} = actionsTypes.messages;

describe("messageReducer", () => {
  const initialState = {
    allMessages: {},
    params: { offset: 0, limit: 30 },
  };

  it("should return the initial state", () => {
    expect(messageReducer(undefined, {})).toEqual(initialState);
  });

  describe("ADD_NEW_MESSAGE", () => {
    it("should handle ADD_NEW_MESSAGE with status update", () => {
      const action = {
        type: ADD_NEW_MESSAGE,
        payload: {
          chatId: "123",
          data: [{ id: 1, text: "Hello" }],
          isHistory: false,
          status: "update",
        },
      };
      const newState = messageReducer(initialState, action);
      expect(newState.allMessages["123"]).toEqual([{ id: 1, text: "Hello" }]);
    });

    it("should handle ADD_NEW_MESSAGE with isHistory true", () => {
      const state = {
        ...initialState,
        allMessages: { 123: [{ id: 1, text: "Old" }] },
      };
      const action = {
        type: ADD_NEW_MESSAGE,
        payload: {
          chatId: "123",
          data: [{ id: 2, text: "New" }],
          isHistory: true,
          status: "add",
        },
      };
      const newState = messageReducer(state, action);
      expect(newState.allMessages["123"]).toEqual([
        { id: 1, text: "Old" },
        { id: 2, text: "New" },
      ]);
    });

    it("should handle ADD_NEW_MESSAGE with isHistory false", () => {
      const state = {
        ...initialState,
        allMessages: { 123: [{ id: 1, text: "Old" }] },
      };
      const action = {
        type: ADD_NEW_MESSAGE,
        payload: {
          chatId: "123",
          data: [{ id: 2, text: "New" }],
          isHistory: false,
          status: "add",
        },
      };
      const newState = messageReducer(state, action);
      expect(newState.allMessages["123"]).toEqual([
        { id: 2, text: "New" },
        { id: 1, text: "Old" },
      ]);
    });
  });

  it("should handle SET_MESSAGE_HISTORY_PARAMS", () => {
    const action = {
      type: SET_MESSAGE_HISTORY_PARAMS,
      payload: { offset: 30, limit: 50 },
    };
    const newState = messageReducer(initialState, action);
    expect(newState.params).toEqual({ offset: 30, limit: 50 });
  });

  it("should handle CLEAR_CHAT_MESSAGES_HISTORY", () => {
    const state = {
      ...initialState,
      allMessages: {
        123: [{ id: 1, text: "Hello" }],
        456: [{ id: 2, text: "World" }],
      },
    };
    const action = {
      type: CLEAR_CHAT_MESSAGES_HISTORY,
      payload: { chatId: "123" },
    };
    const newState = messageReducer(state, action);
    expect(newState.allMessages).toEqual({ 456: [{ id: 2, text: "World" }] });
  });

  it("should handle RESET_STATE", () => {
    const state = {
      allMessages: { 123: [{ id: 1, text: "Hello" }] },
      params: { offset: 30, limit: 50 },
    };
    const action = { type: "RESET_STATE" };
    expect(messageReducer(state, action)).toEqual(initialState);
  });

  it("should return current state for unknown action", () => {
    const state = { ...initialState, allMessages: { 123: [{ id: 1 }] } };
    expect(messageReducer(state, { type: "UNKNOWN_ACTION" })).toEqual(state);
  });
});
