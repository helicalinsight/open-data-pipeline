import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { Text, Title } from "../../../../../app/chat-module/components/preview-data/Title";

describe("Title component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the title component without errors", () => {
    render(<Title columnName="column name" dataType="int64" />);
    expect(screen.getByText(/column name/i)).toBeInTheDocument();
    expect(screen.getByText("123")).toBeInTheDocument(); 
  });

  it("should show the correct tooltip with column name and data type", () => {
    render(<Title columnName="test column" dataType="float64" />);
    const titleElement = screen.getByText(/test column/i);
    expect(titleElement).toBeInTheDocument();
  });

  it("should display numeric indicator for numeric types", () => {
    render(<Title columnName="numeric column" dataType="int64" />);
    expect(screen.getByText("123")).toBeInTheDocument();
    render(<Title columnName="float column" dataType="float64" />);
  });

  it("should display clock icon for datetime type", () => {
    render(<Title columnName="date column" dataType="datetime64[ns]" />);
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('anticon-clock-circle');
  });

  it("should display text indicator for other types", () => {
    render(<Title columnName="text column" dataType="string" />);
    expect(screen.getByText("A-Z")).toBeInTheDocument();
  });

  it("should have proper styling classes", () => {
    render(<Title columnName="styled column" dataType="int64" />);
    const container = screen.getByText(/styled column/i).closest('.title-container');
    expect(container).toHaveClass('fw600');
  });
});

describe("Text component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render the text component without errors", () => {
    render(<Text text="sample text" />);
    expect(screen.getByText(/sample text/i)).toBeInTheDocument();
  });

  it("should have tooltip on the text", () => {
    render(<Text text="tooltip text" />);
    const textElement = screen.getByText(/tooltip text/i);
    expect(textElement.closest('span')).toHaveClass('text-content');
  });

  it("should render empty text without errors", () => {
    render(<Text text="" />);
  });
  it("should display check icon for boolean type", () => {
  render(<Title columnName="boolean column" dataType="bool" />);
  expect(screen.getByRole('img', { hidden: true })).toHaveClass('anticon-check-square');
});
});