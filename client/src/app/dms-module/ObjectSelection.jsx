import React, { useState } from "react";
import { Button, Row, Col } from "antd";
import "./style.scss";
import { useSelector, useDispatch } from "react-redux";
import Editor from "@monaco-editor/react";
import SourceModule from "./SourceModule";
import {
  addsetDmsStepsAction,
  setCustomSqlAction,
  setIncrementKeyAction,
  setPrimaryKeyAction,
  setQueryModeAction,
} from "../../store/actions/dmsAction";
import QueryModeSelect from "./QueryModeSelect";
import { QUERY_MODES } from "./utils";
import { ConnectDataSource, INCREMENT_KEY_ERROR, PRIMARY_INCREMENT_ERROR, PRIMARY_KEY_ERROR, SOURCE_DATASOURCE_ERROR, SQL_QUERY_ERROR } from "./DmsHelperMethod";
import useDatasourceModal from "../../utils/hooks/useDatasourceModal";
import { dispatchMessage } from "../../utils/handleClick";
const ObjectSelectionModule = () => {
  const dispatch = useDispatch();
  const customSql = useSelector((state) => state.dms.customSql);
  const queryMode = useSelector((state) => state.dms.queryMode);
  const primaryKey = useSelector((state) => state.dms.primaryKey);
  const incrementKey = useSelector((state) => state.dms.incrementKey);
  const selectedPipelineMode = useSelector(
    (state) => state.dms.selectedPipelineMode,
  );
  const sourceConnectionId = useSelector(
      (state) => state.dms.sourceConnectionId,
    );
  const selectedSourceTable = useSelector((state) => state.dms.selectedSourceTable);
  const selectedSourceTypeForDrawer = useSelector(
    (state) => state.dms.selectedSourceTypeForDrawer,
  );
  const { openDbModal, setOpenDbModal, handleConnectToDataSource } =
    useDatasourceModal(false);

  const handleQueryModeChange = (value) => {
      dispatch(setQueryModeAction(value));
    if (value !== "merge") {
      dispatch(setPrimaryKeyAction(""));
    }
     if (!["merge", "append"].includes(value)) {
       dispatch(setIncrementKeyAction(""));
     }
  };

  const handlePrimaryKeyChange = (value) => {
    dispatch(setPrimaryKeyAction(value));
  };
  const handleIncrementKeyChange = (value) => {
    dispatch(setIncrementKeyAction(value));
  };

  const handleContinue = () => {
    const isPrimaryKeyEmpty = queryMode === "merge" && !primaryKey?.trim();
    const errorMessage = !customSql?.trim()
      ? SQL_QUERY_ERROR
        : isPrimaryKeyEmpty
          ? PRIMARY_KEY_ERROR
            : !sourceConnectionId?.length
              ? SOURCE_DATASOURCE_ERROR
              : "";
    if (errorMessage) {
      dispatchMessage(dispatch, "error", errorMessage);
      return;
    }
    dispatch(addsetDmsStepsAction(2));
  };
  const renderMainContent = () => {
    return (
      <div>
          <ConnectDataSource
            openDbModal={openDbModal}
            setOpenDbModal={setOpenDbModal}
            onClick={handleConnectToDataSource}
            selectedSourceType={selectedSourceTypeForDrawer}
            selectedDestinationType={null}
          />
        {selectedPipelineMode === "custom_sql" ? (
          <>
            <div className="sql-editor-container">
              <Editor
                height="420px"
                language="sql"
                theme="vs-light"
                value={customSql}
                onChange={(value) => dispatch(setCustomSqlAction(value))}
                options={{
                  fontSize: 12,
                  minimap: { enabled: false },
                  wordWrap: "on",
                  automaticLayout: true,
                }}
              />
            </div>
          </>
        ) : (
          <>
            <SourceModule selectedSourceTable={selectedSourceTable} />
          </>
        )}
        <Row align="middle" justify="space-between">
          <Col flex="auto">
            {selectedPipelineMode === "custom_sql" && (
              <QueryModeSelect
                value={queryMode}
                onChange={handleQueryModeChange}
                primaryKeyValue={primaryKey}
                onPrimaryKeyChange={handlePrimaryKeyChange}
                incrementKeyValue={incrementKey}
                onIncrementKeyChange={handleIncrementKeyChange}
                queryModes={QUERY_MODES}
                size="middle"
                style={{ maxWidth: 400 }}
                custom={true}
              />
            )}
          </Col>
          <Col>
            <Button
              type="primary"
              onClick={handleContinue}
            >
              Continue
            </Button>
          </Col>
        </Row>
      </div>
    );
  };
  return <div className="select-objects-container">{renderMainContent()}</div>;
};

export default ObjectSelectionModule;
