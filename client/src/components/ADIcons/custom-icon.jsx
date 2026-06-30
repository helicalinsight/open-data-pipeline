import React from "react";
import Icon from "@ant-design/icons";
import {
  CsvSvg,
  Excel,
  GridSvg,
  MenuSvg,
  Search,
  EditSvg,
  DeleteSvg,
  AddCircle,
  Time,
  AskData,
  Google,
  LinkedIn,
  Github,
  QuestionSvg,
  ArrowSvg,
  Mongodb,
  Cassandra,
  AstraDB,
  MySQL,
  Postgresql,
  AmazonRedshift,
  Sequencefile,
  Folder,
  ApacheDrill,
  Snowflake,
  Bigquery,
  AmazonS3,
  TableSvg,
  Expression,
  SQL,
  BI,
  Undo,
  Redo,
  Firebird,
  DefaultSVG,
  OracleSVG,
  GoogleSheetsSVG,
  MicroSoftSQLServerSVG,
  CouchDBIcon,
  CouchbaseIcon,
  DatabricksIcon,
} from "./custom-svg";
import { excelTypeExtenstions } from "../../constants/appConstants";

const AskDataIcon = (props) => <Icon component={AskData} {...props} />;
const CsvIcon = (props) => <Icon component={CsvSvg} {...props} />;
const ExcelIcon = (props) => <Icon component={Excel} {...props} />;
const FolderIcon = (props) => <Icon component={Folder} {...props} />;
const GirdIcon = (props) => <Icon component={GridSvg} {...props} />;
const EditIcon = (props) => (
  <Icon component={() => <EditSvg color={props?.color} />} {...props} />
);
const DeleteIcon = (props) => (
  <Icon component={() => <DeleteSvg color={props?.color} />} {...props} />
);
const AddCircleIcon = (props) => <Icon component={AddCircle} {...props} />;
const TimeIcon = (props) => <Icon component={Time} {...props} />;
const GoogleIcon = (props) => <Icon component={Google} {...props} />;
const LinkedInIcon = (props) => <Icon component={LinkedIn} {...props} />;
const GithubIcon = (props) => <Icon component={Github} {...props} />;
const ArrowIcon = (props) => <Icon component={ArrowSvg} {...props} />;
const MenuIcon = (props) => (
  <Icon component={MenuSvg} {...props} className="cursor-pointer" />
);
const SearchIcon = (props) => <Icon component={Search} {...props} />;
const QuestionIcon = (props) => <Icon component={QuestionSvg} {...props} />;
const MongoDbIcon = (props) => <Icon component={Mongodb} {...props} />;
const CassandraIcon = (props) => <Icon component={Cassandra} {...props} />;
const AstraDBIcon = (props) => <Icon component={AstraDB} {...props} />;
const MySqlIcon = (props) => <Icon component={MySQL} {...props} />;
const PostgreSqlIcon = (props) => <Icon component={Postgresql} {...props} />;
const AmazonRedshiftIcon = (props) => (
  <Icon component={AmazonRedshift} {...props} />
);
const SequenceFileIcon = (props) => (
  <Icon component={Sequencefile} {...props} />
);
const ApacheDrillIcon = (props) => <Icon component={ApacheDrill} {...props} />;
const SnowflakeIcon = (props) => <Icon component={Snowflake} {...props} />;
const BigqueryIcon = (props) => <Icon component={Bigquery} {...props} />;
const AmazonS3Icon = (props) => <Icon component={AmazonS3} {...props} />;
const TableIcon = (props) => <Icon component={TableSvg} {...props} />;
const ExpressionIcon = (props) => <Icon component={Expression} {...props} />;
const SQLIcon = (props) => <Icon component={SQL} {...props} />;
const BIIcon = (props) => <Icon component={BI} {...props} />;
const UndoIcon = (props) => <Icon component={Undo} {...props} />;
const RedoIcon = (props) => <Icon component={Redo} {...props} />;
const FirebirdIcon = () => <Icon component={Firebird} />;
const OracleIcon = (props) => <Icon component={OracleSVG} {...props} />;
const CouchBaseIcon = (props) => <Icon component={CouchbaseIcon} {...props} />;
const CouchDatabaseIcon = (props) => (
  <Icon component={CouchDBIcon} {...props} />
);
const DataBricksIcon = (props) => (
  <Icon component={DatabricksIcon} {...props} />
);
const GoogleSheetIcon = (props) => (
  <Icon component={GoogleSheetsSVG} {...props} />
);
const MicroSoftSQLServerIcon = (props) => (
  <Icon component={MicroSoftSQLServerSVG} {...props} />
);
const DefaultIcon = (props) => <Icon component={DefaultSVG} {...props} />;

const CustomIcon = (props) => {
  const { name } = props;
  const isExcel = excelTypeExtenstions.includes(name);
  if (isExcel) {
    return <ExcelIcon {...props} />;
  }

  switch (name) {
    case "askData":
      return <AskDataIcon />;
    case "search":
      return <SearchIcon />;
    case "question":
      return <QuestionIcon />;
    case "folder":
      return <FolderIcon />;
    case "csv":
      return <CsvIcon {...props} />;
    case "table":
      return <TableIcon {...props} />;
    case "grid":
      return <GirdIcon />;
    case "menu":
      return <MenuIcon />;
    case "delete":
      return <DeleteIcon {...props} />;
    case "edit":
      return <EditIcon {...props} />;
    case "addCircle":
      return <AddCircleIcon />;
    case "time":
      return <TimeIcon />;
    case "google":
      return <GoogleIcon />;
    case "linkedIn":
      return <LinkedInIcon />;
    case "github":
      return <GithubIcon />;
    case "arrow":
      return <ArrowIcon />;
    case "Mongo db":
      return <MongoDbIcon />;
    case "Cassandra":
      return <CassandraIcon />;
    case "Astra":
      return <AstraDBIcon />;
    case "MySQL":
      return <MySqlIcon />;
    case "Postgres":
      return <PostgreSqlIcon />;
    case "Amazon Redshift":
      return <AmazonRedshiftIcon />;
    case "Flat Files":
      return <SequenceFileIcon />;
    case "Apache Drill":
      return <ApacheDrillIcon />;
    case "Firebird":
      return <FirebirdIcon />;
    case "Snowflake":
      return <SnowflakeIcon />;
    case "Google BigQuery":
      return <BigqueryIcon />;
    case "S3":
      return <AmazonS3Icon />;
    case "expression":
      return <ExpressionIcon {...props} />;
    case "sql":
      return <SQLIcon {...props} />;
    case "bi":
      return <BIIcon {...props} />;
    case "undo":
      return <UndoIcon {...props} />;
    case "redo":
      return <RedoIcon {...props} />;
    case "Oracle":
      return <OracleIcon {...props} />;
    case "Google Sheets":
      return <GoogleSheetIcon {...props} />;
    case "Microsoft SQL Server":
      return <MicroSoftSQLServerIcon {...props} />;
    case "Couchbase":
      return <CouchBaseIcon {...props} />;
    case "CouchDB":
      return <CouchDatabaseIcon {...props} />;
    case "Databricks":
      return <DataBricksIcon {...props} />;
    default:
      return <DefaultIcon {...props} />;
  }
};

export default CustomIcon;
