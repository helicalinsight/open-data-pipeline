import React from "react";
import { render, screen, act, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import ADFile from "../../components/ADFile";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import { BrowserRouter as Router, MemoryRouter } from "react-router-dom";
import { updateName, deleteDataPreviewFile } from "../../apis/fileService";

// ADFile component props
const ADFileProps = {
  name: "fileName",
  source_id: "662ba40f88e28e8af8679eb0",
  style: { color: "green" },
};

jest.mock("../../apis/fileService", () => ({
  deleteDataPreviewFile: jest.fn(),
  updateName: jest.fn(),
}));

const mockStore = configureStore();

const store = mockStore({
  app: {
    previewState: true,
  },
  chat: {
    chatList: {
      "65d303abc6619e0b2bf7f114": {
        chat_id: "65d303abc6619e0b2bf7f114",
        chat_name: "Job 14",
        columnList: ["index", "customer_id", "first_name", "last_name"],
        selectedFiles: [
          {
            source_id: "662ba55788e28e8af8679eb1",
            alias: "customers-100",
            type: "csv",
          },
        ],
        loadedFiles: [
          {
            source_id: "662ba40f88e28e8af8679eb0",
            alias: "free-test-data",
            type: "csv",
          },
        ],
        fetchChatHistory: false,
      },
    },
    selectedChat: {
      chat_id: "65d303abc6619e0b2bf7f114",
      chat_name: "Job 14",
    },
  },
});

const renderComponent = (props) => {
  render(
    <reactRedux.Provider store={store}>
      <MemoryRouter initialEntries={[`?chat=65d303abc6619e0b2bf7f114`]}>
        <ADFile {...props} />
      </MemoryRouter>
    </reactRedux.Provider>
  );
};

describe("ADFile component", () => {
  //check if component is rendered
  it("renders the component with only name props without errors", () => {
    renderComponent(ADFileProps);
  });
  it("renders the component with all props without errors", () => {
    renderComponent(ADFileProps);
  });

  it("renders the name and image", () => {
    updateName.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    renderComponent(ADFileProps);
    expect(screen.getByTestId("file-name-id")).toBeInTheDocument();
    expect(screen.getByTestId("file-image-id")).toBeInTheDocument();
  });

  it("update API success : false", () => {
    updateName.mockImplementationOnce(({ onSuccess }) => onSuccess({}));
    renderComponent(ADFileProps);
  });

  it("updateName : onError", () => {
    updateName.mockImplementationOnce((params) => params.onError("error"));
    renderComponent(ADFileProps);
  });

  it("edit name functionality", () => {
    updateName.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    renderComponent(ADFileProps);

    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });

    const editIcon = screen.getByTestId("edit-icon-id");

    act(() => {
      fireEvent.click(editIcon);
    });

    const input = screen.getByTestId("file-name-input-id");

    act(() => {
      fireEvent.change(input, { target: { value: "new-name" } });
      fireEvent.blur(input);
    });
  });

  it("edit name functionality with same name", () => {
    updateName.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    renderComponent(ADFileProps);

    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });

    const editIcon = screen.getByTestId("edit-icon-id");

    act(() => {
      fireEvent.click(editIcon);
    });

    const input = screen.getByTestId("file-name-input-id");

    act(() => {
      fireEvent.change(input, { target: { value: "free-test-data" } });
      fireEvent.blur(input);
    });
  });

  it("mouse leave eveent", () => {
    updateName.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ success: true })
    );
    const props = {
      name: "fileName",
      source_id: "662ba40f88e28e8af8679eb0",
    };
    renderComponent(props);

    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
      fireEvent.mouseOut(element);
    });
  });
  // to delete datapreviewfile
  it("should call deleteDataPreviewFile and handle success", async () => {
    deleteDataPreviewFile.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ message: "File deleted successfully" })
    );
    renderComponent(ADFileProps);
    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });
    const deleteIcon = screen.getByTestId("delete-icon-id");
    act(() => {
      fireEvent.click(deleteIcon);
    });
    const deleteButton = screen.getByText("Delete");
    act(() => {
      fireEvent.click(deleteButton);
    });
    expect(deleteDataPreviewFile).toHaveBeenCalledWith({
      payload: {
        chat_id: "65d303abc6619e0b2bf7f114",
        source_id: "662ba40f88e28e8af8679eb0",
      },
      onSuccess: expect.any(Function),
      onError: expect.any(Function),
      finally: expect.any(Function),
    });
    expect(screen.getByText("File deleted successfully")).toBeInTheDocument();
  });

  it("should call deleteDataPreviewFile and handle error", async () => {
    deleteDataPreviewFile.mockImplementationOnce(({ onError }) =>
      onError({ message: "Failed to delete the file" })
    );
    renderComponent(ADFileProps);
    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });
    const deleteIcon = screen.getByTestId("delete-icon-id");
    act(() => {
      fireEvent.click(deleteIcon);
    });
    const deleteButton = screen.getByText("Delete");
    act(() => {
      fireEvent.click(deleteButton);
    });
    expect(deleteDataPreviewFile).toHaveBeenCalledWith({
      payload: {
        chat_id: "65d303abc6619e0b2bf7f114",
        source_id: "662ba40f88e28e8af8679eb0",
      },
      onSuccess: expect.any(Function),
      onError: expect.any(Function),
      finally: expect.any(Function),
    });
  });

  it("should open confirmation modal on delete icon click", async () => {
    renderComponent(ADFileProps);
    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });
    const deleteIcon = screen.getByTestId("delete-icon-id");
    act(() => {
      fireEvent.click(deleteIcon);
    });
  });
  
  it("should remove file from DOM after successful delete", async () => {
    deleteDataPreviewFile.mockImplementationOnce(({ onSuccess }) =>
      onSuccess({ message: "File deleted successfully" })
    );
    renderComponent(ADFileProps);
    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });
    const deleteIcon = screen.getByTestId("delete-icon-id");
    act(() => {
      fireEvent.click(deleteIcon);
    });
    const deleteButton = screen.getByText("Delete");
    act(() => {
      fireEvent.click(deleteButton);
    });
    expect(deleteDataPreviewFile).toHaveBeenCalled();
    await screen.findByText("File deleted successfully"); 
  });
  
  it("should show error message on failed delete", async () => {
    deleteDataPreviewFile.mockImplementationOnce(({ onError }) =>
      onError({ message: "Failed to delete the file" })
    );
    renderComponent(ADFileProps);
    const element = screen.getByTestId("ad-file-662ba40f88e28e8af8679eb0");
    act(() => {
      fireEvent.mouseOver(element);
    });
    const deleteIcon = screen.getByTestId("delete-icon-id");
    act(() => {
      fireEvent.click(deleteIcon);
    });
    const deleteButton = screen.getByText("Delete");
    act(() => {
      fireEvent.click(deleteButton);
    });
  });
  
});
