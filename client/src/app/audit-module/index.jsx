import { useState } from "react";
import DetailedView from "./detailedView";
import SummaryView from "./summaryView";
import "./style.scss";
import { setIsDetailedView } from "../../store/actions/auditAction";
import { useDispatch, useSelector } from "react-redux";

const AuditModule = () => {
  const dispatch = useDispatch();
  const isDetailedView = useSelector((state) => state.audit.isDetailedView);

  const handleBarClick = () => {
    dispatch(setIsDetailedView(true));
  };

  return (
    <div>
      {isDetailedView ? (
        <DetailedView />
      ) : (
        <SummaryView onBarClick={handleBarClick} />
      )}
    </div>
  );
};

export default AuditModule;
