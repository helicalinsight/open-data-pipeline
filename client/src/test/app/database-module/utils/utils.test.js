import {
  convertPoolingInfo,
  getEachConnStatus,
  getOptions,
  getTopLevelDuplicateKeys,
  findNodeInTree,
  prepareS3Payload,
} from "../../../../app/database-module/components/utils";
import { v4 as uuidv4 } from "uuid";

jest.mock("uuid");

describe("database module utils", () => {
  describe("getOptions", () => {
    it("should return an empty array when data is empty", () => {
      const result = getOptions([], "name", "id");
      expect(result).toEqual([]);
    });

    it("should return formatted options when valid data is provided", () => {
      const data = [
        { name: "Option 1", id: 1 },
        { name: "Option 2", id: 2 },
      ];
      const result = getOptions(data, "name", "id");
      expect(result).toEqual([
        { label: "Option 1", value: 1 },
        { label: "Option 2", value: 2 },
      ]);
    });

    it("should return the correct labels and values when items are primitive values", () => {
      const data = [5, "Option", 10];
      const result = getOptions(data, "name", "id");
      expect(result).toEqual([
        { label: 5, value: 5 },
        { label: "Option", value: "Option" },
        { label: 10, value: 10 },
      ]);
    });
  });

  describe("getEachConnStatus", () => {
    it("should return undefined if connectionStatus is not provided", () => {
      const result = getEachConnStatus(
        undefined,
        { connection_id: "1" },
        { _id: "1" }
      );
      expect(result).toBeUndefined();
    });

    it("should return undefined if selectedConnection is undefined", () => {
      const result = getEachConnStatus("active", undefined, { _id: "1" });
      expect(result).toBeUndefined();
    });

    it("should return undefined if record is undefined", () => {
      const result = getEachConnStatus(
        "active",
        { connection_id: "1" },
        undefined
      );
      expect(result).toBeUndefined();
    });

    it("should return connectionStatus if selectedConnection matches record ID", () => {
      const result = getEachConnStatus(
        "active",
        { connection_id: "1" },
        { _id: "1" }
      );
      expect(result).toBe("active");
    });

    it("should return undefined if selectedConnection does not match record ID", () => {
      const result = getEachConnStatus(
        "active",
        { connection_id: "2" },
        { _id: "1" }
      );
      expect(result).toBeUndefined();
    });

    it("should return undefined if connectionStatus is falsy", () => {
      const result = getEachConnStatus(
        "",
        { connection_id: "1" },
        { _id: "1" }
      );
      expect(result).toBeUndefined();
    });
  });

  describe("convertPoolingInfo", () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it("should return undefined if convertTo is not provided", () => {
      const result = convertPoolingInfo(undefined, {});
      expect(result).toBeUndefined();
    });

    it("should convert pooling data to an object", () => {
      const poolingData = {
        pool1: [
          { configKey: "key1", configValue: "value1" },
          { configKey: "key2", configValue: "value2" },
        ],
        pool2: [{ configKey: "keyA", configValue: "valueA" }],
      };

      const result = convertPoolingInfo("object", poolingData);
      expect(result).toEqual({
        pool1: {
          key1: "value1",
          key2: "value2",
        },
        pool2: {
          keyA: "valueA",
        },
      });
    });

    it("should convert pooling data to an array", () => {
      const poolingData = {
        pool1: {
          key1: "value1",
          key2: "value2",
        },
        pool2: {
          keyA: "valueA",
        },
      };

      uuidv4.mockImplementation(() => "unique-id"); // Mock UUID

      const result = convertPoolingInfo("array", poolingData);
      expect(result).toEqual({
        pool1: [
          { configKey: "key1", configValue: "value1", key: "unique-id" },
          { configKey: "key2", configValue: "value2", key: "unique-id" },
        ],
        pool2: [{ configKey: "keyA", configValue: "valueA", key: "unique-id" }],
      });
    });

    it("should handle empty pooling data", () => {
      const poolingData = {};
      const result = convertPoolingInfo("object", poolingData);
      expect(result).toEqual({});
    });

    it("should return an object with arrays when converting from object to array", () => {
      const poolingData = {
        pool1: {
          key1: "value1",
        },
      };

      uuidv4.mockImplementation(() => "unique-id"); // Mock UUID

      const result = convertPoolingInfo("array", poolingData);
      expect(result).toEqual({
        pool1: [{ configKey: "key1", configValue: "value1", key: "unique-id" }],
      });
    });
  });

  describe("getTopLevelDuplicateKeys", () => {
    it("should return an empty array if no duplicates exist", () => {
      const jsonStr = `{
        "a": { "x": 1 },
        "b": { "y": 2 }
      }`;
      const result = getTopLevelDuplicateKeys(jsonStr);
      expect(result).toEqual([]);
    });
  
    it("should return duplicate keys at top level", () => {
      const jsonStr = `{
        "a": { "x": 1 },
        "b": { "y": 2 },
        "a": { "z": 3 }
      }`;
      const result = getTopLevelDuplicateKeys(jsonStr);
      expect(result).toEqual(["a"]);
    });
  
    it("should ignore nested duplicates", () => {
      const jsonStr = `{
        "outer": {
          "a": { "x": 1 },
          "a": { "y": 2 }
        },
        "b": { "z": 3 }
      }`;
      const result = getTopLevelDuplicateKeys(jsonStr);
      expect(result).toEqual([]);
    });
  
    it("should handle empty string gracefully", () => {
      const result = getTopLevelDuplicateKeys("");
      expect(result).toEqual([]);
    });
  
    it("should return multiple duplicate keys", () => {
      const jsonStr = `{
        "a": {},
        "b": {},
        "c": {},
        "a": {},
        "b": {}
      }`;
      const result = getTopLevelDuplicateKeys(jsonStr);
      expect(result.sort()).toEqual(["a", "b"]);
    });
  });

  describe("findNodeInTree", () => {
    const tree = [
      {
        value: "root1",
        children: [
          { value: "child1", type: "file" },
          { value: "child2", type: "folder" },
        ],
      },
      {
        value: "root2",
        children: [
          {
            value: "child3",
            type: "folder",
            children: [
              { value: "grandchild1", type: "sheet" },
              { value: "grandchild2", type: "file" },
            ],
          },
        ],
      },
    ];

    it("should find a node by predicate", () => {
      const predicate = (node) => node.value === "child1";
      const result = findNodeInTree(tree, predicate);
      expect(result).toEqual({ value: "child1", type: "file" });
    });

    it("should return null if node not found", () => {
      const predicate = (node) => node.value === "nonexistent";
      const result = findNodeInTree(tree, predicate);
      expect(result).toBeNull();
    });

    it("should find a parent node when findParent is true", () => {
      const predicate = (node) => node.value === "grandchild1";
      const result = findNodeInTree(tree, predicate, true);
      expect(result).toEqual({
        value: "child3",
        type: "folder",
        children: [
          { value: "grandchild1", type: "sheet" },
          { value: "grandchild2", type: "file" },
        ],
      });
    });

    it("should return null when finding parent of root node", () => {
      const predicate = (node) => node.value === "root1";
      const result = findNodeInTree(tree, predicate, true);
      expect(result).toBeNull();
    });
  });

  describe("prepareS3Payload", () => {
    const s3SampleData = [
      {
        value: "file1.xlsx",
        type: "excel",
        children: [
          { value: "sheet1", type: "sheet" },
          { value: "sheet2", type: "sheet" },
        ],
      },
      {
        value: "file2.csv",
        type: "csv",
      },
    ];

    it("should prepare payload for a regular file", () => {
      const value = [{ value: "file2.csv" }];
      const selectedConnection = { _id: "conn1" };
      const chatId = "chat1";
      const selectedCols = { "file2.csv": ["col1", "col2"] };
      const result = prepareS3Payload(
        value,
        s3SampleData,
        selectedConnection,
        chatId,
        selectedCols
      );
      expect(result).toEqual([
        {
          source: "s3",
          details: {
            connection_id: "conn1",
            chat_id: "chat1",
            type: "csv",
            file_name: "file2.csv",
            catalog: {
              "file2.csv": ["col1", "col2"],
            },
          },
        },
      ]);
    });

    it("should prepare payload for a sheet within a file", () => {
      const value = [{ value: "sheet1" }];
      const selectedConnection = { _id: "conn1" };
      const chatId = "chat1";
      const selectedCols = { sheet1: ["colA", "colB"] };
      const result = prepareS3Payload(
        value,
        s3SampleData,
        selectedConnection,
        chatId,
        selectedCols
      );
      expect(result).toEqual([
        {
          source: "s3",
          details: {
            connection_id: "conn1",
            chat_id: "chat1",
            type: "excel",
            file_name: "file1.xlsx",
            catalog: {
              sheet1: ["colA", "colB"],
            },
          },
        },
      ]);
    });

    it("should handle multiple selected files", () => {
      const value = [{ value: "file2.csv" }, { value: "sheet2" }];
      const selectedConnection = { connection_id: "conn2" };
      const chatId = "chat2";
      const selectedCols = {
        "file2.csv": ["col1"],
        sheet2: ["colX"],
      };
      const result = prepareS3Payload(
        value,
        s3SampleData,
        selectedConnection,
        chatId,
        selectedCols
      );
      expect(result).toEqual([
        {
          source: "s3",
          details: {
            connection_id: "conn2",
            chat_id: "chat2",
            type: "csv",
            file_name: "file2.csv",
            catalog: {
              "file2.csv": ["col1"],
            },
          },
        },
        {
          source: "s3",
          details: {
            connection_id: "conn2",
            chat_id: "chat2",
            type: "excel",
            file_name: "file1.xlsx",
            catalog: {
              sheet2: ["colX"],
            },
          },
        },
      ]);
    });

    it("should handle empty selected columns", () => {
      const value = [{ value: "file2.csv" }];
      const selectedConnection = { _id: "conn1" };
      const chatId = "chat1";
      const selectedCols = {};
      const result = prepareS3Payload(
        value,
        s3SampleData,
        selectedConnection,
        chatId,
        selectedCols
      );
      expect(result).toEqual([
        {
          source: "s3",
          details: {
            connection_id: "conn1",
            chat_id: "chat1",
            type: "csv",
            file_name: "file2.csv",
            catalog: {
              "file2.csv": [],
            },
          },
        },
      ]);
    });

    it("should handle connection_id from connection object", () => {
      const value = [{ value: "file2.csv" }];
      const selectedConnection = { connection_id: "conn3" };
      const chatId = "chat3";
      const selectedCols = { "file2.csv": ["col1"] };
      const result = prepareS3Payload(
        value,
        s3SampleData,
        selectedConnection,
        chatId,
        selectedCols
      );
      expect(result).toEqual([
        {
          source: "s3",
          details: {
            connection_id: "conn3",
            chat_id: "chat3",
            type: "csv",
            file_name: "file2.csv",
            catalog: {
              "file2.csv": ["col1"],
            },
          },
        },
      ]);
    });
  });
});