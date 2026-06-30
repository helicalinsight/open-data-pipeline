import { useLocation } from "react-router-dom";
import { chatRoutes } from "../../router/uiRouteConstants";
import DefaultJobView from "../chat-module/components/DefaultJobView";
import { ADSpace } from "../../components";
import CustomMessage from "../settings-module/CustomMessage";
import { useSelector } from "react-redux";
import ErrorFallback from "../error-boundry/ErrorFallback";
import MigrationModule from "./MigrationModule";
import ObjectSelectionModule from "./ObjectSelection";
import { CommonPipelineSteps, PipelinePageWrapper } from "./DmsHelperMethod";
import DestinationModule from "./DestinationModule";

const DmsModule = () => {
  const location = useLocation();
  const messageData = useSelector((store) => store?.settings?.messageData);
  const hideMessage = useSelector((store) => store?.settings?.hideMessage);
  const searchParams = new URLSearchParams(location.search);
  const chatId = searchParams.get("chat");
  const showDefaultView = !chatId && location.pathname === chatRoutes.dms;
  const step = useSelector((state) => state.dms.step);

  if (showDefaultView) {
    return (
      <ErrorFallback>
        {messageData && !hideMessage && (
          <div style={{ margin: "15px" }}>
            <CustomMessage
              type={messageData.type}
              message={messageData.message}
            />
          </div>
        )}
        <ADSpace className="overflowHidden flex-1">
          <DefaultJobView setShowDefaultPage={() => {}} />
        </ADSpace>
      </ErrorFallback>
    );
  }

  if (chatId) {
    return (
      <ErrorFallback>
        {messageData && !hideMessage && (
          <div style={{ margin: "15px" }}>
            <CustomMessage
              type={messageData.type}
              message={messageData.message}
            />
          </div>
        )}
        <PipelinePageWrapper>
          <CommonPipelineSteps current={step} />

          {step === 0 && <MigrationModule  />}
          {step === 1 && <ObjectSelectionModule  />}
          {step === 2 && <DestinationModule  />}
        </PipelinePageWrapper>{" "}
      </ErrorFallback>
    );
  }
  return null;
};

export default DmsModule;
