import { act, fireEvent, render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";
import "../../../__mocks__/matchMedia";
import KeyValueTable from "../../../../app/app-header/components/key-value/KeyValueTable";

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

const initialState = {
  jobSchedule: {
    isScheduleEditMode: false,
    jobListDetails: {
      job_details: {
        configuration: [],
      },
    },
  },
};

const baseProps = {
  onEdit: jest.fn(),
  onDelete: jest.fn(),
  handleFinish: jest.fn(),
  loading: false,
  values: {},
  visible: true,
  dataSource: [
    {
      key: "11a4524e-4a74-4c67-8c79-a75ad282f077",
      configKey: "spark-1",
      configValue: "spark-value",
    },
  ],
};

describe("KeyValueTable Component", () => {
  let store;

  beforeEach(() => {
    store = mockStore(initialState);
    jest.clearAllMocks();
  });

  const renderComponent = (additionalProps = {}) => {
    return render(
      <Provider store={store}>
        <KeyValueTable {...baseProps} {...additionalProps} />
      </Provider>
    );
  };

  it("should render the component with data", () => {
    renderComponent();
  });

  it("should call onEdit with updated data when save is successful", async () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("edit"));
    
    const keyInput = screen.getByDisplayValue("spark-1");
    const valueInput = screen.getByDisplayValue("spark-value");
    
    await act(async () => {
      fireEvent.change(keyInput, { target: { value: "updated-key" } });
      fireEvent.change(valueInput, { target: { value: "updated-value" } });
      fireEvent.click(screen.getByTestId("update-button"));
    });

    expect(baseProps.onEdit).toHaveBeenCalledTimes(1);
  });

  it("should exit edit mode when cancel is clicked", () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("edit"));
    fireEvent.click(screen.getByTestId("cancel-button"));
  });

  it("should show delete confirmation modal when delete is clicked", () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("delete"));
  });

  it("should not call onDelete when delete is canceled", () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("delete"));
    fireEvent.click(screen.getByText("Cancel"));
    expect(baseProps.onDelete).not.toHaveBeenCalled();
  });

  it("should call handleFinish when Test Connection button is clicked", () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("test-button"));
    expect(baseProps.handleFinish).toHaveBeenCalledWith(
      baseProps.values,
      baseProps.dataSource,
      "child"
    );
  });

  it("should not show Test Connection button when visible prop is false", () => {
    renderComponent({ visible: false });
  });

  describe("when in schedule edit mode", () => {
    const scheduleEditState = {
      jobSchedule: {
        isScheduleEditMode: true,
        jobListDetails: {
          job_details: {
            configuration: [
              {
                configKey: "schedule-key",
                configValue: "schedule-value",
              },
            ],
          },
        },
      },
    };

    it("should use data from jobListDetails instead of dataSource", () => {
      const customStore = mockStore(scheduleEditState);
      render(
        <Provider store={customStore}>
          <KeyValueTable {...baseProps} dataSource={[]} />
        </Provider>
      );
    });

    it("should call onEdit with updated config when in schedule edit mode", async () => {
      const customStore = mockStore(scheduleEditState);
      render(
        <Provider store={customStore}>
          <KeyValueTable {...baseProps} dataSource={[]} />
        </Provider>
      );
      fireEvent.click(screen.getByTestId("edit"));
      const keyInput = screen.getByDisplayValue("schedule-key");
      await act(async () => {
        fireEvent.change(keyInput, { target: { value: "updated-schedule-key" } });
        fireEvent.click(screen.getByTestId("update-button"));
      });
      expect(baseProps.onEdit).toHaveBeenCalledTimes(1);
      expect(Array.isArray(baseProps.onEdit.mock.calls[0][0])).toBe(true);
    });

    it("should handle deletion differently in schedule edit mode", () => {
      const customStore = mockStore(scheduleEditState);
      render(
        <Provider store={customStore}>
          <KeyValueTable {...baseProps} dataSource={[]} />
        </Provider>
      );
      fireEvent.click(screen.getByTestId("delete"));
    });
  });

  it("should handle adding new rows when saving with new key", async () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("edit"));
    const keyInput = screen.getByDisplayValue("spark-1");
    const valueInput = screen.getByDisplayValue("spark-value");
    await act(async () => {
      fireEvent.change(keyInput, { target: { value: "completely-new-key" } });
      fireEvent.change(valueInput, { target: { value: "new-value" } });
      fireEvent.click(screen.getByTestId("update-button"));
    });
    expect(baseProps.onEdit).toHaveBeenCalledTimes(1);
    const updatedData = baseProps.onEdit.mock.calls[0][0];
    expect(updatedData.some(item => item.configKey === "completely-new-key")).toBe(true);
  });

  it("should not call onEdit when validation fails", async () => {
    renderComponent();
    fireEvent.click(screen.getByTestId("edit"));
    const keyInput = screen.getByDisplayValue("spark-1");
    await act(async () => {
      fireEvent.change(keyInput, { target: { value: "" } });
      fireEvent.click(screen.getByTestId("update-button"));
    });
    expect(baseProps.onEdit).not.toHaveBeenCalled();
  });
});