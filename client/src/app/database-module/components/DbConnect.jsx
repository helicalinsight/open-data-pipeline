import { useState, useEffect } from "react";
import { Card, Tabs } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { DbForms } from "./DbForms";
import { FlatFiles } from "./FlatFiles";
import SavedDbConnections from "./SavedDbConnections";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import { setEditConnection } from "../../../store/actions/databaseActions";
import { getSavedConnections } from "../../../apis/databaseService";
import CustomMessage from "../../settings-module/CustomMessage";
import {
  setSavedConnections,
  setSavedConnectionsApiStatus,
} from "../../../store/actions/databaseActions";
const DbConnect = (props) => {
  const { formData, setFormData, current, setCurrent } = props;
  const [activeTab, setActiveTab] = useState("1");
  const [isEdit, setIsEdit] = useState(false);
  const selectedDatasource = useSelector(
    (store) => store.database.selectedDatasource
  );
  const editConnection = useSelector((store) => store.database.editConnection);
  const isFlatFile = selectedDatasource?.driver === "flat_files";
  const dispatch = useDispatch();
  const [savedList, setsavedList] = useState([]);
  const messageData = useSelector((store) => store?.settings?.messageData);

 
  useEffect(() => {
    if (selectedDatasource?.driver) {
      getData();
    }
  }, [selectedDatasource?.driver]);

  const getData = () => {
    return new Promise((resolve) => {
      if (!selectedDatasource || !selectedDatasource.driver) {
        resolve(undefined);
        return;
      }
      getSavedConnections({
        query: selectedDatasource.driver,
        onSuccess: (response) => {
          if (response?.databases) {
            setsavedList(response);
          }
          dispatch(setSavedConnectionsApiStatus("SUCCESS"));
          resolve(undefined);
        },
        onError: (error) => {
          resolve(undefined);
        },
      });
    });
  };

  const items = [
    {
      key: "1",
      label: "Create",
      children: (
        <DbForms
          formData={formData}
          setFormData={setFormData}
          setActiveTab={setActiveTab}
          activeTab={activeTab}
          isEdit={isEdit}
          getData={getData}
        />
      ),
    },
    {
      key: "2",
      label: "Saved Connections",
      children: (
        <SavedDbConnections
          setActiveTab={setActiveTab}
          setIsEdit={setIsEdit}
          savedList={savedList}
          getData={getData}
        />
      ),
    },
  ];

  const onTabChange = (key) => {
    setActiveTab(key);
    if (key === "2") {
      setIsEdit(false);
      if (Object.keys(editConnection).length > 0) {
        dispatch(setEditConnection({}));
      }
    }
  };

  return (
    <div
    // style={{
    //   margin: "10px",
    //   boxShadow: "rgba(99, 99, 99, 0.2) 0px 2px 8px 0px",
    // }}
    // className="h-100"
    >
      {messageData && (
        <div style={{ margin: "15px" }}>
          <CustomMessage
            type={messageData.type}
            message={messageData.message}
          />
        </div>
      )}
      <div
        className="forms-card-container w-100 h-100"
        size="small"
        bordered={false}
      >
        {isFlatFile ? (
          <FlatFiles setCurrent={setCurrent} current={current} />
        ) : (
          <div
            style={{
              padding: "10px",
              marginTop: "-10px",
            }}
            data-testid="create-connection"
          >
            <Tabs
              style={{ marginLeft: "5px" }}
              defaultActiveKey="1"
              items={items}
              activeKey={activeTab}
              onChange={onTabChange}
              data-testid="change-tab-id"
              tabBarExtraContent={{
                right: (
                  <div style={{ display: "flex", alignItems: "center" }}>
                    <CustomIcon name={selectedDatasource?.name} />
                  </div>
                ),
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default DbConnect;
