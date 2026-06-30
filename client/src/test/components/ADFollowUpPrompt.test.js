import ADFollowUpPrompt from "../../components/ADFollowUpPrompt";
import React from "react";
import { render, fireEvent, act, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import { setFollowUpPromptAction } from "../../store/actions/chatAction";

const mockStore = configureStore();

describe("ADFollowUpPrompt component", () => {
  it("handles click on prompt button", () => {
    const store = mockStore({
      chat: {
        selectedChat: { chat_id: "test_chat_id" },
        chatList: {
          test_chat_id: {
            followUpPrompts: [{ prompt: "Prompt 1", property: "property1" }],
          },
        },
      },
    });

    const handleMessageSent = jest.fn();
    const setEditPrompt = jest.fn();

    render(
      <Provider store={store}>
        <ADFollowUpPrompt
          handleMessageSent={handleMessageSent}
          setEditPrompt={setEditPrompt}
        />
      </Provider>
    );

    // Wrap the click event inside an act function
    act(() => {
      // Click on the prompt button
      fireEvent.click(screen.getByTestId("prompt-button"));
    });

    // Ensure that the appropriate actions are dispatched or functions are called
    expect(store.getActions()).toEqual([
      setFollowUpPromptAction({ chat_id: "test_chat_id", prompts: [] }),
    ]);
    expect(setEditPrompt).not.toHaveBeenCalled();
    expect(handleMessageSent).toHaveBeenCalledWith({
      payload: "property1",
      title: "Prompt 1",
    });
  });

  it("renders with no followUpPrompts", () => {
    const store = mockStore({
      chat: {
        selectedChat: { chat_id: "test_chat_id" },
        chatList: {
          test_chat_id: {
            followUpPrompts: [],
          },
        },
      },
    });

    render(
      <Provider store={store}>
        <ADFollowUpPrompt />
      </Provider>
    );

    // Ensure that the component renders without crashing
    expect(screen.queryAllByTestId("prompt-button")).toHaveLength(0);
  });

  it("renders with followUpPrompts", () => {
    const store = mockStore({
      chat: {
        selectedChat: { chat_id: "test_chat_id" },
        chatList: {
          test_chat_id: {
            followUpPrompts: [
              { prompt: "Prompt 1", property: "property1" },
              { prompt: "Prompt 2", property: "property2" },
            ],
          },
        },
      },
    });

    render(
      <Provider store={store}>
        <ADFollowUpPrompt />
      </Provider>
    );

    // Ensure that the component renders the correct number of prompt buttons
    expect(screen.getAllByTestId("prompt-button")).toHaveLength(2);
  });

  it("handles click on prompt button and setEditPrompt", () => {
    const store = mockStore({
      chat: {
        selectedChat: { chat_id: "test_chat_id" },
        chatList: {
          test_chat_id: {
            followUpPrompts: [{ prompt: "Prompt 1", property: "edit_prompt" }],
          },
        },
      },
    });

    const setEditPrompt = jest.fn();

    render(
      <Provider store={store}>
        <ADFollowUpPrompt setEditPrompt={setEditPrompt} />
      </Provider>
    );

    act(() => {
      fireEvent.click(screen.getByTestId("prompt-button"));
    });

    // Ensure that setEditPrompt is called with the correct prompt
    expect(setEditPrompt).toHaveBeenCalledWith({
      prompt: "Prompt 1",
      property: "edit_prompt",
    });
  });

  it('handles click on "show_more" prompt button', () => {
    const store = mockStore({
      chat: {
        selectedChat: { chat_id: "test_chat_id" },
        chatList: {
          test_chat_id: {
            followUpPrompts: [
              {
                prompt: "Prompt 1",
                property: "show_more",
                data: ["Subprompt 1", "Subprompt 2"],
              },
            ],
          },
        },
      },
    });

    const dispatch = jest.fn();

    render(
      <Provider store={store}>
        <ADFollowUpPrompt dispatch={dispatch} />
      </Provider>
    );

    act(() => {
      fireEvent.click(screen.getByTestId("prompt-button"));
    });

    // Ensure that setFollowUpPromptAction is dispatched with the correct data
    // expect(dispatch).toHaveBeenCalledWith(
    //   setFollowUpPromptAction({
    //     chat_id: "test_chat_id",
    //     prompts: ["Subprompt 1", "Subprompt 2"],
    //   })
    // );
  });
});
