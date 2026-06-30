import {
  convertToString,
  sortByName,
  fetchDagListUtil,
} from "../../utils/appUtils";
import { getDagList } from "../../apis/jobScheduleService";
import { setDagsListAction } from "../../store/actions/jobScheduleActions";
import { handleSessionExpiry } from "../../utils/handleSessionExpiry";

jest.mock("../../apis/jobScheduleService");
jest.mock("../../store/actions/jobScheduleActions");
jest.mock("../../utils/handleSessionExpiry");

describe("appUtils", () => {
  describe("convertToString function", () => {
    it("converts numbers to strings correctly", () => {
      const result = convertToString(123);
      expect(result).toBe("123");
    });

    it("converts strings to strings correctly", () => {
      const result = convertToString("hello");
      expect(result).toBe("hello");
    });

    it("converts booleans to strings correctly", () => {
      const result = convertToString(true);
      expect(result).toBe("true");
    });

    it('converts null to string "null"', () => {
      const result = convertToString(null);
      expect(result).toBe("null");
    });

    it('converts undefined to string "undefined"', () => {
      const result = convertToString(undefined);
      expect(result).toBe("undefined");
    });

    it("converts arrays to JSON strings correctly", () => {
      const result = convertToString([1, 2, 3]);
      expect(result).toBe("[1,2,3]");
    });

    it("converts objects to JSON strings correctly", () => {
      const result = convertToString({ key: "value" });
      expect(result).toBe('{"key":"value"}');
    });
  });

  describe("sortByName function", () => {
    it("sorts an array of objects by name property", () => {
      const data = [
        { name: "Zebra" },
        { name: "apple" },
        { name: "Banana" },
      ];
      const expected = [
        { name: "apple" },
        { name: "Banana" },
        { name: "Zebra" },
      ];
      const result = sortByName(data);
      expect(result).toEqual(expected);
    });

    it("handles empty array", () => {
      const result = sortByName([]);
      expect(result).toEqual([]);
    });

    it("handles case sensitivity", () => {
      const data = [
        { name: "apple" },
        { name: "Apple" },
        { name: "banana" },
      ];
      const expected = [
        { name: "apple" },
        { name: "Apple" },
        { name: "banana" },
      ];
      const result = sortByName(data);
      expect(result).toEqual(expected);
    });
  });

  describe("fetchDagListUtil function", () => {
    const mockDispatch = jest.fn();
    const mockSetLoading = jest.fn();
    const mockUser = { id: "user123" };
    const mockResponse = { dags: [{ id: 1, name: "Test DAG" }] };
    const mockError = { message: "Error occurred" };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    it("should call setLoading with true initially", () => {
      fetchDagListUtil({
        dispatch: mockDispatch,
        setLoading: mockSetLoading,
        user: mockUser,
      });
      expect(mockSetLoading).toHaveBeenCalledWith(true);
    });

    it("should call getDagList with correct payload", () => {
      fetchDagListUtil({
        dispatch: mockDispatch,
        setLoading: mockSetLoading,
        user: mockUser,
      });
      expect(getDagList).toHaveBeenCalledWith({
        payload: { user_id: "user123" },
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      });
    });

    it("should dispatch setDagsListAction on success", () => {
      getDagList.mockImplementation(({ onSuccess }) => {
        onSuccess(mockResponse);
      });
      fetchDagListUtil({
        dispatch: mockDispatch,
        setLoading: mockSetLoading,
        user: mockUser,
      });
      expect(mockDispatch).toHaveBeenCalledWith(
        setDagsListAction(mockResponse.dags)
      );
      expect(mockSetLoading).toHaveBeenCalledWith(false);
    });

    it("should handle error and call handleSessionExpiry", () => {
      getDagList.mockImplementation(({ onError }) => {
        onError(mockError);
      });
      fetchDagListUtil({
        dispatch: mockDispatch,
        setLoading: mockSetLoading,
        user: mockUser,
      });
      expect(handleSessionExpiry).toHaveBeenCalledWith(mockDispatch, mockError);
      expect(mockSetLoading).toHaveBeenCalledWith(false);
    });

    it("should work without setLoading function", () => {
      getDagList.mockImplementation(({ onSuccess }) => {
        onSuccess(mockResponse);
      });
      expect(() => {
        fetchDagListUtil({
          dispatch: mockDispatch,
          user: mockUser,
        });
      }).not.toThrow();
    });
  });
});