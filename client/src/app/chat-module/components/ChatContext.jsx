import { createContext } from "react";

const defaultHandleMessage = () => {
  // Default implementation or leave it empty
};

export const ChatContext = createContext({
  handleMessage: defaultHandleMessage,
});
