import React from "react";
import "./style.scss";
import { ADSpace } from "../../components";
import { Button } from "antd";
import { getLocalStorageItem } from "../../utils/userData";
import { chatRoutes, userRoutes } from "../../router/uiRouteConstants";
import { useNavigate } from "react-router-dom";

function ErrorModule() {
  const { token } = getLocalStorageItem() || "";
  const navigate = useNavigate();

  const handleClick = () => {
    if (!token) {
      navigate(userRoutes.login);
    } else {
      navigate(chatRoutes.chat);
    }
  };

  return (
    <ADSpace
      justifyContent="center"
      alignItem="center"
      stack="vertical"
      className="page-not-found"
    >
      <h1>404</h1>
      <h4>Oops!! Page Not Found</h4>
      <p>Sorry, we couldn't find the page you are looking for</p>
      <Button type="primary" onClick={handleClick} data-testid="btn-id">
        {token ? "Return to Homepage" : "Login"}
      </Button>
    </ADSpace>
  );
}

export default ErrorModule;
