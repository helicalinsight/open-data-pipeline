import { setEditConnection,setSelectedDatasourceAction } from "../../store/actions/databaseActions";
import { setMessageAction } from "../../store/actions/settingActions";
import { dispatchMessage } from "../../utils/handleClick";
import handleBackClick from "../../utils/handleClick";

jest.mock("../../store/actions/databaseActions", () => ({
  setEditConnection: jest.fn(),
  setSelectedDatasourceAction: jest.fn(),
}));
jest.mock("../../store/actions/settingActions", () => ({
  setMessageAction: jest.fn(),
}));

describe("handleBackClick", () => {
  let dispatch;
  let setCurrent;
  let current;

  beforeEach(() => {
    dispatch = jest.fn();
    jest.useFakeTimers(); 
    setCurrent = jest.fn();
    current = 2; 
  });

  afterEach(() => {
    jest.clearAllMocks(); 
  });

  it("dispatches setSelectedDatasourceAction with an empty object", () => {
    const editConnection = {};
    handleBackClick(dispatch, editConnection, setCurrent, current);
    expect(dispatch).toHaveBeenCalledWith(setSelectedDatasourceAction({}));
  });

  it("dispatches setEditConnection with an empty object if editConnection is not empty", () => {
    const editConnection = { someKey: "someValue" };
    handleBackClick(dispatch, editConnection, setCurrent, current);
    expect(dispatch).toHaveBeenCalledWith(setEditConnection({}));
  });

  it("calls setCurrent with the decremented current value", () => {
    const editConnection = { someKey: "someValue" };
    handleBackClick(dispatch, editConnection, setCurrent, current);
    expect(setCurrent).toHaveBeenCalledWith(current - 1);
  });

  it("calls setCurrent with the decremented current value when editConnection is empty", () => {
    const editConnection = {};
    handleBackClick(dispatch, editConnection, setCurrent, current);
    expect(setCurrent).toHaveBeenCalledWith(current - 1);
  });

  it("dispatches setMessageAction with the correct type and message", () => {
    const type = "success";
    const message = "Operation completed successfully.";
    dispatchMessage(dispatch, type, message);
    expect(dispatch).toHaveBeenCalledWith(setMessageAction({ type, message }));
  });

  it("dispatches setMessageAction with null after 3 seconds", () => {
    const type = "success";
    const message = "Operation completed successfully.";
    dispatchMessage(dispatch, type, message);
    jest.advanceTimersByTime(3000);
    expect(dispatch).toHaveBeenCalledWith(setMessageAction(null));
  });
});
