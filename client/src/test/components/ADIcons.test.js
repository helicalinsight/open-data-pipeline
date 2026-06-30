import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import CustomIcon from "../../components/ADIcons/custom-icon";

const customIconArray = [
  "askData",
  "search",
  "question",
  "csv",
  "grid",
  "menu",
  "delete",
  "xls",
  "folder",
  "edit",
  "addCircle",
  "time",
  "google",
  "linkedIn",
  "github",
  "arrow",
  "Amazon Redshift",
  "Flat Files",
  "Mongo db",
  "Cassandra",
  "Astra",
  "MySQL",
  "Postgres",
  "Apache Drill",
  "Snowflake",
  "Google BigQuery",
  "S3",
  "table",
  "default"
];

describe("CustomIcon component", () => {
  it("renders the component with passed prop name without errors", () => {
    customIconArray.forEach((icon) => {
      render(<CustomIcon name={icon} />);
    });
  });
});
