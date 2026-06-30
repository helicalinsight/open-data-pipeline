import { Button } from "antd";
import { ADSpace } from "../../../components";
import { downloadFileApi } from "../../../apis/fileService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { useDispatch, useSelector } from "react-redux";
import { handleFileBlobDownload } from "../utils/listFiles.utils";

function DownloadFiles({ message, files }) {
  const dispatch = useDispatch();
  const selectedChat = useSelector((state) => state.chat?.selectedChat);

  function handleFileDownload(file) {
    downloadFileApi({
      chat_id: selectedChat?.chat_id,
      featherId: file.source_id,
      onSuccess: (blobData, contentType) => {
        handleFileBlobDownload({
          blobData,
          contentType,
          fallbackExtension: "xlsx",
          fallbackFileName: "export",
          originalFileName: file.export_name,
          supportedTypes: ["xlsx", "xls", "csv", "pdf", "doc", "docx"],
        });
      },
      onError: (error) => handleSessionExpiry(dispatch, error),
    });
  }

  return (
    <ADSpace stack="vertical" space={4} data-testid="download-files">
      <div data-testid="message-id">{message}</div>
      {files?.map((file, index) => (
        <Button
          key={file?.source_id || index}
          onClick={() => handleFileDownload(file)}
          type="primary"
          ghost
          data-testid="export-file-id"
        >
          {file.export_name}
        </Button>
      ))}
    </ADSpace>
  );
}

export default DownloadFiles;
