export const CLIENT_ID = process.env?.REACT_APP_CLIENT_ID;

export const imagePath = "static/react/images";

export const appSuggestionsData = [
  {
    title: "Expression",
    extension: "/expression",
    value: "expression",
    description:
      "Stuck on a quick calculation? This function is here to help! Simply type /expression followed by your equation, like /expression 1+2+a. It understands basic math symbols like plus, minus, multiply, and divide. It can even handle variables like a, b, or c, as long as their values are defined elsewhere. Let this function be your pocket calculator!",
  },
  {
    title: "SQL",
    extension: "/sql",
    value: "sql",
    description:
      "Want to quickly peek at data in a database without the hassle of a full interface? This function is your shortcut! Use /sql followed by your SELECT query, like /sql SELECT * FROM customers. It can handle various SELECT statements to retrieve data from tables.  Think of it as a mini database explorer for on-the-spot checks.  Remember, this function is currently limited to SELECT queries only.",
  },
  {
    title: "BI",
    extension: "/bi",
    value: "bi",
    description: `Ditch the SQL! Use /bi with plain English to ask your database questions.  Just say what you want to know, like "total students by age?". It translates those questions into queries for you.   Easy to use, but keep in mind it might take some practice to perfect your questions.`,
  },
];

export const excelTypeExtenstions = [
  "xls",
  "xlsx",
  "xlsm",
  "xlsb",
  "xltx",
  "xltm",
];

const CompletionItemKind = {
  0: "Method",
  1: "Function",
  2: "Constructor",
  3: "Field",
  4: "Variable",
  5: "Class",
  6: "Struct",
  7: "Interface",
  8: "Module",
  9: "Property",
  10: "Event",
  11: "Operator",
  12: "Unit",
  13: "Value",
  14: "Constant",
  15: "Enum",
  16: "EnumMember",
  17: "Keyword",
  18: "Text",
  19: "Color",
  20: "File",
  21: "Reference",
  22: "Customcolor",
  23: "Folder",
  24: "TypeParameter",
  25: "User",
  26: "Issue",
  27: "Snippet",
};
