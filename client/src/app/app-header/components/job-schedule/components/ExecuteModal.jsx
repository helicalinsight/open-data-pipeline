import { useState } from "react";
import { runCode } from "../../../../../apis/jobScheduleService";
import { ADModal } from "../../../../../components/ADModal";
import { useDispatch, useSelector } from "react-redux";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry";
import { setIsYamlSaved } from "../../../../../store/actions/chatAction";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../../../apis/commonAPIs";

const ExecuteModal = ({ open, setOpen }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const selectedChat = useSelector((state) => state.chat?.selectedChat);

  const handleExecute = () => {
    setLoading(true);
    runCode({
      payload: {
        mode: "yaml",
        dry_run: false,
        chat_id: selectedChat?.chat_id,
      },
      onSuccess: (res) => {
        if (res.success) {
          setLoading(false);
          setOpen(false);
          dispatch(
            setIsYamlSaved({ chat_id: selectedChat?.chat_id, saved: false })
          );
          triggerGetInfoAPI(dispatch, selectedChat?.chat_id);
          triggerPipelineHistory(dispatch, selectedChat?.chat_id);
        } else {
          setLoading(false);
        }
      },
      onError: (err) => {
        setLoading(false);
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  return (
    <ADModal
      open={open}
      title="Execute Pipeline"
      showIcon={false}
      description="Please re-execute pipeline as you made changes in yaml"
      hideButtons={false}
      okText="Execute"
      onOk={handleExecute}
      loading={loading}
      onCancel={() => setOpen(false)}
      showCancelButton={true}
      cancelText="cancel"
    />
  );
};

export default ExecuteModal;
