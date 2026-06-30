import {
  getRowClassName,
  transformChatHistoryData,
} from "../../../app/chat-module/utils";
import getTimeStamp from "../../../utils/getCurrentTime";

describe("transformChatHistoryData", () => {
  test("should return an empty array if input is an empty array", () => {
    const result = transformChatHistoryData([]);
    expect(result).toEqual([]);
  });

  test("should transform chat data correctly with valid input", () => {
    const chatData = [
      { text: "Hello", timestamp: 1644268800, message_id: "1" },
    ];

    const expectedOutput = [
      {
        message_id: "1",
        text: "Hello",
        time: getTimeStamp(1644268800000),
        timestamp: 1644268800,
        id: "1",
      },
    ];

    const result = transformChatHistoryData(chatData);

    expect(result).toEqual(expectedOutput);
  });

  test("should handle input with non-text messages", () => {
    const chatData = [
      { image: "image_url", timestamp: 1644268800, message_id: "1" },
      { video: "video_url", timestamp: 1644272400, message_id: "2" },
    ];

    const result = transformChatHistoryData(chatData);
    expect(result).toEqual([]);
  });

  test("should handle input with mixed text and non-text messages", () => {
    const chatData = [
      { text: "Hello", timestamp: 1644268800, message_id: "1" },
      { image: "image_url", timestamp: 1644272400, message_id: "2" },
    ];

    const expectedOutput = [
      {
        id: "1",
        message_id: "1",
        text: "Hello",
        time: getTimeStamp(1644268800000),
        timestamp: 1644268800,
      },
    ];

    const result = transformChatHistoryData(chatData);
    expect(result).toEqual(expectedOutput);
  });
});

describe("getRowClassName", () => {
  it('should return "row-bg-color" for odd-numbered rows', () => {
    const record = {
      /* some record data */
    };
    const index = 1; // odd-numbered row
    const className = getRowClassName(record, index);
    expect(className).toBe("row-bg-color");
  });

  it('should return "row-bg-color" for odd-numbered rows (different index)', () => {
    const record = {
      /* some record data */
    };
    const index = 5; // odd-numbered row
    const className = getRowClassName(record, index);
    expect(className).toBe("row-bg-color");
  });

  it('should return "row-white-bg-color" for even-numbered rows', () => {
    const record = {
      /* some record data */
    };
    const index = 0; // even-numbered row
    const className = getRowClassName(record, index);
    expect(className).toBe("row-white-bg-color");
  });

  it('should return "row-white-bg-color" for even-numbered rows (different index)', () => {
    const record = {
      /* some record data */
    };
    const index = 4; // even-numbered row
    const className = getRowClassName(record, index);
    expect(className).toBe("row-white-bg-color");
  });

  it("should handle negative indexes", () => {
    const record = {
      /* some record data */
    };
    const index = -1; // negative index
    const className = getRowClassName(record, index);
    expect(className).toBe("row-white-bg-color");
  });
});
