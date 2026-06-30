import { triggerDms } from "../../../../../apis/dmsService";
import {
  dagRunStatus,
  exportConfig,
  getStreamLogs,
  triggerDag,
  updateScheduleDetails,
} from "../../../../../apis/jobScheduleService";
import { addsetDmsStepsAction, setDmsLogStatus, setDmsLogValue, setDmsRunHistory } from "../../../../../store/actions/dmsAction";
import {
  setJobDetails,
  setLogValue,
  setRunHistory,
  setRunNowStatus,
} from "../../../../../store/actions/jobScheduleActions";
import { fetchDagListUtil } from "../../../../../utils/appUtils";
import { dispatchMessage } from "../../../../../utils/handleClick";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry";
import { getLocalStorageItem } from "../../../../../utils/userData";

const handleExportAndTrigger = ({
  payload,
  dispatch,
  messageApi,
  setLoading,
  onSuccessCallback,
}) => {
  exportConfig({
    payload,
    onSuccess: onSuccessCallback,
    onError: (error) => {
      messageApi?.open?.({
        type: "error",
        content: error.msg || "Something went wrong!!",
      });
      handleSessionExpiry(dispatch, error);
      setLoading(false);
    },
  });
};

const fetchJobLogs = (
  job_id,
  run_id,
  local,
  schedule_id,
  engine_type,
  message,
  setLoading,
  dispatch,
  pollRef,
  isDms
) => {
  setLoading(true);
  const payload = {
    job_id,
    dag_run_id: run_id,
    engine_type,
  };
  if (pollRef.current) {
    clearInterval(pollRef.current);
  }
  pollRef.current = setInterval(() => {
    dagRunStatus({
      payload: {
        dag_id: "",
        dag_run_id: run_id,
      },
      onSuccess: (res) => {
        if (res.success) {
          if (isDms) {
            dispatch(setDmsLogStatus(res.state));
          } else {
            dispatch(setRunNowStatus(res.state));
          }
          if (res.state === "success" || res.state === "failed") {
            clearInterval(pollRef.current);
          }
        }
      },
      onError: (err) => {
        clearInterval(pollRef.current);
        handleSessionExpiry(dispatch, err);
      },
    });
  }, 1000);
  getStreamLogs({
    payload,
    onSuccess: (response) => {
      if (isDms) {
        dispatch(setDmsLogValue(response));
      } else {
        dispatch(setLogValue(response));
      }
      setLoading(false);
      dispatch(setJobDetails(run_id, job_id, local, schedule_id, message));
    },
    onError: (error) => {
      setLoading(false);
      handleSessionExpiry(dispatch, error);
      console.log(error, "Error loading logs in logViewer");
    },
  });
};

export const triggerSchedule = (params) => {
  const {
    jobData,
    jobDataForm,
    scheduleConfig,
    selectedChat,
    messageApi,
    dispatch,
    loadedFiles,
    frequency,
    setLoading,
    isScheduleEditMode,
    scheduleId,
    jobListDetails,
    exportFile,
    isDms,
    selectedDmsChat,
    customFormData,
    onClose,
    dmsProgressDetails,
    pollRef,
    dmsScheduleConfig,
  } = params;
  //dms schedule schedule call
  const { user } = getLocalStorageItem() || {};
  const executionMode = params.mode;
  if (isDms) {
    setLoading(true);
    const formValues = jobData || jobDataForm.getFieldsValue();
    const { schedule_name, engineType } = formValues;
    const {
      dms_migration_mode,
      source_details = {},
      destination_details = {},
    } = dmsProgressDetails || {};
    const {
  mode,
  table_name: sourceTable,
  file_name,
  query,
  primary_key,
  increment_key,
  connection_id: sourceConnectionId,
  file_id,
} = source_details;
    const {
      schema,
      table_name: destinationTable,
      connection_id: destinationConnectionId,
    } = destination_details;
    const isFlatFileSource = source_details?.type === "flat_files";
    const sourceParameters = isFlatFileSource
      ? {
          file_id,
          file_name,
        }
      : {
          connection_id: sourceConnectionId,
          table_name: sourceTable,
        };
    const payload = {
      user_id: user?.id,
      chat_id: selectedDmsChat?.chat_id,
      schedule_name: schedule_name?.trim(),
      scheduling_interval: executionMode === "skipAndRun" ? "once" : frequency,
      engine_type: engineType,
      advanced_scheduling: customFormData || {},
      notification: {},
      migration_details: {
        mode,
        source_parameters:sourceParameters,
        destination_parameters: {
          connection_id: destinationConnectionId,
          ...(schema && destinationTable
            ? { table_name: `${schema}.${destinationTable}` }
            : {}),
        },
        migration_type: dms_migration_mode,
      },
    };
      if (["merge", "append"].includes(mode)) {
        payload.migration_details.increment_key = increment_key || null;
      }
      if (mode === "merge") {
        payload.migration_details.primary_key = primary_key || "";
      }
    if (dms_migration_mode === "custom-sql") {
      payload.migration_details.query = query || "";
    }
    const formattedDmsConfig = (
      dmsScheduleConfig?.dmsScheduleConfig || []
    ).reduce((acc, item) => {
      if (item?.configKey) {
        acc[item.configKey] = item.configValue;
      }
      return acc;
    }, {});
    handleExportAndTrigger({
      payload: {
        chat_id: selectedDmsChat?.chat_id,
        configurations: formattedDmsConfig,
      },
      dispatch,
      messageApi,
      setLoading,
      onSuccessCallback: () => {
        triggerDms({
          payload,
          onSuccess: (response) => {
            setLoading(false);
            dispatchMessage(
              dispatch,
              "success",
              response.message || "chat configured successfully!",
              true,
            );
            if (executionMode !== "skipAndRun") {
              dispatch(addsetDmsStepsAction(0));
              dispatch({ type: "RESET_DMS_STATE" });
            }
        // dispatch(addsetDmsStepsAction(0));
        // dispatch({ type: "RESET_DMS_STATE" });
        if (executionMode === "skipAndRun") {
          fetchJobLogs(
            response.job_id,
            response.run_id,
            response.local,
            response.schedule_id,
            response.engine_type,
            response.message,
            setLoading,
            dispatch,
            pollRef,
            true
          );
        }
         dispatch(
           setDmsRunHistory({
             job_id: response.job_id,
             run_id: response.run_id,
             timestamp: new Date().toISOString(),
             local: response.local,
             engine_type: response?.engine_type,
           }),
         );
        onClose?.();
      },
      onError: (error) => {
        setLoading(false);
        dispatchMessage(
          dispatch,
          "error",
          error.message || "Failed to configure chat.",
        );
      },
    });
      },
    });
    return;
  }
  //
  const {
    destination,
    database,
    catalog,
    files,
    schedule_name,
    exportFile: formExportFile,
  } = frequency ? jobData : jobDataForm.getFieldsValue();
  setLoading(true);
  const { chat_id } = selectedChat;
  //File Lists
  const filesList = isScheduleEditMode
    ? jobListDetails?.job_details?.files_list?.filter(
        (file) =>
          files?.includes(file.alias) || files?.includes(file.source_id)
      )
    : loadedFiles?.filter((file) => files?.includes(file.source_id));
  //Config
  let configurations = {};

  const configSource = isScheduleEditMode
    ? jobListDetails?.job_details?.configuration
    : scheduleConfig;

  if (configSource) {
    configurations = configSource.reduce((curr, data) => {
      const value =
        isScheduleEditMode && typeof data["configValue"] === "string"
          ? (() => {
              try {
                return JSON.parse(data["configValue"]);
              } catch {
                return data["configValue"];
              }
            })()
          : data["configValue"];

      return {
        ...curr,
        [data["configKey"]]: value,
      };
    }, {});
  }
  const finalExportFile = exportFile || formExportFile;

  const payload = {
    chat_id,
    configurations,
  };

  const job_details = {
    files_list: filesList,
    type: destination,
    database,
    connection_id: database,
    catalog,
  };

  const commonArgs = {
    ...params,
    frequency,
    job_details,
    schedule_name,
    engine_type: params.engineType,
    exportFile: finalExportFile,
    execution_type: params.isEditExecutiontype,
  };

  if (isScheduleEditMode) {
    handleUpdateSchedule({
      ...commonArgs,
      scheduleId,
      setLoading,
      configurations,
    });
  } else {
    handleExportAndTrigger({
      payload,
      dispatch,
      messageApi,
      setLoading,
      onSuccessCallback: () => {
        handleTriggerDag({
          ...commonArgs,
          pollRef,
        });
      },
    });
  }
};
/// edit mode update codeee
export const handleUpdateSchedule = ({
  frequency,
  dispatch,
  customFormData,
  onClose,
  setLoading,
  job_details,
  schedule_name,
  mappedData,
  notification,
  jobData,
  configurations,
  jobListDetails,
  isScheduleEditMode,
}) => {
  const { user } = getLocalStorageItem() || {};
  const payload = {
    schedule_id: jobListDetails.schedule_id,
    configurations,
    schedule_interval: frequency,
    job_details,
    schedule_name,
    engine_type: jobData.engineType,
    replace_connections: mappedData,
    notification: {
      active: frequency ? jobData.notification : notification,
      type: "email",
      details: {
        to: null,
        subject: null,
        body: null,
      },
    },
    advanced_scheduling: customFormData,
  };
  if (isScheduleEditMode && jobListDetails?.meta_schedule_version === 1) {
    payload.execution_type = jobData.isEditExecutiontype;
    payload.upgrade_schedule_version = 2;
  }
  updateScheduleDetails({
    payload,
    onSuccess: (res) => {
      setLoading(false);
      onClose?.();
      dispatchMessage(dispatch, "success", res.msg);
      fetchDagListUtil({
        dispatch,
        setLoading,
        user,
        current: 1,
        pageSize: 10,
      });
    },
    onError: (error) => {
      dispatchMessage(
        dispatch,
        "error",
        error.message || "Failed to update the Schedule",
      );
      handleSessionExpiry(dispatch, error);
      setLoading(false);
    },
  });
};

// function to trigger dag
export const handleTriggerDag = ({
  frequency,
  messageApi,
  selectedChat,
  dispatch,
  mode,
  customFormData,
  onClose,
  setLoading,
  job_details,
  engine_type,
  schedule_name,
  executionType,
  mappedData,
  notification,
  jobData,
  isImmediateExecution,
  exportFile,
  pollRef,
}) => {
  const { chat_id, chat_name } = selectedChat;
  const { user } = getLocalStorageItem() || {};
  const payload = {
    job_id: chat_id,
    job_name: chat_name,
    user_id: user?.id,
    schedule_interval: mode === "skipAndRun" ? "once" : frequency,
    job_details,
    engine_type: mode === "skipAndRun" ? engine_type : jobData.engineType,
    schedule_name,
    export_format: exportFile || jobData?.exportFile,
    executionType: executionType?.toLowerCase(),
    replace_connections: mappedData,
    notification: {
      active: frequency ? jobData.notification : notification,
      type: "email",
      details: {
        to: null,
        subject: null,
        body: null,
      },
    },
    advance_scheduling: customFormData,
  };

  triggerDag({
    payload,
    onSuccess: (res) => {
      setLoading(false);
      onClose?.();
      dispatchMessage(dispatch, "success", res.message);
      if (isImmediateExecution) {
        fetchJobLogs(
          res.job_id,
          res.run_id,
          res.local,
          res.schedule_id,
          res?.engine_type,
          res.message,
          setLoading,
          dispatch,
          pollRef,
          false
        );
      }
      dispatch(
        setRunHistory({
          job_id: res.job_id,
          run_id: res.run_id,
          timestamp: new Date().toISOString(),
          local: res.local,
          engine_type: res?.engine_type,
          schedule_id:res?.schedule_id
        }),
      );
    },
    onError: (error) => {
      messageApi.open({
        type: "error",
        content: error.message || "Failed to schedule the Job",
      });
      handleSessionExpiry(dispatch, error);
      setLoading(false);
    },
  });
};
