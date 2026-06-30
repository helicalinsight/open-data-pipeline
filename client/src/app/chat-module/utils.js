import getTimeStamp from "../../utils/getCurrentTime";

export function transformChatHistoryData(chatData) {
  if (!chatData?.length) return [];
  let newChatData = [];
  chatData.forEach((chat) => {
    if (chat.text) {
      newChatData.push({
        ...chat,
        time: getTimeStamp(chat.timestamp * 1000),
        id: chat.message_id,
      });
    }
  });
  return newChatData;
}

export const getRowClassName = (record, index) => {
  if (index % 2 === 1) return "row-bg-color";
  return "row-white-bg-color";
};
