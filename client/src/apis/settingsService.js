import { preferencesConstants } from "./apiUrlConstants.js";
import axios from "./axios.js";

export async function getPreferences({ onError, onSuccess }) {
  try {
    const response = await axios.get(preferencesConstants.preferences, {
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}

export async function postPreferences({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      preferencesConstants.preferences,
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
    onError(error?.response?.data);
  }
}

export async function createGenerateKey({ onSuccess, onError, payload }) {
  try {
    const response = await axios.post(
      preferencesConstants.generateKey,
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
    onError(error?.response?.data);
  }
}

export async function getGenerateKey({ onError, onSuccess,payload }) {
  try {
    const response = await axios.get(preferencesConstants.generateKey,
     {
      params: payload,
      headers: {
        "Content-Type": "application/json",
        Authorization: JSON.parse(localStorage.getItem("user")).token,
      },
    });
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}
export async function deleteGenerateKey({ onSuccess, onError, payload }) {
  try {
    const response = await axios.delete(
      preferencesConstants.generateKey,
      {
        params: payload, 
        headers: {
          "Content-Type": "application/json",
          Authorization: JSON.parse(localStorage.getItem("user")).token,
        },
      }
    );
    onSuccess(response?.data);
  } catch (error) {
    onError(error?.response?.data);
  }
}