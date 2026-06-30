import { produce } from "immer";
import actionsTypes from "../actions/actionTypes";

const intialState = {
  allMessages: {},
  params: { offset: 0, limit: 30 },
};

const {
  ADD_NEW_MESSAGE,
  SET_MESSAGE_HISTORY_PARAMS,
  CLEAR_CHAT_MESSAGES_HISTORY,
} = actionsTypes.messages;

function messageReducer(state = intialState, action) {
  switch (action.type) {
    case ADD_NEW_MESSAGE: {
      const { chatId, data, isHistory, status } = action.payload;
      return produce(state, (draft) => {
        if (status === "update") {
          draft.allMessages[chatId] = data;
        } else {
          let previousMsgs = [];
          if (state.allMessages[chatId])
            previousMsgs = [...state.allMessages[chatId]];
          if (isHistory) {
            draft.allMessages[chatId] = [...previousMsgs, ...data];
          } else {
            draft.allMessages[chatId] = [...data, ...previousMsgs];
          }
        }
      });
    }
    case SET_MESSAGE_HISTORY_PARAMS: {
      // const { offset, limit } = action.payload;
      return produce(state, (draft) => {
        draft.params = { ...state.params, ...action.payload };
      });
    }

    case CLEAR_CHAT_MESSAGES_HISTORY: {
      const { chatId } = action.payload;
      return produce(state, (draft) => {
        delete draft.allMessages[chatId];
      });
    }

    case "RESET_STATE":
      return intialState;

    default: {
      return state;
    }
  }
}

export default messageReducer;
