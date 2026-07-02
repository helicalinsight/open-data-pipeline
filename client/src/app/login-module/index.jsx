import axios from "axios";
import { Button, Form, message, Input } from "antd";
import { useEffect, useState } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import { setLocalStorageItem } from "../../utils/userData";
import { useNavigate } from "react-router-dom";
import { userRoutes } from "../../router/uiRouteConstants";
import { loginApi } from "../../apis/authService";
import { CLIENT_ID, imagePath } from "../../constants/appConstants";
import { baseApi } from "../../apis/apiUrlConstants";
import CustomIcon from "../../components/ADIcons/custom-icon";
import "./index.scss";
import CustomMessage from "../settings-module/CustomMessage";
import { dispatchMessage } from "../../utils/handleClick";
import { useDispatch, useSelector } from "react-redux";

const isDevEnv = process.env.REACT_APP_SERVER_ENVIRONMENT === "dev";
const isLocalEnv = process.env.REACT_APP_SERVER_ENVIRONMENT === "local";

const GoogleSignInButton = ({ onSuccess }) => {
  const handleGoogleLogin = useGoogleLogin({
    onSuccess,
    onError: (error) => console.log("Login Failed:", error),
  });

  return (
    <Button
      block
      className="google-btn"
      onClick={handleGoogleLogin}
      icon={<CustomIcon name="google" />}
    >
      <span>Sign In With Google</span>
    </Button>
  );
};

const LoginPage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState();
  const [profile, setProfile] = useState();
  const [messageApi, contextHolder] = message.useMessage();
  const [loginStatus, setLoginStatus] = useState("");
  const messageData = useSelector((store) => store?.settings?.messageData);
  const dispatch = useDispatch();

  useEffect(() => {
    if (user) {
      axios
        .get(
          `https://www.googleapis.com/oauth2/v1/userinfo?access_token=${user.access_token}`,
          {
            headers: {
              Authorization: `Bearer ${user.access_token}`,
              Accept: "application/json",
            },
          }
        )
        .then((res) => {
          setProfile(res.data);
        })
        .catch((err) => console.log(err));
    }
  }, [user]);

  useEffect(() => {
    if (profile) {
      handleLogin();
    }
  }, [profile]);

  useEffect(() => {
    if (loginStatus === "FETCHING") {
      dispatchMessage(
        dispatch,
        "info",
        "Logging you in. Please wait..."
      );
    }
  }, [loginStatus, dispatch]);

  const onLoginSuccess = (data) => {
    const userData = {
      ...data,
      user: { ...profile, id: data.userid, ...(data.users || {}) },
    };
    setLocalStorageItem(userData);
    navigate(userRoutes.userSetup);
    setLoginStatus("SUCCESS");
  };

  const onLoginError = (err) => {
    setLoginStatus("FAILED");
    dispatchMessage(
      dispatch,
      "error",
      "Incorrect username or password. Please try again"
    );
  };

  const handleLogin = () => {
    setLoginStatus("FETCHING");
    loginApi({
      payload: profile,
      onSuccess: (data) => onLoginSuccess(data),
      onError: (err) => onLoginError(err),
    });
  };

  const onFinish = async (values) => {
    try {
      const response = await axios.post(`${baseApi.url}login`, values);
      if (response.data.success) {
        onLoginSuccess(response.data);
      }
    } catch (error) {
      onLoginError(error);
    }
  };

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
  };

  const handleSignUpNavigation = () => {
    navigate(userRoutes.signup);
  };
  return (
    <>
      {contextHolder}
      <div className="login-main-container">
        <div className="top-left-text">
          <h1 className="askondata-text">Ask On Data</h1>
          <sup>
            <img
              src={`${imagePath}/favicon.svg`}
              className="aod-logo"
              alt="logo"
            />
          </sup>
        </div>
        {messageData && (
          <div className="message-container">
            <CustomMessage
              type={messageData.type}
              message={messageData.message}
            />
          </div>
        )}
        <div className="login-box">
          <h2 className="sign-in-heading">Sign In</h2>
          {isDevEnv || isLocalEnv ? (
            <Form
              name="basic"
              initialValues={{ remember: false }}
              onFinish={onFinish}
              onFinishFailed={onFinishFailed}
              requiredMark={false}
              className="login-form"
            >
              <Form.Item
                name="email"
                label="Email"
                rules={[
                  { required: true, message: "Please input your email!" },
                ]}
                labelCol={{ span: 24 }}
              >
                <Input placeholder="Enter your Email" />
              </Form.Item>
              <Form.Item
                name="password"
                label="Password"
                rules={[
                  { required: true, message: "Please input your password!" },
                ]}
                labelCol={{ span: 24 }}
              >
                <Input.Password placeholder="Enter your Password" />
              </Form.Item>
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  block
                  className="login-btn"
                  style={{ marginBottom: "-14px" }}
                >
                  Sign In
                </Button>
              </Form.Item>
              {CLIENT_ID && (
                <>
                  <div className="divider">
                    <span>OR</span>
                  </div>
                  <GoogleSignInButton
                    onSuccess={(codeResponse) => setUser(codeResponse)}
                  />
                </>
              )}
            </Form>
          ) : (
            CLIENT_ID && (
              <GoogleSignInButton
                onSuccess={(codeResponse) => setUser(codeResponse)}
              />
            )
          )}
          {(isDevEnv || isLocalEnv) && (
            <div className="signup-prompt">
              Don't have an account?{" "}
              <a onClick={handleSignUpNavigation} className="signup-link">
                Sign Up
              </a>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default LoginPage;