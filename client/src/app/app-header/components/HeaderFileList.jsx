import { useEffect, useMemo, useState } from "react";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import { getLoadedFiles, getRangeText } from "../utils";
import { useSearchParams } from "react-router-dom";
import { switchSelectedFile } from "../../../apis/fileService";
import {
  setIndexRanges,
  setSelectedFilesAction,
  setSplitIndex,
} from "../../../store/actions/chatAction";
import { useDispatch, useSelector } from "react-redux";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { triggerGetInfoAPI } from "../../../apis/commonAPIs";
import useWidth from "../../../utils/hooks/useWidth";
import ADFile from "../../../components/ADFile";
import ADSpace from "../../../components/ADSpace";

function HeaderFileList({ loadedFiles, selectedFiles }) {
  const dispatch = useDispatch();
  const [searchParms] = useSearchParams();
  const chatId = searchParms.get("chat");
  const width = useWidth();
  const splitIndex = useSelector((state) => state.chat.splitIndex);
  const indexRange = useSelector((state) => state.chat.indexRange);
  const [memoizedLoadedFiles, memoizedRangeText] = useMemo(() => {
    return [
      getLoadedFiles(loadedFiles, indexRange, selectedFiles),
      getRangeText(loadedFiles, indexRange),
    ];
  }, [loadedFiles, indexRange, selectedFiles]);

  useEffect(() => {
    const newSplitIndex = width <= 1200 ? 1 : 2;
    dispatch(setSplitIndex(newSplitIndex));
    dispatch(setIndexRanges([0, newSplitIndex]));
  }, [chatId, splitIndex, width, loadedFiles.length]);

  const onLeftIconClick = () => {
    if (indexRange[0] <= 0) return;
    dispatch(setIndexRanges([indexRange[0] - splitIndex, indexRange[0]]));
  };

  const onRightIconClick = () => {
    if (indexRange[1] >= loadedFiles.length) return;
    dispatch(setIndexRanges([indexRange[1], indexRange[1] + splitIndex]));
  };
  const handleClick = (file) => {
    if (
      selectedFiles.length > 0 &&
      selectedFiles[0].source_id === file.source_id
    ) {
      return; // when user clicks on selected file
    }
    switchSelectedFile({
      payload: {
        chat_id: chatId,
        source_id: file.source_id,
      },
      onSuccess: (res) => {
        if (res.success) {
          dispatch(setIndexRanges([0, splitIndex]));
          dispatch(
            setSelectedFilesAction({
              chat_id: chatId,
              files: [file],
            })
          );
          triggerGetInfoAPI(dispatch, chatId);
        }
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  return (
    <ADSpace
      alignItem="center"
      className="header-file-list-container"
      data-testid="header-container-id"
    >
      {loadedFiles?.length ? (
        <div
          className="ad-header__file-header fw600 f14 mw-fitcontent"
          data-testid="file-text-id"
        >
          {loadedFiles?.length > 1 ? "Files" : "File"}
        </div>
      ) : null}
      <ADSpace alignItem="center" space="4">
        {memoizedLoadedFiles?.length ? (
          <>
            {memoizedLoadedFiles.map((file) => {
              const isSelected = selectedFiles.some(
                (eachFile) => eachFile.source_id === file.source_id
              );
              return (
                <div
                  key={file?.source_id}
                  data-testid={`file-${file?.source_id}`}
                >
                  <ADFile
                    name={file.alias}
                    style={{
                      backgroundColor: isSelected ? "#63aaa945" : "#FBFBFB",
                      border: "1px solid #ced6d0",
                    }}
                    type={file?.type}
                    source_id={file.source_id}
                    fileId={file._id}
                    onClick={handleClick}
                  />
                </div>
              );
            })}
          </>
        ) : null}
        {loadedFiles?.length > splitIndex && (
          <ADSpace alignItem="center" space="2">
            <span
              style={{ fontSize: "12px", lineHeight: "1.8" }}
              className="memoizedRangeText"
            >
              {memoizedRangeText}
            </span>
            <LeftOutlined
              size="10px"
              style={{
                color: "#4F5057",
                cursor: indexRange[0] <= 0 ? "not-allowed" : "pointer",
              }}
              onClick={onLeftIconClick}
              data-testid="left-arrow-id"
              className={indexRange[0] <= 0 && "disabled"}
            />
            <RightOutlined
              size="10px"
              style={{
                color: "#4F5057",
                cursor:
                  indexRange[1] >= loadedFiles.length
                    ? "not-allowed"
                    : "pointer",
              }}
              className={indexRange[1] >= loadedFiles.length && "disabled"}
              onClick={onRightIconClick}
              data-testid="right-arrow-id"
            />
          </ADSpace>
        )}
      </ADSpace>
    </ADSpace>
  );
}

export default HeaderFileList;
