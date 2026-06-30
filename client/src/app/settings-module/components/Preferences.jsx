import React, { useEffect, useState } from "react";
import { Button, Divider, Input, Radio, Skeleton, message, Space } from "antd";
import { ADSpace } from "../../../components";
import { getPreferences, postPreferences } from "../../../apis/settingsService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { useDispatch, useSelector } from "react-redux";
import { setPreferencesAction } from "../../../store/actions/settingActions";
import { InfoCircleOutlined } from "@ant-design/icons";
import { preferenceText } from "../../app-header/components/job-schedule/constants";
import { dispatchMessage } from "../../../utils/handleClick";
const Preferences = ({ activeTab }) => {
  const dispatch = useDispatch();
  const allPreferences = useSelector(
    (store) => store?.settings?.allPreferences
  );
  const [preferences, setPreferences] = useState(
    allPreferences?.files?.num_records === -1 ? "full" : "custom"
  );
  const [records, setRecords] = useState("");
  const [fileSize, setFileSize] = useState("");
  const userConfig = useSelector((state) => state.app.userConfig);
  const [recordError, setRecordError] = useState(null);
  const [fileSizeError, setFileSizeError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showInfoText, setShowInfoText] = useState(false);
  useEffect(() => {
    // if active tab is preferences then only call preferences api
    if (activeTab === "2") {
      fetchPreferences();
    }
  }, [activeTab]);

  useEffect(() => {
    const numRecords = allPreferences?.files?.num_records;
    setRecords(
      numRecords === -1 || numRecords == null ? "" : String(numRecords),
    );
    const size = allPreferences?.files?.file_size;
    setFileSize(size == null ? "" : String(size));
  }, [allPreferences]);

  // function to fetch all the preferences
  const fetchPreferences = () => {
    setLoading(true);
    getPreferences({
      onSuccess: (response) => {
        dispatch(setPreferencesAction(response));
        setLoading(false);
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        setLoading(false);
      },
    });
  };

  // function to save preferences
  const handleSavePreferences = () => {
    const parsedFileSize = parseFloat(fileSize);
    const parsedRecords = parseInt(records);

    const recordsError =
      preferences !== "full"
        ? isNaN(parsedRecords) || parsedRecords <= 0
          ? "Number of records must be greater than 0."
          : null
        : null;
    const fileSizeError =
      isNaN(parsedFileSize) ||
      (parsedFileSize <= 0 && "File size must be greater than 0.");
    setRecordError(recordsError);
    setFileSizeError(fileSizeError);
    if (recordsError || fileSizeError) return;

    const payload = {
      files: {
        file_size: parsedFileSize,
        num_records: preferences === "full" ? -1 : parsedRecords,
      },
    };

    postPreferences({
      payload,
      onSuccess: (response) => {
        dispatch(setPreferencesAction(response));
        dispatchMessage(dispatch, "success", "Preferences Saved Successfully");
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        dispatchMessage(dispatch, "error", error?.msg);
      },
    });
  };

  const disaleEditing = userConfig?.role === "free" ? true : false;
  return (
    <div className="settings-section__preferences">
      <ADSpace
        justifyContent="start"
        className="settings-section__preferences-details"
      >
        <div className="fx-1">
          <LeftSection
            title="Data Preferences"
            description="Choose the number of records to show"
          />
        </div>
        <div className="fx-1 radio-btn">
          <Radio.Group
            onChange={(e) => {
              setPreferences(e.target.value);
              setShowInfoText(true);
            }}
            value={preferences}
          >
            <ADSpace stack="vertical" space="7">
              <Radio value="full" data-testid="radio-full">
                Full
              </Radio>
              <Radio value="custom" data-testid="radio-custom">
                Custom
              </Radio>
            </ADSpace>
          </Radio.Group>
          {preferences === "custom" && (
            <div className="settings-section__preferences-custom-input">
              {loading ? (
                <Skeleton.Button active={true} block={true} />
              ) : (
                <>
                  <Input
                    type="number"
                    min="1"
                    value={records}
                    placeholder="Number of records"
                    onChange={(event) => {
                      setRecords(event.target.value);
                      setShowInfoText(true);
                      setRecordError(null);
                    }}
                    status={recordError ? "error" : ""}
                    data-testid="input-custom-id"
                    disabled={disaleEditing}
                  />
                  {recordError && (
                    <div style={{ color: "red" }}>{recordError}</div>
                  )}
                </>
              )}
            </div>
          )}
          {showInfoText && (
            <Space className="info-text">
              <InfoCircleOutlined />
              {preferenceText}
            </Space>
          )}
        </div>
      </ADSpace>
      <Divider style={{ margin: "17px 0px" }} />
      <ADSpace
        justifyContent="start"
        className="settings-section__preferences-details"
      >
        <div className="fx-1">
          <LeftSection title="File Size" description="Enter the file size" />
        </div>

        <div className="fx-1">
          <div className="settings-section__preferences-custom-input file-input">
            {loading ? (
              <Skeleton.Button active={true} block={false} />
            ) : (
              <div style={{ display: "flex", flexDirection: "column" }}>
                <Input
                  type="number"
                  min="1"
                  value={fileSize}
                  onChange={(event) => {
                    setFileSize(event.target.value);
                    setFileSizeError(null);
                  }}
                  status={fileSizeError ? "error" : ""}
                  disabled={disaleEditing}
                  data-testid="file-input-id"
                  addonAfter={<span style={{ fontSize: "10px" }}>MB</span>}
                />
                {fileSizeError && (
                  <div style={{ color: "red" }}>{fileSizeError}</div>
                )}
              </div>
            )}
          </div>
        </div>
      </ADSpace>
      <Divider style={{ margin: "17px 0px" }} />
      <Button
        type="primary"
        onClick={handleSavePreferences}
        data-testid="save-button-id"
      >
        Save Preferences
      </Button>
    </div>
  );
};

const LeftSection = ({ title, description }) => (
  <>
    <p className="f14 fw600">{title}</p>
    <span className="settings-section__preferences-subhead">{description}</span>
  </>
);
export default Preferences;
