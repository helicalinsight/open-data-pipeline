import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import SourceModule from "../../../app/dms-module/SourceModule";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import { BrowserRouter } from "react-router-dom";

const mockedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

jest.mock("../../../store/actions/dmsAction", () => ({
  setQueryModeAction: jest.fn(),
  setPrimaryKeyAction: jest.fn(),
}));

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

describe("SourceModule Component", () => {
  let store;
  const selectedSourceTableMock = [
    { value: "table1",name: "schema1.table1", title: "Table 1", schema: "schema1" },
  ];

  beforeEach(() => {
    store = mockStore({});
    jest.clearAllMocks();
  });

  it("renders correctly with selected objects", () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <SourceModule selectedSourceTable={selectedSourceTableMock} mode={false} />
        </BrowserRouter>
      </Provider>
    );
  });

  it("enables Continue button when a primary key is provided for merge mode", () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <SourceModule selectedSourceTable={selectedSourceTableMock} mode={false} />
        </BrowserRouter>
      </Provider>
    );
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "merge" } });
  });

  it("disables Continue button when no objects are selected", () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <SourceModule selectedSourceTable={[]} mode={false} />
        </BrowserRouter>
      </Provider>
    );
    const continueButton = screen.getByRole("button", { name: /Continue/i });
  });

  it("disables Continue button if query mode is merge but primary key is empty", () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <SourceModule selectedSourceTable={selectedSourceTableMock} mode={false} />
        </BrowserRouter>
      </Provider>
    );
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "merge" } });
    const continueButton = screen.getByRole("button", { name: /Continue/i });
  });
});
