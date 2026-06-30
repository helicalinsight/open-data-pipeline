import { Collapse, Divider, Timeline } from "antd";
import { useSelector } from "react-redux";
import { useSearchParams } from "react-router-dom";
import { convertToTitleCase } from "./utils";
import { v4 as uuidv4 } from "uuid";
import ADSpace from "../../../components/ADSpace";

function PipelineExecution() {
  const [searchParams] = useSearchParams();
  const chatId = searchParams.get("chat");
  const pipelineHistory =
    useSelector((state) => state.chat.chatList[chatId]?.pipelineHistory) || {};
    
  const connectionAliasMap = {};
  const connectionTypeMap = {};

  pipelineHistory?.connections?.forEach((conn) => {
    const id = conn._id;
    if (id) {
      connectionAliasMap[id] = conn.alias || "";
      connectionTypeMap[id] = conn.type || "";
    }
  });

  const renderTimeline = (timelineData) => (
    <Timeline mode="left">
      {timelineData?.map((event) => (
        <Timeline.Item key={uuidv4()} color={"green"}>
          <Collapse accordion bordered={false}>
            <Collapse.Panel
              header={convertToTitleCase(event?.function)}
              key={event?.id}
              showArrow={false}
            >
              <div className="history-row">
                {event?.files?.length > 0 && (
                  <strong className="file-name p-text">
                    Files: {event?.files[0]?.alias?.join(" | ")}
                  </strong>
                )}
                {event?.parameters?.map((param, index) => (
                  <ADSpace key={index} justifyContent="space-between">
                    <div className="history-columns">
                      {Object.entries(param)?.map(([key, value]) => {
                        if (key === "_id") return null;

                        const formatValue = (value) => {
                          if (Array.isArray(value)) {
                            return value
                              .map((item) =>
                                typeof item === "object"
                                  ? Object.entries(item)
                                      .map(
                                        ([subKey, subValue]) =>
                                          `${subKey}: ${subValue}`
                                      )
                                      .join(", ")
                                  : String(item)
                              )
                              .join(", ");
                          }

                          if (typeof value === "object" && value !== null) {
                            return Object.entries(value)
                              .map(
                                ([subKey, subValue]) => `${subKey}: ${subValue}`
                              )
                              .join(", ");
                          }

                          return String(value);
                        };

                        return (
                          <div key={key}>
                            {param?._id && (
                              <>
                                {connectionTypeMap[param._id] && (
                                  <p className="fx-1 ml-2 alias-tag">
                                    Datasource: {connectionTypeMap[param._id]}
                                  </p>
                                )}
                                {connectionAliasMap[param._id] && (
                                  <p className="fx-1 ml-2 alias-tag">
                                    Connection Name:{" "}
                                    {connectionAliasMap[param._id]}
                                  </p>
                                )}
                              </>
                            )}

                            <ADSpace space="1">
                              <p className="p-text">{key} :</p>
                              <p className="fx-1">{formatValue(value)}</p>
                            </ADSpace>
                          </div>
                        );
                      })}
                    </div>
                  </ADSpace>
                ))}
              </div>
            </Collapse.Panel>
          </Collapse>
        </Timeline.Item>
      ))}
    </Timeline>
  );

  return (
    <>
      {(!pipelineHistory?.history ||
        pipelineHistory?.history?.length === 0) && (
        <p className="no-history text-center">No History found!</p>
      )}
      {pipelineHistory?.history && pipelineHistory?.history?.length > 0 && (
        <div className="pipeline-execution-container">
          {renderTimeline(pipelineHistory?.history)}
        </div>
      )}
      {pipelineHistory?.next && pipelineHistory?.next?.length > 0 && (
        <>
          <Divider />
          <div className="pipeline-execution-container">
            {renderTimeline(pipelineHistory?.next)}
          </div>
        </>
      )}
    </>
  );
}

export default PipelineExecution;
