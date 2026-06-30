import { combineReducers, configureStore } from "@reduxjs/toolkit";
import {
  appReducer,
  chatReducer,
  messageReducer,
  databaseReducer,
  jobScheduleReducer,
  settingReducer,
} from "./reducers";
import auditReducer from "./reducers/auditReducer";
import dmsReducer from "./reducers/dmsReducer";

const reducer = combineReducers({
  app: appReducer,
  chat: chatReducer,
  messages: messageReducer,
  database: databaseReducer,
  jobSchedule: jobScheduleReducer,
  settings: settingReducer,
  audit: auditReducer,
  dms: dmsReducer,
});

const store = configureStore({
  reducer,
  // compose
  // middleware: () => {}, //thunk or saga middleware
});

export default store;
