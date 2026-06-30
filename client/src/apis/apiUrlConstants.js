const url = window.location.origin;

export const baseApi = {
  url: url + "/api/v1/",
};

export const completionAPIURL = "completion";

export const authApiConstants = {
  login: "googleauth/login",
  logout: "",
  register: "users/register",
};

export const userApiConstants = {
  register: "users/register",
};

export const featureConstants = {
  getApplication: "get_application",
};

export const chatServiceConstants = {
  chat: "chat",
  sendMessage: "parse",
  chatHistory: "chat_history",
  pipelineHistory: "pipeline_history",
  undoPipelineHistory: "undo",
  redoPipelineHistory: "redo",
  getInformation: "get_information",
  jobMode: "update_mode",
};

export const filesServiceConstants = {
  getAllFiles: "files",
  uploadFile: "upload_file",
  download: "download",
  uploadConfig: "upload_config",
  deleteFile: "remove_file",
};

export const previewFileConstants = {
  previewFile: "execute",
};

export const databaseServiceConstants = {
  datasources: "datasources",
  dataConnectors: "Data_connectors",
  connections: "connections",
  savedConnections: "Saved_connections",
  listCatalogs: "List_catalogs",
  dataLoads: "data_loads",
  fetchColumns: "get_columns",
};

export const jobScheduleServiceConstants = {
  dag: "dag",
  listDags: "list/runs",
  individualDag: "dag/info/",
  dagLogs: "airflow/log",
  delete: "airflow/delete",
  runDag: "trigger_dag",
  // we are using the fetch API for streamLogs,baseApi is only appended when using Axios.
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
};

export const preferencesConstants = {
  preferences: "user_preferences",
  generateKey: "generate_api_key",
};

export const auditConstants = {
  auditBilling: "/audit/billing/summary",
};

export const fileConstants = {
  rename: "rename_file_cache",
  cwf: "/cwf",
};

export const dmsConstants ={
  dmsList: "dms",
  dmsSchedule:"dms",
  deleteDmsSchedule:"dms",
  dmsPostProgress:"dms/progress",
  dmsGetProgress:"dms/progress"
}
