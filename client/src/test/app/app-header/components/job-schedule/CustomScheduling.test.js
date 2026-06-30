import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter as Router } from "react-router-dom";
import configureStore from "redux-mock-store";
import * as reactRedux from "react-redux";
import "../../../../__mocks__/matchMedia";
import CustomScheduling from "../../../../../app/app-header/components/job-schedule/components/CustomScheduling";
import { act } from "react-dom/test-utils";
import { Form } from "antd";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { disabledTime } from "../../../../../app/app-header/components/job-schedule/components/CustomScheduling"; 

dayjs.extend(utc);
dayjs.extend(timezone);
const mockStore = configureStore();
const engineType = [
  { value: "engine1", label: "Engine 1" },
  { value: "engine2", label: "Engine 2" },
];

const appStore = mockStore({
  chat: {
    chatList: {
      abcd: {
        loadedFiles: [],
      },
    },
    selectedChat: {
      chat_id: "absd",
      chat_id: "Job1",
    },
  },
  database: {
    datasources: [
      {
        driver: "flat_files",
        name: "Flat Files",
        categoryName: "Flat File",
        categoryType: "Flat Files",
        available: true,
      },
    ],
    savedConnections: [],
  },
});

const FormWrapper = (props) => {
  const [form] = Form.useForm();

  if (props?.customFormData) {
    form.setFieldsValue(props.customFormData);
  }

  return <CustomScheduling scheduleForm={form} {...props} />;
};

const renderComponent = (appStore, props) => {
  render(
    <reactRedux.Provider store={appStore}>
      <Router>
        <FormWrapper {...props} />
      </Router>
    </reactRedux.Provider>
  );
};

const appProps = {
  handleScheduleJob: jest.fn(),
  setCurrent: jest.fn(),
};
const userTimezone = "Asia/Calcutta";

describe("Custom Scheduling  component", () => {
 
  beforeAll(() => {
    // Mock dayjs and its timezone plugin
    jest.mock("dayjs", () => {
      const dayjs = require("dayjs");
      dayjs.tz = jest.fn().mockImplementation(() => dayjs);
      return dayjs;
    });
  });


  it("render the component without erros", () => {
    renderComponent(appStore, appProps);
  });

  it("go back onclick of back button", () => {
    renderComponent(appStore, appProps);
    const backButton = screen.getByTestId("back-button");
    act(() => {
      fireEvent.click(backButton);
    });
  });

  it("should save the options onclick of button", () => {
    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when frequency is weekly", () => {
    appProps.customFormData = {
      repeats: "weekly",
      repeatsEvery: 1,
      timezone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "never",
      repeatOn: ["Monday", "Tuesday"],
    };
    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when frequency is weekly is greater than 1", () => {
    appProps.customFormData = {
      repeats: "weekly",
      repeatsEvery: 2,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "never",
    };

    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when frequency is monthly and dayOfTheWeek", () => {
    appProps.customFormData = {
      repeats: "monthly",
      repeatsEvery: 1,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "never",
      repeatBy: "dayOfTheWeek",
    };
    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when frequency is monthly and dayOfTheMonth", () => {
    appProps.customFormData = {
      repeats: "monthly",
      repeatsEvery: 1,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "never",
      repeatBy: "dayOfTheMonth",
    };
    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when ends occurences", () => {
    appProps.customFormData = {
      repeats: "hourly",
      repeatsEvery: 1,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "after",
      EndAfterExecutions: 35,
    };
    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when ends after time", () => {
    appProps.customFormData = {
      repeats: "hourly",
      repeatsEvery: 1,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "on",
      EndDate: "2024-06-21",
      EndTime: "19:47:00",
    };
    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when frequency daily", () => {
    appProps.customFormData = {
      repeats: "daily",
      repeatsEvery: 3,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "never",
    };

    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

  it("should set the values when frequency yearly", () => {
    appProps.customFormData = {
      repeats: "yearly",
      repeatsEvery: 3,
      StartDate: "2024-06-21",
      StartTime: "19:41:23",
      timeZone: "Asia/Calcutta",
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends: "never",
    };

    renderComponent(appStore, appProps);
    const saveButton = screen.getByTestId("save-options");
    act(() => {
      fireEvent.click(saveButton);
    });
  });

   it("should disable hours and minutes when the selected date is today", () => {
    const selectedDate = dayjs().tz(userTimezone).toDate();
    const disabledTimes = disabledTime(selectedDate, userTimezone);
    const minHour = dayjs().tz(userTimezone).add(15, "minute").hour();
    const minMinute = dayjs().tz(userTimezone).add(15, "minute").minute();

    expect(disabledTimes.disabledHours()).toEqual(
      Array.from({ length: minHour }, (_, i) => i)
    );
    expect(disabledTimes.disabledMinutes(minHour)).toEqual(
      Array.from({ length: minMinute }, (_, i) => i)
    );
    expect(disabledTimes.disabledMinutes(minHour + 1)).toEqual([]);
  });

  it("should not disable any hours or minutes when the selected date is not today", () => {
    const selectedDate = dayjs().tz(userTimezone).add(1, "day").toDate(); // Select a date tomorrow
    const disabledTimes = disabledTime(selectedDate, userTimezone);
    expect(disabledTimes.disabledHours()).toEqual([]); // No hours should be disabled
    expect(disabledTimes.disabledMinutes(10)).toEqual([]); // No minutes should be disabled
  });

  it("should handle a case where no current time is passed", () => {
    const disabledTimes = disabledTime(null, userTimezone);
    expect(disabledTimes.disabledHours()).toEqual([]); // No hours should be disabled
    expect(disabledTimes.disabledMinutes(10)).toEqual([]); // No minutes should be disabled
  });

  it("should disable only specific minutes for the selected hour", () => {
    const selectedDate = dayjs().tz(userTimezone).toDate();
    const disabledTimes = disabledTime(selectedDate, userTimezone);
    const minHour = dayjs().tz(userTimezone).add(15, "minute").hour();
    const minMinute = dayjs().tz(userTimezone).add(15, "minute").minute();

    // Expect the disabled minutes for the minHour to match the calculated disabled minutes
    expect(disabledTimes.disabledMinutes(minHour)).toEqual(
      Array.from({ length: minMinute }, (_, i) => i)
    );

    // Check that the next hour has no disabled minutes
    expect(disabledTimes.disabledMinutes(minHour + 1)).toEqual([]);
  });
});
