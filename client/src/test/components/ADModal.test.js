import React from "react";
import { render, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom/extend-expect";
import { ADModal } from "../../components/ADModal";

describe("ADModal Component", () => {
  const defaultProps = {
    title: "Test Modal",
    open: true,
    onOk: jest.fn(),
    onCancel: jest.fn(),
    description: "This is a test description",
    okText: "OK",
    cancelText: "Cancel",
    iconName: "test-icon",
    showCancelButton: true,
    hideButtons: false,
  };

  it("renders without crashing", () => {
    render(<ADModal {...defaultProps} />);
  });

  it("renders title and description correctly", () => {
    const { getByText } = render(<ADModal {...defaultProps} />);
    expect(getByText("Test Modal")).toBeInTheDocument();
    expect(getByText("This is a test description")).toBeInTheDocument();
  });

  it("calls onOk when OK button is clicked", () => {
    const { getByText } = render(<ADModal {...defaultProps} />);
    fireEvent.click(getByText("OK"));
    expect(defaultProps.onOk).toHaveBeenCalled();
  });

  it("calls onCancel when Cancel button is clicked", () => {
    const { getByText } = render(<ADModal {...defaultProps} />);
    fireEvent.click(getByText("Cancel"));
    expect(defaultProps.onCancel).toHaveBeenCalled();
  });

  it("does not render Cancel button when showCancelButton is false", () => {
    const { queryByText } = render(
      <ADModal {...defaultProps} showCancelButton={false} />
    );
    expect(queryByText("Cancel")).toBeNull();
  });
});
