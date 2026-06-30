import { featureConstants } from "./apiUrlConstants.js";
import axios from "./axios.js";

export async function getApplication({ onSuccess, onError }) {
  try {
    const response = await axios.get(featureConstants.getApplication, {
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
