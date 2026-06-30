import { fireEvent, render, screen, act } from "@testing-library/react";
import AdvancedPooling from "../../../../app/database-module/components/AdvancedPooling";
import "../../../__mocks__/matchMedia";
import { Provider } from "react-redux";
import { createStore } from "redux";
const store = createStore(() => ({
  someState: {}, // Replace with your actual store structure
}));
const props = {
  poolingData: {
    spark_pooling: [
      {
        key: "e63e6acc-6bd3-44a7-92e6-38130dfe2319",
        configKey: "spark",
        configValue: "spark-value",
      },
    ],
    pandas_pooling: [],
  },
  setPoolingData: jest.fn(),
  poolingOn: "spark_pooling",
};

describe("Advanced Pooling", () => {
  it("should render the compoenent without errors", () => {
    render(
      <Provider store={store}>
        <AdvancedPooling {...props} />
      </Provider>
      // AdvancedPooling {...props} />
    );
  });

  it("should trigger onAdd func", () => {
    render(
      <Provider store={store}>
        <AdvancedPooling {...props} />
      </Provider>
      // <AdvancedPooling {...props} />
    );

    const keyInput = screen.getByTestId("configKey");
    const valueInput = screen.getByTestId("configValue");
    act(() => {
      fireEvent.change(keyInput, { target: { value: "$23.0" } });
      fireEvent.change(valueInput, { target: { value: "$23.0" } });
    });
    act(() => {
      fireEvent.submit(screen.getByTestId("key-value-form"));
    });
  });

  it("should trigger onDelete func", () => {
    render(
      <Provider store={store}>
        <AdvancedPooling {...props} />
      </Provider>
      // <AdvancedPooling {...props} />
    );
    act(() => {
      fireEvent.click(screen.getByTestId("delete"));
    });
  });

  it("should trigger onEdit func", () => {
    render(
      <Provider store={store}>
        <AdvancedPooling {...props} />
      </Provider>
      // <AdvancedPooling {...props} />
    );

    act(() => {
      fireEvent.click(screen.getByTestId("edit"));
    });
    act(() => {
      fireEvent.click(screen.getByTestId("update-button"));
    });
  });
});
