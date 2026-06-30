import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { dataPreview } from "../../../apis/chatService";
import PreviewTable from "./preview-data/PreviewTable";
import PreviewFooter from "./preview-data/PreviewFooter";
import PreviewEmpty from "./preview-data/PreviewEmpty";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import {
  setPreviewRefreshData,
  setPreviewTableData,
} from "../../../store/actions/chatAction";
import { ADSpace } from "../../../components";
import { getTableColumns } from "./utils";
import { getLocalStorageItem } from "../../../utils/userData";
import { message } from "antd";
import { dispatchMessage } from "../../../utils/handleClick";

const ADPreview = () => {
  const dispatch = useDispatch();
  const [activeTabData, setActiveTabData] = useState();
  const [messageApi, contextHolder] = message.useMessage();
  const [paginationData, setPaginationData] = useState({
    limit_by: 10,
    offset: 0,
  });
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const selectedChat = useSelector((state) => state.chat?.selectedChat);
  const chatId = selectedChat?.chat_id;
  const previewRefresh = useSelector((state) => state.chat?.previewRefresh);
  const previewTableData = useSelector((state) => state.chat?.previewTableData);
  const loadedFiles =
    useSelector((state) => state.chat?.chatList[chatId]?.loadedFiles) || [];
  const selectedFile =
    useSelector((state) => state.chat?.chatList[chatId]?.selectedFiles) || [];
  const previewState = useSelector((state) => state.app.previewState);
  const { user } = getLocalStorageItem() || {};
  useEffect(() => {
    if (selectedFile?.length) {
      setActiveTabData(selectedFile[0]);
    } else {
      setActiveTabData(null);
    }
  }, [selectedFile]);

  // useEffect(() => {
  //   setPaginationData((prev) => ({
  //     ...prev,
  //     offset: 0, // Reset offset to 0 when file changes
  //   }));
  // }, [activeTabData]);

  const fetchDataPreview = (mode) => {
    let alias;
    let source_id;

    if (mode) {
      alias = selectedFile[0]?.alias;
      source_id = selectedFile[0]?.source_id;
    } else {
      alias = activeTabData.alias;
      source_id = activeTabData.source_id;
    }

    if (!alias || !source_id) return;

    const payload = {
      type: "preview",
      per_page: paginationData?.limit_by,
      page: currentPage,
      preview_info: [{ alias, source_id }],
      user_info: {
        user_id: user?.id,
        chat_id: chatId,
      },
    };

    if (!mode) {
      setLoading(true);
    }

    dataPreview({
      payload,
      onSuccess: (dataObj = []) => {
        if (dataObj?.length) {
          let fileData = dataObj[0];
          const columns = getTableColumns(fileData);
          setLoading(false);
          dispatch(setPreviewTableData({ columns, datasource: fileData }));
        }
      },
      onError: (error) => {
        setLoading("error");
        handleSessionExpiry(dispatch, error);
        dispatchMessage(dispatch, "error", error?.message);
      },
    });
  };

  useEffect(() => {
    if (activeTabData) {
      fetchDataPreview();
    }
  }, [activeTabData, paginationData]);

  useEffect(() => {
    if (
      previewRefresh?.refresh &&
      previewRefresh?.id &&
      loadedFiles?.length > 0
    ) {
      fetchDataPreview("onTrasformation"); // Trigger API

      dispatch(setPreviewRefreshData({ id: "", refresh: false }));
      if (selectedFile?.length > 0) {
        setPaginationData({ limit_by: 10, offset: 0 });
      }
    }
  }, [previewRefresh]);

  return (
    <>
      {contextHolder}
      <div
        className={`ad-preview-container h-100 ${
          previewState && "preview-section"
        }`}
      >
        {loadedFiles.length ? (
          <ADSpace
            stack="vertical"
            justifyContent="space-between"
            data-testid="preview-table-id"
            className="h-100"
          >
            <PreviewTable
              previewTableData={previewTableData}
              loading={loading}
              paginationData={paginationData}
              currentPage={currentPage}
              activeTabData={activeTabData}
            />
            <PreviewFooter
              previewTableData={previewTableData}
              setActiveTabData={setActiveTabData}
              activeTabData={activeTabData}
              paginationData={paginationData}
              setPaginationData={setPaginationData}
              chatId={chatId}
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
            />
          </ADSpace>
        ) : (
          <PreviewEmpty />
        )}
      </div>
    </>
  );
};

export default ADPreview;
