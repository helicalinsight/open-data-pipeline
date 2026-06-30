import { Typography, Tooltip } from "antd";
import { LinkOutlined } from "@ant-design/icons";
import { ADSpace } from "../../../components";
import { baseApi } from "../../../apis/apiUrlConstants";

const { Link } = Typography;

const Documentation = () => {
  return (
    <ADSpace
      direction="vertical"
      style={{ height: "100%" }}
      data-testid="ad-space"
    >
      <div style={{ marginBottom: 16, paddingLeft: 16 }}>
        <ul className="documentation-list">
          <li>
            <Tooltip
              title="Open AOD API Documentation"
              placement="right"
              overlayClassName="custom-tooltip"
              data-testid="tooltip"
            >
              <Link
                href={`${baseApi.url}doc/`}
                target="_blank"
                rel="noopener noreferrer"
                className="documentation-link"
                data-testid="documentation-link"
              >
                <LinkOutlined
                  data-testid="link-icon"
                  className="documentation-link-icon"
                />
                AOD API Documentation
              </Link>
            </Tooltip>
          </li>
        </ul>
      </div>
    </ADSpace>
  );
};

export default Documentation;
