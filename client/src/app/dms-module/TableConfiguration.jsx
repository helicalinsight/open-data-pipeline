import { useState, useCallback } from "react";

const DEFAULT_QUERY_MODE = "replace";

const useTableConfiguration = () => {
  const [queryModes, setQueryModes] = useState({});
  const [primaryKeys, setPrimaryKeys] = useState({});
  const [incrementKeys, setIncrementKeys] = useState({});
  const updateState = (setter, table, value) =>
    setter((prev) => ({ ...prev, [table]: value }));
  const removeKey = (setter, table) =>
    setter((prev) => {
      const updated = { ...prev };
      delete updated[table];
      return updated;
    });
  const getValue = (state, table, fallback = "") =>
    state[table] || fallback;

  const handleQueryModeChange = useCallback((table, value) => {
    updateState(setQueryModes, table, value);
    value !== "merge" && removeKey(setPrimaryKeys, table);
    !["merge", "append"].includes(value) &&
      removeKey(setIncrementKeys, table);
  }, []);

  const handlePrimaryKeyChange = useCallback(
    (table, value) => updateState(setPrimaryKeys, table, value),
    [],
  );

const handleIncrementKeyChange = useCallback((table, value) => {
  const values = Array.isArray(value)
    ? value.filter(Boolean)
    : value
      ? value
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean)
      : [];
  updateState(
    setIncrementKeys,
    table,
    values.length === 0 ? "" : values.length === 1 ? values[0] : values,
  );
}, []);

  const getQueryMode = useCallback(
    (table) => getValue(queryModes, table, DEFAULT_QUERY_MODE),
    [queryModes],
  );

  const getPrimaryKey = useCallback(
    (table) => getValue(primaryKeys, table),
    [primaryKeys],
  );

  const getIncrementKey = useCallback(
    (table) => getValue(incrementKeys, table),
    [incrementKeys],
  );

  const hasEmptyPrimaryKey = useCallback(
    (tables) =>
      tables.some(
        ({ value }) =>
          getQueryMode(value) === "merge" && !getPrimaryKey(value),
      ),
    [getQueryMode, getPrimaryKey],
  );

  const hasEmptyIncrementKey = useCallback(
    (tables) =>
      tables.some(
        ({ value }) =>
          ["append", "merge"].includes(getQueryMode(value)) &&
          !getIncrementKey(value),
      ),
    [getQueryMode, getIncrementKey],
  );

  const getTableConfigurations = useCallback(
    (tables) =>
      tables.map(({ value, title, schema, schemaTitle }) => {
        const queryMode = getQueryMode(value);
        return {
          tableName: value,
          tableTitle: title,
          schema,
          schemaTitle: schemaTitle || schema,
          queryMode,
          primaryKey:
            queryMode === "merge" ? getPrimaryKey(value) : "",
          incrementKey:
            ["append", "merge"].includes(queryMode)
              ? getIncrementKey(value)
              : "",
        };
      }),
    [getQueryMode, getPrimaryKey, getIncrementKey],
  );

  return {
    queryModes,
    primaryKeys,
    incrementKeys,
    handleQueryModeChange,
    handlePrimaryKeyChange,
    handleIncrementKeyChange,
    getQueryMode,
    getPrimaryKey,
    getIncrementKey,
    hasEmptyPrimaryKey,
    hasEmptyIncrementKey,
    getTableConfigurations,
    setQueryModes,
    setPrimaryKeys,
    setIncrementKeys,
  };
};

export default useTableConfiguration;