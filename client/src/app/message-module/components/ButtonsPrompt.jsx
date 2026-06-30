import { Button, Space } from "antd";
import { useContext, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { ChatContext } from "../../chat-module/components/ChatContext";

function ButtonsPrompt({ message }) {
  const { handleMessage } = useContext(ChatContext);
  const [isDisabled, setIsDisabled] = useState(false);
  function handleButtonClick(data) {
    handleMessage(data);
    setIsDisabled(true);
  }
  return (
    <Space direction="vertical" data-testid="buttons-prompt">
      <Space key={uuidv4()}>
        <div>{message.text}</div>
      </Space>
      <Space key={uuidv4()}>
        {message.quick_replies.map((btn) => (
          <Button
            type="primary"
            shape="round"
            ghost
            size="small"
            key={btn.payload}
            disabled={isDisabled}
            onClick={() => handleButtonClick(btn)}
            data-testid={"buttons-prompt-" + btn.payload}
          >
            {btn.title}
          </Button>
        ))}
      </Space>
    </Space>
  );
}

export default ButtonsPrompt;
