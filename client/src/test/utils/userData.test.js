import {
  getLocalStorageItem,
  setLocalStorageItem,
  removeLocalStorageData,
} from "../../utils/userData";

// Mocking localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};

beforeEach(() => {
  // Reset mocks before each test
  jest.clearAllMocks();
  Object.defineProperty(window, "localStorage", {
    value: localStorageMock,
  });
});

describe("LocalStorage Utility Functions", () => {
  it("getLocalStorageItem retrieves data from localStorage", () => {
    const key = "user";
    const testData = { id: 1, name: "John Doe" };
    localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(testData));

    const result = getLocalStorageItem(key);

    expect(localStorageMock.getItem).toHaveBeenCalledWith(key);
    expect(result).toEqual(testData);
  });

  it("getLocalStorageItem returns null for non-existing key", () => {
    const key = "nonExistingKey";
    localStorageMock.getItem.mockReturnValueOnce(null);

    const result = getLocalStorageItem(key);

    expect(localStorageMock.getItem).toHaveBeenCalledWith(key);
    expect(result).toBeNull();
  });

  it("setLocalStorageItem stores data in localStorage", () => {
    const key = "user";
    const testData = { id: 1, name: "John Doe" };

    setLocalStorageItem(testData, key);

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      key,
      JSON.stringify(testData)
    );
  });

  it("removeLocalStorageData removes data from localStorage", () => {
    const key = "user";

    removeLocalStorageData(key);

    expect(localStorageMock.removeItem).toHaveBeenCalledWith(key);
  });

  it("removeLocalStorageData does nothing for non-existing key", () => {
    const key = "nonExistingKey";

    removeLocalStorageData(key);

    expect(localStorageMock.removeItem).toHaveBeenCalledWith(key);
    // No assertion for localStorageMock.removeItem being called with null or undefined,
    // as it's the expected behavior to do nothing when removing a non-existing key.
  });
});
