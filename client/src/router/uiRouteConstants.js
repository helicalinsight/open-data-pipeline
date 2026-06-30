export const userRoutes = {
  login: "/login",
  google: "/google",
  signup: "/signup",
  userSetup: "/user-setup",
};

export const chatRoutes = {
  chat: "/app-space",
  datasource: "/data-source",
  audit: "/audit",
  schedule: "/schedule",
  setting: "/setting",
  dms: "/dms",
  overview: "overview",
  createPipeline: "create-pipeline",
  objectSelect: "source",
  destinationObjectSelect: "destination",

};

export const errorRoute = "/error";

export const fileRoutes = {};
export const dmsPath = (...paths) => {
  return ["/dms", ...paths].join("/");
};

export const isDmsRoute = (pathname) => {
  if (!pathname) return false;
  return pathname === chatRoutes.dms || pathname.startsWith(`${chatRoutes.dms}/`);
};