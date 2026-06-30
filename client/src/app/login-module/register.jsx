import axios from "axios";
import { Button, Form, message, Input, Row, Col } from "antd";
import { useState } from "react";
import { setLocalStorageItem } from "../../utils/userData";
import { useNavigate } from "react-router-dom";
import { userRoutes } from "../../router/uiRouteConstants";
import { imagePath } from "../../constants/appConstants";
import { baseApi } from "../../apis/apiUrlConstants";
import "./index.scss";
import { CloseOutlined } from "@ant-design/icons";
import { dispatchMessage } from "../../utils/handleClick";
import { useDispatch, useSelector } from "react-redux";
import CustomMessage from "../settings-module/CustomMessage";

const RegisterPage = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState();
  const [messageApi, contextHolder] = message.useMessage();
  const [loginStatus, setLoginStatus] = useState("");
  const dispatch = useDispatch();
  const messageData = useSelector((store) => store?.settings?.messageData);

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
  };

  const onFinish = async (values) => {
    try {
      const response = await axios.post(`${baseApi.url}register`, values);
      if (response.data.success) {
        dispatchMessage(
          dispatch,
          "success",
          response?.data?.msg || "Registration successful!"
        );
        onLoginSuccess(response.data);
      }
    } catch (error) {
      onLoginError(error);
      dispatchMessage(
        dispatch,
        "error",
        error?.response?.data?.msg || "Already Registered."
      );
    }
  };

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
  };

  const handleSignIn = () => {
    navigate(userRoutes.login);
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
          <div className="message-container" style={{ margin: "10px" }}>
            <CustomMessage
              type={messageData.type}
              message={messageData.message}
            />
          </div>
        )}
        <div className="login-box">
          <CloseOutlined className="close-icon" onClick={handleSignIn} />
          <h2 className="sign-in-heading">Sign Up</h2>
          <Form
            name="basic"
            initialValues={{ remember: false }}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            requiredMark={false}
            className="login-form"
          >
            <Row gutter={16}>
              <Col span={12} style={{ marginBottom: "4px" }}>
                <Form.Item
                  label="First Name"
                  name="name"
                  rules={[
                    {
                      required: true,
                      message: "First name is required!",
                    },
                  ]}
                  labelCol={{ span: 24 }}
                >
                  <Input placeholder="Enter your First Name" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="Last Name"
                  name="family_name"
                  labelCol={{ span: 24 }}
                  rules={[
                    {
                      required: true,
                      message: "Last name is required!",
                    },
                  ]}
                >
                  <Input placeholder="Enter your Last Name" />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item
              name="email"
              label="Email"
              rules={[
                {
                  required: true,
                  message: "Email is required!",
                },
                {
                  pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                  message: "Please enter a valid email (e.g  user@example.com)",
                },
              ]}
              labelCol={{ span: 24 }}
            >
              <Input placeholder="Enter your Email" />
            </Form.Item>
            <Form.Item
              name="password"
              label="Password"
              rules={[{ required: true, message: "Password is required!" }]}
              labelCol={{ span: 24 }}
            >
              <Input.Password placeholder="Enter your Password" />
            </Form.Item>
            <Form.Item
              name="confirm"
              label="Confirm Password"
              dependencies={["password"]}
              labelCol={{ span: 24 }}
              rules={[
                {
                  required: true,
                  message: "Confirm password is required!",
                },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue("password") === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(
                      new Error("The two passwords do not match!")
                    );
                  },
                }),
              ]}
            >
              <Input.Password placeholder="Enter your Confirm Password" />
            </Form.Item>
            <Form.Item>
              <Button
                data-testid="sign-up-button"
                type="primary"
                htmlType="submit"
                block
                className="login-btn"
              >
                Sign Up
              </Button>
            </Form.Item>
          </Form>
          <div className="signup-prompt">
            Already have an account?{" "}
            <a onClick={handleSignIn} className="signup-link">
              Sign In
            </a>
          </div>
        </div>
      </div>
    </>
  );
};
export default RegisterPage;
