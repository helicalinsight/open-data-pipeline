import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import Documentation from "../../../../app/settings-module/components/Documentation";

beforeAll(() => {
  window.URL.createObjectURL = jest.fn();
  window.URL.revokeObjectURL = jest.fn();
});

describe("Documentation Component", () => {
  const originalEnv = process.env.REACT_APP_SERVER_ENVIRONMENT;
  afterEach(() => {
    process.env.REACT_APP_SERVER_ENVIRONMENT = originalEnv;
  });
  if (!window.matchMedia) {
    window.matchMedia = function () {
      return {
        matches: false,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
      };
    };
  }

  const renderComponent = () => {
    return render(<Documentation />);
  };

  it("should render component without error", () => {
    process.env.REACT_APP_SERVER_ENVIRONMENT = "dev";
    renderComponent();
    expect(screen.getByText("AOD API Documentation")).toBeInTheDocument();
  });

  it("should contain a link with correct attributes", () => {
    process.env.REACT_APP_SERVER_ENVIRONMENT = "dev";
    renderComponent();
    const link = screen.getByRole("link", { name: /AOD API Documentation/i });
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("should display the LinkOutlined icon", () => {
    process.env.REACT_APP_SERVER_ENVIRONMENT = "dev";
    renderComponent();
    const icon = screen.getByTestId("link-icon");
    expect(icon).toBeInTheDocument();
    const icons = screen.getAllByRole("img");
    expect(icons.length).toBeGreaterThan(0);
  });
});
