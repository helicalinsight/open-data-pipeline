import { Button, Menu, Space, Typography } from "antd";
import { useState, useContext } from "react";
import { ChatContext } from "../../chat-module/components/ChatContext";
import {
  generateListData,
  getLoadedFiles,
  isLoadFileDisabled,
} from "../utils/listFiles.utils";

const { Text } = Typography;

function ListFiles({ message, files, isLastItem }) {
  const listData = generateListData(files, isLastItem);
  const { handleMessage } = useContext(ChatContext);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDisabled, setIsDisabled] = useState(true);

  function handleItemSelect(item) {
    setIsDisabled((prev) => false);
    setSelectedFiles(item.selectedKeys);
  }
  function loadFile() {
    setIsDisabled((prev) => true);
    const { loadedFiles, fileNames } = getLoadedFiles(files, selectedFiles);
    handleMessage({
      title: `Loaded files: ${fileNames}`,
      type: "load_file",
      payload: loadedFiles,
      isCustom: true,
    });
  }
  return (
    <Space direction="vertical" data-testid="list-files">
      <Text strong>{message}</Text>
      <Menu
        items={listData}
        style={{ background: "inherit", border: "none" }}
        inlineIndent="50px"
        onSelect={(item) => handleItemSelect(item)}
        multiple
        onDeselect={handleItemSelect}
      />

      <Space direction="vertical">
        <Button
          shape="round"
          type="primary"
          ghost
          disabled={isLoadFileDisabled(isLastItem, isDisabled)}
          onClick={loadFile}
        >
          Load File
        </Button>
      </Space>
    </Space>
  );
}

export default ListFiles;
