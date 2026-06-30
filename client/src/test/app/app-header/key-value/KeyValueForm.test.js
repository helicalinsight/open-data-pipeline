import { act, fireEvent, render, screen } from "@testing-library/react";

import KeyValueForm from "../../../../app/app-header/components/key-value/KeyValueForm";
import "../../../__mocks__/matchMedia";
import * as reactRedux from "react-redux";
import "@testing-library/jest-dom";
import configureStore from "redux-mock-store";


const props = {
  keyValueData: [{ configKey: "testkey" }],
  onAdd: jest.fn(),
};
const mockStore = configureStore();
const store = mockStore({}); 
const renderWithProvider = (component) => {
  return render(<reactRedux.Provider store={store}>{component}</reactRedux.Provider>);
};
describe("KeyValueForm Component", () => {
  it("should render component without errors", () => {
    renderWithProvider(<KeyValueForm {...props} />);
  });

  it("should trigger on submit when user clicks on add button", () => {
    renderWithProvider(<KeyValueForm {...props} />);
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

  it("it should show warning if user enters same key again", () => {
    renderWithProvider(<KeyValueForm {...props} />);
    const keyInput = screen.getByTestId("configKey");
    const valueInput = screen.getByTestId("configValue");
    act(() => {
      fireEvent.change(keyInput, { target: { value: "testkey" } });
      fireEvent.change(valueInput, { target: { value: "$23.0" } });
    });
    act(() => {
      fireEvent.submit(screen.getByTestId("key-value-form"));
    });
  });
});
