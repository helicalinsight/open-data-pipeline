import { handleSessionExpiry } from "../../utils/handleSessionExpiry";
import { setSessionExpiry } from "../../store/actions/appActions";

describe("handleSessionExpiry function", () => {
  const mockDispatch = jest.fn();

  beforeEach(() => {
    mockDispatch.mockClear();
  });

  test('calls setSessionExpiry with true when error message is "Token is invalid"', () => {
    const error = { msg: "Token is invalid" };
    handleSessionExpiry(mockDispatch, error);

    expect(mockDispatch).toHaveBeenCalledWith(setSessionExpiry(true));
  });

  test('calls setSessionExpiry with true when error message is "Token expired"', () => {
    const error = { msg: "Token expired" };
    handleSessionExpiry(mockDispatch, error);

    expect(mockDispatch).toHaveBeenCalledWith(setSessionExpiry(true));
  });

  test('does not call setSessionExpiry when error message is not "Token is invalid" or "Token expired"', () => {
    const error = { msg: "Some other error" };
    handleSessionExpiry(mockDispatch, error);

    expect(mockDispatch).not.toHaveBeenCalledWith(setSessionExpiry(true));
  });

  test("does not call setSessionExpiry when error is not provided", () => {
    handleSessionExpiry(mockDispatch);

    expect(mockDispatch).not.toHaveBeenCalledWith(setSessionExpiry(true));
  });

  test("does not call setSessionExpiry when error has no msg property", () => {
    const error = { someOtherProperty: "Some value" };
    handleSessionExpiry(mockDispatch, error);

    expect(mockDispatch).not.toHaveBeenCalledWith(setSessionExpiry(true));
  });
});
