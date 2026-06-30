import getTimeStamp from "../../utils/getCurrentTime";

describe("getTimeStamp function", () => {
  test("returns a valid timestamp for a given date", () => {
    const date = new Date("2023-12-07T12:34:56");
    const timestamp = date.getTime();
    const result = getTimeStamp(timestamp);
    // Assuming the result format is 'hh:mm AM/PM'
    expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4} \d{1,2}:\d{2} [APMapm]{2}$/);
  });

  test("returns a valid timestamp for the current date", () => {
    const result = getTimeStamp();
    // Assuming the result format is 'hh:mm AM/PM'
    expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4} \d{1,2}:\d{2} [APMapm]{2}$/);
  });

  test("handles midnight correctly", () => {
    const date = new Date("2023-12-07T00:00:00");
    const timestamp = date.getTime();
    const result = getTimeStamp(timestamp);
    expect(result).toBe("07/12/2023 12:00 AM");
  });

  test("handles noon correctly", () => {
    const date = new Date("2023-12-07T12:00:00");
    const timestamp = date.getTime();
    const result = getTimeStamp(timestamp);
    expect(result).toBe("07/12/2023 12:00 PM");
  });
});
