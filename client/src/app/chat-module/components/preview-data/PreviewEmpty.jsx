import React from "react";

import { Typography } from "antd";
import { imagePath } from "../../../../constants/appConstants";
const { Text } = Typography;

const PreviewEmpty = () => {
  return (
    <div
      className="preview-empty-container items-center flexColumn"
      data-testid="preview-empty-container"
    >
      <img src={`${imagePath}/no-data.png`} alt="empty" data-testid="empty-image" />
      <h2 className="no-data-heading">No Files Yet!</h2>
      <span>It seems you haven't added any files yet.</span>
      <span>
        To load files, you can use a prompt like{" "}
        <Text italic>'Load my files..'</Text>
      </span>
    </div>
  );
};

export default PreviewEmpty;
