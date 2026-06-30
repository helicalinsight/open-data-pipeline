import { Button, Drawer, Space, Table, Tag, Tooltip } from "antd";
import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { PlusOutlined } from "@ant-design/icons";
import { InfoCircleOutlined } from "@ant-design/icons";
import DataBaseModule from "../../../../database-module";
import { useSelector } from "react-redux";

const ConnectionMapping = ({
  openDbDrawer,
  setOpenDbDrawer,
  mappedData,
  setMappedData,
  dataSource,
  setDataSource,
}) => {
  const [open, setOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );
  const isScheduleEditMode = useSelector(
    (state) => state?.jobSchedule?.isScheduleEditMode
  );
  const datasources = useSelector((state) => state.database.datasources);

  const getDisplayName = (driver) => {
    const matchingDatasource = datasources.find(ds => ds.driver === driver);
    return matchingDatasource ? matchingDatasource.name : driver;
  };

  useEffect(() => {
    if (
      isScheduleEditMode &&
      jobListDetails?.job_details?.replace_connections
    ) {
      setMappedData(jobListDetails.job_details.replace_connections);
    }
  }, [isScheduleEditMode, jobListDetails]);

  const editModeDataSource = isScheduleEditMode
    ? Object.entries(
        jobListDetails?.job_details?.replace_connections || {}
      ).map(([key, item]) => ({
        key: key,
        fileName: item.connectionName,
        id: key,
        databaseAlias: getDisplayName(item.connectionType), // Use display name here
        connection_type: getDisplayName(item.connectionType), // And here
      }))
    : [];

  const combinedDataSource = isScheduleEditMode
    ? [
        ...editModeDataSource,
        ...dataSource.filter(
          (item) =>
            !editModeDataSource.some((editItem) => editItem.id === item.id)
        ),
      ]
    : dataSource;

  const getConnectionId = (record) => {
    const key = selectedItem?.id || "";
    const recordId = record?._id;
    const connectionType = record.driver || record.connection_type;
    const displayName = getDisplayName(connectionType);

    if (key) {
      setMappedData((prev) => {
        return {
          ...prev,
          [key]: {
            connectionId: recordId,
            connectionName: record.alias,
            connectionType: connectionType,
          },
        };
      });

      setDataSource((prevData) => {
        const updatedData = prevData.map((eachData) => {
          if (eachData.key === key) {
            return {
              ...eachData,
              mappedName: connectionType === "flat_files" ? record.alias : displayName,
              databaseAlias: displayName,
              connection_type: displayName
            };
          }
          return eachData;
        });
        return updatedData;
      });
    } else {
      setMappedData((prev) => {
        return {
          ...prev,
          [uuidv4()]: {
            connectionId: recordId,
            connectionName: record.alias,
            connectionType: connectionType,
          },
        };
      });

      const obj = {
        key: recordId,
        fileName: record.alias,
        id: recordId,
        databaseAlias: displayName,
        connection_type: displayName
      };
      setDataSource((prev) => [...(prev || []), obj]);
    }
  };

  const removeMapping = (id) => {
    setMappedData((prev) => {
      const mapData = { ...prev };
      delete mapData[id];
      return mapData;
    });

    setDataSource((prevData) => {
      const updatedData = prevData.map((eachData) => {
        if (eachData.key === id) {
          delete eachData["mappedName"];
        }
        return eachData;
      });
      return updatedData;
    });
  };

  const columns = [
    {
      title: "Connection Type",
      dataIndex: "connection_type",
      key: "connection_type",
      render: (_, record) => {
        return (
          <Space>
            <span>{record.connection_type || record.databaseAlias}</span>
          </Space>
        );
      },
    },
    {
      title: "Connection Name",
      dataIndex: "connectionName",
      key: "connectionName",
      render: (_, record) => {
        return (
          <Space>
            <span>{record.fileName}</span>
          </Space>
        );
      },
    },
    {
      title: isScheduleEditMode ? "Details" : "Update Connection",
      render: (record) => {
        const connectionData = mappedData[record.id];
        const showTag =
          connectionData || (mappedData[record.id] && record?.mappedName);
        const tagContent = connectionData?.connectionName || record?.mappedName;
        const shouldShowTag =
          showTag &&
          (isScheduleEditMode || (mappedData[record.id] && record?.mappedName));

        return (
          <Space>
            <Tooltip
              title={`Connection Id : ${record?.id}`}
              overlayClassName="custom-tooltip"
            >
              <InfoCircleOutlined className="info-icon-font connection" />
            </Tooltip>
            <>
              <Button
                className="update-btn"
                onClick={() => {
                  setSelectedItem(record);
                  setOpen(true);
                }}
                data-testid={`update-conn-button-${record.id}`}
              >
                Update
              </Button>
              {shouldShowTag && (
                <Tag
                  color="#87d068"
                  closable
                  onClose={() => removeMapping(record.id)}
                  data-testid="remove-mapping-button"
                >
                  {tagContent}
                </Tag>
              )}{" "}
            </>
          </Space>
        );
      },
    },
  ];

  return (
    <Drawer
      open={openDbDrawer}
      onClose={() => setOpenDbDrawer(false)}
      size="large"
      destroyOnClose={true}
      title="Connection Mapping"
    >
      <Space direction="vertical" align="end" className="w-100 mb-10">
        <Button
          onClick={() => {
            setSelectedItem({});
            setOpen(true);
          }}
          type="primary"
          icon={<PlusOutlined />}
          data-testid="new-connection-button"
        >
          New connection
        </Button>
      </Space>
      <Table
        dataSource={combinedDataSource}
        columns={columns}
        pagination={false}
        size="small"
      />
      <DataBaseModule
        getConnectionId={getConnectionId}
        openDbModal={open}
        setOpenDbModal={setOpen}
        haveLoad={true}
        mode="schedule"
        selectedItem={selectedItem}
      />
    </Drawer>
  );
};

export default ConnectionMapping;