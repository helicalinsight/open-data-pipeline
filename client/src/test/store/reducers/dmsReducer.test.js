import actionsTypes from "../../../store/actions/actionTypes";
import { dmsReducer } from "../../../store/reducers";
const {
  SET_PIPELINE_MODE,
  SET_SELECTED_SOURCE_TABLE,
  SET_QUERY_MODE,
  SET_PRIMARY_KEY,
  SET_INCREMENT_KEY,
  SET_CUSTOM_SQL,
  SET_DESTINATION_SCHEMA,
  SET_DMS_SELECTED_CHAT,
  DMS_STEPS,
  SET_DMS_JOBS,
  SET_SELECTED_SOURCE_TYPE_FOR_DRAWER,
  SET_SELECTED_DESTINATION_TYPE_FOR_DRAWER,
  SET_PIPELINE_MODE_SOURCE_AND_DESTINATION_TYPES,
  SET_SOURCE_TYPE_ERROR,
  SET_DESTINATION_TYPE_ERROR,
  SET_TARGET_TABLE_NAME,
  SET_TARGET_SCHEMA_NAME,
  SET_DMS_LOG_STATUS
} = actionsTypes.dms;

describe("dmsReducer", () => {
  const initialState = {
    selectedPipelineMode: "",
    selectedSourceTable: [],
    queryMode: "replace",
    primaryKey: "",
    incrementKey:"",
    customSql: "",
    selectedServiceType: null,
    dmsJobs: {},
    step: 0,
    selectedDmsChat: {},
    selectedSourceTypeForDrawer: null,
    selectedDestinationTypeForDrawer: null,
    pipelineModeSourceType: null,
    pipelineModeDestinationType: null,
    sourceTypeError: "",
    destinationTypeError: "",
    targetTableName: "",
    targetSchemaName: "public",
    sourceConnectionId: "",
    destinationConnectionId: "",
    selectedDestinationTable: [],
    dmsProgressDetails: {},
    dmsLogValue: "",
    dmsStatus: "",
    dmsRunHistory: {},
  };

  it("should return the initial state", () => {
    expect(dmsReducer(undefined, {})).toEqual(initialState);
  });

  describe("SET_PIPELINE_MODE", () => {
    it("should handle SET_PIPELINE_MODE with string value", () => {
      const action = {
        type: SET_PIPELINE_MODE,
        payload: "full-load",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedPipelineMode: "full-load",
      });
    });

    it("should handle SET_PIPELINE_MODE with empty string", () => {
      const action = {
        type: SET_PIPELINE_MODE,
        payload: "",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedPipelineMode: "",
      });
    });

    it("should handle SET_PIPELINE_MODE with complex mode", () => {
      const action = {
        type: SET_PIPELINE_MODE,
        payload: "cdc-full-load",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedPipelineMode: "cdc-full-load",
      });
    });

    it("should replace existing pipeline mode", () => {
      const existingState = {
        ...initialState,
        selectedPipelineMode: "old-mode",
      };
      const action = {
        type: SET_PIPELINE_MODE,
        payload: "new-mode",
      };
      expect(dmsReducer(existingState, action)).toEqual({
        ...existingState,
        selectedPipelineMode: "new-mode",
      });
    });
  });

  describe("SET_SELECTED_SOURCE_TABLE", () => {
    it("should handle SET_SELECTED_SOURCE_TABLE with string value", () => {
      const action = {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: "table1,table2,table3",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedSourceTable: "table1,table2,table3",
      });
    });

    it("should handle SET_SELECTED_SOURCE_TABLE with empty string", () => {
      const action = {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: "",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedSourceTable: "",
      });
    });

    it("should handle SET_SELECTED_SOURCE_TABLE with JSON string", () => {
      const objects = JSON.stringify([
        { table: "users" },
        { table: "products" },
      ]);
      const action = {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: objects,
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedSourceTable: objects,
      });
    });

    it("should replace existing selected objects", () => {
      const existingState = {
        ...initialState,
        selectedSourceTable: "old-table",
      };
      const action = {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: "new-table1,new-table2",
      };
      expect(dmsReducer(existingState, action)).toEqual({
        ...existingState,
        selectedSourceTable: "new-table1,new-table2",
      });
    });
  });

  describe("SET_QUERY_MODE", () => {
    it("should handle SET_QUERY_MODE with string value", () => {
      const action = {
        type: SET_QUERY_MODE,
        payload: "select",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        queryMode: "select",
      });
    });

    it("should handle SET_QUERY_MODE with insert mode", () => {
      const action = {
        type: SET_QUERY_MODE,
        payload: "insert",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        queryMode: "insert",
      });
    });

    it("should handle SET_QUERY_MODE with update mode", () => {
      const action = {
        type: SET_QUERY_MODE,
        payload: "update",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        queryMode: "update",
      });
    });

    it("should handle SET_QUERY_MODE with upsert mode", () => {
      const action = {
        type: SET_QUERY_MODE,
        payload: "upsert",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        queryMode: "upsert",
      });
    });

    it("should replace existing query mode", () => {
      const existingState = {
        ...initialState,
        queryMode: "old-mode",
      };
      const action = {
        type: SET_QUERY_MODE,
        payload: "new-mode",
      };
      expect(dmsReducer(existingState, action)).toEqual({
        ...existingState,
        queryMode: "new-mode",
      });
    });
  });

  describe("SET_PRIMARY_KEY", () => {
    it("should handle SET_PRIMARY_KEY with string value", () => {
      const action = {
        type: SET_PRIMARY_KEY,
        payload: "id",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        primaryKey: "id",
      });
    });

    it("should handle SET_PRIMARY_KEY with composite key", () => {
      const action = {
        type: SET_PRIMARY_KEY,
        payload: "id,created_at",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        primaryKey: "id,created_at",
      });
    });

    it("should handle SET_PRIMARY_KEY with empty string", () => {
      const action = {
        type: SET_PRIMARY_KEY,
        payload: "",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        primaryKey: "",
      });
    });

    it("should replace existing primary key", () => {
      const existingState = {
        ...initialState,
        primaryKey: "old_key",
      };
      const action = {
        type: SET_PRIMARY_KEY,
        payload: "new_key",
      };
      expect(dmsReducer(existingState, action)).toEqual({
        ...existingState,
        primaryKey: "new_key",
      });
    });
  });

  describe("SET_INCREMENT_KEY", () => {
    it("should handle SET_INCREMENT_KEY with a single string key", () => {
      const action = {
        type: SET_INCREMENT_KEY,
        payload: "updated_at",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        incrementKey: "updated_at",
      });
    });

    it("should handle SET_INCREMENT_KEY with multiple keys as an array", () => {
      const action = {
        type: SET_INCREMENT_KEY,
        payload: ["updated_at", "region"],
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        incrementKey: ["updated_at", "region"],
      });
    });

    it("should handle SET_INCREMENT_KEY with null (no key selected)", () => {
      // scheduleAPI.js now sends null instead of "" when no key is set
      const action = {
        type: SET_INCREMENT_KEY,
        payload: null,
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        incrementKey: null,
      });
    });

    it("should handle SET_INCREMENT_KEY with empty string (legacy empty)", () => {
      const action = {
        type: SET_INCREMENT_KEY,
        payload: "",
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        incrementKey: "",
      });
    });

    it("should replace an existing multi-key array with a single key", () => {
      const existingState = {
        ...initialState,
        incrementKey: ["updated_at", "region"],
      };
      const action = {
        type: SET_INCREMENT_KEY,
        payload: "updated_at",
      };
      expect(dmsReducer(existingState, action)).toEqual({
        ...existingState,
        incrementKey: "updated_at",
      });
    });

    it("should replace an existing single key with a multi-key array", () => {
      const existingState = {
        ...initialState,
        incrementKey: "updated_at",
      };
      const action = {
        type: SET_INCREMENT_KEY,
        payload: ["updated_at", "created_at"],
      };
      expect(dmsReducer(existingState, action)).toEqual({
        ...existingState,
        incrementKey: ["updated_at", "created_at"],
      });
    });

    it("should not affect other state properties when setting increment key", () => {
      const existingState = {
        ...initialState,
        queryMode: "append",
        primaryKey: "id",
        incrementKey: "",
      };
      const action = {
        type: SET_INCREMENT_KEY,
        payload: ["col_a", "col_b"],
      };
      const newState = dmsReducer(existingState, action);
      expect(newState.incrementKey).toEqual(["col_a", "col_b"]);
      expect(newState.queryMode).toBe("append");
      expect(newState.primaryKey).toBe("id");
    });
  });

  describe("State immutability", () => {
    it("should return new state object for valid actions", () => {
      const existingState = {
        selectedPipelineMode: "old-mode",
        selectedSourceTable: "",
        destSelectedObjects: "",
        schemaName: "public",
        queryMode: "",
        primaryKey: "",
      };
      const action = {
        type: SET_PIPELINE_MODE,
        payload: "new-mode",
      };
      const newState = dmsReducer(existingState, action);
      expect(newState).not.toBe(existingState);
      expect(newState.selectedPipelineMode).toBe("new-mode");
      expect(existingState.selectedPipelineMode).toBe("old-mode");
    });
  });

  describe("Multiple state updates", () => {
    it("should handle multiple sequential updates correctly", () => {
      let state = initialState;
      state = dmsReducer(state, {
        type: SET_PIPELINE_MODE,
        payload: "full-load",
      });
      expect(state.selectedPipelineMode).toBe("full-load");
      state = dmsReducer(state, {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: "users,products",
      });
      expect(state.selectedPipelineMode).toBe("full-load");
      expect(state.selectedPipelineMode).toBe("full-load");
      expect(state.selectedSourceTable).toBe("users,products");
      state = dmsReducer(state, {
        type: SET_QUERY_MODE,
        payload: "upsert",
      });
      expect(state.selectedPipelineMode).toBe("full-load");
      expect(state.selectedSourceTable).toBe("users,products");
      expect(state.queryMode).toBe("upsert");
      state = dmsReducer(state, {
        type: SET_PRIMARY_KEY,
        payload: "id",
      });
      expect(state.selectedPipelineMode).toBe("full-load");
      expect(state.selectedSourceTable).toBe("users,products");
      expect(state.queryMode).toBe("upsert");
      expect(state.primaryKey).toBe("id");
    });

    it("should update one property without affecting others", () => {
      const state = {
        selectedPipelineMode: "cdc",
        selectedSourceTable: "table1",
        destSelectedObjects: "table2",
        schemaName: "public",
        queryMode: "insert",
        primaryKey: "id",
      };
      const newState = dmsReducer(state, {
        type: SET_QUERY_MODE,
        payload: "update",
      });
      expect(newState).toEqual({
        selectedPipelineMode: "cdc",
        selectedSourceTable: "table1",
        destSelectedObjects: "table2",
        schemaName: "public",
        queryMode: "update",
        primaryKey: "id",
      });
      expect(state.queryMode).toBe("insert");
    });
  });

  describe("Edge cases", () => {
    it("should handle null payload", () => {
      const action = {
        type: SET_PIPELINE_MODE,
        payload: null,
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedPipelineMode: null,
      });
    });

    it("should handle undefined payload", () => {
      const action = {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: undefined,
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedSourceTable: undefined,
      });
    });

    it("should handle numeric payload", () => {
      const action = {
        type: SET_PRIMARY_KEY,
        payload: 123,
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        primaryKey: 123,
      });
    });

    it("should handle object payload", () => {
      const action = {
        type: SET_SELECTED_SOURCE_TABLE,
        payload: { table: "users", schema: "public" },
      };
      expect(dmsReducer(initialState, action)).toEqual({
        ...initialState,
        selectedSourceTable: { table: "users", schema: "public" },
      });
    });
  });
});
describe("SET_CUSTOM_SQL", () => {
  it("should handle SET_CUSTOM_SQL with simple SQL query", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "SELECT * FROM users",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql: "SELECT * FROM users",
    });
  });

  it("should handle SET_CUSTOM_SQL some complexx SQL query", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload:
        "SELECT u.id, u.name, o.total FROM users u INNER JOIN orders o ON u.id = o.user_id WHERE u.active = true",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql:
        "SELECT u.id, u.name, o.total FROM users u INNER JOIN orders o ON u.id = o.user_id WHERE u.active = true",
    });
  });

  it("should handle SET_CUSTOM_SQL wuth an empty string", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql: "",
    });
  });

  it("should handle SET_CUSTOM_SQL empty INSERT query", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "INSERT INTO target_table SELECT * FROM source_table",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql: "INSERT INTO target_table SELECT * FROM source_table",
    });
  });

  it("should handle SET_CUSTOM_SQL with UPDATE query", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload:
        "UPDATE users SET status = 'inactive' WHERE last_login < '2024-01-01'",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql:
        "UPDATE users SET status = 'inactive' WHERE last_login < '2024-01-01'",
    });
  });

  it("should handle SET_CUSTOM_SQL with JOIN and aggregation", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload:
        "SELECT c.customer_id, c.name, SUM(o.amount) as total_spent FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql:
        "SELECT c.customer_id, c.name, SUM(o.amount) as total_spent FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name",
    });
  });

  it("should replace existing custom SQL", () => {
    const existingState = {
      ...initialState,
      customSql: "SELECT * FROM old_table",
    };
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "SELECT * FROM new_table",
    };
    expect(dmsReducer(existingState, action)).toEqual({
      ...existingState,
      customSql: "SELECT * FROM new_table",
    });
  });

  it("should update custom SQL without affecting other state properties", () => {
    const existingState = {
      selectedPipelineMode: "full-load",
      selectedSourceTable: "users,orders",
      destSelectedObjects: "target_users,target_orders",
      schemaName: "public",
      queryMode: "custom",
      primaryKey: "id",
      customSql: "SELECT * FROM old_view",
    };
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "SELECT * FROM new_view WHERE active = true",
    };
    expect(dmsReducer(existingState, action)).toEqual({
      selectedPipelineMode: "full-load",
      selectedSourceTable: "users,orders",
      destSelectedObjects: "target_users,target_orders",
      schemaName: "public",
      queryMode: "custom",
      primaryKey: "id",
      customSql: "SELECT * FROM new_view WHERE active = true",
    });
  });

  it("should handle SET_CUSTOM_SQL with line breaks and formatting", () => {
    const sql = `SELECT 
        id,
        name,
        email,
        created_at
    FROM users
    WHERE status = 'active'
    ORDER BY created_at DESC`;

    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: sql,
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql: sql,
    });
  });

  it("should handle SET_CUSTOM_SQL with parameterized query", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload:
        "SELECT * FROM products WHERE category = :category AND price > :min_price",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql:
        "SELECT * FROM products WHERE category = :category AND price > :min_price",
    });
  });

  it("should handle SET_CUSTOM_SQL with CTE (Common Table Expression)", () => {
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload:
        "WITH recent_orders AS (SELECT * FROM orders WHERE order_date > CURRENT_DATE - INTERVAL '30 days') SELECT * FROM recent_orders",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      customSql:
        "WITH recent_orders AS (SELECT * FROM orders WHERE order_date > CURRENT_DATE - INTERVAL '30 days') SELECT * FROM recent_orders",
    });
  });

  it("should handle SET_CUSTOM_SQL when queryMode is custom", () => {
    const existingState = {
      ...initialState,
      queryMode: "custom",
    };
    const action = {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "SELECT * FROM custom_table",
    };
    expect(dmsReducer(existingState, action)).toEqual({
      ...existingState,
      customSql: "SELECT * FROM custom_table",
    });
  });
});

const initialState = {
  selectedPipelineMode: "",
  selectedSourceTable: "",
  destSelectedObjects: "",
  schemaName: "public",
  queryMode: "replace",
  primaryKey: "",
  customSql: "",
  dmsJobs: {},
};

describe("Multiple state updates", () => {
  it("should handle multiple sequential updates correctly including customSql", () => {
    let state = initialState;
    state = dmsReducer(state, {
      type: actionsTypes.dms.SET_PIPELINE_MODE,
      payload: "full-load",
    });
    expect(state.selectedPipelineMode).toBe("full-load");
    state = dmsReducer(state, {
      type: actionsTypes.dms.SET_SELECTED_SOURCE_TABLE,
      payload: "users,products",
    });
    state = dmsReducer(state, {
      type: actionsTypes.dms.SET_QUERY_MODE,
      payload: "custom",
    });
    expect(state.queryMode).toBe("custom");
    state = dmsReducer(state, {
      type: actionsTypes.dms.SET_CUSTOM_SQL,
      payload: "SELECT * FROM users WHERE active = 1",
    });
    expect(state.customSql).toBe("SELECT * FROM users WHERE active = 1");
    state = dmsReducer(state, {
      type: actionsTypes.dms.SET_PRIMARY_KEY,
      payload: "id",
    });
    expect(state.primaryKey).toBe("id");
  });
    it("should handle SET_DMS_LOG_STATUS", () => {
    const action = {
      type: SET_DMS_LOG_STATUS,
      payload: "loading",
    };
    expect(dmsReducer(initialState, action)).toEqual({
      ...initialState,
      dmsStatus: "loading",
    });
  });
});
