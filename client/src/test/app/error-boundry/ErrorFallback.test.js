import React from "react";
import { render, screen } from "@testing-library/react";
import ErrorFallback from "../../../app/error-boundry/ErrorFallback"; // Adjust the path as needed
import "@testing-library/jest-dom";

// Mock lodash.isequal
jest.mock("lodash.isequal", () => jest.fn());

// Mock react-redux connect function
jest.mock("react-redux", () => ({
  connect: () => (Component) => Component,
}));

describe("ErrorFallback", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorFallback>
        <div>Test Child</div>
      </ErrorFallback>
    );
    expect(screen.getByText("Test Child")).toBeInTheDocument();
  });

  it("updates error state when an error occurs", () => {
    const error = new Error("Test error");
    const instance = new ErrorFallback({});
    instance.setState = jest.fn();

    instance.componentDidCatch(error);

    expect(instance.setState).toHaveBeenCalledWith({ error });
  });

  it("attempts to reset error state when props change", () => {
    const isEqual = require("lodash.isequal");
    isEqual.mockReturnValue(false);

    const instance = new ErrorFallback({});
    instance.state = { error: new Error("Test error") };
    instance.setState = jest.fn();

    instance.componentDidUpdate({});

    expect(instance.setState).toHaveBeenCalledWith({ error: false });
  });

  it("does not attempt to reset error state when props are the same", () => {
    const isEqual = require("lodash.isequal");
    isEqual.mockReturnValue(true);

    const instance = new ErrorFallback({});
    instance.state = { error: new Error("Test error") };
    instance.setState = jest.fn();

    instance.componentDidUpdate({});

    expect(instance.setState).not.toHaveBeenCalled();
  });
});
