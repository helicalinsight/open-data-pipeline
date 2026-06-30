import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom/extend-expect";
import ADSpace from "../../components/ADSpace";

describe("ADSpace Component", () => {
  it("renders without crashing", () => {
    render(<ADSpace />);
  });

  it("renders children", () => {
    const { getByText } = render(<ADSpace>Test Children</ADSpace>);
    expect(getByText("Test Children")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(<ADSpace className="custom-class" />);
    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("applies space prop correctly", () => {
    const { container } = render(<ADSpace space="2" />);
    expect(container.firstChild).toHaveClass(
      "ad-space ad-space__horizontal ad-space__horizontal__row ad-space__horizontal__row__2 ad-space__flex-wrap--nowrap"
    );
  });

  it("applies stack prop correctly", () => {
    const { container } = render(<ADSpace stack="vertical" />);
    expect(container.firstChild).toHaveClass("ad-space__vertical");
  });

  it("applies alignItem prop correctly", () => {
    const { container } = render(<ADSpace alignItem="center" />);
    expect(container.firstChild).toHaveClass("ad-space__align-item--center");
  });

  it("applies justifyContent prop correctly", () => {
    const { container } = render(<ADSpace justifyContent="flex-end" />);
    expect(container.firstChild).toHaveClass(
      "ad-space__justify-content--flex-end"
    );
  });

  it("applies flexWrap prop correctly", () => {
    const { container } = render(<ADSpace flexWrap="wrap" />);
    expect(container.firstChild).toHaveClass("ad-space__flex-wrap--wrap");
  });

  it("applies flexDirection prop correctly", () => {
    const { container } = render(<ADSpace stack="vertical" />);
    expect(container.firstChild).toHaveClass("ad-space__vertical__column");
  });
});
