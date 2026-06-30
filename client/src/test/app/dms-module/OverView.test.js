import React from "react";
import { render, screen } from "@testing-library/react";
import OverviewModule from "../../../app/dms-module/OverView";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { getDmsList } from "../../../apis/dmsService";
import { getLocalStorageItem } from "../../../utils/userData";
import { useLocation } from "react-router-dom";

jest.mock("../../../apis/dmsService");
jest.mock("../../../utils/userData");
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useLocation: jest.fn(),
}));

const createMockStore = () =>
  configureStore({
    reducer: () => ({}), 
  });
window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };

const renderWithStore = (ui) => {
  return render(<Provider store={createMockStore()}>{ui}</Provider>);
};

describe("OverviewModule", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    getLocalStorageItem.mockReturnValue({
      user: { id: "user123" },
    });
  });

  it("renders loading state", () => {
    useLocation.mockReturnValue({
      search: "?scheduleId=123",
    });
    getDmsList.mockImplementation(() => {});
    renderWithStore(<OverviewModule />);
  });

  it("renders error when no scheduleId", () => {
    useLocation.mockReturnValue({ search: "" });
    renderWithStore(<OverviewModule />);
  });

  it("renders pipeline details on success", () => {
    useLocation.mockReturnValue({
      search: "?scheduleId=123",
    });
    getDmsList.mockImplementation(({ onSuccess }) => {
      onSuccess([
        {
          schedule_id: "123",
          schedule_name: "Test Pipeline",
          migration_details: {
            migration_type: "Full",
            mode: "Auto",
            primary_key: "id",
          },
        },
      ]);
    });
    renderWithStore(<OverviewModule />);
  });
});
