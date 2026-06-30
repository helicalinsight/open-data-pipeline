import { v4 as uuidv4 } from "uuid";

export const getOptions = (data, fileName, fileID) => {
  if (!data?.length) return [];
  let options = [];

  data.forEach((eachItem) => {
    const name = eachItem[fileName];
    const id = eachItem[fileID];

    options.push({
      label: name ? name : eachItem,
      value: id ? id : eachItem,
    });
  });
  return options;
};

export const getEachConnStatus = (
  connectionStatus,
  selectedConnection,
  record
) => {
  const isSameId = selectedConnection?.connection_id === record?._id;
  if (connectionStatus && isSameId) {
    return connectionStatus;
  }
};

export const convertPoolingInfo = (convertTo, poolingData) => {
  if (!convertTo) return;

  const convertedData = {};
  Object.entries(poolingData).forEach(([key, values]) => {
    let data;

    if (convertTo === "object") {
      const info = {};
      values.forEach((value) => {
        info[value.configKey] = value.configValue;
      });
      data = info;
    }
    if (convertTo === "array") {
      const info = [];
      Object.entries(values).forEach(([configKey, configValue]) => {
        const obj = {
          configKey,
          configValue,
          key: uuidv4(),
        };
        info.push(obj);
      });
      data = info;
    }

    convertedData[key] = data;
  });
  return convertedData;
};

export const getTopLevelDuplicateKeys = (jsonStr) => {
  const regex = /"([^"]+)"\s*:/g;
  const keyCounts = {};
  let match;
  while ((match = regex?.exec(jsonStr)) !== null) {
    const depth =
      (jsonStr?.slice(0, match.index)?.match(/{/g) || [])?.length -
      (jsonStr?.slice(0, match.index)?.match(/}/g) || [])?.length;

    if (depth === 1) {
      keyCounts[match[1]] = (keyCounts[match[1]] || 0) + 1;
    }
  }
  return Object?.keys(keyCounts)?.filter((key) => keyCounts[key] > 1);
};

export const validKey = (value) => {
  if (typeof value !== "string") {
    return "The key must be a valid string.";
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return "Key cannot be empty.";
  }
  return null;
};

export const validateKeysRecursive = (obj) => {
  if (typeof obj !== "object" || obj === null) return true;
  for (const key of Object.keys(obj)) {
    if (typeof key !== "string" || key.trim() === "") {
      return false;
    }
    const val = obj[key];
    if (!validateKeysRecursive(val)) {
      return false;
    }
  }
  return true;
};

export const findNodeInTree = (nodes, predicate, findParent = false) => {
  for (const node of nodes) {
    if (!findParent && predicate(node)) return node;
    if (node.children) {
      if (findParent && node.children.find((child) => predicate(child)))
        return node;
      const found = findNodeInTree(node.children, predicate, findParent);
      if (found) return found;
    }
  }
  return null;
};

export const prepareS3Payload = (
  value,
  dbList,
  selectedConnection,
  chatId,
  selectedCols
) => {
  return value.map((selectedFile) => {
    const selectedNode = findNodeInTree(
      dbList,
      (node) => node.value === selectedFile.value
    );
    const isSheet = selectedNode?.type === "sheet";
    const parentNode = isSheet
      ? findNodeInTree(dbList, (node) =>
          node.children?.some((child) => child.value === selectedFile.value)
        )
      : null;

    const fileType = isSheet ? parentNode?.type : selectedNode?.type;
    const fileName = isSheet ? parentNode?.value : selectedFile.value;

    return {
      source: "s3",
      details: {
        connection_id:
          selectedConnection?._id || selectedConnection?.connection_id,
        chat_id: chatId,
        type: fileType,
        file_name: fileName,
        catalog: {
          [selectedFile.value]: selectedCols[selectedFile.value] || [],
        },
      },
    };
  });
};
export const capitalizeFirstLetter = (str) => {
  if (!str) return;
  return str.charAt(0).toUpperCase() + str.slice(1);
};
