import {
  baseApi,
  completionAPIURL,
  authApiConstants,
  userApiConstants,
  featureConstants,
  chatServiceConstants,
  filesServiceConstants,
  previewFileConstants,
  databaseServiceConstants,
  jobScheduleServiceConstants,
  preferencesConstants,
  auditConstants,
  fileConstants,
  dmsConstants,
} from "../../apis/apiUrlConstants";

describe("API Constants", () => {
  const url = window.location.origin;
  const baseUrl = `${url}/api/v1/`;

  it("baseApi should have correct URL", () => {
    expect(baseApi.url).toBe(baseUrl);
  });

  it("completionAPIURL should be defined", () => {
    expect(completionAPIURL).toBe("completion");
  });

  it("authApiConstants should have correct values", () => {
    expect(authApiConstants).toEqual({
      login: "googleauth/login",
      logout: "",
      register: "users/register",
    });
  });

  it("userApiConstants should have correct values", () => {
    expect(userApiConstants).toEqual({
      register: "users/register",
    });
  });

  it("featureConstants should have correct values", () => {
    expect(featureConstants).toEqual({
      getApplication: "get_application",
    });
  });

  it("chatServiceConstants should have correct values", () => {
    expect(chatServiceConstants).toEqual({
      chat: "chat",
      sendMessage: "parse",
      chatHistory: "chat_history",
      pipelineHistory: "pipeline_history",
      undoPipelineHistory: "undo",
      redoPipelineHistory: "redo",
      getInformation: "get_information",
      jobMode: "update_mode",
    });
  });

  it("filesServiceConstants should have correct values", () => {
    expect(filesServiceConstants).toEqual({
      getAllFiles: "files",
      uploadFile: "upload_file",
      download: "download",
      uploadConfig: "upload_config",
      deleteFile: "remove_file",
    });
  });

  it("previewFileConstants should have correct values", () => {
    expect(previewFileConstants).toEqual({
      previewFile: "execute",
    });
  });

  it("databaseServiceConstants should have correct values", () => {
    expect(databaseServiceConstants).toEqual({
      datasources: "datasources",
      dataConnectors: "Data_connectors",
      connections: "connections",
      savedConnections: "Saved_connections",
      listCatalogs: "List_catalogs",
      dataLoads: "data_loads",
      fetchColumns: "get_columns",
    });
  });

  it("jobScheduleServiceConstants should have correct values", () => {
    expect(jobScheduleServiceConstants).toEqual({
      dag: "dag",
      listDags: "list/runs",
      individualDag: "dag/info/",
      dagLogs: "airflow/log",
      delete: "airflow/delete",
      runDag: "trigger_dag",
      streamLogs: "/api/v1/airflow/stream_log",
      downloadDagInfo: "download_file",
      exportConfig: "export_config",
      codeConfig: "get_data",
      runCode: "run_pipeline",
      pyspark: "pyspark/generate",
      pysparkReset: "pyspark/reset",
      updateSchedule: "schedule",
      listTags: "dag_search_filters",
      dagRunStatus: "get_dag_run_status",
    });
  });

  it("preferencesConstants should have correct values", () => {
    expect(preferencesConstants).toEqual({
      preferences: "user_preferences",
      generateKey: "generate_api_key",
    });
  });

  it("auditConstants should have correct values", () => {
    expect(auditConstants).toEqual({
      auditBilling: "/audit/billing/summary",
    });
  });

  it("fileConstants should have correct values", () => {
    expect(fileConstants).toEqual({
      rename: "rename_file_cache",
      cwf: "/cwf",
    });
  });
});
describe("dmsConstants", () => {
  it("should have correct values", () => {
    expect(dmsConstants).toEqual({
      dmsList: "dms",
      dmsSchedule: "dms",
      deleteDmsSchedule: "dms",
      dmsPostProgress: "dms/progress",
      dmsGetProgress: "dms/progress",
    });
  });

  it("should have the correct keys", () => {
    const expectedKeys = ["dmsList", "dmsSchedule","deleteDmsSchedule","dmsPostProgress",
  "dmsGetProgress",];
    const actualKeys = Object.keys(dmsConstants);
    expect(actualKeys).toEqual(expectedKeys);
  });

  it("should have string values for all properties", () => {
    Object.values(dmsConstants).forEach((value) => {
      expect(typeof value).toBe("string");
    });
  });

  it("dmsList should be 'dms'", () => {
    expect(dmsConstants.dmsList).toBe("dms");
  });

  it("dmsSchedule should be 'dms'", () => {
    expect(dmsConstants.dmsSchedule).toBe("dms");
  });

  it("deleteDmsSchedule should be 'dms'", () => {
    expect(dmsConstants.deleteDmsSchedule).toBe("dms");
  });

  it("should have exactly 5 properties", () => {
    expect(Object.keys(dmsConstants).length).toBe(5);
  });
});
