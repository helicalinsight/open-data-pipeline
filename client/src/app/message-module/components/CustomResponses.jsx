import RenderMarkDown from "../../database-module/components/RenderMarkDown";
import ListFiles from "../components/ListFiles";
import ButtonsPrompt from "./ButtonsPrompt";
import DownloadFiles from "./DownloadFiles";

function CustomResponses({ item, index }) {
  const { text, shipment } = item;
  const isLastItem = index === 0;

  if (item.quick_replies) {
    return <ButtonsPrompt message={item} isLastItem={isLastItem} />;
  }

  if (!item.shipment) {
    return (
        <RenderMarkDown description={item.text} />
    );
  }

  if (shipment?.hasOwnProperty("list_files")) {
    return (
      <ListFiles
        message={text}
        files={shipment.list_files}
        isLastItem={isLastItem}
      />
    );
  } else if (shipment?.hasOwnProperty("load_files")) {
    return item.text;
  } else if (shipment?.hasOwnProperty("download_files")) {
    return (
      <DownloadFiles
        message={text}
        files={shipment.download_files}
        isLastItem={isLastItem}
      />
    );
  } else {
    return item.text;
  }
}
export default CustomResponses;
