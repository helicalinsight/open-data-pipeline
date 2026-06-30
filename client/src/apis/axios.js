import axios from "axios";
import { baseApi } from "./apiUrlConstants.js";


const instance = axios.create({
  baseURL: baseApi.url,
});

// instance.interceptors.request.use((config) => {
//   const authToken = ""; //get auth-token
//   if (authToken) {
//     config.headers.Authorization = `Bearer ${authToken}`;
//   }
//   config.headers.po = performance.now();
//   return config;
// });

export default instance;
