import React from "react";
import { Card, Alert,  Button } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import "./style.scss";
import { useDispatch } from "react-redux";
import {
  setQueryModeAction,
  setPrimaryKeyAction,
  addsetDmsStepsAction,
  setIncrementKeyAction,
} from "../../store/actions/dmsAction";
import TableConfigRow from "./TableConfigRow";
import useTableConfiguration from "./TableConfiguration";
import { filterPoolingSection } from "../app-header/components/job-schedule/constants";
import { QUERY_MODES } from "./utils";
import RenderMarkDown from "../database-module/components/RenderMarkDown";
import { dispatchMessage } from "../../utils/handleClick";
import { INCREMENT_KEY_ERROR, PRIMARY_INCREMENT_ERROR, PRIMARY_KEY_ERROR, SOURCE_DATASOURCE_ERROR } from "./DmsHelperMethod";

const SourceModule = ({ selectedSourceTable }) => {
  const dispatch = useDispatch();
  const {
    handleQueryModeChange,
    handlePrimaryKeyChange,
    handleIncrementKeyChange,
    getQueryMode,
    getPrimaryKey,
    getIncrementKey,
    hasEmptyPrimaryKey,
    hasEmptyIncrementKey,
    getTableConfigurations,
  } = useTableConfiguration();

  const handleContinue = () => {
    const isPrimaryKeyEmpty = hasEmptyPrimaryKey(selectedSourceTable);
    const errorMessage = !selectedSourceTable?.length
      ? SOURCE_DATASOURCE_ERROR
        : isPrimaryKeyEmpty
          ? PRIMARY_KEY_ERROR
            : "";
    if (errorMessage) {
      dispatchMessage(dispatch, "error", errorMessage);
      return;
    }
    const firstTable = selectedSourceTable?.[0]?.value;
    const firstTableMode = getQueryMode(firstTable);
    dispatch(setQueryModeAction(firstTableMode));
    firstTableMode === "merge" &&
      dispatch(setPrimaryKeyAction(getPrimaryKey(firstTable) || ""));
    ["merge", "append"].includes(firstTableMode) &&
      dispatch(setIncrementKeyAction(getIncrementKey(firstTable) || ""));
    dispatch(addsetDmsStepsAction(2));
  };

  return (
    <div className="configure-object">
      <div className="pipeline-layout">
        <Card className="form-cards">
          <Alert
            message={
              <>
                Each job queries records from a table in your Source according
                to the selected Query Mode.
              </>
            }
            type="info"
            showIcon
            icon={<InfoCircleOutlined style={{ color: "#F28E1E" }} />}
            className="alert-box"
          />

          <div className="table-list">
            {selectedSourceTable.map((obj) => (
              <TableConfigRow
                key={obj.value}
                table={obj}
                queryModeValue={getQueryMode(obj.value)}
                onQueryModeChange={handleQueryModeChange}
                primaryKeyValue={getPrimaryKey(obj.value)}
                onPrimaryKeyChange={handlePrimaryKeyChange}
                incrementKeyValue={getIncrementKey(obj.value)}
                onIncrementKeyChange={handleIncrementKeyChange}
                queryModes={QUERY_MODES}
              />
            ))}
          </div>
        </Card>

        <Card className="sidebar-card">
          <div className="sidebar-title">QUERY MODES</div>
          <ul className="sidebar-list">
            {QUERY_MODES.map((modeOption) => (
              <li key={modeOption.label}>
                <strong>{modeOption.label}</strong>
                <RenderMarkDown
                  description={filterPoolingSection(modeOption.details || "")}
                />
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <div className="footer-configure">
        <div className="footer-configure-text"></div>
        <Button type="primary" onClick={handleContinue}>
          Continue
        </Button>
      </div>
    </div>
  );
};

export default SourceModule;
