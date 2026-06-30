export const getLoadedFiles = (loadedFiles, indexRange, selectedFiles = []) => {
  if (!loadedFiles || loadedFiles?.length === 0) return [];
  const selectedFileId = selectedFiles[0]?.source_id;
  let files = [...loadedFiles];
  const selectedIndex = files.findIndex(
    (file) => file.source_id === selectedFileId
  );
  if (selectedIndex > -1) {
    const [selectedFile] = files.splice(selectedIndex, 1);
    files.unshift(selectedFile);
  }
  const [startIndex, endIndex] = indexRange;
  return files.slice(startIndex, endIndex);
};

export const getRangeText = (loadedFiles = [], [startIndex, endIndex]) => {
  let size = loadedFiles.length;
  if (size === 0) return null;
  endIndex = endIndex > size ? size : endIndex;

  if (startIndex + 1 === endIndex) {
    return `${startIndex + 1} of ${loadedFiles.length}`;
  }
  return `${startIndex + 1}-${endIndex} of ${loadedFiles.length}`;
};

export const capitalize = (string) => {
  if (!isString(string)) {
    return string;
  }
  return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
};

export const isString = (value) => {
  return typeof value === "string";
};

export const disableNodesBasedOnAlias = (catalogList) => {
  const processNodes = (nodes) => {
    return nodes?.map((node) => {
      const children = node?.children
        ? processNodes(node?.children)
        : undefined;
      const isNonClickable = node?.children && node?.children?.length > 0;

      return {
        ...node,
        selectable: !isNonClickable,
        children,
      };
    });
  };

  return processNodes(catalogList);
};
export const validateConfigKey = (_, value) => {
  if (typeof value !== "string") {
    return Promise.reject(new Error("The key must be a valid string."));
  }

  const trimmed = value?.trim();

  if (!trimmed) {
    return Promise.reject(new Error("Key cannot be empty."));
  }

  if (value !== trimmed) {
    return Promise.reject(new Error("Key cannot contain extraspaces."));
  }
  return Promise.resolve();
};
export const validateConfigValue = (_, value) => {
  if (value == null || value === "") {
    return Promise.reject(new Error("Value cannot be empty"));
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed === "") {
      return Promise.reject(new Error("Value cannot be just whitespace"));
    }
    if (value !== trimmed) {
      return Promise.reject(new Error("Value cannot contain extraspaces"));
    }
  }
  if (typeof value === "object") {
    for (const key in value) {
      if (key.trim() !== key) {
        return Promise.reject(
          new Error(`Key "${key}" cannot have spaces at start/end`)
        );
      }
    }
  }
  return Promise.resolve();
};
export const formatKeyValue = (value) => {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") {
    return value.replace(/\s+/g, " ").trim();
  }
  return value;
};

export const toApiCase = (str) => str?.toLowerCase() || "";
export const toDisplayCase = (str) => str;
export const compareCaseInsensitive = (a, b) =>
  String(a).toLowerCase() === String(b).toLowerCase();

export const getStatusTagColor = (status) => {
  switch (status?.toLowerCase()) {
    case "success":
      return "success";
    case "queued":
      return "warning";
    case "running":
      return "warning";
    case "failed":
      return "error";
    default:
      return "default";
  }
};

export const totalMetricsOptions = [
  {
    value: "total_audit_cost",
    label: `Total Audit Cost`,
  },
  {
    value: "total_audit_rows",
    label: `Total Audit Rows`,
  },
  {
    value: "total_audit_cols",
    label: `Total Audit Columns`,
  },
  {
    value: "total_audit_steps",
    label: `Total Audit Steps`,
  },
];

export const metricConfig = {
  total_audit_cost: {
    label: "Total Audit Cost",
    detailKey: "audit_cost",
    tooltipName: "Cost",
  },
  total_audit_rows: {
    label: "Total Audit Rows",
    detailKey: "audit_rows",
    tooltipName: "Rows",
  },
  total_audit_cols: {
    label: "Total Audit Columns",
    detailKey: "audit_cols",
    tooltipName: "Columns",
  },
  total_audit_steps: {
    label: "Total Audit Steps",
    detailKey: "audit_steps",
    tooltipName: "Steps",
  },
};
