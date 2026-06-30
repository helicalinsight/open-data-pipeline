import { renderHook, act } from "@testing-library/react";
import useTableConfiguration from "../../../app/dms-module/TableConfiguration";

describe("useTableConfiguration", () => {
  const tables = [
    {
      value: "users",
      title: "Users",
      schema: "public",
    },
  ];

  it("should return default query mode", () => {
    const { result } = renderHook(() => useTableConfiguration());
    expect(result.current.getQueryMode("users")).toBe("replace");
  });

  it("should update query mode", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handleQueryModeChange("users", "merge");
    });
    expect(result.current.getQueryMode("users")).toBe("merge");
  });

  it("should update primary key", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handlePrimaryKeyChange("users", "id");
    });
    expect(result.current.getPrimaryKey("users")).toBe("id");
  });

  it("should update increment key", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handleIncrementKeyChange("users", "created_at");
    });
    expect(result.current.getIncrementKey("users")).toBe("created_at");
  });

  it("should clear primary key when mode is not merge", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handlePrimaryKeyChange("users", "id");
      result.current.handleQueryModeChange("users", "replace");
    });
    expect(result.current.getPrimaryKey("users")).toBe("");
  });

  it("should clear increment key when mode is replace", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handleIncrementKeyChange("users", "created_at");
      result.current.handleQueryModeChange("users", "replace");
    });
    expect(result.current.getIncrementKey("users")).toBe("");
  });

  it("should validate empty primary key", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handleQueryModeChange("users", "merge");
    });
    expect(result.current.hasEmptyPrimaryKey(tables)).toBe(true);
  });

  it("should validate empty increment key", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handleQueryModeChange("users", "append");
    });
    expect(result.current.hasEmptyIncrementKey(tables)).toBe(true);
  });

  it("should return table configurations", () => {
    const { result } = renderHook(() => useTableConfiguration());
    act(() => {
      result.current.handleQueryModeChange("users", "merge");
      result.current.handlePrimaryKeyChange("users", "id");
      result.current.handleIncrementKeyChange("users", "created_at");
    });
    expect(result.current.getTableConfigurations(tables)).toEqual([
      {
        tableName: "users",
        tableTitle: "Users",
        schema: "public",
        schemaTitle: "public",
        queryMode: "merge",
        primaryKey: "id",
        incrementKey: "created_at",
      },
    ]);
  });
});