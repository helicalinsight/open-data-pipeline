import { fileConstants, filesServiceConstants } from "./apiUrlConstants.js";
import axios from "./axios.js";

export async function getAllFilesApi({ payload, onError, onSuccess }) {
  try {
    const response = await axios.get(filesServiceConstants.getAllFiles, {
      // params: payload,
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    console.log(
      "error in getAllFiles function inside filesService.js file",
      error
    );
    onError(error?.response?.data || "");
  }
}

export async function deleteFile({ fileIds, onError, onSuccess }) {
  const url = filesServiceConstants.getAllFiles;
  try {
    const response = await axios.delete(url, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
      data: JSON.stringify({
        ids: fileIds,
      }),
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}

export async function renameFile({ payload, onError, onSuccess }) {
  try {
    const response = await axios.patch(
      filesServiceConstants.getAllFiles,
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
    onError(error?.response?.data || "");
  }
}

export async function uploadFileApi({
  key,
  formdata,
  onError,
  onSuccess,
  progressEvent,
  signal,
}) {
  const endPoint = key
    ? filesServiceConstants[key]
    : filesServiceConstants.getAllFiles;

  try {
    const response = await axios.post(endPoint, formdata, {
      signal,
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
      onUploadProgress: progressEvent,
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}

export async function downloadFileApi({
  chat_id,
  featherId,
  onError,
  onSuccess,
}) {
  try {
    const response = await axios.get(
      filesServiceConstants.download +
        "/" +
        featherId +
        "?" +
        "chat_id=" +
        chat_id,
      {
        responseType: "blob",
        headers: {
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    
    const contentType = response.headers['content-type'] || '';
    onSuccess(response.data, contentType);
  } catch (error) {
    console.log(
      "error in sendMessage function inside chatService.js file ",
      error
    );
    onError(error?.response?.data || "");
  }
}

export async function updateName({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(fileConstants.rename, payload, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}

export async function switchSelectedFile({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(fileConstants.cwf, payload, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response.data);
  } catch (error) {
    onError(error?.response?.data || "");
  }
}
export async function deleteDataPreviewFile({ payload, onSuccess, onError }) {
  try {
    const response = await axios.delete(filesServiceConstants.deleteFile, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
      data: payload,
    });
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
