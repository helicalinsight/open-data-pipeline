import { useEffect, useState } from "react";
import { Checkbox, Col, Input, Row, Space, Table } from "antd";
import { fetchColumns } from "../../../apis/databaseService";
import { useDispatch, useSelector } from "react-redux";
import { setTableColumns } from "../../../store/actions/databaseActions";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { sortByName } from "../../../utils/appUtils";
const { Column } = Table;

const AdvancedOptions = (props) => {
  const {
    tables,
    isCsvFile,
    selectedConnection,
    selectedCols,
    setSelectedCols,
  } = props;
  const dispatch = useDispatch();
  const [showData, setShowData] = useState(false);
  const [dataSource, setDataSource] = useState([]);
  const [expandedRowKeys, setExpandedRowKeys] = useState([]);
  const tableColumns = useSelector((state) => state.database.tableColumns);
  const [searchText, setSearchText] = useState("");
  const handleClick = () => {
    setShowData(true);
  };

  useEffect(() => {
    const tableValues = tables.map(({ value }) => value);
    setExpandedRowKeys((prev) =>
      prev.filter((key) => tableValues.includes(key))
    );
    setDataSource((prev) => {
      const updated = [];
      prev.forEach((data) => {
        if (tableValues.includes(data.key)) {
          updated.push(data);
        }
      });

      if (tables.length > prev.length) {
        const newTable = tables[tables.length - 1];
        updated.push({
          key: newTable.value,
          name: newTable.name,
          type: "table",
          children: [],
        });
      }

      return sortByName(updated);
    });
    setSelectedCols((prev) => {
      const updated = {};
      tables.forEach(({ value }) => {
        if (prev[value]) {
          updated[value] = prev[value];
        } else {
          updated[value] = [];
        }
      });
      return updated;
    });
  }, [tables]);

  const updateDataSource = (key, cols) => {
    setDataSource((prev) => {
      const newData = prev.map((data) => {
        if (key === data.key) {
          return { ...data, children: sortByName(cols) };
        }
        return data;
      });
      return sortByName(newData);
    });
  };

  const getColumns = (key) => {
    if (tableColumns[key]) {
      updateDataSource(key, tableColumns[key]);
      return;
    }

    fetchColumns({
      payload: {
        source: selectedConnection.source,
        connection_id: selectedConnection.connection_id,
        catalog: isCsvFile ? null : key,
      },
      onSuccess: (res) => {
        if (res.success) {
          setExpandedRowKeys((prev) => [...prev, key]);
          const updated = res?.columns?.map((col) => {
            return {
              key: `${key} ${col}`,
              name: col,
              parent: key,
            };
          });
          const payload = {
            table: key,
            cols: updated,
          };
          dispatch(setTableColumns(payload));
          updateDataSource(key, updated);
        }
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
      },
    });
  };

  const handleColSelect = (record) => {
    const { parent, name } = record;
    setSelectedCols((prev) => {
      const newMap = { ...prev };
      if (newMap[parent]) {
        let data = newMap[parent];
        if (data.includes(name)) {
          const filterData = data.filter((d) => d !== name);
          data = filterData;
        } else {
          data.push(name);
        }
        newMap[parent] = data;
      } else {
        newMap[parent] = [name];
      }
      return newMap;
    });
  };

  const handleSelectAll = (tableKey, checked) => {
    setSelectedCols((prev) => {
      const updated = { ...prev };
      if (checked) {
        const table = dataSource.find((t) => t.key === tableKey);
        const allColumns = table?.children.map((col) => col.name) || [];
        updated[tableKey] = allColumns;
      } else {
        updated[tableKey] = [];
      }
      return updated;
    });
  };

  const onExpand = (expanded, record) => {
    if (!expanded) {
      setExpandedRowKeys((prev) => prev.filter((row) => row !== record.key));
    } else {
      setExpandedRowKeys((prev) => [...prev, record.key]);
      getColumns(record.key);
    }
  };
  const filteredDataSource = dataSource.map((table) => {
    const filteredChildren = table.children.filter((column) =>
      column.name.toLowerCase().includes(searchText.toLowerCase())
    );
    return { ...table, children: filteredChildren };
  });
  return (
    <Row className="justifyCenter advanced-config-container">
      <Col span={12}>
        <div
          onClick={handleClick}
          className="cursor-pointer"
          data-testid="advanced-button"
          style={{ fontSize: "10px" }}
        >
          Select columns
        </div>
        {showData && (
          <>
            {expandedRowKeys.length > 0 && (
              <Input
                className="search-columns"
                placeholder="Search Column Names"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
              />
            )}
            <Table
              className="select-columns"
              expandable={{
                indentSize: 2,
                rowExpandable: () => true,
                onExpand,
                expandedRowKeys,
                // onExpandedRowsChange: (...args) => console.log(args),
              }}
              onRow={(record, rowIndex) => {
                return {
                  onClick: (event) => {
                    if (record.type === "table") return;
                    handleColSelect(record);
                  }, // click row
                };
              }}
              tableLayout="auto"
              virtual={false}
              pagination={false}
              dataSource={sortByName(filteredDataSource)}
              scroll={{
                y: 200,
              }}
            >
              <Column
                render={(text, record) => {
                  if (record.type === "table") {
                    const allSelected =
                      selectedCols[record.key]?.length ===
                        record.children.length && record.children.length > 0;
                    const indeterminate =
                      !allSelected && selectedCols[record.key]?.length > 0;
                    return (
                      <Space>
                        {expandedRowKeys.includes(record.key) && (
                          <Checkbox
                            className="col-font"
                            checked={allSelected}
                            indeterminate={indeterminate}
                            onChange={(e) =>
                              handleSelectAll(record.key, e.target.checked)
                            }
                          >
                           {record.name}
                          </Checkbox>
                        )}
                        {!expandedRowKeys.includes(record.key) && (
                          <span>{record.name}</span>
                        )}
                      </Space>
                    );
                  }
                  const checked =
                    selectedCols[record?.parent]?.includes(record.name) ||
                    false;
                  return (
                    <Checkbox checked={checked} className="col-font">
                      {record.name}
                    </Checkbox>
                  );
                }}
              />
            </Table>
          </>
        )}
      </Col>
    </Row>
  );
};

export default AdvancedOptions;
