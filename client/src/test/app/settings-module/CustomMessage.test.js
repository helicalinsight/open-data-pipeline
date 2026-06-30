import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { CheckCircleOutlined, CloseCircleOutlined, InfoCircleOutlined, WarningOutlined } from "@ant-design/icons";
import CustomMessage from "../../../app/settings-module/CustomMessage";

jest.useFakeTimers(); 

describe("CustomMessage Component", () => {
  const message = "This is a test message";

  it("renders the correct icon for 'success' type", () => {
    render(<CustomMessage type="success" message={message} />);
  });
});
