export const removeFirstDot = (str) => {
  if (!str) return null;
  if (str.charAt(0) === ".") {
    return str.substring(1);
  }
  return str;
};
