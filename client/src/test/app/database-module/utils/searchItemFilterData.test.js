import { searchItemFilterData } from "../../../../app/database-module/utils/searchItemFilterData";

const data = [
  {
    alias: "test-data.csv",
    source_id: "1",
  },
  {
    alias: "user-info.csv",
    source_id: "1",
  },
  {
    alias: "students.csv",
    source_id: "1",
  },
];

describe("filter data with searchIem", () => {
  test("should return original array when there is no searchTerm", () => {
    expect(searchItemFilterData(data)).toEqual(data);
  });

  test("should return filtered array when there is searchTerm", () => {
    const result = [
      {
        alias: "user-info.csv",
        source_id: "1",
      },
    ];
    const searchIem = "user";
    expect(searchItemFilterData(data, searchIem)).toEqual(result);
  });

  test("should return filtered array when there is searchTerm", () => {
    const result = [
      {
        alias: "test-data.csv",
        source_id: "1",
      },
      {
        alias: "students.csv",
        source_id: "1",
      },
    ];
    const searchIem = "t";
    expect(searchItemFilterData(data, searchIem)).toEqual(result);
  });

  test("should return empty array when there is no matching searchTerm", () => {
    const result = [];
    const searchIem = "tjajksj";
    expect(searchItemFilterData(data, searchIem)).toEqual(result);
  });
});
