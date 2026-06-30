import React, { useEffect, useState } from "react";
import { Drawer, Breadcrumb } from "antd";
import "./style.scss";
import DbListing from "./components/DbListing";
import DbConnect from "./components/DbConnect";
import LoadData from "./components/LoadData";
import DbStepper from "./components/DbStepper";
import { useDispatch, useSelector } from "react-redux";
import {
  setConnectionsStatus,
  setDataSourceConnectionName,
  setDataSourceNames,
  setSelectedConnection,
  setSelectedDatasourceAction,
  setTestConnectionMessage,
} from "../../store/actions/databaseActions";
import { setHideMessageAction } from "../../store/actions/settingActions";
import { useLocation } from "react-router-dom";
import { chatRoutes } from "../../router/uiRouteConstants";
import { triggerGetDatasources } from "../../apis/commonAPIs";
import handleBackClick from "../../utils/handleClick";

function DataBaseModule({
  setOpenDbModal,
  openDbModal,
  haveLoad,
  mode,
  getConnectionId,
  selectedItem,
  selectedSourceType,
  selectedDestinationType,
}) {
  const location = useLocation();
  const dispatch = useDispatch();
  const [current, setCurrent] = useState(0);
  const [formData, setFormData] = useState();
  const selectedDatasource = useSelector(
    (state) => state.database.selectedDatasource
  );
  const dataSourceName = useSelector((store) => store.database.dataSourceName);
  const testConnectionMessage = useSelector(
    (store) => store.database.testConnectionMessage
  );
  const connectionName = useSelector((store) => store.database.connectionName);

  const editConnection = useSelector((store) => store.database.editConnection);
  const handleClose = () => {
    dispatch(setDataSourceNames(""));
    dispatch(setDataSourceConnectionName(""));
    dispatch(setSelectedConnection(null));
    dispatch(setConnectionsStatus(false));
    dispatch(setTestConnectionMessage(""));
    setCurrent(0);
    setOpenDbModal(false);
    dispatch(setHideMessageAction(false));
    if (selectedDatasource?.driver) {
      dispatch(setSelectedDatasourceAction({}));
    }
  };

  const steps = [
    {
      title: "Choose",
      content: (
        <DbListing
          openDbModal={openDbModal}
          setCurrent={setCurrent}
          current={current}
          mode={mode}
          selectedItem={selectedItem}
          selectedSourceType={selectedSourceType}
          selectedDestinationType={selectedDestinationType}
        />
      ),
      description: "Pick from the available connectors",
    },
    {
      title: haveLoad ? "Load" : "Connect",
      content: haveLoad ? (
        <LoadData
          mode={mode}
          formData={formData}
          getConnectionId={getConnectionId}
          handleClose={handleClose}
        />
      ) : (
        <DbConnect
          current={current}
          setCurrent={setCurrent}
          formData={formData}
          setFormData={setFormData}
        />
      ),
      description: haveLoad ? "Load the data" : "Provide connector credentials",
    },
    {
      title: "Load",
      content: (
        <LoadData
          mode={mode}
          getConnectionId={getConnectionId}
          formData={formData}
          handleClose={handleClose}
        />
      ),
      description: "Load the data",
    },
  ];

  const selectStepElements = haveLoad
    ? [0, 2].map((index) => steps[index])
    : [0, 1].map((index) => steps[index]);

  const items = selectStepElements.map((item) => ({
    key: item.title,
    title: item.title,
    description: item.description,
  }));
  const showCloseButton = (haveLoad && current === 1) || current === 2;

  const renderTitleWithBreadcrumb = () => (
    <div className="breadcrumb-container">
      <Breadcrumb className="breadcrumb-text">
        {!dataSourceName && !connectionName ? (
          <Breadcrumb.Item>
            <span className="hover-underline" style={{}}>
              Connection
            </span>
          </Breadcrumb.Item>
        ) : (
          <>
            <Breadcrumb.Item
              onClick={() => {
                handleBackClick(dispatch, editConnection, setCurrent, current);
                dispatch(setDataSourceNames(""));
                dispatch(setDataSourceConnectionName(""));
                dispatch(setTestConnectionMessage(""));
                dispatch(setSelectedConnection(null));
                dispatch(setConnectionsStatus(false));
              }}
            >
              <span className="hover-underline">Connection</span>
            </Breadcrumb.Item>
            {dataSourceName && !connectionName ? (
              <Breadcrumb.Item
                onClick={() => {
                  dispatch(setConnectionsStatus(false));
                  dispatch(setSelectedConnection(null));
                  dispatch(setDataSourceConnectionName(""));
                  dispatch(setTestConnectionMessage(""));
                }}
              >
                <span className="hover-underline">{dataSourceName}</span>
              </Breadcrumb.Item>
            ) : (
              dataSourceName &&
              connectionName && (
                <>
                  <Breadcrumb.Item
                    onClick={() => {
                      dispatch(setConnectionsStatus(false));
                      dispatch(setSelectedConnection(null));
                      dispatch(setDataSourceConnectionName(""));
                      dispatch(setTestConnectionMessage(""));
                    }}
                  >
                    <span className="hover-underline">{dataSourceName}</span>
                  </Breadcrumb.Item>
                  {selectedDatasource?.driver === "flat_files" ? (
                    <Breadcrumb.Item>
                      <span className="hover-underline">{connectionName}</span>
                    </Breadcrumb.Item>
                  ) : (
                    testConnectionMessage?.length > 0 && (
                      <Breadcrumb.Item>
                        <span className="hover-underline">
                          {connectionName}
                        </span>
                      </Breadcrumb.Item>
                    )
                  )}
                </>
              )
            )}
          </>
        )}
      </Breadcrumb>
    </div>
  );
  useEffect(() => {
    if (openDbModal) {
      dispatch(setHideMessageAction(true));
    }
  }, [openDbModal, dispatch]);

  useEffect(() => {
    if (location?.pathname === chatRoutes?.datasource) {
      triggerGetDatasources(dispatch);
    }
  }, [location.pathname]);

  return (
    <>
      {location?.pathname !== chatRoutes?.datasource ? (
        <Drawer
          title={renderTitleWithBreadcrumb()}
          placement="right"
          onClose={handleClose}
          open={openDbModal}
          size="large"
          width="79%"
          data-testid="db-steps-drawer"
          destroyOnClose={true}
          className="ds-draw"
        >
          <div className="db-connect-wrapper dFlex flexColumn ds-draw">
            <DbStepper
              current={current}
              items={items}
              steps={steps}
              setCurrent={setCurrent}
              showCloseButton={showCloseButton}
            />
          </div>
        </Drawer>
      ) : (
        <div
          className="db-connect-wrapper dFlex flexColumn"
          data-testid="db-stepper-page"
        >
          <DbStepper
            current={current}
            items={items}
            steps={steps}
            setCurrent={setCurrent}
          />
        </div>
      )}
    </>
  );
}

export default DataBaseModule;
