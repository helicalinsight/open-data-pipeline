import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import dayjs from "dayjs";
import isToday from "dayjs/plugin/isToday";
import isTomorrow from "dayjs/plugin/isTomorrow";
import { InfoCircleOutlined } from "@ant-design/icons";
import {
  Form,
  Checkbox,
  Row,
  Tooltip,
  Select,
  DatePicker,
  Radio,
  InputNumber,
  Button,
  Space,
} from "antd";
import {
  days,
  repeatOptions,
  repeateByMonthOptions,
  radioOptions,
  timezoneOptions,
  dateFormat,
  weeksText,
  userTimezone,
  initialStartsOn,
  initialEndsOn,
  repeatSummary,
  TOOLTIPS_INFO,
} from "../constants";
import { ArrowLeftOutlined } from "@ant-design/icons";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { setJobModal } from "../../../../../store/actions/jobScheduleActions";

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(isToday);
dayjs.extend(isTomorrow);

const layout = {
  labelCol: {
    span: 8,
  },
};

function getWeekOfMonth(date) {
  const startOfMonth = date.startOf("month");
  const startOfWeek = startOfMonth.startOf("week");
  const diff = date.diff(startOfWeek, "week");
  return diff + 1;
}

const disabledDate = (current) => {
  return dayjs().tz(userTimezone).subtract(0, "day") >= current;
};

const disabledTime = (current, userTimezone = "Asia/Calcutta") => {
  const minTime = dayjs().tz(userTimezone).add(15, "minute");
  if (current && dayjs(current).isSame(minTime, "day")) {
    const minHour = minTime.hour();
    const minMinute = minTime.minute();
    return {
      disabledHours: () => Array.from({ length: minHour }, (_, i) => i),
      disabledMinutes: (selectedHour) =>
        selectedHour === minHour
          ? Array.from({ length: minMinute }, (_, i) => i)
          : [],
    };
  }
  return { disabledHours: () => [], disabledMinutes: () => [] };
};

const parseScheduleDate = (dateStr, timeStr, fallback) => {
  if (!dateStr || !timeStr) return fallback();
  const dateTime = dayjs(`${dateStr} ${timeStr}`);
  return dateTime.isValid() ? dateTime : fallback();
};

const CustomScheduling = ({
  handleScheduleJob,
  setCurrent,
  scheduleForm,
  loading,
}) => {
  const dispatch = useDispatch();
  const [summaryText, setSummaryText] = useState("");
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );

  const getRepeatsArray = (num) => new Array(num).fill().map((_, i) => i + 1);
  useEffect(() => {
    document.addEventListener("mouseover", (e) => {
      if (e.target?.title) e.target.removeAttribute("title");
    });
  }, []);
  useEffect(() => {
    if (!isScheduleEditMode) {
      // Set default values for new schedule
      const timezone = userTimezone;
      const startsOn = initialStartsOn(timezone);
      const endsOn = initialEndsOn(timezone);

      scheduleForm.setFieldsValue({
        repeats: "weekly",
        repeatsEvery: 1,
        timezone,
        startsOn,
        ends: "never",
        endsOn,
      });
      updateSummary();
      return;
    }

    // Handle edit mode initialization
    const scheduling = jobListDetails?.job_details?.advanced_scheduling || {};
    const {
      Frequency = "weekly",
      RepeatsEvery = 1,
      StartDate,
      StartTime,
      timeZone = userTimezone,
      ends = "never",
      EndDate,
      EndTime,
      DaysofWeek = [],
      RepeatBy = repeateByMonthOptions[0].value,
      EndAfterExecutions = 35,
    } = scheduling;

    const startsOn = parseScheduleDate(StartDate, StartTime, () =>
      initialStartsOn(timeZone)
    );

    const endsOn = parseScheduleDate(EndDate, EndTime, () =>
      initialEndsOn(timeZone)
    );

    scheduleForm.setFieldsValue({
      repeats: Frequency,
      repeatsEvery: RepeatsEvery,
      timezone: timeZone,
      repeatOn: DaysofWeek,
      startsOn,
      repeatBy: RepeatBy,
      ends,
      endsAfter: EndAfterExecutions,
      endsOn: ends === "on" ? endsOn : initialEndsOn(timeZone),
    });
    updateSummary();
  }, [isScheduleEditMode, scheduleForm, jobListDetails]);

  const updateSummary = (changedValues) => {
    if (changedValues?.repeats) {
      scheduleForm.setFieldValue("repeatsEvery", 1);
    }
    if (changedValues?.timezone) {
      const tz = changedValues.timezone;
      scheduleForm.setFieldValue("startsOn", dayjs().tz(tz).add(15, "minute"));
      scheduleForm.setFieldValue("endsOn", dayjs().tz(tz).add(30, "minute"));
    }

    if (!scheduleForm) return;

    let summary = "Starting ";
    const {
      repeats,
      repeatsEvery,
      startsOn,
      timezone,
      repeatOn,
      repeatBy,
      ends,
      endsAfter,
      endsOn,
    } = scheduleForm.getFieldsValue();

    // Handle start date
    if (!startsOn || !startsOn.isValid()) {
      setSummaryText("Invalid schedule configuration");
      return;
    }

    if (dayjs(startsOn).isToday()) {
      summary += "today, ";
    } else if (dayjs(startsOn).isTomorrow()) {
      summary += "tomorrow, ";
    } else {
      summary += `on ${startsOn.format("Do MMMM, YYYY")}, `;
    }

    // Handle repeat frequency
    if (repeatsEvery === 1) {
      switch (repeats) {
        case "minutes":
          summary += "repeats every minute ";
          break;
        case "hourly":
          summary += "repeats every hour ";
          break;
        case "weekly":
          summary += `repeats every week `;
          break;
        case "daily":
          summary += `repeats daily `;
          break;
        case "monthly":
          summary += `repeats monthly `;
          break;
        case "yearly":
          summary += `repeats yearly `;
          break;
        default:
          summary += `repeats `;
      }
    } else {
      switch (repeats) {
        case "minutes":
          summary += `repeats every ${repeatsEvery} minutes `;
          break;
        case "hourly":
          summary += `repeats every ${repeatsEvery} hours `;
          break;
        case "weekly":
          summary += `repeats every ${repeatsEvery} weeks `;
          break;
        case "daily":
          summary += `repeats every ${repeatsEvery} days `;
          break;
        case "monthly":
          summary += `repeats every ${repeatsEvery} months `;
          break;
        case "yearly":
          summary += `repeats every ${repeatsEvery} years `;
          break;
        default:
          summary += `repeats every ${repeatsEvery} `;
      }
    }

    // Handle weekly repeats
    if (repeats === "weekly" && repeatsEvery === 1 && repeatOn?.length) {
      summary += `on ${days
        .filter((e) => repeatOn.includes(e.value))
        .map((e) => e.value)
        .join(", ")} `;
    }

    // Handle monthly repeats
    if (repeats === "monthly" && repeatBy) {
      const time = startsOn.format("hh:mm A");
      if (repeatBy === "dayOfTheMonth") {
        const date = dayjs(startsOn).date();
        summary += `on day ${date} at ${time}`;
      } else {
        const day = days[dayjs(startsOn).day()].value;
        const week = getWeekOfMonth(dayjs(startsOn));
        const weekText = weeksText[week] || "";
        summary += `on ${weekText} ${day} at ${time}`;
      }
    } else {
      // adding starting time
      summary += `from ${startsOn.format("Do MMMM, YYYY hh:mm A")}`;
    }

    // Handle end conditions
    if (ends === "on" && endsOn && endsOn.isValid()) {
      summary += `, until ${endsOn.format("Do MMMM, YYYY hh:mm A")} `;
    } else if (ends === "after") {
      summary += ` for ${endsAfter} times `;
    }

    summary += `(${timezone})`;
    setSummaryText(summary);
  };

  const repeateOptionObj = repeatOptions.find(
    (e) => e.value === scheduleForm.getFieldValue("repeats")
  );
  const repeatsEveryArray = getRepeatsArray(
    repeateOptionObj ? repeateOptionObj.max : 100
  );

  const repeatsEveryOptions = repeatsEveryArray.map((num) => ({
    label: num,
    value: num,
  }));

  const buildScheduleObj = () => {
    const {
      ends,
      endsAfter,
      endsOn,
      repeatBy,
      repeatOn,
      repeats,
      repeatsEvery,
      startsOn,
      timezone,
    } = scheduleForm.getFieldsValue();

    const formData = {
      Frequency: repeats,
      RepeatsEvery: repeatsEvery,
      StartDate: startsOn.format("YYYY-MM-DD"),
      StartTime: startsOn.format("HH:mm:ss"),
      timeZone: timezone.split(" ")[0],
      dateFormat: "DD/MM/YYYY hh:mm A",
      ends,
    };

    if (repeats === "weekly" && repeatsEvery === 1) {
      formData.DaysofWeek = repeatOn || [];
    }

    if (repeats === "monthly") {
      formData.RepeatBy = repeatBy;
    }

    if (ends === "after") {
      formData.EndAfterExecutions = endsAfter;
    }

    if (ends === "on" && endsOn && endsOn.isValid()) {
      formData.EndDate = endsOn.format("YYYY-MM-DD");
      formData.EndTime = endsOn.format("HH:mm:ss");
    }

    return formData;
  };

  const onFinish = (values) => {
    const customFormData = buildScheduleObj(values);
    handleScheduleJob({
      dispatch,
      frequency: customFormData.Frequency,
      customFormData,
      isImmediateExecution: false,
    });
    dispatch(setJobModal(false));
  };

  const handleSave = () => {
    scheduleForm
      .validateFields()
      .then(() => {
        scheduleForm.submit();
      })
      .catch((e) => console.error("Validation failed:", e));
  };

  const {
    repeats,
    repeatOn,
    repeatsEvery,
    timezone,
    startsOn,
    repeatBy,
    ends,
    endsAfter,
    endsOn,
  } = scheduleForm.getFieldsValue() || {};

  return (
    <>
      <Form
        {...layout}
        form={scheduleForm}
        onValuesChange={updateSummary}
        onFinish={onFinish}
        name="control-hooks"
        labelAlign="left"
        initialValues={{
          repeats: repeats || "weekly",
          repeatOn: repeatOn || [],
          repeatsEvery: repeatsEvery || 1,
          timezone: timezone || userTimezone,
          startsOn: startsOn?.isValid() ? startsOn : initialStartsOn(),
          repeatBy: repeatBy || repeateByMonthOptions[0].value,
          ends: ends || radioOptions[0].value,
          endsAfter: endsAfter || 35,
          endsOn: endsOn?.isValid() ? endsOn : initialEndsOn(),
        }}
      >
        <Form.Item
          label="Repeats"
          name="repeats"
          key="repeats"
          className="fields-font"
        >
          <Select
            className="select-dropdown"
            style={{ width: 120 }}
            options={repeatOptions}
          />
        </Form.Item>
        <Form.Item label="Repeats Every" key="repeatsEvery">
          <Form.Item name="repeatsEvery" noStyle>
            <Select
              className="select-dropdown"
              style={{ width: 120 }}
              virtual={false}
              options={repeatsEveryOptions}
            />
          </Form.Item>
          <span style={{ fontSize: 12, marginLeft: 8 }}>
            {repeateOptionObj
              ? repeateOptionObj.text +
                `(s) ${
                  repeateOptionObj.text === "week"
                    ? "(" +
                      scheduleForm.getFieldValue("repeatsEvery") +
                      " * 7 days)"
                    : ""
                }`
              : ""}
          </span>
        </Form.Item>
        <Form.Item
          className="repeaton"
          label="Repeat On"
          name="repeatOn"
          hidden={
            scheduleForm.getFieldValue("repeats") !== "weekly" ||
            (scheduleForm.getFieldValue("repeats") === "weekly" &&
              scheduleForm.getFieldValue("repeatsEvery") > 1)
          }
          key="repeatOn"
        >
          <Checkbox.Group>
            <Row>
              {days.map((day) => (
                <Checkbox key={day?.value} value={day?.value}>
                  {day?.title}
                </Checkbox>
              ))}
            </Row>
          </Checkbox.Group>
        </Form.Item>
        <Form.Item
          label="Repeat By"
          key="repeatBy"
          name="repeatBy"
          hidden={scheduleForm.getFieldValue("repeats") !== "monthly"}
        >
          <Radio.Group className="radio-btn">
            {repeateByMonthOptions.map((option) => (
              <Radio key={option.value} value={option.value}>
                {option.title}
              </Radio>
            ))}
          </Radio.Group>
        </Form.Item>
        <Form.Item label="Timezone" name="timezone" key="timezone">
          <Select
            className="select-dropdown"
            showSearch
            virtual={false}
            options={timezoneOptions}
          />
        </Form.Item>
        <Form.Item
          label="Starts On"
          name="startsOn"
          key="startsOn"
          className="no-click-label"
        >
          <DatePicker
            className="startson"
            allowClear={false}
            showTime
            format={dateFormat}
            disabledDate={disabledDate}
            disabledTime={(current) =>
              disabledTime(current, scheduleForm.getFieldValue("timezone"))
            }
            onSelect={(moment) => {
              scheduleForm.setFieldsValue({
                startsOn: moment,
              });
            }}
            showNow={false}
          />
        </Form.Item>
        <Form.Item
          label="Ends"
          name="ends"
          key="ends"
          style={{
            marginBottom:
              scheduleForm.getFieldValue("ends") === "never" ? 24 : 10,
          }}
        >
          <Radio.Group className="radio-btn">
            {radioOptions.map((option) => (
              <Radio key={option.value} value={option.value}>
                {option.title}
              </Radio>
            ))}
          </Radio.Group>
        </Form.Item>
        <Row
          align="middle"
          style={{
            marginLeft: "33%",
            marginBottom:
              scheduleForm.getFieldValue("ends") &&
              scheduleForm.getFieldValue("ends") === "after"
                ? 24
                : 0,
          }}
        >
          <Form.Item
            style={{ margin: 0 }}
            name="endsAfter"
            key="endsAfter"
            hidden={
              !(
                scheduleForm.getFieldValue("ends") &&
                scheduleForm.getFieldValue("ends") === "after"
              )
            }
          >
            {/* occurances */}
            <InputNumber min={1} max={99} />
          </Form.Item>
          {scheduleForm.getFieldValue("ends") &&
            scheduleForm.getFieldValue("ends") === "after" && (
              <div style={{ marginLeft: 8 }}>Occurences</div>
            )}
        </Row>
        <Form.Item
          name="endsOn"
          key="endsOn"
          hidden={
            !(
              scheduleForm.getFieldValue("ends") &&
              scheduleForm.getFieldValue("ends") === "on"
            )
          }
          style={{ marginLeft: "33%" }}
        >
          <DatePicker
            allowClear={false}
            showTime
            format={dateFormat}
            disabledDate={disabledDate}
            disabledTime={(current) =>
              disabledTime(current, scheduleForm.getFieldValue("timezone"))
            }
            onSelect={(moment) => {
              scheduleForm.setFieldsValue({
                endsOn: moment,
              });
            }}
          />
        </Form.Item>
        <Form.Item
          className="summary"
          label={[
            "Summary",
            <Tooltip
              title={repeatSummary[scheduleForm.getFieldValue("repeats")]}
              overlayClassName="custom-tooltip"
            >
              <InfoCircleOutlined
                style={{ marginLeft: 5, fontSize: 11, cursor: "pointer" }}
              />
            </Tooltip>,
          ]}
          labelWrap={true}
          fontSize={20}
          key="summaryText"
        >
          {summaryText}
        </Form.Item>
      </Form>
      <Space className="next-button">
        <Tooltip title={TOOLTIPS_INFO.backButton}>
          <Button
            onClick={() => setCurrent((prev) => prev - 1)}
            data-testid="back-button"
            disabled={loading}
          >
            <ArrowLeftOutlined />
          </Button>
        </Tooltip>
        <Button
          type="primary"
          onClick={handleSave}
          data-testid="save-options"
          loading={loading}
        >
          {isScheduleEditMode ? "Update Schedule" : "Schedule"}
        </Button>
      </Space>
    </>
  );
};

export default CustomScheduling;
export { disabledTime };
