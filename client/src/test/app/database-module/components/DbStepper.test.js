// DbStepper.test.js
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import DbStepper from "../../../../app/database-module/components/DbStepper";
import "@testing-library/jest-dom";

jest.mock("../../../../utils/handleClick");
const mockStore = configureStore([]);

describe("DbStepper Component", () => {
  let store;
  let current = 0;
  let setCurrent = jest.fn();

  beforeEach(() => {
    store = mockStore({
      database: {
        editConnection: {},
      },
    });
  });

  test("renders the current step content", () => {
    const steps = [
      { content: "Step 1 Content" },
      { content: "Step 2 Content" },
    ];
    render(
      <Provider store={store}>
        <DbStepper
          current={current}
          items={[]}
          steps={steps}
          setCurrent={setCurrent}
          showCloseButton={false}
        />
      </Provider>
    );
    expect(screen.getByText("Step 1 Content")).toBeInTheDocument();
  });

  test("does not render CloseButton when showCloseButton is false", () => {
    const steps = [{ content: "Step 1 Content" }];
    render(
      <Provider store={store}>
        <DbStepper
          current={current}
          items={[]}
          steps={steps}
          setCurrent={setCurrent}
          showCloseButton={false}
        />
      </Provider>
    );
    expect(screen.queryByText("Close")).not.toBeInTheDocument();
  });

  test("renders CloseButton when showCloseButton is true and current > 0", () => {
    current = 1;
    const steps = [
      { content: "Step 1 Content" },
      { content: "Step 2 Content" },
    ];
    render(
      <Provider store={store}>
        <DbStepper
          current={current}
          items={[]}
          steps={steps}
          setCurrent={setCurrent}
          showCloseButton={true}
        />
      </Provider>
    );
  });

  test("calls handleBackClick on CloseButton click", () => {
    current = 1;
    const steps = [
      { content: "Step 1 Content" },
      { content: "Step 2 Content" },
    ];
    render(
      <Provider store={store}>
        <DbStepper
          current={current}
          items={[]}
          steps={steps}
          setCurrent={setCurrent}
          showCloseButton={true}
        />
      </Provider>
    );
  });
});
