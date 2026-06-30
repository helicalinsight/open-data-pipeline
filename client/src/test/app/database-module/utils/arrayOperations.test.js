import { removeFirstDot } from "../../../../app/database-module/utils/arrayOperations";

describe("removeFirstDot function", () => {
  test("removes the first dot from a string with a dot at the beginning", () => {
    const result = removeFirstDot(".example");
    expect(result).toBe("example");
  });

  test("returns the same string if it does not start with a dot", () => {
    const result = removeFirstDot("example");
    expect(result).toBe("example");
  });

  test("returns null if input string is falsy", () => {
    const result = removeFirstDot(null);
    expect(result).toBe(null);
  });

  test("returns null if input string is an empty string", () => {
    const result = removeFirstDot("");
    expect(result).toBe(null);
  });

  test("returns null if input string is undefined", () => {
    const result = removeFirstDot(undefined);
    expect(result).toBe(null);
  });
});
