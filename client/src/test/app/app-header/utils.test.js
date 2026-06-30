import { getLoadedFiles, getRangeText } from "../../../app/app-header/utils";

describe("getLoadedFiles", () => {
  test("returns an empty array when loadedFiles is empty", () => {
    const result = getLoadedFiles([], [0, 5]);
    expect(result).toEqual([]);
  });

  test("returns the correct subset of loadedFiles based on indexRange", () => {
    const loadedFiles = ["file1", "file2", "file3", "file4", "file5"];
    const result = getLoadedFiles(loadedFiles, [1, 4]);
    expect(result).toEqual(["file2", "file3", "file4"]);
  });

  test("handles indexRange exceeding the length of loadedFiles", () => {
    const loadedFiles = ["file1", "file2", "file3"];
    const result = getLoadedFiles(loadedFiles, [0, 5]);
    expect(result).toEqual(["file1", "file2", "file3"]);
  });
});

describe("getRangeText", () => {
  test("returns null when loadedFiles is empty", () => {
    const result = getRangeText([], [0, 5]);
    expect(result).toBeNull();
  });

  test("formats the range text correctly", () => {
    const loadedFiles = ["file1", "file2", "file3", "file4", "file5"];
    const result = getRangeText(loadedFiles, [1, 4]);
    expect(result).toBe("2-4 of 5");
  });

  test("handles endIndex exceeding the length of loadedFiles", () => {
    const loadedFiles = ["file1", "file2", "file3"];
    const result = getRangeText(loadedFiles, [0, 5]);
    expect(result).toBe("1-3 of 3");
  });

  test("handles startIndex and endIndex equal to the length of loadedFiles", () => {
    const loadedFiles = ["file1", "file2", "file3"];
    const result = getRangeText(loadedFiles, [0, 3]);
    expect(result).toBe("1-3 of 3");
  });
});
