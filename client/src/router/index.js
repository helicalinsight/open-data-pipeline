import {
  Navigate,
  createHashRouter,
  Outlet,
  useLocation,
} from "react-router-dom";
import { userRoutes, chatRoutes } from "./uiRouteConstants";
import CreateSession from "../app/chat-module/CreateSession";
import ErrorModule from "../app/error-module";
import LoginPage from "../app/login-module";
import ChatModule from "../app/chat-module";
import RegisterPage from "../app/login-module/register";
import DataBaseModule from "../app/database-module";
import AuditModule from "../app/audit-module";
import JobScheduleModule from "../app/job-schedule-module";
import SettingsModule from "../app/settings-module";
import ADSpace from "../components/ADSpace";
import { Layout } from "antd";
import Sidebar from "../app/sidebar";
import JobViewHeader from "../app/app-header";
import DbConnect from "../app/database-module/components/DbConnect";
import { getLocalStorageItem } from "../utils/userData";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { resetRedux } from "../store/actions/sessionActions";
import { ADModal } from "../components/ADModal";
import MigrationModule from "../app/dms-module/MigrationModule";
import ObjectSelectionModule from "../app/dms-module/ObjectSelection";
import OverviewModule from "../app/dms-module/OverView";
import DestinationModule from "../app/dms-module/DestinationModule";
import { useEffect, useState } from "react";
import DmsModule from "../app/dms-module/DmsModule";

const routeRegex = new RegExp(
  `^(${[...Object.values(userRoutes), ...Object.values(chatRoutes)]
    .filter(Boolean)
    .map((route) => route.replace(/^\//, ""))
    .join("|")})(\/.*)?$`,
);

const useHashNormalizer = () => {
  const [isNormalizing, setIsNormalizing] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isNormalizing) return;
    const currentPath = window.location.href;
    const url = new URL(currentPath);
    const needsNormalization = shouldNormalizeUrl(url);
    if (needsNormalization) {
      setIsNormalizing(true);
      const normalizedUrl = getNormalizedUrl(url);
      window.history.replaceState(null, "", normalizedUrl);
      const hashPath = normalizedUrl.split("#")[1] || "";
      navigate(hashPath, { replace: true });
    }
  }, [location.pathname]);
  return isNormalizing;
};

const shouldNormalizeUrl = (url) => {
  const pathname = url.pathname;
  const hash = url.hash;
  if (
    pathname &&
    pathname !== "/" &&
    pathname !== "/index.html" &&
    !pathname.includes(".") &&
    !hash.includes(pathname.replace(/^\//, ""))
  ) {
    return true;
  }
  return false;
};

const getNormalizedUrl = (url) => {
  const origin = url.origin;
  const pathname = url.pathname;
  const search = url.search;
  const hash = url.hash;
  const cleanPath = pathname.replace(/^\//, "");
  if (routeRegex.test(cleanPath)) {
    let newHash = `/${cleanPath}`;
    if (hash && hash !== "#") {
      const existingHash = hash.replace(/^#/, "");
      if (existingHash && !existingHash.startsWith("/")) {
        newHash = `${newHash}/${existingHash}`;
      } else if (existingHash && existingHash.startsWith("/")) {
        newHash = existingHash;
      }
    }
    return `${origin}/index.html#${newHash}${search}`;
  }
  return url.toString();
};

const AppWithNormalizer = () => {
  const isNormalizing = useHashNormalizer();
  if (isNormalizing) {
    return <div style={{ display: "none" }}>Normalizing URL...</div>;
  }
  return <Outlet />;
};

const RequireAuth = ({ children }) => {
  const user = getLocalStorageItem();
  const location = useLocation();
  if (!user) {
    return (
      <Navigate to={userRoutes.login} state={{ from: location }} replace />
    );
  }
  return children;
};

// Session Expired
export const SessionExpiredModal = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const isSessionExpired = useSelector((state) => state.app.isSessionExpired);
  const handleOk = () => {
    dispatch(resetRedux());
    navigate(userRoutes.login);
  };
  return (
    <ADModal
      iconName="time"
      title="Session expired"
      open={isSessionExpired}
      description={
        <div style={{ textAlign: "center" }}>
          Your session has expired. Please log in again.
        </div>
      }
      okText="Login"
      onOk={handleOk}
      showCancelButton={false}
      hideButtons={false}
      data-testid="session-modal"
    />
  );
};

const LayoutWrapper = () => {
  return (
    <>
      <Layout className="job-view-main-container overflowHidden h-100-vh">
        <ADSpace>
          <Sidebar />
          <ADSpace
            stack="vertical"
            style={{ backgroundColor: "white" }}
            className="job-view-wrapper flex-1"
          >
            <JobViewHeader />
            <Outlet />
          </ADSpace>
        </ADSpace>
      </Layout>
      <SessionExpiredModal />
    </>
  );
};

const router = createHashRouter([
  {
    element: <AppWithNormalizer />,
    children: [
      {
        element: <LayoutWrapper />,
        children: [
          {
            path: userRoutes.userSetup,
            element: (
              <RequireAuth>
                <CreateSession />
              </RequireAuth>
            ),
          },
          {
            path: chatRoutes.chat,
            element: (
              <RequireAuth>
                <ChatModule />
              </RequireAuth>
            ),
          },
          {
            path: `${chatRoutes.datasource}/:id`,
            element: (
              <RequireAuth>
                <DbConnect />
              </RequireAuth>
            ),
          },
          {
            path: chatRoutes.datasource,
            element: (
              <RequireAuth>
                <DataBaseModule />
              </RequireAuth>
            ),
          },
          {
            path: chatRoutes.audit,
            element: (
              <RequireAuth>
                <AuditModule />
              </RequireAuth>
            ),
          },
          {
            path: chatRoutes.schedule,
            element: (
              <RequireAuth>
                <JobScheduleModule />
              </RequireAuth>
            ),
          },
          {
            path: chatRoutes.setting,
            element: (
              <RequireAuth>
                <SettingsModule />
              </RequireAuth>
            ),
          },
          {
            path: chatRoutes.dms,
            children: [
              {
                index: true,
                element: (
                  <RequireAuth>
                    <DmsModule />
                  </RequireAuth>
                ),
              },
              {
                path: chatRoutes.overview,
                element: (
                  <RequireAuth>
                    <OverviewModule />
                  </RequireAuth>
                ),
              },
              {
                path: chatRoutes.createPipeline,
                children: [
                  {
                    index: true,
                    element: (
                      <RequireAuth>
                        <MigrationModule />
                      </RequireAuth>
                    ),
                  },
                  {
                    path: chatRoutes.objectSelect,
                    children: [
                      {
                        index: true,
                        element: (
                          <RequireAuth>
                            <ObjectSelectionModule />
                          </RequireAuth>
                        ),
                      },
                      {
                        path: chatRoutes.destinationObjectSelect,
                        element: (
                          <RequireAuth>
                            <DestinationModule />
                          </RequireAuth>
                        ),
                      },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        path: userRoutes.login,
        element: <LoginPage />,
      },
      {
        path: userRoutes.signup,
        element: <RegisterPage />,
      },
      {
        path: "/",
        element: <Navigate to={userRoutes.login} replace />,
      },
      {
        path: "*",
        element: <ErrorModule />,
      },
    ],
  },
]);

export default router;