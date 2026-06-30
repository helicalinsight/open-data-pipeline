import React from "react";
import { Typography } from "antd";
import QueryModeSelect from "./QueryModeSelect";

const { Text } = Typography;

const TableConfigRow = ({
  table,
  queryModeValue,
  onQueryModeChange,
  primaryKeyValue = "",
  onPrimaryKeyChange,
  incrementKeyValue = "",
  onIncrementKeyChange,
  queryModes = [],
}) => {
  return (
    <div className="table-row">
      <div className="table-header">
        <Text className="table-name">Selected Table : {table.name.split(".").pop()}</Text>
      </div>

      <div className="config-section">
        <QueryModeSelect
          value={queryModeValue}
          onChange={(value) => onQueryModeChange(table.value, value)}
          primaryKeyValue={primaryKeyValue}
          onPrimaryKeyChange={(value) => onPrimaryKeyChange(table.value, value)}
          incrementKeyValue={incrementKeyValue}
          onIncrementKeyChange={(value) =>
            onIncrementKeyChange(table.value, value)
          }
          queryModes={queryModes}
        />
      </div>
    </div>
  );
};

export default TableConfigRow;