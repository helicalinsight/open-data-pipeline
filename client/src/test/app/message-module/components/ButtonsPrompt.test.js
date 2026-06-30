import React from "react";
import { render, fireEvent, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import "@testing-library/jest-dom/extend-expect";
import ButtonsPrompt from "../../../../app/message-module/components/ButtonsPrompt";
import { ChatContext } from "../../../../app/chat-module/components/ChatContext";

// Mock the ChatContext
const mockContextValue = {
  handleMessage: jest.fn(),
};

jest.mock("../../../../app/chat-module/components/ChatContext", () => ({
  ...jest.requireActual("../../../../app/chat-module/components/ChatContext"),
  __esModule: true, // this is important for useContext to work properly
  ChatContext: {
    ...jest.requireActual("../../../../app/chat-module/components/ChatContext")
      .ChatContext,
    Consumer: ({ children }) => children(mockContextValue),
  },
}));

const message = {
  message_id: "b4f87439-43f3-48bd-bed5-5b01cb35ef25",
  isUser: false,
  time: "3:57 PM",
  text: "Which Type of File would you like to load?",
  quick_replies: [
    {
      content_type: "text",
      title: "CSV",
      payload: '/read_files{"FILE_TYPE": "csv"}',
    },
    {
      content_type: "text",
      title: "EXCEL",
      payload: '/read_files{"FILE_TYPE": "excel"}',
    },
  ],
};

describe("ButtonsPrompt Component", () => {
  it("renders without crashing", () => {
    render(
      <ButtonsPrompt message={{ text: "Test Message", quick_replies: [] }} />
    );
  });

  it("renders the prompt message correctly", () => {
    const { getByText } = render(<ButtonsPrompt message={message} />);
    const promptMessage = getByText(
      "Which Type of File would you like to load?"
    );
    expect(promptMessage).toBeInTheDocument();
  });

  it("renders quick replies correctly", () => {
    const { getByText } = render(<ButtonsPrompt message={message} />);
    const csvButton = getByText("CSV");
    const excelButton = getByText("EXCEL");
    expect(csvButton).toBeInTheDocument();
    expect(excelButton).toBeInTheDocument();
  });

  it("does not call handleMessage when there are no quick replies", () => {
    render(
      <ButtonsPrompt
        message={{ text: "No Quick Replies", quick_replies: [] }}
      />
    );
    expect(mockContextValue.handleMessage).not.toHaveBeenCalled();
  });

  test("handles button click and disables buttons", async () => {
    // Arrange
    const message = {
      text: "Test message",
      quick_replies: [
        { title: "Option 1", payload: "option_1" },
        { title: "Option 2", payload: "option_2" },
      ],
    };

    const mockContextValue = {
      handleMessage: jest.fn(),
    };

    // Render the component with ChatContext
    const { debug } = render(
      <ChatContext.Provider value={mockContextValue}>
        <ButtonsPrompt message={message} />
      </ChatContext.Provider>
    );

    // Act
    const button1 = screen.getByTestId("buttons-prompt-option_1");
    const button2 = screen.getByTestId("buttons-prompt-option_2");

    fireEvent.click(button1);

    // Assert
    expect(button1).toHaveClass("ant-btn-background-ghost");
    expect(button2).toHaveClass("ant-btn-background-ghost");

    // debug();
  });
});
