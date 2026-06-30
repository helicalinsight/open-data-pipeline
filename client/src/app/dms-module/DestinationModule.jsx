import React, { useState } from "react";
import { Button, Input, Card } from "antd";
import "./style.scss";
import { useSelector, useDispatch } from "react-redux";
import {
  addsetDmsStepsAction,
  setTargetSchemaNameAction,
  setTargetTableNameAction,
} from "../../store/actions/dmsAction";
import useDatasourceModal from "../../utils/hooks/useDatasourceModal";
import { ConnectDataSource, DESTINATION_DATASOURCE_ERROR, validateTableName } from "./DmsHelperMethod";
import { dispatchMessage } from "../../utils/handleClick";
import { getLocalStorageItem } from "../../utils/userData";
import { saveProgressDms } from "../../apis/dmsService";
import { setJobModal } from "../../store/actions/jobScheduleActions";

const DestinationModule = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const targetTableName = useSelector((state) => state.dms.targetTableName);
  const targetSchemaName = useSelector((state) => state.dms.targetSchemaName);
  const selectedPipelineMode = useSelector(
    (state) => state.dms.selectedPipelineMode,
  );
  const selectedSourceTable = useSelector(
    (state) => state.dms.selectedSourceTable,
  );
  const selectedDestinationTable = useSelector(
    (state) => state.dms.selectedDestinationTable,
  );
  const queryMode = useSelector((state) => state.dms.queryMode);
  const primaryKey = useSelector((state) => state.dms.primaryKey);
  const incrementKey = useSelector((state) => state.dms.incrementKey);
  const customSql = useSelector((state) => state.dms.customSql);
  const selectedDestinationTypeForDrawer = useSelector(
    (state) => state.dms.selectedDestinationTypeForDrawer,
  );
  const selectedDmsChat = useSelector((state) => state.dms.selectedDmsChat);
  const sourceConnectionId = useSelector(
    (state) => state.dms.sourceConnectionId,
  );
  const destinationConnectionId = useSelector(
    (state) => state.dms.destinationConnectionId,
  );
  const selectedSourceType = useSelector(
    (state) => state.dms.pipelineModeSourceType,
  );
  console.log(selectedSourceType,"ggg")
  const selectedDestinationType = useSelector(
    (state) => state.dms.pipelineModeDestinationType,
  );
  const { user } = getLocalStorageItem() || {};
  const [tableError, setTableError] = useState("");
  const { openDbModal, setOpenDbModal, handleConnectToDataSource } =
    useDatasourceModal(false);
  const tableName = selectedSourceTable?.[0]?.value || "";
  const handleDmsSave = () => {
    const error = validateTableName(targetTableName);
    if (!destinationConnectionId || error) {
      const message = !destinationConnectionId
        ? DESTINATION_DATASOURCE_ERROR
        : error;
      if (error) setTableError(error);
      dispatchMessage(dispatch, "error", message);
      return;
    }
    setLoading(true);
    setTableError("");
    const isFlatFile = selectedSourceType === "flat_files";
    const sourceDetails = {
      type: selectedSourceType,
      ...(isFlatFile
        ? {
            file_id: sourceConnectionId,
            ...(selectedPipelineMode !== "custom_sql" && {
              file_name: tableName || "",
            }),
          }
        : {
            connection_id: sourceConnectionId,
            ...(selectedPipelineMode !== "custom_sql" && {
              table_name: tableName || "",
            }),
          }),
      mode: queryMode,
      ...(selectedPipelineMode === "custom_sql" && {
        query: customSql || "",
      }),
      ...(queryMode === "merge" && {
        primary_key: primaryKey || "",
      }),
      ...(["merge", "append"].includes(queryMode) &&
        incrementKey && {
          increment_key: incrementKey,
        }),
    };
    const payload = {
      user_id: user.id,
      chat_id: selectedDmsChat?.chat_id,
      source_details:sourceDetails,
      
      destination_details: {
        type: selectedDestinationType,
        connection_id: destinationConnectionId,
        schema: targetSchemaName,
        table_name: targetTableName,
      },
      dms_migration_mode:
        selectedPipelineMode === "custom_sql" ? "custom-sql" : "table-to-table",
    };
    saveProgressDms({
      payload,
      onSuccess: (response) => {
        setLoading(false);
        dispatchMessage(
          dispatch,
          "success",
          response.msg || "chat successfully updated",
          true,
        );
        // dispatch(addsetDmsStepsAction(0));
        // dispatch({ type: "RESET_DMS_STATE" });
        dispatch(setJobModal(true));
      },
      onError: (error) => {
        setLoading(false);
        dispatchMessage(
          dispatch,
          "error",
          error.error || "Failed to update chat. Please try again.",
        );
      },
    });
  };

  const handleTargetTableNameChange = (e) => {
    const value = e.target.value;
    dispatch(setTargetTableNameAction(value));
    if (tableError) {
      const error = validateTableName(value);
      if (!error) {
        setTableError("");
      }
    }
  };
  const handleTargetSchemaNameChange = (e) => {
    dispatch(setTargetSchemaNameAction(e.target.value));
  };
  return (
    <div>
      <ConnectDataSource
        openDbModal={openDbModal}
        setOpenDbModal={setOpenDbModal}
        onClick={handleConnectToDataSource}
        selectedSourceType={null}
        selectedDestinationType={selectedDestinationTypeForDrawer}
      />
      <div style={{ marginTop: "10px" }}></div>
      <Card className="objects-card">
        <div style={{ marginBottom: "20px", padding: "0 10px" }}>
          <div style={{ marginBottom: "16px" }}>
            <div
              style={{
                display: "block",
                marginBottom: "8px",
                fontSize: "12px",
              }}
            >
              Target schema name
            </div>
            <Input
              placeholder="Enter target schema name "
              value={targetSchemaName}
              onChange={handleTargetSchemaNameChange}
              style={{ width: "40%" }}
              size="middle"
            />
          </div>
          <div>
            <div
              style={{
                display: "block",
                marginBottom: "8px",
                fontSize: "12px",
              }}
            >
              Target table name
            </div>
            <Input
              placeholder="Enter target table name"
              value={targetTableName}
              onChange={handleTargetTableNameChange}
              style={{ width: "40%" }}
              size="middle"
              status={tableError ? "error" : ""}
            />
            {tableError && (
              <div
                style={{
                  color: "#ff4d4f",
                  marginTop: "4px",
                  fontSize: "10px",
                }}
              >
                {tableError}
              </div>
            )}
            {targetTableName && targetSchemaName && (
              <div
                type="secondary"
                style={{
                  display: "block",
                  marginTop: "8px",
                  fontSize: "10px",
                }}
              >
                The pipeline run will create{" "}
                <strong>
                 {targetSchemaName}.dms_{targetTableName}
                </strong>{" "}
                table in the destination
              </div>
            )}
          </div>
        </div>

        <div className="footer">
          <Button
            style={{ float: "right" }}
            type="primary"
            onClick={handleDmsSave}
            loading={loading}
          >
            Save
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default DestinationModule;
