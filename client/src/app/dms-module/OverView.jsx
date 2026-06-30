import { Card, Row, Col, Typography, Space, Tag } from "antd";
import {
  DatabaseOutlined,
  ClusterOutlined,
  DeploymentUnitOutlined,
  FileSearchOutlined,
} from "@ant-design/icons";
import "./style.scss";
import { useSelector } from "react-redux";
import CustomMessage from "../settings-module/CustomMessage";

const { Text } = Typography;

const OverviewModule = () => {
  const messageData = useSelector((store) => store?.settings?.messageData);
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails ||{},
  );
  const { migration_details =[] } = jobListDetails;
  const calculateActivityValues = () => {
    const { last_run } = jobListDetails || {};
    if (!last_run) {
      return {
        ingestion: 0,
        transformations: 0,
        schemaMapper: 0,
        load: 0,
      };
    }
    const totalRows = last_run?.total_rows_transferred || 0;
    const failedStep = last_run?.failed_step;
    if (failedStep === "load") {
      return {
        ingestion: totalRows,
        transformations: totalRows,
        schemaMapper: totalRows,
        load: 0,
      };
    }
    return {
      ingestion: totalRows,
      transformations: totalRows,
      schemaMapper: totalRows,
      load: totalRows,
    };
  };
  const activityValues = calculateActivityValues();
  return (
    <div>
      {messageData && (
        <div style={{ margin: "15px" }}>
          <CustomMessage
            type={messageData.type}
            message={messageData.message}
          />
        </div>
      )}
      <div className="pipeline-page" style={{ overflowY: "auto" }}>
        <Card
          className="migration-details-card"
          bordered={false}
          style={{ marginBottom: "16px", padding: "8px" }}
        >
          <Row gutter={[8, 8]}>
            <Col xs={24} sm={8}>
              <Card
                className="detail-card"
                bordered={false}
                size="small"
                style={{ padding: "4px 8px" }}
              >
                <Space
                  direction="vertical"
                  size={2}
                  align="center"
                  style={{ width: "100%" }}
                >
                  <Text strong style={{ fontSize: "12px" }}>
                    Migration Type
                  </Text>
                  <Tag
                    color="blue"
                    style={{ fontSize: "11px", padding: "2px 6px" }}
                  >
                    {migration_details[0]?.migration_type || "N/A"}
                  </Tag>
                </Space>
              </Card>
            </Col>

            <Col xs={24} sm={8}>
              <Card
                className="detail-card"
                bordered={false}
                size="small"
                style={{ padding: "4px 8px" }}
              >
                <Space
                  direction="vertical"
                  size={2}
                  align="center"
                  style={{ width: "100%" }}
                >
                  <Text strong style={{ fontSize: "12px" }}>
                    Mode
                  </Text>
                  <Tag
                    color="green"
                    style={{ fontSize: "11px", padding: "2px 6px" }}
                  >
                    {migration_details[0]?.mode || "N/A"}
                  </Tag>
                </Space>
              </Card>
            </Col>

            <Col xs={24} sm={8}>
              <Card
                className="detail-card"
                bordered={false}
                size="small"
                style={{ padding: "4px 8px" }}
              >
                <Space
                  direction="vertical"
                  size={2}
                  align="center"
                  style={{ width: "100%" }}
                >
                  <Text strong style={{ fontSize: "12px" }}>
                    Primary Key
                  </Text>
                  <Tag
                    color="purple"
                    style={{ fontSize: "11px", padding: "2px 6px" }}
                  >
                    {migration_details[0]?.primary_key || "N/A"}
                  </Tag>
                </Space>
              </Card>
            </Col>
          </Row>
        </Card>
        <Card className="pipeline-activity" bordered={false}>
          <div level={5} className="section-title">
            Pipeline Activity
          </div>

          <Row gutter={16} className="activity-row">
            <Col span={6}>
              <Card className="activity-card" bordered={false}>
                <Space direction="vertical">
                  <Space align="center">
                    <DatabaseOutlined style={{ fontSize: 18 }} />
                    <div className="activity-title">INGESTION</div>
                  </Space>
                  <div level={4} className="activity-value">
                    {activityValues?.ingestion}
                  </div>
                </Space>
              </Card>
            </Col>

            <Col span={6}>
              <Card className="activity-card" bordered={false}>
                <Space direction="vertical">
                  <Space align="center">
                    <ClusterOutlined style={{ fontSize: 18 }} />
                    <div className="activity-title">TRANSFORMATIONS</div>
                  </Space>
                  <div level={4} className="activity-value">
                    {activityValues?.transformations}
                  </div>
                </Space>
              </Card>
            </Col>

            <Col span={6}>
              <Card className="activity-card" bordered={false}>
                <Space direction="vertical">
                  <Space align="center">
                    <DeploymentUnitOutlined style={{ fontSize: 18 }} />
                    <div className="activity-title">SCHEMA MAPPER</div>
                  </Space>
                  <div level={4} className="activity-value">
                    {activityValues?.schemaMapper}
                  </div>
                </Space>
              </Card>
            </Col>

            <Col span={6}>
              <Card className="activity-card" bordered={false}>
                <Space direction="vertical">
                  <Space align="center">
                    <FileSearchOutlined style={{ fontSize: 18 }} />
                    <div className="activity-title">LOAD</div>
                  </Space>
                  <div level={4} className="activity-value">
                    {activityValues?.load}
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </Card>
      </div>
    </div>
  );
};

export default OverviewModule;
