export const isNumeric = (str) => {
  if (!str) return false;
  return !isNaN(Number(str));
};

export const getNameForAvtar = (chatName) => {
  if (!chatName) return "";
  chatName.trim();
  const names = chatName.split(" ");
  if (names.length > 1 && isNumeric(names.slice(1).join(""))) {
    return `${names[0][0].toUpperCase()}${names.slice(1).join("")}`;
  } else if (names.length > 1) {
    return `${names[0][0]?.toUpperCase()}${names[1][0]?.toUpperCase() || ""}`;
  }
  return chatName?.slice(0, 2).toUpperCase();
};
export const validateIntegerInput = (value, fieldName) => {
  if (value && value % 1 !== 0) {
    return `${fieldName} must be an integer (no decimals).`;
  }
  return null;
};
