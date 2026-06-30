import {
  convertToTitleCase,
  getTableColumns,
} from "../../../../app/chat-module/components/utils";

describe("getTableColumns function", () => {
  test("returns an array of columns with correct properties", () => {
    const fileData = {
      columns: [
        { name: "column1", dataType: "string" },
        { name: "column2", dataType: "int64" },
      ],
    };
    const columns = getTableColumns(fileData);

    expect(columns).toHaveLength(2);
    expect(columns[0]).toHaveProperty("title");
    expect(columns[0]).toHaveProperty("dataIndex", "column1");
    expect(columns[0]).toHaveProperty("width", 100);
    expect(columns[0]).toHaveProperty("key", "column1");
    expect(columns[0]).toHaveProperty("ellipsis", true);
    expect(columns[0]).toHaveProperty("onFilter");
    expect(columns[0]).toHaveProperty("render");
    expect(columns[0]).not.toHaveProperty("sorter");

    expect(columns[1]).toHaveProperty("title");
    expect(columns[1]).toHaveProperty("dataIndex", "column2");
    expect(columns[1]).toHaveProperty("width", 100);
    expect(columns[1]).toHaveProperty("key", "column2");
    expect(columns[1]).toHaveProperty("ellipsis", true);
    expect(columns[1]).toHaveProperty("onFilter");
    expect(columns[1]).toHaveProperty("render");
    expect(columns[1]).toHaveProperty("sorter");
  });

  test("returns empty array if fileData.columns is empty", () => {
    const fileData = { columns: [] };
    const columns = getTableColumns(fileData);
    expect(columns).toHaveLength(0);
  });
});

describe("convertToTitleCase function", () => {
  test("converts string to title case", () => {
    const str = "this_is_a_test_string";
    const result = convertToTitleCase(str);
    expect(result).toBe("This Is A Test String");
  });

  test("handles empty string input", () => {
    const str = "";
    const result = convertToTitleCase(str);
    expect(result).toBe("");
  });

  test("handles null input", () => {
    const str = null;
    const result = convertToTitleCase(str);
    expect(result).toBe(undefined);
  });

  test("handles undefined input", () => {
    const str = undefined;
    const result = convertToTitleCase(str);
    expect(result).toBe(undefined);
  });
});
