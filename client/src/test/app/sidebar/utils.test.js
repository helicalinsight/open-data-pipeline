import { getNameForAvtar, isNumeric,validateIntegerInput  } from "../../../app/sidebar/utils";

describe("isNumeric", () => {
  it("should return true for a numeric string", () => {
    expect(isNumeric("123")).toBe(true);
  });

  it("should return false for a non-numeric string", () => {
    expect(isNumeric("abc")).toBe(false);
  });

  it("should return false for an empty string", () => {
    expect(isNumeric("")).toBe(false);
  });

  it("should return false for null input", () => {
    expect(isNumeric(null)).toBe(false);
  });
});

describe("getNameForAvtar", () => {
  it("should return an empty string for undefined input", () => {
    expect(getNameForAvtar()).toBe("");
  });

  it("should return an empty string for an empty string input", () => {
    expect(getNameForAvtar("")).toBe("");
  });

  it("should return the capitalized first two letters for a single-word name", () => {
    expect(getNameForAvtar("john")).toBe("JO");
  });

  it("should return the first letter of the first word and the first letter of the second word for a two-word name", () => {
    expect(getNameForAvtar("john doe")).toBe("JD");
  });

  it("should return the first letter of the first word and the numeric part of the second word for a two-word name with a numeric second part", () => {
    expect(getNameForAvtar("john 123")).toBe("J123");
  });

  it("should handle multiple words and return the first letter of the first word and the first letter of the second word for a multi-word name", () => {
    expect(getNameForAvtar("john smith doe")).toBe("JS");
  });

  it("trim the spaces and return same name", () => {
    expect(getNameForAvtar("Job    ")).toBe("J");
  });
});
describe('validateIntegerInput', () => {
  it('should return null for an integer value', () => {
    expect(validateIntegerInput('42', 'Test Field')).toBeNull();
    expect(validateIntegerInput('0', 'Test Field')).toBeNull();
    expect(validateIntegerInput('-5', 'Test Field')).toBeNull();
  });

  it('should return error message for decimal values', () => {
    const expected = 'Test Field must be an integer (no decimals).';
    expect(validateIntegerInput('3.14', 'Test Field')).toBe(expected);
    expect(validateIntegerInput('0.5', 'Test Field')).toBe(expected);
    expect(validateIntegerInput('-2.718', 'Test Field')).toBe(expected);
  });

  it('should return null for empty/undefined/null values', () => {
    expect(validateIntegerInput('', 'Test Field')).toBeNull();
    expect(validateIntegerInput(undefined, 'Test Field')).toBeNull();
    expect(validateIntegerInput(null, 'Test Field')).toBeNull();
  });

  it('should include the field name in the error message', () => {
    const result = validateIntegerInput('1.23', 'Age');
    expect(result).toBe('Age must be an integer (no decimals).');
  });
});