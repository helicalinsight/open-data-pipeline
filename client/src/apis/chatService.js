import {
  chatServiceConstants,
  completionAPIURL,
  previewFileConstants,
} from "./apiUrlConstants.js";
import axios from "./axios.js";

export async function createChat({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(chatServiceConstants.chat, payload, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

export async function getAllJobsApi({ onError, onSuccess,params = {} }) {
  try {
    const response = await axios.get(chatServiceConstants.chat, {
      params: params, 
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}
export async function updateChat({ payload, onError, onSuccess }) {
  const { name, chat_id } = payload;
  try {
    const url = chatServiceConstants.chat + "/" + chat_id;

    const response = await axios.patch(
      url,
      {
        chat_name: name,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);

    if (error.response?.data?.msg === "Token is invalid") {
      window.location.href = "/login";
    }
  }
}
export async function updateJobMode({ payload, onError, onSuccess }) {
  const { name, chatId } = payload;
  try {
    const url = chatServiceConstants.jobMode + "/" + chatId;

    const response = await axios.patch(
      url,
      {
        job_mode: name,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}
export async function deleteChat({ chatId, onError, onSuccess }) {
  try {
    const url = chatServiceConstants.chat + "/" + chatId;
    const response = await axios.delete(url, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

export async function sendMessage({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(
      chatServiceConstants.sendMessage,
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
    console.log(
      "error in sendMessage function inside chatService.js file ",
      error
    );
    onError(error.response?.data);
  }
}

export async function dataPreview({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(
      previewFileConstants.previewFile,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data?.preview);
  } catch (error) {
    onError(error.response?.data);
  }
}

export async function chatHistoryApi({ chatId, params, onError, onSuccess }) {
  try {
    const response = await axios.get(
      chatServiceConstants.chatHistory + "/" + chatId,
      {
        params: { ...params },
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

export async function getInformationApi({ query, onError, onSuccess }) {
  try {
    const response = await axios.get(
      chatServiceConstants.getInformation + "?" + query,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

//api calling for job history pipeline
export async function pipelineHistoryApi({ query, onError, onSuccess }) {
  try {
    const response = await axios.get(
      chatServiceConstants.pipelineHistory + "?" + query,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

// clear chat history
export async function clearChatMessageHistory({ chatId, onError, onSuccess }) {
  try {
    const url = chatServiceConstants.chatHistory + "/" + chatId;
    const response = await axios.delete(url, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

// undo pipleine history
export async function undoPipelineHistory({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(
      chatServiceConstants.undoPipelineHistory,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

// redo pipleine history
export async function redoPipelineHistory({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(
      chatServiceConstants.redoPipelineHistory,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

export async function completionApi({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(completionAPIURL, payload, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}
