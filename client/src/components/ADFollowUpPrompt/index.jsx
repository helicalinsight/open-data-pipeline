import React from "react";
import { Button } from "antd";
import ADSpace from "../ADSpace";
import "./style.scss";
import { setFollowUpPromptAction } from "../../store/actions/chatAction";
import { useDispatch, useSelector } from "react-redux";

function ADFollowUpPrompt({ handleMessageSent, setEditPrompt }) {
  const dispatch = useDispatch();
  const currentChat = useSelector((state) => state.chat?.selectedChat);
  const followUpPrompts =
    useSelector(
      (state) => state.chat?.chatList[currentChat?.chat_id]?.followUpPrompts
    ) ?? [];

  function handleTagClick(prompt) {
    dispatch(
      setFollowUpPromptAction({ chat_id: currentChat.chat_id, prompts: [] })
    );
    if (prompt.property === "edit_prompt") {
      setEditPrompt(prompt);
      return;
    }
    if (prompt.property === "show_more") {
      dispatch(
        setFollowUpPromptAction({
          chat_id: currentChat.chat_id,
          prompts: prompt.data ?? [],
        })
      );
      return;
    }
    //TODO: ask data from b.e in proper format for upload file
    if (prompt.property === "upload_file") {
      let data = {
        payload: prompt.property,
        title: prompt.prompt,
      };
      handleMessageSent(data);
      return;
    }
    let data = {
      payload: prompt.response ?? prompt.property,
      title: prompt.prompt,
    };
    handleMessageSent(data);
  }

  if (followUpPrompts.length) {
    return (
      <ADSpace space="4" justifyContent="start" className="follow-up-prompt">
        {followUpPrompts?.map((prompt, index) => {
          return (
            <Button
              className="follow-up-prompt__tag-item"
              onClick={(e) => handleTagClick(prompt)}
              key={index}
              data-testid="prompt-button"
            >
              {prompt.prompt}
            </Button>
          );
        })}
      </ADSpace>
    );
  }
  return;
}

export default ADFollowUpPrompt;
