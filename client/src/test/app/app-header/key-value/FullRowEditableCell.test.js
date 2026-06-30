import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react";
import { Form } from "antd";
import FullRowEditableCell from "../../../../app/app-header/components/key-value/FullRowEditableCell";

beforeAll(() => {
  window.matchMedia =
    window.matchMedia ||
    function () {
      return {
        matches: false,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
      };
    };
});

const renderWithForm = (dataIndex, visible = false) => {
  const Wrapper = () => {
    const [form] = Form.useForm();
    return (
      <Form form={form} component="form">
        <table>
          <tbody>
            <FullRowEditableCell
              editing={true}
              dataIndex={dataIndex}
              title={dataIndex === "configKey" ? "Key" : "Value"}
              inputType="text"
              record={{}}
              index={0}
              visible={visible}
            />
          </tbody>
        </table>
      </Form>
    );
  };
  return render(<Wrapper />);
};

describe("FullRowEditableCell - configKey validation", () => {
  it("fails if not a string", async () => {
    const { getByRole } = renderWithForm("configKey");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: 123 } });
    fireEvent.blur(input);
  });

  it("fails if string is empty or only spaces", async () => {
    const { getByRole, findByText } = renderWithForm("configKey");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.blur(input);
    await findByText("Key cannot be empty.");
  });

  it("passes with valid key using underscore", async () => {
    const { getByRole, queryByText } = renderWithForm("configKey");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: "valid_key" } });
    fireEvent.blur(input);
    await waitFor(() => {
      expect(queryByText(/Key cannot be empty/)).toBeNull();
    });
  });

  it("passes with valid key using hyphen", async () => {
    const { getByRole, queryByText } = renderWithForm("configKey");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: "valid-key" } });
    fireEvent.blur(input);
    await waitFor(() => {
      expect(queryByText(/Key cannot be empty/)).toBeNull();
    });
  });
});

describe("FullRowEditableCell - configValue validation", () => {
  it("fails if value is only whitespace", async () => {
    const { getByRole, findByText } = renderWithForm("configValue");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.blur(input);
    await findByText("Value cannot be just whitespace");
  });

  it("fails if value has leading/trailing spaces", async () => {
    const { getByRole, findByText } = renderWithForm("configValue");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: " value " } });
    fireEvent.blur(input);
    await findByText("Value cannot contain extraspaces");
  });

  it("passes with valid string value", async () => {
    const { getByRole, queryByText } = renderWithForm("configValue");
    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: "valid value" } });
    fireEvent.blur(input);
    await waitFor(() => {
      expect(queryByText(/Value cannot be/)).toBeNull();
    });
  });

  it("passes with valid JSON object (as string)", async () => {
    const { getByRole, queryByText } = renderWithForm("configValue");
    const input = getByRole("textbox");
    fireEvent.change(input, {
      target: { value: '{"name":"example","age":30}' },
    });
    fireEvent.blur(input);
    await waitFor(() => {
      expect(queryByText(/Value cannot be/)).toBeNull();
    });
  });
});