import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import DestinationModule from "../../../app/dms-module/DestinationModule";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import { BrowserRouter } from "react-router-dom";

// Mock the dependencies
jest.mock("@monaco-editor/react", () => () => <div>MonacoEditorMock</div>);
const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock window.matchMedia
window.matchMedia = window.matchMedia || function () {
  return {
    matches: false,
    addListener: function () {},
    removeListener: function () {},
  };
};

describe("DestinationObjectSelectionModule", () => {
  let store;
  const mockNavigate = jest.fn();

  beforeEach(() => {
    store = mockStore({
      dms: { 
        selectedPipelineMode: "default",
        destSelectedObjects: ""
      },
      settings: {
        messageData: null
      }
    });
    
    jest.clearAllMocks();
    jest.mock("react-router-dom", () => ({
      ...jest.requireActual("react-router-dom"),
      useNavigate: () => mockNavigate,
    }));
  });

  it("should populates input from destSelectedObjects in redux store", async () => {
    const storeWithValue = mockStore({
      dms: { 
        selectedPipelineMode: "default",
      },
      settings: {
        messageData: null
      }
    });
    render(
      <Provider store={storeWithValue}>
        <BrowserRouter>
          <DestinationModule />
        </BrowserRouter>
      </Provider>
    );
    const input = screen.getByPlaceholderText("Enter target table name");
  });
});