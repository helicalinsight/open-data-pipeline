import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import store from "./store";
import "./scss/style.scss";
import { App, ConfigProvider } from "antd";
import { RouterProvider } from "react-router-dom";
import router from "./router";
import customTheme from "./scss/antdThemeColors";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { CLIENT_ID } from "./constants/appConstants";

//for dev server only
const mode = process.env?.REACT_APP_MODE;
if (mode && mode === "dev") {
  window.store = store;
}
const root = ReactDOM.createRoot(document.getElementById("root"));

const app = (
  <Provider store={store}>
    <ConfigProvider theme={customTheme.light}>
      <App>
        <RouterProvider router={router} />
      </App>
    </ConfigProvider>
  </Provider>
);

root.render(
  CLIENT_ID ? (
    <GoogleOAuthProvider clientId={CLIENT_ID}>{app}</GoogleOAuthProvider>
  ) : (
    app
  )
);
