import { Title, Text } from "./preview-data/Title";

export const getTableColumns = (fileData) => {
  let columns = fileData.columns.map((col) => {
    const { name: columnName, dataType } = col;
    let columnData = {
      title: () => <Title columnName={columnName} dataType={dataType} />,
      dataIndex: columnName,
      width: 100,
      key: columnName,
      ellipsis: true,
      onFilter: (value, record) => record.name.indexOf(value) === 0,
      render: (text) => <Text text={String(text)} />,
      dataType
    };
    if (["int64", "float64"].includes(dataType)) {
      columnData.sorter = (a, b) => a[columnName] - b[columnName];
    }
    return columnData;
  });
  return columns;
};

export const convertToTitleCase = (str) =>
  str
    ?.split("_")
    ?.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
