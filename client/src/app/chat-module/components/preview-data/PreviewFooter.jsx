import { useEffect, useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import { MenuOutlined } from "@ant-design/icons";
import { Button, Dropdown, Pagination, Space, Tooltip } from "antd";
import { ADSpace } from "../../../../components";
import {
  setPreviewTableData,
  setSelectedFilesAction,
  setIndexRanges,
  setOpenInfo,
} from "../../../../store/actions/chatAction";
import { switchSelectedFile } from "../../../../apis/fileService";
import { handleSessionExpiry } from "../../../../utils/handleSessionExpiry";

const PreviewFooter = (props) => {
  const {
    previewTableData,
    setActiveTabData,
    activeTabData,
    paginationData,
    setPaginationData,
    chatId,
    currentPage,
    setCurrentPage,
  } = props;

  const dispatch = useDispatch();
  const splitIndex = useSelector((state) => state.chat.splitIndex);

  const [items, setItems] = useState([]);
  const [indexRange, setIndexRange] = useState([0, 6]);
  const loadedFiles =
    useSelector((state) => state.chat.chatList[chatId]?.loadedFiles) || [];
  const memoizedLoadedFiles = useMemo(() => loadedFiles, [loadedFiles]);
  const start = (currentPage - 1) * paginationData.limit_by + 1;
  const end = Math.min(
    currentPage * paginationData.limit_by,
    previewTableData?.datasource?.total_records
  );
  const pipelineHistory =
    useSelector((state) => state.chat.chatList[chatId]?.pipelineHistory) || {};
  const paginationProps = {
    itemRender: (page, type, orginalElement) => {
      return (
        <Button
          size="small"
          style={{ background: "white", padding: "2px", height: "20px" }}
        >
          {orginalElement}
        </Button>
      );
    },

    total: previewTableData?.datasource?.total_records,
    current: currentPage,
    pageSize: paginationData?.limit_by,
    size: "small",
    showSizeChanger: true,
    // onChange: (page) => {
    //   setCurrentPage(page);
    // },
    pageSizeOptions: ["10", "20", "50", "100"],
    onShowSizeChange: (current, size) => {
      setPaginationData((prev) => ({
        ...prev,
        limit_by: size,
        offset: 0,
      }));
      setCurrentPage(1);
    },
    onChange: (page) => {
      const newOffset = (page - 1) * paginationData.limit_by;
      setPaginationData((prev) => ({
        ...prev,
        offset: newOffset,
      }));
      setCurrentPage(page);
    },
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [activeTabData]);

  useEffect(() => {
    if (memoizedLoadedFiles.length) {
      let newItems = memoizedLoadedFiles.map((file) => ({
        key: file?.source_id,
        label: (
          <Tooltip
            title={file?.alias}
            placement="right"
            overlayClassName="custom-tooltip"
          >
            <div
              style={{
                display: "flex",
                width: "100%",
              }}
            >
              <span className="menu-font-tooltip">{file?.alias}</span>
            </div>
          </Tooltip>
        ),
      }));
      setItems(newItems);
    }
  }, [memoizedLoadedFiles]);

  const handleClick = (e) => {
    dispatch(setOpenInfo(false));
    const liElement = e?.target;
    const sourceId = e?.currentTarget?.getAttribute("data-custom-key");
    const alias = liElement?.textContent;

    const clickedFile = loadedFiles?.find(
      (file) => file?.source_id === sourceId
    );
    if (activeTabData?.source_id && activeTabData?.source_id === sourceId) {
      return;
    }
    switchSelectedFile({
      payload: {
        chat_id: chatId,
        source_id: sourceId,
      },
      onSuccess: (res) => {
        if (res.success) {
          dispatch(setIndexRanges([0, splitIndex]));
          dispatch(
            setSelectedFilesAction({
              chat_id: chatId,
              files: [clickedFile],
            })
          );
          setActiveTabData({
            source_id: sourceId,
            alias,
          });
          dispatch(setPreviewTableData({ columns: [], datasource: {} }));
        }
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  const onClick = ({ key, domEvent }) => {
    dispatch(setOpenInfo(false));
    const alias = domEvent?.target?.innerText;
    const selectedFile = loadedFiles?.find((file) => file?.source_id === key);
    if (activeTabData?.source_id && activeTabData?.source_id === key) {
      return;
    }
    switchSelectedFile({
      payload: {
        chat_id: chatId,
        source_id: key,
      },
      onSuccess: (res) => {
        if (res.success) {
          dispatch(setIndexRanges([0, splitIndex]));
          dispatch(
            setSelectedFilesAction({
              chat_id: chatId,
              files: [selectedFile],
            })
          );
          setActiveTabData({
            source_id: key,
            alias,
          });
          dispatch(setPreviewTableData({ columns: [], datasource: {} }));
        }
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  const onLeftIconClick = () => {
    if (indexRange[0] <= 0) return;
    setIndexRange((prev) => [prev[0] - 6, prev[1] - 6]);
  };

  const onRightIconClick = () => {
    if (indexRange[1] >= loadedFiles.length) return;
    setIndexRange((prev) => [prev[0] + 6, prev[1] + 6]);
  };

  return (
    <ADSpace stack="vertical">
      <ADSpace justifyContent="space-between" className="pagination-container">
        <div className="page-count" data-testid="pagination-id">
          {previewTableData?.datasource?.total_records > 0 && (
            <span>{`${start}-${end} of ${previewTableData.datasource.total_records}`}</span>
          )}
        </div>
        {previewTableData?.datasource?.total_records > 0 && (
          <Pagination
            {...paginationProps}
            simple
            style={{ marginRight: "10px" }}
          />
        )}
      </ADSpace>
      <div
        className="preview-footer-container alignCenter dFlex w-100 flex-1"
        data-testid="file-info-id"
      >
        <Dropdown
          menu={{
            items,
            selectable: true,
            onClick,
            selectedKeys: [activeTabData?.source_id],
            style: {
              background: "#e9e9e9",
              padding: "5px",
            },
          }}
        >
          <div className="menu-icon-container items-center h-100">
            <MenuOutlined className="cursor-pointer" data-testid="menu-icon" />
          </div>
        </Dropdown>
        <div className="files-container dFlex h-100 overflowHidden">
          {loadedFiles?.slice(indexRange[0], indexRange[1]).map((file) => {
            const isActive = activeTabData?.source_id === file.source_id;
            const connection = pipelineHistory?.connections?.find(
              (conn) => conn?._id === file?._id
            );
            const displayName =
              file.type === "table" ? "Table name" : "File name";
            const infoItems = connection
              ? [
                  [displayName, file?.alias || ""],
                  ["Datasource name", connection.type || ""],
                  ["Connection name", connection.alias || ""],
                  ["Connection Id", connection._id || ""],
                ]
              : [[displayName, file?.alias || ""]];

            const tooltipTitle = (
              <div style={{ fontSize: "10px", whiteSpace: "pre-line" }}>
                {infoItems.map(([label, value]) => (
                  <div key={`${file.source_id}-${label}`}>
                    <strong>{label} :</strong> {value}
                  </div>
                ))}
              </div>
            );
            return (
              <span
                className="preview-tab cursor-pointer dFlex alignCenter f14 h-100"
                style={{
                  backgroundColor: isActive ? "#DDEBED" : "transparent",
                }}
                key={file.source_id}
                data-custom-key={file.source_id}
                data-testid={`file-${file.source_id}`}
                onClick={handleClick}
              >
                <Tooltip title={tooltipTitle}>
                  <span
                    className="text-ellipsis"
                    style={{
                      fontSize: "12px",
                      width: "90%",
                      margin: "0 10px",
                      color: isActive ? "#307378" : "",
                    }}
                  >
                    {file.alias}
                  </span>
                </Tooltip>
              </span>
            );
          })}
        </div>
        <div className="items-center flex-1 files-button">
          <Space>
            <Button
              icon={<LeftOutlined />}
              disabled={indexRange[0] <= 0}
              type="text"
              onClick={onLeftIconClick}
              style={{ width: "20px" }}
              data-testid="left-arrow-id"
            />
            <Button
              icon={<RightOutlined />}
              onClick={onRightIconClick}
              disabled={indexRange[1] >= loadedFiles?.length}
              type="text"
              style={{ width: "20px" }}
              data-testid="right-arrow-id"
            />
          </Space>
        </div>
      </div>
    </ADSpace>
  );
};

export default PreviewFooter;
