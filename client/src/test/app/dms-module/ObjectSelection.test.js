import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ObjectSelectionModule from "../../../app/dms-module/ObjectSelection";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import { BrowserRouter } from "react-router-dom";
import * as databaseService from "../../../apis/databaseService";

jest.mock("@monaco-editor/react", () => () => <div>MonacoEditorMock</div>);

const middlewares = [thunk];
const mockStore = configureStore(middlewares);
window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };
describe("ObjectSelectionModule", () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      dms: { selectedPipelineMode: "default", selectedSourceTable: [] },
    });
    localStorage.setItem("dms_connection_id", JSON.stringify(1));
    jest.clearAllMocks();
  });

  it("renders correctly and fetches objects", async () => {
    const mockData = {
      success: true,
      dataCatalog: [
        {
          title: "Schema1",
          value: "schema1",
          children: [{ title: "Table1", value: "table1" }],
        },
      ],
    };
    jest
      .spyOn(databaseService, "fecthDbsAndTables")
      .mockImplementation(({ onSuccess }) => onSuccess(mockData));
    render(
      <Provider store={store}>
        <BrowserRouter>
          <ObjectSelectionModule />
        </BrowserRouter>
      </Provider>
    );
  });
  it("renders SQL editor in custom_sql mode", async () => {
    store = mockStore({
      dms: { selectedPipelineMode: "custom_sql" },
    });
    render(
      <Provider store={store}>
        <BrowserRouter>
          <ObjectSelectionModule />
        </BrowserRouter>
      </Provider>
    );
  });
});
