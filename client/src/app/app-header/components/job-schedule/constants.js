import mtz from "moment-timezone";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
// import warning from "antd/es/_util/warning";
dayjs.extend(utc);
dayjs.extend(timezone);

export const dateFormat = "DD/MM/YYYY hh:mm A";

export const userTimezone = dayjs.tz.guess();

export const initialStartsOn = () => dayjs().tz(userTimezone).add(15, "minute");
export const initialEndsOn = () => dayjs().tz(userTimezone).add(30, "minute");

export const initialValues = {
  repeats: "weekly",
  repeatOn: [],
  repeatsEvery: 1,
  timezone: userTimezone,
  startsOn: initialStartsOn(),
  endsAfter: 35,
  endsOn: initialEndsOn(),
};

export const timezones = mtz.tz.names();

export const timezoneOptions = timezones.map((eachZone) => {
  return {
    label: eachZone,
    value: eachZone,
  };
});

export const repeatOptions = [
  // { label: "Minutes", value: "minutes", text: "minute", max: 59 },
  { label: "Hourly", value: "hourly", text: "hour", max: 24 },
  { label: "Daily", value: "daily", text: "day", max: 31 },
  { label: "Weekly", value: "weekly", text: "week", max: 4 },
  { label: "Monthly", value: "monthly", text: "month", max: 12 },
  { label: "Yearly", value: "yearly", text: "year", max: 31 },
];

export const repeatSummary = {
  hourly:
    "If you schedule the DAG to run every hour, say at 2:00 PM, the run will collect data for the previous hour (from 1:00 PM to 2:00 PM). When does it run? At 3:00 PM, after the data interval from 2:00 PM to 3:00 PM has ended.",
  daily:
    "If the DAG is scheduled to run daily at midnight (12:00 AM), it will collect data from the previous day (from 12:00 AM to 11:59 PM of the previous day).When does it run? At 12:00 AM of the next day, after the current day has ended.",
  weekly:
    "If the DAG is scheduled to run weekly, say at midnight on Sunday, it will collect data from the previous week (Sunday 12:00 AM to Saturday 11:59 PM). When does it run? At midnight on the next Sunday, after the full week has ended.",
  monthly:
    "If the DAG is scheduled to run monthly on the first day of the month at 12:00 AM, it will collect data from the previous month. When does it run? On the first day of the next month at 12:00 AM, after the entire month has ended.",
  yearly:
    "If the DAG is scheduled to run yearly, say on January 1 at 12:00 AM, it will collect data for the entire previous year. When does it run? At 12:00 AM on January 1 of the next year, after the year has ended.",
};

export const days = [
  { value: "Sunday", title: "S", id: 1 },
  { value: "Monday", title: "M", id: 2 },
  { value: "Tuesday", title: "T", id: 3 },
  { value: "Wednesday", title: "W", id: 4 },
  { value: "Thursday", title: "T", id: 5 },
  { value: "Friday", title: "F", id: 6 },
  { value: "Saturday", title: "S", id: 7 },
];

export const repeateByMonthOptions = [
  { value: "dayOfTheMonth", title: "day of the month" },
  { value: "dayOfTheWeek", title: "day of the week" },
];

export const radioOptions = [
  { value: "never", title: "Never" },
  // The "max_active_runs" flag only limits active runs, not total runs. No direct support for total run limits per ticket #1068. Hiding this option in the frontend
  // { value: "after", title: "After" },
  { value: "on", title: "On" },
];
export const engineType = [
  { value: "spark", label: "Spark" },
  { value: "dlt", label: "Dlt" },
];
export const executionTypeOpt = [
  { value: "pipeline", label: "Pipeline" },
  { value: "code", label: "Code" },
];
export const destinationOptions = [
  {
    label: "Database",
    value: "database",
  },
  {
    label: "Local Storage",
    value: "localstorage",
  },
];
export const chooseExportType = [
  { value: "xlsx", label: "excel" },
  { value: "csv", label: "csv" },
  { value: "json", label: "json" },
];
export const initialFormValue = {
  destination: "",
  database: "",
  connection: "",
};

export const weeksText = {
  1: "first",
  2: "second",
  3: "third",
  4: "fourth",
};

export const editorOptions = [
  { label: "Python", value: "python" },
  { label: "Yaml", value: "yaml" },
];

export const scheduleFilters = [
  {
    text: "Once",
    value: "@once",
  },
  {
    text: "Hourly",
    value: "@hourly",
  },
  {
    text: "Daily",
    value: "@daily",
  },
  {
    text: "Weekly",
    value: "@weekly",
  },
  {
    text: "Monthly",
    value: "@monthly",
  },
  {
    text: "Yearly",
    value: "@yearly",
  },
];

export const dagStateFilters = [
  {
    text: "Failed",
    value: "failed",
  },
  {
    text: "Success",
    value: "success",
  },
  {
    text: "Running",
    value: "running",
  },
  {
    text: "Queued",
    value: "queued",
  },
];

export const TOOLTIPS_INFO = {
  editorInfoMessage: "Updating the job will also affect the scheduled job.",
  oldScheduleJobMessage: "Old schedule job can't be editable",
  notification:
    "Enable this option to receive job scheduling notifications via email.",
  scheduleName: "Enter a name to identify this schedule.",
  filesToExport: "Select the pipeline stage you wish to export.",
  destination: "Select your target data source.",
  database:
    "Select the connection. If none is available, you can add a new connection.",
  catalog: "Select the target table.",
  runNow: "Execute the task immediately.",
  backButton: "Go back to previous stage",
  nextButton: "Go to next stage",
  updateConnections:
    "Update the connections. You can map the existing connection with the new one. The updated connections will be used at the time of execution.",
  pipeline:
    "Select the type of pipeline you wish to execute. If 'Code' is selected, only the code will be executed.",
  datasourceUsage: "To check which data sources are connected to this job.",
  engineTypeInfo: (
    <>
      <div>Spark - Runs the code on Spark server engine.</div>
      <div>Dlt - Runs the code using Data Load Tool (DLT) engine.</div>
    </>
  ),
  runNowLogsInfo:
    "Shows only the 10 most recent log records. These are not persisted.",
  exportFileInfo: "Select File type",
  executionTypeInfo: "Select your execution type.",
};

export const ACEHelpInfo = `
# Assistant Guide

Our ACE assistant helps you generate and refine code through a conversational interface. Follow the steps below to make the most of its features:

## Conversational Code Generation

You can interact with the assistant by asking it to generate or modify code. For example, request "Write a script to read an enrollments file," and the assistant will provide the corresponding code. Continue the conversation to enhance or adjust the code. For instance, you can say "Add another step to drop the age column," and the assistant will update the code accordingly, remembering previous instructions.

## Reset Conversation

If you wish to start a new session and clear previous instructions, use the **Reset** button. This will remove all prior memory, allowing you to initiate a new request without considering earlier interactions.

This intuitive approach enables seamless collaboration between you and the assistant, making code development more efficient.
`;
export const summaryTypeOptions = [
  { label: "Daily", value: "daily", text: "day" },
  { label: "Weekly", value: "weekly", text: "week" },
  { label: "Monthly", value: "monthly", text: "month" },
  { label: "Yearly", value: "yearly", text: "year" },
];

export const notificationText = {
  warningMessage:
    "The connection cannot be saved. Use aod_schema and aod_table to filter schemas and tables for better performance.",
};
export const preferenceText =
  "You have changed the data preference. This will not affect the data already loaded. To fetch the latest data, please reload.";
export const downloadFileErrorMessage =
  "Please wait for the job to finish. Data file is available only for successfully completed jobs";
export const runnowLogsMessage = "Run Now Logs ";

export const getSchemaTooltip = "Setup Guide";
export const scheduleRunId =
  "This is the unique ID generated each time a schedule is run.";

export const summaryTypeTooltips = {
  daily:
    "By default, the chart shows today’s data. When you select previous date, it displays data only for that specific day.",
  weekly:
    "By default, the chart shows data for the current week. Selecting any previous date displays data for the full week that includes the selected date (e.g., Nov 2–8).",
  monthly:
    "By default, the chart shows data for the current month. Selecting any previous date displays data for the entire month that includes the selected date (e.g., Nov 1–30).",
  yearly:
    "By default, the chart shows data for the current year. Selecting any previous date displays data for the full year that includes the selected date (e.g., Jan 1–Dec 31, 2025).",
};

export const DEFAULT_QUERY_MODE = "replace";
export const elipsisText = (text, limit = 20) =>
  text?.length > limit ? `${text.slice(0, limit)}...` : text;

export const filterPoolingSection = (description) => {
  if (!description) return "";
  const sections = description.split("\n## ");
  if (!sections || !Array.isArray(sections)) return "";
  const filteredSections = sections.filter(
    (section) => !section.toLowerCase().startsWith("pooling options")
  );
  return filteredSections.join("\n## ");
};
