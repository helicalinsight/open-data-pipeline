import React from "react";
import { render, screen } from "@testing-library/react";
import PreviewEmpty from "../../../../../app/chat-module/components/preview-data/PreviewEmpty";

describe("PreviewEmpty component", () => {
  it("renders without crashing", () => {
    render(<PreviewEmpty />);
    const emptyContainer = screen.getByTestId("preview-empty-container");
    expect(emptyContainer).toBeTruthy();
  });

  // it("displays the empty image", () => {
  //   render(<PreviewEmpty />);
  //   const emptyImage = screen.getByTestId("empty-image");
  //   expect(emptyImage).toBeTruthy();
  //   expect(emptyImage).toHaveAttribute(
  //     "src",
  //     expect.stringContaining("no-data.png")
  //   );
  //   expect(emptyImage).toHaveAttribute("alt", "empty");
  // });

  it("displays the heading and messages", () => {
    render(<PreviewEmpty />);
    const heading = screen.getByText("No Files Yet!");
    const message1 = screen.getByText(
      "It seems you haven't added any files yet."
    );
    const message2 = screen.getByText(
      "To load files, you can use a prompt like"
    );

    expect(heading).toBeTruthy();
    expect(message1).toBeTruthy();
    expect(message2).toBeTruthy();
  });
  
});
