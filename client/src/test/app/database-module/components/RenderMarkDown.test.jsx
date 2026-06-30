import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import RenderMarkDown, {
  addCopyButton,
} from "../../../../app/database-module/components/RenderMarkDown";
import "@testing-library/jest-dom/extend-expect";

Object.defineProperty(navigator, "clipboard", {
  value: {
    writeText: jest.fn().mockResolvedValue(undefined),
  },
  writable: true,
});

describe("RenderMarkDown Component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders no setup guide message when description is not provided", () => {
    render(<RenderMarkDown description="" />);
    expect(screen.getByText(/No Setup Guide found/i)).toBeInTheDocument();
  });

  it("renders markdown content when description is provided", () => {
    const description =
      "## Sample Markdown\n\n```javascript\nconsole.log('Hello, World!');\n```";
    render(<RenderMarkDown description={description} />);
    expect(screen.getByText(/Sample Markdown/i)).toBeInTheDocument();
    expect(screen.getByText(/Hello, World!/i)).toBeInTheDocument();
  });

  it("adds a copy button to a pre element", () => {
    const preElement = document.createElement("pre");
    preElement.innerHTML = '<code>console.log("Hello, World!");</code>';
    addCopyButton(preElement);
  });

  it("renders all links with target=_blank and rel=noopener noreferrer", async () => {
    const description = `
    [Regular Link](https://example.com)
    [Another Link](https://test.com)
  `;
    render(<RenderMarkDown description={description} />);
    await waitFor(() => {
      const links = document.querySelectorAll("a");
      links.forEach((link) => {
        expect(link).toHaveAttribute("target", "_blank");
        expect(link).toHaveAttribute("rel", "noopener noreferrer");
      });
    });
  });
});
