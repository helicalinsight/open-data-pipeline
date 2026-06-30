import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import QueryModeSelect from "../../../app/dms-module/QueryModeSelect";

describe("QueryModeSelect", () => {
  const queryModes = [
    { value: "replace", label: "Replace" },
    { value: "append", label: "Append" },
    { value: "merge", label: "Merge" },
  ];

  it("it should calls primary key change handler", () => {
    const onPrimaryKeyChange = jest.fn();
    render(
      <QueryModeSelect
        value="merge"
        onChange={jest.fn()}
        onPrimaryKeyChange={onPrimaryKeyChange}
        queryModes={queryModes}
      />,
    );
    fireEvent.change(screen.getByPlaceholderText("Enter primary key"), {
      target: { value: "id" },
    });
    expect(onPrimaryKeyChange).toHaveBeenCalledWith("id");
  });

  it("it should calls increment key change handler on Enter", () => {
    const onIncrementKeyChange = jest.fn();
    render(
      <QueryModeSelect
        value="append"
        onChange={jest.fn()}
        onIncrementKeyChange={onIncrementKeyChange}
        queryModes={queryModes}
      />,
    );
    const input = screen.getByPlaceholderText("Enter increment key(s)");
    fireEvent.change(input, {
      target: { value: "created_at" },
    });
    fireEvent.keyDown(input, {
      key: "Enter",
      code: "Enter",
    });
    expect(onIncrementKeyChange).toHaveBeenCalledWith("created_at");
  });

  it("commits a single increment key on blur", () => {
    const onIncrementKeyChange = jest.fn();
    render(
      <QueryModeSelect
        value="append"
        onChange={jest.fn()}
        onIncrementKeyChange={onIncrementKeyChange}
        queryModes={queryModes}
      />,
    );
    const input = screen.getByPlaceholderText("Enter increment key(s)");
    fireEvent.change(input, {
      target: { value: "created_at" },
    });
    fireEvent.blur(input);
    expect(onIncrementKeyChange).toHaveBeenCalledWith("created_at");
  });
});
