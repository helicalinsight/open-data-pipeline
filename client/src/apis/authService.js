import { authApiConstants } from "./apiUrlConstants.js";
import axios from "./axios.js";

export async function loginApi({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(authApiConstants.login, payload);
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}

export async function registerUserApi({ payload, onError, onSuccess }) {
  try {
    const response = await axios.post(authApiConstants.register, payload);
    onSuccess(response.data);
  } catch (error) {
    onError(error.response?.data);
  }
}
