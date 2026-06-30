import {
  Button,
  Col,
  Form,
  Input,
  Row,
  Space,
  Card,
  message,
  Collapse,
  Select,
  Tooltip,
} from "antd";
import { useEffect, useRef, useState } from "react";
import {
  CheckCircleFilled,
  UploadOutlined,
  CloseOutlined,
  InfoCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import {
  saveConnection,
  testConnection,
  updateConnection,
} from "../../../apis/databaseService";
import {
  setFormData,
  setSavedConnections,
  updateSavedConnection,
} from "../../../store/actions/databaseActions";
import { uploadFileApi } from "../../../apis/fileService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { convertPoolingInfo } from "./utils";
import AdvancedPooling from "./AdvancedPooling";
import RenderMarkDown from "./RenderMarkDown";
import {
  getSchemaTooltip,
  notificationText,
} from "../../app-header/components/job-schedule/constants";
import { dispatchMessage } from "../../../utils/handleClick";

export const DbForms = (props) => {
  const { setActiveTab, activeTab, isEdit, getData } = props;
  const dispatch = useDispatch();
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const [showPooling, setShowPooling] = useState(false);
  const [isTestConnSuccess, setIsTestConnSuccess] = useState(false);
  const [filesDetails, setFilesDetails] = useState({});
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [loading, setLoading] = useState(false);
  const [poolingOn, setPoolingOn] = useState("pandas_pooling");
  const [poolingData, setPoolingData] = useState({
    spark_pooling: [],
    pandas_pooling: [],
  }); // In frontend to show data in tables we are in array
  const [finalPoolingInfo, setFinalPoolingInfo] = useState({
    spark_pooling: {},
    pandas_pooling: {},
  }); // Final pooling is the one which we send to backend as an objects
  const selectedDatasource = useSelector(
    (store) => store.database.selectedDatasource
  );
  const editConnection = useSelector((store) => store.database.editConnection);
  const formData = useSelector((store) => store.database.formData);
  const findInitialValues = (name, defaultValue) => {
    return (
      selectedDatasource?.parameters?.basic_auth.find(
        (item) => item.name === name
      )?.default || defaultValue
    );
  };

  const initialFormValues = {
    sourceName: "",
    host: findInitialValues("Host", ""),
    port: findInitialValues("Port", 0),
    username: "",
    password: findInitialValues("Password", ""),
    database: "",
    client_id: "",
    secret: "",
  };

  useEffect(() => {
    if (Object.keys(editConnection).length > 0) {
      const { connection_details } = editConnection || {};
      form.setFieldsValue(connection_details);
    } else {
      form.setFieldsValue(initialFormValues);
    }
    if (editConnection?.connection_details?.connection_pool) {
      const convertedDtaa = convertPoolingInfo(
        "array",
        editConnection?.connection_details?.connection_pool
      );
      setPoolingData(convertedDtaa);
    }
  }, [editConnection]);
  const onSaveUpdate = () => {
    setActiveTab("2");
    setIsTestConnSuccess(false);
    form.resetFields();
    setUploadedFiles({});
    setFilesDetails({});
  };
  const handleFinish = (formData, val, type) => {
    const hasRequiredKeys =
      Array.isArray(val) &&
      val.some(
        (item) =>
          item.configKey === "aod_schema" || item.configKey === "aod_table"
      );
    // Check if finalPoolingInfo has any required keys
    const poolingKeys = ["aod_schema", "aod_table"];
    const finalPoolingHasKeys = ["spark_pooling", "pandas_pooling"].some(
      (poolType) => poolingKeys.some((key) => finalPoolingInfo[poolType]?.[key])
    );

    if (
      selectedDatasource.driver === "oracle" &&
      !hasRequiredKeys &&
      !finalPoolingHasKeys
    ) {
      // messageApi.open({
      //   type: "error",
      //   content: notificationText.warningMessage,
      // });
      dispatchMessage(dispatch, "error", notificationText.warningMessage);
      return;
    }
    let payload = {};
    if (type === "parent") {
      payload = {
        type: "test",
        connector: selectedDatasource.driver,
        details: { ...formData, ...filesDetails },
      };
    } else if (type === "child" && !isEdit) {
      payload = {
        type: "test",
        connector: selectedDatasource.driver,
        details: { ...formData, ...filesDetails },
      };
    } else if (type === "child" && isEdit) {
      payload = {
        type: "test",
        connector: selectedDatasource.driver,
        details: { ...filesDetails },
      };
    }
    if (type === "parent") {
      if (selectedDatasource?.pooling) {
        payload.details.connection_pool = finalPoolingInfo;
      }
    } else {
      const output =
        val.length &&
        val.reduce((acc, item) => {
          acc[item.configKey] = item.configValue;
          return acc;
        }, {});

      const connectionPool =
        val.length > 0
          ? {
              spark_pooling: poolingOn === "spark_pooling" ? output : {},
              pandas_pooling: poolingOn === "pandas_pooling" ? output : {},
            }
          : {
              spark_pooling: {},
              pandas_pooling: {},
            };
      payload.details.connection_pool = connectionPool;
    }
    if (type === "child" && isEdit) {
      payload.details = form.getFieldValue();
    }
    setLoading(true);
    testConnection({
      payload,
      onSuccess: (response) => {
        if (response.success) {
          // messageApi.open({
          //   type: "success",
          //   content: response.msg || "Connection tested successfully",
          // });
          dispatchMessage(
            dispatch,
            "success",
            response.msg || "Connection tested successfully"
          );
          setIsTestConnSuccess(true);
          dispatch(setFormData(payload.details));
        } else {
          // messageApi.open({
          //   type: "error",
          //   content: response.message || "Failed to test the Connection",
          // });
          dispatchMessage(
            dispatch,
            "error",
            response.message || "Failed to test the Connection"
          );
          setIsTestConnSuccess(true);
        }
        setLoading(false);
      },
      onError: (error) => {
        setIsTestConnSuccess(false);
        setLoading(false);
        // messageApi.open({
        //   type: "error",
        //   content: error.message || "Failed to test the Connection",
        // });
        dispatchMessage(
          dispatch,
          "error",
          error.message || "Failed to test the Connection"
        );
        handleSessionExpiry(dispatch, error);
      },
    });
  };
  useEffect(() => {
    if (activeTab === "2") {
      form.resetFields();
      setUploadedFiles({});
      setFilesDetails({});
      setIsTestConnSuccess(false);
    }
  }, [activeTab]);
  useEffect(() => {
    if (activeTab === "1" && !isEdit) {
      form.resetFields();
      setPoolingData({ spark_pooling: [], pandas_pooling: [] });
      setFinalPoolingInfo({ spark_pooling: {}, pandas_pooling: {} });
      setIsTestConnSuccess(false);
    }
  }, [activeTab, !isEdit]);

  useEffect(() => {
    const convertedPooling = convertPoolingInfo("object", poolingData);
    setFinalPoolingInfo(convertedPooling);
  }, [poolingData]);

  const handleFormSubmit = () => {
    let payload = {};
    payload = {
      connection_alias: formData?.sourceName,
      type: selectedDatasource?.driver,
      connection_details: formData || {},
    };
    if (selectedDatasource?.pooling) {
      payload.connection_details.connection_pool = finalPoolingInfo;
    }
    payload = isEdit
      ? { ...payload, connection_id: editConnection?.connection_id }
      : payload;
    isEdit ? handleUpdateConnection(payload) : handleSaveConntion(payload);
    getData?.();
  };

  const handleSaveConntion = (payload) => {
    saveConnection({
      payload,
      onSuccess: (response) => {
        if (response.success) {
          onSaveUpdate();
          const data = [
            {
              _id: response.connection_id,
              alias: payload.connection_alias,
              type: selectedDatasource.driver,
            },
          ];
          dispatch(setSavedConnections({ key: "insert", data }));
          // messageApi.open({
          //   type: "success",
          //   content: response.message || "Connection saved successfully.",
          // });
          dispatchMessage(
            dispatch,
            "success",
            response.message || "Connection saved successfully."
          );
        } else {
          // messageApi.open({
          //   type: "error",
          //   content: response.message || "Failed to save the Connection",
          // });
          dispatchMessage(
            dispatch,
            "error",
            response.message || "Failed to save the Connection"
          );
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        // messageApi.open({
        //   type: "error",
        //   content: error.message || "Failed to save the Connection",
        // });
        dispatchMessage(
          dispatch,
          "error",
          error.message || "Failed to save the Connection"
        );
      },
    });
  };

  const handleUpdateConnection = (payload) => {
    updateConnection({
      payload,
      onSuccess: (response) => {
        if (response.success) {
          onSaveUpdate();
          dispatch(updateSavedConnection(payload));

          // messageApi.open({
          //   type: "success",
          //   content: response.message || "Connection updated successfully.",
          // });
          dispatchMessage(
            dispatch,
            "success",
            response.message || "Connection updated successfully."
          );
        } else {
          // messageApi.open({
          //   type: "error",
          //   content: response.message || "Failed to update the Connection",
          // });
          dispatchMessage(
            dispatch,
            "error",
            response.message || "Failed to update the Connection"
          );
        }
      },
      onError: (error) => {
        handleSessionExpiry(dispatch, error);
        // messageApi.open({
        //   type: "error",
        //   content: error.message || "Failed to update the Connection",
        // });
        dispatchMessage(
          dispatch,
          "error",
          error.message || "Failed to update the Connection"
        );
      },
    });
  };

  const handleChange = (e) => {
    const variable = e.target.dataset.variable;
    const file = e.target.files[0];
    if (
      file &&
      file.type !== "application/json" &&
      !file.name.endsWith(".json")
    ) {
      setUploadedFiles((prev) => ({
        ...prev,
        [variable]: {
          fileName: file.name,
          status: "failed",
        },
      }));
      e.target.value = "";
      return;
    }
    setUploadedFiles((prev) => {
      return {
        ...prev,
        [variable]: {
          fileName: file.name,
          status: "uploading",
        },
      };
    });
    uploadFileApi({
      key: "uploadConfig",
      formdata: { file: file, db_name: selectedDatasource.driver },
      onSuccess: (res) => {
        setFilesDetails((prev) => {
          return {
            ...prev,
            [variable]: res.details,
          };
        });
        setUploadedFiles((prev) => {
          return {
            ...prev,
            [variable]: {
              fileName: file.name,
              status: "success",
            },
          };
        });
      },
      // signal, // to abort API
      progressEvent: (event) => {
        // let progress = Math.floor(event.progress * 100);
      },
      onError: (error) => {
        setUploadedFiles((prev) => {
          return {
            ...prev,
            [variable]: {
              fileName: file.name,
              status: "failed",
            },
          };
        });
        handleSessionExpiry(dispatch, error);
      },
    });

    e.target.value = "";
  };

  const GetFormItem = ({ item }) => {
    const { type, category, variable, name } = item || {};

    const inputRef = useRef();

    if (category === "upload") {
      const { fileName, status } = uploadedFiles[variable] || {};
      return (
        <Col key={name} className={"w-50"} data-testid={variable}>
          <Form.Item label={<span className="form-font">{name}</span>}>
            <>
              <input
                ref={inputRef}
                data-testid="upload-input"
                type="file"
                icon={<UploadOutlined />}
                onChange={handleChange}
                data-variable={variable}
                style={{ display: "none" }}
              />
              <Button
                className="form-font"
                data-testid="upload-button"
                icon={<UploadOutlined />}
                onClick={() => inputRef.current?.click()}
                loading={status === "uploading" ? true : false}
              >
                {variable === "credentials_object" ? "Credentials" : variable}
              </Button>
              {fileName && (
                <Space style={{ fontSize: "12px" }}>
                  {status === "success" ? (
                    <CheckCircleFilled
                      style={{ color: "#52c41a", fontSize: "12px" }}
                    />
                  ) : (
                    <CloseCircleOutlined
                      style={{ color: "#ff4d4f", fontSize: "12px" }}
                    />
                  )}
                  {fileName}
                </Space>
              )}
            </>
          </Form.Item>
        </Col>
      );
    }
    return (
      <Col
        key={name}
        className={variable === "sourceName" ? "w-100" : "w-50"}
        data-testid={variable}
      >
        <Form.Item
          key={variable}
          name={variable}
          // label={[name]}
          label={<span className="form-font">{name}</span>}
          rules={[
            {
              required: true,
              message: `Please enter ${
                variable === "sourceName" ? "Source Name" : name
              }`,
            },
          ]}
          className="custom-form-item"
        >
          {type === "password" ? (
            <Input.Password className="form-font" />
          ) : (
            <Input className="form-font" />
          )}
        </Form.Item>
      </Col>
    );
  };

  const renderAdvancedParameter = () => {
    return Object.keys(selectedDatasource?.advanceParameters).map((key) => {
      const value = selectedDatasource?.advanceParameters[key];
      if (Array.isArray(value) && value.length > 0) {
        return (
          <Row gutter={16}>
            {value.map((ele, index) => (
              <GetFormItem item={ele} key={index} />
            ))}
          </Row>
        );
      }
    });
  };

  const renderForm = () => {
    return (
      <Form
        name="basic"
        layout="vertical"
        onFinish={(formData) => handleFinish(formData, [], "parent")}
        form={form}
        id="connect-data"
        initialValues={initialFormValues}
        data-testid="form"
      >
        <Row gutter={16}>
          <GetFormItem
            item={{
              variable: "sourceName",
              name: (
                <span>
                  Source Name{" "}
                  {isEdit && editConnection?.connection_id && (
                    <Tooltip
                      title={`Connection Id : ${editConnection?.connection_id}`}
                      overlayClassName="custom-tooltip"
                    >
                      <InfoCircleOutlined
                        style={{
                          fontSize: "12px",
                          cursor: "pointer",
                        }}
                      />
                    </Tooltip>
                  )}
                </span>
              ),
            }}
          />
          {selectedDatasource?.parameters?.basic_auth?.map((eachItem) => {
            return <GetFormItem item={eachItem} />;
          })}
        </Row>

        <Row gutter={16}>
          {selectedDatasource?.advanceParameters && (
            <>
              <Collapse
                items={[
                  {
                    key: "1",
                    label: "Advance Parameters",
                    children: renderAdvancedParameter(),
                  },
                ]}
                ghost={true}
              />
            </>
          )}
        </Row>

        <Row gutter={16} className="items-center">
          <Col style={{ margin: "auto" }}>
            <Space
              direction="vertical"
              className="items-center"
              size={1}
              style={{ marginTop: isTestConnSuccess && "-23px" }}
            >
              {isTestConnSuccess ? (
                <CheckCircleFilled
                  style={{ color: "#52c41a", fontSize: "15px" }}
                />
              ) : (
                <Button
                  type="primary"
                  htmlType="submit"
                  key={"test"}
                  loading={loading}
                  style={{
                    backgroundColor: "rgb(242, 142, 30)",
                    color: "#ffffff",
                  }}
                  data-testid="test-button"
                >
                  Test Connection
                </Button>
              )}

              {isTestConnSuccess && (
                <Button
                  key={"Save connection"}
                  onClick={handleFormSubmit}
                  style={{
                    backgroundColor: "rgb(242, 142, 30)",
                    color: "#ffffff",
                  }}
                  data-testid="save-button"
                >
                  {isEdit ? "Update Datasource" : "Save Datasource"}
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Form>
    );
  };

  const togglePooling = () => {
    setShowPooling((prev) => !prev);
  };

  const handleClose = () => {
    togglePooling();
    setPoolingOn("pandas_pooling");
    const convertedPooling = convertPoolingInfo("object", poolingData);
    setFinalPoolingInfo(convertedPooling);
  };

  return (
    <>
      {contextHolder}
      <div className="w-100 h-100 dFlex" style={{ marginTop: "-10px" }}>
        <Card bordered={false} className="w-100 setup-guide-card m-5" hoverable>
          <div
            className={`w-100 dFlex ${
              showPooling ? "justifyBetween" : "justifyEnd"
            }`}
          >
            {showPooling ? (
              <>
                <div
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  <Select
                    className="select-dropdown options"
                    value={poolingOn}
                    options={[
                      { label: "Spark", value: "spark_pooling" },
                      { label: "Pandas", value: "pandas_pooling" },
                    ]}
                    style={{
                      width: 120,
                      fontSize: "10px",
                    }}
                    onChange={(value) => setPoolingOn(value)}
                  />
                  <Tooltip title={getSchemaTooltip}>
                    <InfoCircleOutlined
                      style={{
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                      onClick={handleClose}
                    />
                  </Tooltip>
                </div>
                <Tooltip
                  title={`Close this section to return ${
                    isEdit ? "update" : "save"
                  } datasource section`}
                  placement="left"
                >
                  <Button
                    onClick={handleClose}
                    type="text"
                    icon={<CloseOutlined />}
                    data-testid="close-button"
                  />
                </Tooltip>
              </>
            ) : (
              selectedDatasource?.pooling && (
                <Tooltip title="Navigate to the advanced section to provide additional connection details, such as connection pooling">
                  <Space
                    onClick={togglePooling}
                    className="cursor-pointer"
                    style={{ fontSize: "12px" }}
                    data-testid="advanced-button"
                  >
                    Advanced
                  </Space>
                </Tooltip>
              )
            )}
          </div>
          {showPooling ? (
            <AdvancedPooling
              poolingOn={poolingOn}
              poolingData={poolingData}
              setPoolingData={setPoolingData}
              handleFinish={handleFinish}
              loading={loading}
              values={form.getFieldValue()}
            />
          ) : (
            renderForm()
          )}
        </Card>
        <Card
          title="Setup Guide"
          bordered={false}
          hoverable
          className="w-100 setup-guide-card m-5"
        >
          <RenderMarkDown description={selectedDatasource?.description || ""} />
        </Card>
      </div>
    </>
  );
};
