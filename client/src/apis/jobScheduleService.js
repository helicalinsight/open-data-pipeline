import axios from "./axios.js";
import { jobScheduleServiceConstants } from "./apiUrlConstants";

// http://localhost:5000 -------------> BASE URL for DAGS

// export files config
export async function exportConfig({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.exportConfig,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data || error || "");
  }
}

export async function dagRunStatus({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.dagRunStatus,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data || error || "");
  }
}

// triggering new DAG
export async function triggerDag({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.dag,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    console.log("err", error);
    onError(error?.response?.data || error || "");
  }
}

export async function getDagList({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.listDags,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
export async function getListTags({ userId, onSuccess, onError }) {
  try {
    const response = await axios.get(
      jobScheduleServiceConstants.listTags + "/" + userId,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function getIndividualDag({
  dagId,
  onSuccess,
  onError,
  current,
  pageSize,
  stateFilters = [],
  dateRange = [],
  sortField = "",
  sortOrder = "",
}) {
  try {
    let params = {
      page: current,
      per_page: pageSize,
    };
    if (stateFilters.length > 0) {
      params.state = stateFilters.join(",");
    }
    if (dateRange.length === 2) {
      const formatDateWithZ = (dateString) => {
        return `${dateString.replace(" ", "T")}Z`;
      };
      params.start_date = formatDateWithZ(dateRange[0]);
      params.end_date = formatDateWithZ(dateRange[1]);
    }
    if (sortField && sortOrder) {
      params.sort_field = sortField;
      params.sort_order = sortOrder;
    }
    const response = await axios.get(
      `${jobScheduleServiceConstants.individualDag}${dagId}`,
      {
        params,
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function deleteSchedule({ payload, onSuccess, onError }) {
  try {
    const response = await axios.delete(jobScheduleServiceConstants.delete, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
      data: JSON.stringify(payload),
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function runDag({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.runDag,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function pauseDag({ dagId, payload, onSuccess, onError }) {
  try {
    const response = await axios.patch(
      jobScheduleServiceConstants.dag + "/" + dagId,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
export async function updateScheduleDetails({ payload, onSuccess, onError }) {
  try {
    const response = await axios.patch(
      jobScheduleServiceConstants.updateSchedule,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function getDagLogs({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.dagLogs,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error.response.data);
  }
}

export async function getStreamLogs({ payload, onSuccess, onError }) {
  try {
    const response = await fetch(jobScheduleServiceConstants?.streamLogs, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
      body: JSON.stringify(payload),
    });

    // Check if the response supports streaming
    if (response.body && response.body.getReader) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let buffer = "";

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        lines.forEach((line) => {
          if (line.startsWith("data: ")) {
            const message = line.replace("data: ", "").trim();
            if (message) onSuccess(message + "\n");
          }
        });
      }

      if (buffer.trim()) {
        if (buffer.startsWith("data: ")) {
          const message = buffer.replace("data: ", "").trim();
          if (message) onSuccess(message + "\n");
        }
      }
    } else {
      // If streaming is not available, read the response as text directly
      const text = await response.text();
      onSuccess(text);
    }
  } catch (error) {
    console.error("Error during log streaming:", error);
    onError(error?.response?.data || error?.message);
  }
}

export async function downloadDagInfo({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.downloadDagInfo,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
        responseType: "blob",
      }
    );
    const contentType = response.headers["content-type"] || "";
    onSuccess(response.data, contentType);
  } catch (error) {
    onError(error.response?.data || error);
  }
}
export async function getCode({ chatId, onSuccess, onError }) {
  try {
    const response = await axios.get(
      jobScheduleServiceConstants.codeConfig + "/" + chatId,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function updateCode({ chatId, payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.codeConfig + "/" + chatId,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function runCode({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.runCode,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function triggerBot({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.pyspark,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function resetBot({ payload, onSuccess, onError }) {
  try {
    const response = await axios.post(
      jobScheduleServiceConstants.pysparkReset,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}




