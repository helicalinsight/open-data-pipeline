import { useState, useEffect } from "react";
import { triggerGetDatasources } from "../../apis/commonAPIs";
import { useDispatch } from "react-redux";

const useDatasourceModal = (shouldFetch = true) => {
  const dispatch = useDispatch();
  const [openDbModal, setOpenDbModal] = useState(false);

  useEffect(() => {
    if (shouldFetch) {
    triggerGetDatasources(dispatch);
    }
  }, [dispatch,shouldFetch]);

  const handleConnectToDataSource = () => {
    // if (shouldFetch) {
      setOpenDbModal(true);
    // }
  };

  return {
    openDbModal,
    setOpenDbModal,
    handleConnectToDataSource,
  };
};

export default useDatasourceModal;