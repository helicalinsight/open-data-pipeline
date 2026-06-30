import { useState, useEffect } from "react";
import {
  Button,
  Form,
  Row,
  Col,
  Result,
  TreeSelect,
  message,
  Skeleton,
} from "antd";
import { v4 as uuidv4 } from "uuid";
import { useLocation, useSearchParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { addNewMessageAction } from "../../../store/actions/messageActions";
import { CheckCircleFilled } from "@ant-design/icons";
import { dataLoads, fecthDbsAndTables } from "../../../apis/databaseService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../apis/commonAPIs";

import AdvancedOptions from "./AdvancedOptions";
import getTimeStamp from "../../../utils/getCurrentTime";
import { setSidebarState } from "../../../store/actions/appActions";
import { prepareS3Payload } from "./utils";
import { isDmsRoute } from "../../../router/uiRouteConstants";
import {  setSelectedSourceTableAction, setSourceConnectionIdAction } from "../../../store/actions/dmsAction";
import { dispatchMessage } from "../../../utils/handleClick";

function LoadForm({ selectedConnection, handleClose }) {
  const dispatch = useDispatch();
  const location = useLocation();
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const [searchParms] = useSearchParams();
  const [dbList, setDbList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dbFetchStatus, setDbFetchStatus] = useState("");
  const [value, setValue] = useState([]);
  const [selectedCols, setSelectedCols] = useState({});
  const chatId = searchParms.get("chat");
  const isFlatFile = selectedConnection?.source === "flat_files";
  const isCsvFile = selectedConnection?.fileType === ".csv";
  const savedConnections = useSelector(
    (state) => state.database.savedConnections
  );
  const selectedDatasource = useSelector(
    (store) => store.database.selectedDatasource
  );
  const connectionName = useSelector((store) => store.database.connectionName);
  const isS3 = selectedDatasource.driver === "s3";
  const isDms = isDmsRoute(location.pathname);
  const loadedFiles =
    useSelector((state) => state.chat.chatList[chatId]?.loadedFiles) ?? [];
  const step = useSelector((state) => state.dms.step);

  useEffect(() => {
    if (isFlatFile && isCsvFile) {
      const updatedData = [];
      savedConnections.forEach((eachConn) => {
        if (selectedConnection.connection_id === eachConn._id) {
          updatedData.push({ value: eachConn._id, name: eachConn.alias });
        }
      });
      setValue(updatedData);
    } else {
      getCatalogs();
    }
  }, []);

  const disableNodesBasedOnAlias = (dbList) => {
    const processNodes = (nodes) => {
      return nodes.map((node) => {
        let children = node.children ? processNodes(node.children) : [];
        if (
          selectedDatasource.driver !== "google_sheets" &&
          selectedDatasource.driver !== "s3" &&
          Array.isArray(node.children) &&
          node.children.length === 0
        ) {
          children = [
            {
              title: "No tables",
              value: `${node.value}-no-tables`,
              disabled: true,
            },
          ];
        }
        let disabled =
          Array.isArray(node.children) && node.children.length === 0
            ? !!node.value
            : node.children && node.children.length;

        if (
          selectedDatasource.driver === "google_sheets" ||
          selectedDatasource.driver === "s3"
        ) {
          disabled = !!node?.children?.length;
        }
        return {
          ...node,
          disabled: disabled,
          children,
        };
      });
    };

    return processNodes(dbList);
  };

  const modifiedTreeData = disableNodesBasedOnAlias(dbList, loadedFiles);
  const sortSchemasAndTables = (dbList) => {
    const sortedDbList = [...dbList]?.sort((a, b) =>
      a.title.localeCompare(b.title)
    );
    const sortedDbListWithChildren = sortedDbList.map((schema) => {
      const sortedChildren = schema.children
        ? [...schema.children]?.sort((a, b) => a.title.localeCompare(b.title))
        : [];
      return {
        ...schema,
        children: sortedChildren,
      };
    });
    return sortedDbListWithChildren;
  };
  if (isDms && step !== 2) {
    dispatch(
      (step === 1 && setSourceConnectionIdAction)(
        selectedConnection?.connection_id,
      ),
    );
  }
  const getCatalogs = () => {
    setDbFetchStatus("fetching");
    const payload = {
      source: selectedConnection?.source,
      connection_id: selectedConnection?.connection_id,
    };
    fecthDbsAndTables({
      onSuccess: (res) => {
        if (res.success) {
          const sortedData = sortSchemasAndTables(res?.dataCatalog);
          setDbList(sortedData);
          setDbFetchStatus("success");
        } else {
          showErrorMsg(res.msg);
          setDbFetchStatus("failed");
        }
      },
      onError: (err) => {
        setDbFetchStatus("failed");
        handleSessionExpiry(dispatch, err);
        showErrorMsg(err.msg);
      },
      payload,
    });
  };

  const showErrorMsg = (msg) => {
    messageApi.open({
      type: "error",
      content: msg || "Failed to load file",
    });
  };

  const handleFinish = (e) => {
     if (isDms && step === 1) {
       const finalValue = isCsvFile
         ? value.map((item) => ({
             name: item.name,
             value: item.name,
           }))
         : value;
  dispatch(setSelectedSourceTableAction(finalValue));
   dispatchMessage(
     dispatch,
     "success",
     "Source Table connected successfully",
     true,
   );
   handleClose();
 }
    let source;
    let payload;
      if (isS3) {
        payload = prepareS3Payload(
          value,
          dbList,
          selectedConnection,
          chatId,
          selectedCols
        );
    } else {
      source = isFlatFile ? "file" : "database";
      payload = [
        {
          source: source,
          details: {
            connection_id: selectedConnection?.connection_id,
            chat_id: chatId,
            type: isFlatFile ? selectedConnection.fileType : "table",
            database_name: selectedDatasource?.driver,
            file_name: isFlatFile ? selectedConnection.alias : "",
            catalog: selectedCols,
          },
        },
      ];
    }

    setLoading(true);
   if(!isDms){
    dataLoads({
      payload,
      onSuccess: (response) => {
        const { success, files_uploaded, files_failed } = response;
        setLoading(false);

        if (!success) {
          showErrorMsg(response.message || "Few Files Failed to load.");
        }
        if (files_failed?.length > 0) {
          files_failed.forEach((msg) => {
            showErrorMsg(msg);
          });
        }
        if (success && files_uploaded?.length) {
          messageApi.open({
            type: "success",
            content: response.message || "Files loaded successfully",
          });

          const chatMessage = {
            isUser: true,
            text: "Initiating database load",
            message_id: uuidv4(),
            time: getTimeStamp(),
          };
          dispatch(addNewMessageAction({ chatId, data: [chatMessage] }));
          triggerPipelineHistory(dispatch, chatId);
          triggerGetInfoAPI(dispatch, chatId, { showPreview: true });
          dispatch(setSidebarState(true));
          handleClose();
        }
      },
      onError: (error) => {
        setLoading(false);
        if (error.message) {
          showErrorMsg(error.message || "Files Failed to load.");
        }

        if (error?.files_failed?.length > 0) {
          error.files_failed.forEach((msg) => {
            showErrorMsg(msg);
          });
        }
        handleSessionExpiry(dispatch, error);
      },
    });
  }
  };
  const onChange = (selectedValues) => {
    if (isDms) {
      // single select
      const updated = selectedValues
        ? [{ name: selectedValues, value: selectedValues }]
        : [];
      setValue(updated);
    } else {
      // multi select
      const updated = selectedValues.map((eachVal) => ({
        name: eachVal,
        value: eachVal,
      }));
      setValue(updated);
    }
  };

  return (
    <>
      {contextHolder}
      <Result
        icon={
          <CheckCircleFilled
            style={{ color: "#52c41a", fontSize: "17px" }}
            className="pulse"
          />
        }
        status="success"
        title={
          <span style={{ fontSize: "14px" }}>
            Successfully connected to{" "}
            {isFlatFile ? selectedConnection.alias : connectionName}!
          </span>
        }
      />
      <Form
        layout="vertical"
        onFinish={handleFinish}
        form={form}
        id="loadData"
        data-testid="load-form"
      >
        <Row className="justifyCenter">
          <Col span={12}>
            <Form.Item
              className="form-font"
              name="catalog"
              rules={[
                {
                  required: isCsvFile ? false : true,
                  message: `Please select atleast one item`,
                },
              ]}
            >
              {dbFetchStatus !== "fetching" || isCsvFile ? (
                <TreeSelect
                  showSearch
                  data-testid="tree-select-load"
                  value={isDms ? value?.[0]?.value : value}
                  treeData={modifiedTreeData}
                  placeholder="Please select"
                  virtual={false}
                  onChange={onChange}
                  style={{ width: "100%" }}
                  disabled={
                    dbFetchStatus === "failed" ? true : isCsvFile ? true : false
                  }
                  dropdownStyle={{
                    maxHeight: 400,
                    minHeight: 200,
                    overflow: "auto",
                  }}
                  allowClear
                  {...(!isDms && {
                    multiple: true,
                    mode:"multiple",
                    maxTagCount:"responsive",
                  })}
                />
              ) : (
                <Skeleton.Button active={true} block={true} />
              )}
            </Form.Item>
          </Col>
        </Row>
        {(value.length > 0 || isCsvFile) && (
          <AdvancedOptions
            tables={value}
            selectedConnection={selectedConnection}
            setSelectedCols={setSelectedCols}
            selectedCols={selectedCols}
            isCsvFile={isCsvFile}
          />
        )}
        <Row gutter={16} className="items-center">
          <Col>
            <Button
              data-testid="load-button"
              type="primary"
              htmlType="submit"
              style={{
                backgroundColor: "rgb(242, 142, 30)",
                color: "#ffffff",
                marginTop: "10px",
              }}
              loading={loading}
            >
             {isDms?"Choose":"Load"} 
            </Button>
          </Col>
        </Row>
      </Form>
    </>
  );
}
export default LoadForm;
