import actionsTypes from "./actionTypes";

//use action as suffix for all action methods

function addNewMessageAction(payload) {
  return {
    type: actionsTypes.messages.ADD_NEW_MESSAGE,
    payload,
  };
}

function setMessageParamsAction(payload) {
  return {
    type: actionsTypes.messages.SET_MESSAGE_HISTORY_PARAMS,
    payload,
  };
}

function clearChatMessagesHistoryAction(payload){
  return{
    type: actionsTypes.messages.CLEAR_CHAT_MESSAGES_HISTORY,
    payload
  }
}

export { addNewMessageAction, setMessageParamsAction, clearChatMessagesHistoryAction };
