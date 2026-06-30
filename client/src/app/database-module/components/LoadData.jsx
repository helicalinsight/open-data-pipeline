import { Button, Card, Input, Space } from "antd";
import SavedDbConnections from "./SavedDbConnections";
import LoadForm from "./LoadForm";
import { useState } from "react";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import { useSelector } from "react-redux";
import CustomMessage from "../../settings-module/CustomMessage";


const LoadData = (props) => {
  const [searchTerm, setSearchTerm] = useState("");

  const selectedDatasource = useSelector(
    (store) => store.database.selectedDatasource
  );
  const isConnected = useSelector((store) => store.database.isConnected);
  const selectedConnection = useSelector(
    (store) => store.database.selectedConnection
  );
  const messageData = useSelector((store) => store?.settings?.messageData);
  const renderContent = () => {
    if (selectedConnection && isConnected) {
      return <LoadForm {...props} selectedConnection={selectedConnection} />;
    }
    return (
      <SavedDbConnections
        {...props}
        module="load"
        selectedConnection={selectedConnection}
        searchTerm={searchTerm}
      />
    );
  };

  return (
    <div className="load-container flexColumn w-100">
      <div>
        {messageData && (
          <div style={{ margin: "15px" }}>
            <CustomMessage
              type={messageData.type}
              message={messageData.message}
            />
          </div>
        )}
        <div className="load-header-continer dFlex justifyBetween alignCenter margin-left">
          <Space>
            <div className="datasource-img" data-testid="datasource-img-id">
              <CustomIcon name={selectedDatasource.name} />
            </div>
            <span
              className="selected-db-header"
              data-testid="datasource-name-id"
            >
              {selectedDatasource.name}
            </span>
          </Space>
          {!(selectedConnection && isConnected) && (
            <Input
              style={{ width: "200px", right: "15px" }}
              placeholder="Search name"
              onChange={(e) => setSearchTerm(e.target.value)}
              allowClear
            />
          )}
        </div>
        <div className="table-container">{renderContent()}</div>
      </div>
    </div>
  );
};

export default LoadData;
