import {
  Skeleton,
  Table,
  Checkbox,
  Popover,
  Button,
  Tooltip,
  Input,
} from "antd";
import { ADSpace } from "../../../../components";
import { getRowClassName } from "../../utils";
import { useEffect, useState, useRef, useCallback } from "react";
import { CloseOutlined, SettingOutlined } from "@ant-design/icons";
import { useSelector, useDispatch } from "react-redux";
import { setOpenInfo } from "../../../../store/actions/chatAction";
import Editor from "@monaco-editor/react";

const PreviewTable = (props) => {
  const dispatch = useDispatch();
  const { previewTableData, loading, paginationData, currentPage } = props;
  const [selectedCellData, setSelectedCellData] = useState(null);
  const openInfo = useSelector((state) => state.chat.openInfo);
  const startIndex = (currentPage - 1) * paginationData?.limit_by;
  const endIndex = startIndex + paginationData?.limit_by;
  const [dataSource, setDataSource] = useState([]);
  const [checkedList, setCheckedList] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [filteredColumns, setFilteredColumns] = useState([]);
  const [tempCheckedList, setTempCheckedList] = useState([]);
  const [visibleColumns, setVisibleColumns] = useState([]);
  const [noMatchesFound, setNoMatchesFound] = useState(false);
  const [popoverVisible, setPopoverVisible] = useState(false);
  const editorRef = useRef(null);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monaco.editor.defineTheme("custom-whitespace", {
      base: "vs",
      inherit: true,
      rules: [
        {
          token: "whitespace",
          foreground: "FF0000",
          fontStyle: "bold",
        },
      ],
      colors: {
        "editorWhitespace.foreground": "#FF0000",
      },
    });
    monaco.editor.setTheme("custom-whitespace");
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      schemas: [],
      enableSchemaRequest: true,
    });
  };

  const handleCellClick = useCallback((col, record) => {
    setSelectedCellData({
      columnKey: col.key,
      value: record[col.dataIndex],
      dataType: col.dataType,
    });
    dispatch(setOpenInfo(true));
  }, [dispatch]);

  useEffect(() => {
    if (previewTableData?.datasource?.data) {
      setDataSource(previewTableData?.datasource?.data);
    }
    if (previewTableData?.columns) {
      const defaultCheckedList = previewTableData?.columns?.map(
        (col) => col.key
      );
      setCheckedList(defaultCheckedList);
      setFilteredColumns(previewTableData?.columns);
      setTempCheckedList(defaultCheckedList);

      const columnsWithClick = previewTableData.columns.map((col) => ({
        ...col,
        onCell: (record) => ({
          onClick: () => handleCellClick(col, record),
          style: { cursor: "pointer" },
        }),
      }));
      setVisibleColumns(columnsWithClick);
    }
  }, [previewTableData?.datasource?.data, previewTableData?.columns, handleCellClick]);

  const handleTableChange = (pagination, filters, sorter) => {
    if (sorter) {
      const sortedData = [...dataSource].sort((a, b) => {
        if (sorter.order === "ascend") {
          return a[sorter.field] - b[sorter.field];
        } else {
          return b[sorter.field] - a[sorter.field];
        }
      });
      setDataSource(sortedData);
    }
  };

  const handleCheckboxChange = (columnKey) => {
    const updatedCheckedList = tempCheckedList?.includes(columnKey)
      ? tempCheckedList?.filter((key) => key !== columnKey)
      : [...tempCheckedList, columnKey];
    setTempCheckedList(updatedCheckedList);
  };

  const handleSearchChange = (e) => {
    const value = e?.target?.value;
    setSearchText(value);
    if (value?.trim() === "") {
      setFilteredColumns(previewTableData?.columns || []);
      setNoMatchesFound(false);
      setTempCheckedList(checkedList);
    } else {
      const filtered = previewTableData?.columns?.filter((column) =>
        column?.key?.toLowerCase()?.includes(value?.toLowerCase())
      );
      setFilteredColumns(filtered);
      setNoMatchesFound(filtered?.length === 0);
      const filteredKeys = filtered?.map((col) => col?.key);
      setTempCheckedList((prev) =>
        prev?.filter((key) => filteredKeys?.includes(key))
      );
    }
  };

  const handleApplyChanges = () => {
    setCheckedList(tempCheckedList);
    const updatedVisibleColumns = previewTableData.columns
      .filter((col) => tempCheckedList.includes(col.key))
      .map((col) => ({
        ...col,
        onCell: (record) => ({
          onClick: () => handleCellClick(col, record),
          style: { cursor: "pointer" },
        }),
      }));
    setVisibleColumns(updatedVisibleColumns);
    setFilteredColumns(previewTableData?.columns);
    setSearchText("");
    setPopoverVisible(false);
  };

  const handleSelectAllChange = (e) => {
    if (e?.target?.checked) {
      const allColumnKeys = filteredColumns?.map((col) => col?.key);
      setTempCheckedList(allColumnKeys);
    } else {
      setTempCheckedList([]);
    }
  };

  
  const popoverContent = (
    <div>
      <div className="checkbox-list">
        <Input
          placeholder="Search column"
          value={searchText}
          onChange={handleSearchChange}
          className="column-search-input"
          allowClear
        />
        {noMatchesFound && <div className="no-matches">No matches found</div>}
        {!noMatchesFound && (
          <div className="select-all-box" style={{ fontWeight: "bold" }}>
            <Checkbox
              indeterminate={
                tempCheckedList?.length > 0 &&
                tempCheckedList?.length < filteredColumns?.length
              }
              checked={tempCheckedList?.length === filteredColumns?.length}
              onChange={handleSelectAllChange}
            >
              Select All
            </Checkbox>
          </div>
        )}
        {filteredColumns?.map((column) => (
          <div key={column.key}>
            <Checkbox
              checked={tempCheckedList?.includes(column?.key)}
              onChange={() => handleCheckboxChange(column?.key)}
            >
              {column.key}
            </Checkbox>
          </div>
        ))}
      </div>
      {!noMatchesFound && (
        <Button type="primary" onClick={handleApplyChanges} className="ok-btn">
          OK
        </Button>
      )}
    </div>
  );

  const showTable =
    !loading && filteredColumns?.length > 0 && checkedList?.length > 0;

  const editorValue =
    selectedCellData?.value === null
      ? "null"
      : selectedCellData?.value === 0 || selectedCellData?.value === false
      ? selectedCellData.value.toString()
      : selectedCellData?.value
      ? typeof selectedCellData.value === "object"
        ? JSON.stringify(selectedCellData.value, null, 2)
        : selectedCellData.value.toString()
      : "";
      
  const editorLanguage =
    selectedCellData?.value === null ||
    typeof selectedCellData?.value === "object" ||
    (typeof selectedCellData?.value === "string" &&
      (selectedCellData?.value.startsWith("{") ||
        selectedCellData?.value.startsWith("[")))
      ? "json"
      : "plaintext";

  return (
    <ADSpace
      stack="vertical"
      className="preview-table-container overflowHidden"
      style={{
        fontSize: "10px",
      }}
    >
      <ADSpace className="preview-title preview-container">
        <ADSpace className="data-preview-title">Data Preview</ADSpace>
        <Tooltip title="Column Settings">
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            <Popover
              content={popoverContent}
              trigger="click"
              overlayClassName="custom-popover"
              visible={popoverVisible}
              onVisibleChange={setPopoverVisible}
            >
              <SettingOutlined
                className="settings-icon"
                aria-label="Column settings"
              />
            </Popover>
          </div>
        </Tooltip>
      </ADSpace>
      <div className="tablePreviewContainer">
        <div
          className={`tableMainSection ${openInfo ? "expanded" : "fullWidth"}`}
        >
          {loading ? (
            <div className="skeletonLoading" data-testid="skeleton-element">
              <Skeleton active size="small" paragraph={{ rows: 10 }} />
            </div>
          ) : showTable ? (
            <div className="preview-table-main">
              <Table
                data-testid="preview-table-id"
                showSorterTooltip={false}
                dataSource={dataSource}
                columns={visibleColumns}
                rowClassName={getRowClassName}
                pagination={false}
                onChange={handleTableChange}
              />
            </div>
          ) : (
            <div className="noDataMessage">No data</div>
          )}
        </div>
        {openInfo && (
          <div
            className="sidePanel"
            style={{
              width: "400px",
              height: "100%",
              display: "flex",
              flexDirection: "column",
              borderLeft: "1px solid #d9d9d9",
            }}
          >
            <div
              className="panelHeader"
              style={{
                height: "29px",
                padding: "12px",
                borderBottom: "1px solid #d9d9d9",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <span className="columnTitle">
                  {selectedCellData?.columnKey}
                </span>
                <span className="dataTypeLabel">
                  ({selectedCellData?.dataType || "unknown"})
                </span>
              </div>
              <Tooltip title="Close" overlayClassName="custom-tooltip">
                <CloseOutlined
                  data-testid="cancel-button"
                  style={{ fontSize: "10px" }}
                  onClick={() => dispatch(setOpenInfo(false))}
                />
              </Tooltip>
            </div>
            <div
              className="panelContent cellData"
              style={{
                flex: 1,
                overflow: "hidden",
                padding: "0px",
              }}
            >
              <Editor
                className="custom-monaco-editor"
                height="100%"
                language={editorLanguage}
                value={editorValue}
                options={{
                  readOnly: true,
                  scrollBeyondLastLine: false,
                  fontSize: 10,
                  lineHeight: 20,
                  wordWrap: "on",
                  automaticLayout: true,
                  renderWhitespace: "all",
                  renderControlCharacters: true,
                  whitespace: {
                    render: "all",
                    renderEmpty: true,
                    renderSpace: "all",
                    renderTab: "all",
                    renderLineTerminator: "all",
                  },
                  fontLigatures: false,
                  letterSpacing: 2.9,
                }}
                onMount={handleEditorDidMount}
              />
            </div>
          </div>
        )}
      </div>
    </ADSpace>
  );
};

export default PreviewTable;