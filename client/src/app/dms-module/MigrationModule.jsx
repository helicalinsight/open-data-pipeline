import React, { useEffect } from "react";
import { Button, Select, Typography, Tooltip } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import "./style.scss";
import {
  addsetDmsStepsAction,
  setSelectPipelineModeAction,
  setSelectedSourceTypeForDrawerAction,
  setSelectedDestinationTypeForDrawerAction,
  setPipelineModeSourceAndDestinationTypesAction,
  setSourceTypeErrorAction,
  setDestinationTypeErrorAction,
} from "../../store/actions/dmsAction";
import { useDispatch, useSelector } from "react-redux";
import { PIPELINE_MODE_OPTIONS } from "./utils";
import useDatasourceModal from "../../utils/hooks/useDatasourceModal";
import { CommonSelectWithLabel } from "./DmsHelperMethod";

const { Text } = Typography;
const { Option } = Select;
const MigrationModule = () => {
  const dispatch = useDispatch();
  const selectedPipelineMode = useSelector(
    (state) => state.dms.selectedPipelineMode,
  );
    const datasources = (
      useSelector((state) => state?.database?.datasources) || []
    ).filter((item) => item.available !== false);
    const sourceOptions = datasources.filter(
      (item) => item.is_valid_dms_source,
    );

    const destinationOptions = datasources.filter(
      (item) => item.is_valid_dms_destination,
    );
  const selectedSourceType = useSelector(
    (state) => state.dms.pipelineModeSourceType,
  );
  const selectedDestinationType = useSelector(
    (state) => state.dms.pipelineModeDestinationType,
  );
  const sourceTypeError = useSelector((state) => state.dms.sourceTypeError);
  const destinationTypeError = useSelector(
    (state) => state.dms.destinationTypeError,
  );
  useEffect(() => {
    if (!selectedPipelineMode) {
      dispatch(setSelectPipelineModeAction("table"));
    }
  }, [selectedPipelineMode, dispatch]);
  useDatasourceModal();

  const handleSelect = (value) => {
    dispatch(setSelectPipelineModeAction(value));
  };
  const handleTypeChange = (type, value) => {
    dispatch({ type: "RESET_DMS_STATE" });
    const updatedSource = type === "source" ? value : selectedSourceType;
    const updatedDestination =
      type === "destination" ? value : selectedDestinationType;
    dispatch(
      setPipelineModeSourceAndDestinationTypesAction(
        updatedSource,
        updatedDestination,
      ),
    );
    if (value) {
      dispatch(
        type === "source"
          ? setSourceTypeErrorAction("")
          : setDestinationTypeErrorAction(""),
      );
    }
  };
  const handleSourceTypeChange = (value) => {
    handleTypeChange("source", value);
  };
  const handleDestinationTypeChange = (value) => {
    handleTypeChange("destination", value);
  };
  const handleContinue = () => {
    let hasError = false;
    if (!selectedSourceType) {
      dispatch(setSourceTypeErrorAction("Please select Source Type"));
      hasError = true;
    }
    if (!selectedDestinationType) {
      dispatch(setDestinationTypeErrorAction("Please select Destination Type"));
      hasError = true;
    }
    if (hasError) return;
    dispatch(addsetDmsStepsAction(1));
    if (selectedSourceType) {
      dispatch(setSelectedSourceTypeForDrawerAction(selectedSourceType));
    }
    if (selectedDestinationType) {
      dispatch(
        setSelectedDestinationTypeForDrawerAction(selectedDestinationType),
      );
    }
  };
  return (
    <div className="pipeline-mode-module">
      <div className="content-wrapper">
        <div className="title-section">
          <div className="main-title">Migration Mode</div>
          <div className="subtitle">
            Define how your source data will be captured and ingested.
          </div>
        </div>
        {/* sourcee */}
        <CommonSelectWithLabel
          label="Source Type"
          value={selectedSourceType}
          onChange={handleSourceTypeChange}
          options={sourceOptions}
          placeholder="Select Source Type"
          error={sourceTypeError}
        />
        <CommonSelectWithLabel
          label="Destination Type"
          value={selectedDestinationType}
          onChange={handleDestinationTypeChange}
          options={destinationOptions}
          placeholder="Select Destination Type"
          error={destinationTypeError}
        />
        <div className="pm-row">
          <div className="pm-label">Pipeline Mode :</div>
          <Select
            value={selectedPipelineMode || "table"}
            onChange={handleSelect}
            size="middle"
            style={{ width: 240 }}
            optionLabelProp="label"
          >
            {PIPELINE_MODE_OPTIONS.map((mode) => {
              const labelWithIcon = (
                <div className="pm-info-icon">
                  <span>{mode.label}</span>
                  <Tooltip title={mode.description}>
                    <InfoCircleOutlined style={{ color: "#8c8c8c" }} />
                  </Tooltip>
                </div>
              );

              return (
                <Option key={mode.key} value={mode.key} label={labelWithIcon}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <span>{mode.label}</span>
                    <Tooltip title={mode.description}>
                      <InfoCircleOutlined style={{ color: "#8c8c8c" }} />
                    </Tooltip>
                  </div>
                </Option>
              );
            })}
          </Select>
        </div>

        <div className="pm-footer">
          <Button type="primary" onClick={handleContinue}>
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MigrationModule;
