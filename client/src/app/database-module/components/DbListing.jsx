import { useEffect, useState } from "react";
import { Card, Typography, Badge, Input, Select, Tooltip, Switch } from "antd";
import {
  setDataSourceNames,
  setSavedConnections,
  setSavedConnectionsApiStatus,
  setSelectedDatasourceAction,
} from "../../../store/actions/databaseActions";
import { useDispatch, useSelector } from "react-redux";
import { getSavedConnections } from "../../../apis/databaseService";
import { getAllFilesApi } from "../../../apis/fileService";
import { handleSessionExpiry } from "../../../utils/handleSessionExpiry";
import { checkIsPremiumFeature } from "../../../utils/isPremiumFeature";
import { CheckCircleFilled } from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import { chatRoutes, isDmsRoute } from "../../../router/uiRouteConstants";
// Safe capitalize function
const safeCapitalizeFirstLetter = (str) => {
  try {
    if (str == null || str === "") return "";
    const stringValue = String(str);
    return stringValue.charAt(0).toUpperCase() + stringValue.slice(1);
  } catch (error) {
    console.error("Error in capitalize function:", error, "Input:", str);
    return "";
  }
};

function DbListing({
  setCurrent,
  current,
  selectedItem,
  mode,
  openDbModal,
  sourceType,
  onItemSelect,
  destinationType,
  onDestItemSelect,
  selectedSourceType,
  selectedDestinationType,
}) {
  const location = useLocation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const datasources = useSelector((state) => state.database.datasources);
  const userConfig = useSelector((state) => state.app.userConfig);
  const [activeCategory, setActiveCategory] = useState("all");
  const [categoryItems, setCategoryItems] = useState([]);
  const [toggleStates, setToggleStates] = useState({});
  const isDms = isDmsRoute(location.pathname);

  const getFilteredDatasources = () => {
    if (selectedSourceType) {
      return datasources?.filter((ds) => ds.driver === selectedSourceType) || [];
    }
    if (selectedDestinationType) {
      return datasources?.filter((ds) => ds.driver === selectedDestinationType) || [];
    }
    return datasources;
  };

  const [dbListing, setDbListing] = useState(
    getFilteredDatasources()
  );

  useEffect(() => {
    let categoryTypes = [];
    const currentDatasources = getFilteredDatasources();
    if (sourceType || destinationType) {
      categoryTypes =
        currentDatasources
          ?.map((ele) => {
            if (!ele || !ele.categoryType) return null;
            if (typeof ele.categoryType === "object") {
              return ele.categoryType.value || ele.categoryType.label || null;
            }
            return ele.categoryType;
          })
          .filter(Boolean) || [];
    } else {
      categoryTypes =
        currentDatasources?.map((ele) => ele?.categoryType).filter(Boolean) || [];
    }
    const categoryGroup = [...new Set(categoryTypes)];
    const finalCategoryItems = [
      { key: "0", label: "all", value: "all" },
      ...categoryGroup.map((label, index) => ({
        key: String(index + 1),
        label: String(label),
        value: String(label),
      })),
    ];
    setCategoryItems(finalCategoryItems);
  }, [datasources, sourceType, destinationType, selectedSourceType]);

  // show datasource listings based on selected tab
  const filterDatasource = (label) => {
    const currentDatasources = getFilteredDatasources();
    if (label === "all") {
      setDbListing(currentDatasources);
    } else {
      if (sourceType || destinationType) {
        const filtered = currentDatasources?.filter((element) => {
          const elementCategoryType = element?.categoryType;
          if (typeof elementCategoryType === "object") {
            return (
              String(elementCategoryType?.value) === label ||
              String(elementCategoryType?.label) === label
            );
          }
          return String(elementCategoryType) === label;
        });
        setDbListing(filtered || []);
      } else {
        const filtered = currentDatasources?.filter(
          (element) => String(element?.categoryType) === label
        );
        setDbListing(filtered || []);
      }
    }
  };

  // clicking a datasource from the list
  const handleSelectedDB = (item) => {
    if (item?.available) {
      dispatch(setSelectedDatasourceAction(item));
      setCurrent(current + 1);
    }
  };

  // search change
  const handleSearchChange = (event) => {
    const { value } = event.target;
    const filterCondition = (element) =>
      element?.name?.toLowerCase().includes(value.toLowerCase());

    const baseDatasources = getFilteredDatasources();
    let result = [];
    if (sourceType || destinationType) {
      result =
        baseDatasources?.filter((element) =>
          activeCategory !== "all"
            ? (() => {
                const elementCategoryType = element?.categoryType;
                if (typeof elementCategoryType === "object") {
                  return (
                    (String(elementCategoryType?.value) === activeCategory ||
                      String(elementCategoryType?.label) === activeCategory) &&
                    filterCondition(element)
                  );
                }
                return (
                  String(elementCategoryType) === activeCategory &&
                  filterCondition(element)
                );
              })()
            : filterCondition(element)
        ) || [];
    } else {
      result =
        baseDatasources?.filter((element) =>
          activeCategory !== "all"
            ? String(element?.categoryType) === activeCategory &&
              filterCondition(element)
            : filterCondition(element)
        ) || [];
    }

    setDbListing(result.length > 0 ? result : []);
  };

  // onclick of group tabs
  const onTabChange = (item) => {
    setActiveCategory(item.label);
    filterDatasource(item.label);
  };

  // Handle toggle switch change
  const handleToggleChange = (itemId, checked) => {
    setToggleStates((prev) => ({
      ...prev,
      [itemId]: checked,
    }));
  };

  const handleSelect = (item) => {
    if (onItemSelect) {
      onItemSelect(item);
      localStorage.setItem("sourceTypeIcon", JSON.stringify(item));
      return;
    }
    if (onDestItemSelect) {
      onDestItemSelect(item);
      localStorage.setItem("DestinationTypeIcon", JSON.stringify(item));
      return;
    }
    dispatch(setDataSourceNames(item.name));
    const { driver } = item;
    const itemId = item?.driver;
    handleSelectedDB(item);
    dispatch(setSavedConnectionsApiStatus("FETCHING"));
    if (!openDbModal) {
      navigate(`${chatRoutes.datasource}/${itemId}`);
    }
    const onSuccess = (res) => {
      const data =
        (driver === "flat_files" ? res.filesList : res?.databases) || [];
      dispatch(setSavedConnections({ data }));
      dispatch(setSavedConnectionsApiStatus("SUCCESS"));
    };

    const onError = (error) => {
      handleSessionExpiry(dispatch, error);
      dispatch(setSavedConnectionsApiStatus("ERROR"));
    };

    if (driver === "flat_files") {
      getAllFilesApi({ onSuccess, onError });
    } else if (openDbModal) {
      const query = item.driver;
      getSavedConnections({ query, onSuccess, onError });
    }
  };

  useEffect(() => {
    setActiveCategory("all");
    setDbListing(getFilteredDatasources());
  }, [
    location.pathname,
    datasources,
    sourceType,
    destinationType,
    selectedSourceType,
    selectedDestinationType,
  ]);

  // Safe rendering of category items
  const renderCategoryItems = () => {
    return categoryItems.map((eachItem, index) => {
      const displayLabel = safeCapitalizeFirstLetter(eachItem?.label);

      return (
        <span
          data-testid="category-name-id"
          key={index}
          onClick={() => onTabChange(eachItem)}
          style={{
            color: activeCategory === eachItem.label && "rgb(242, 142, 30)",
          }}
          className="cursor-pointer category-item"
        >
          {displayLabel}
        </span>
      );
    });
  };

  // Safe options for Select
  const selectOptions = categoryItems?.map((item) => ({
    ...item,
    label: safeCapitalizeFirstLetter(item?.label),
  }));

  return (
    <div className=" text-center">
      {!isDms &&
      <div className="ant-drawer-body__search-wrapper dFlex justifyBetween alignCenter">
        <div className="category-select-container">
          <Select
            options={selectOptions}
            defaultValue={{ key: "0", label: "all", value: "all" }}
            onChange={(value) => filterDatasource(value)}
            style={{
              width: "100%",
            }}
            data-testid="category-select-id"
          />
        </div>

        <ul className="category-item-container">{renderCategoryItems()}</ul>

        <Input
          placeholder="Search datasource"
          onChange={handleSearchChange}
          allowClear
          className="search-container"
          icon={<CustomIcon name="search" />}
          data-testid="search-connectors"
        />
      </div>}

      <div className="card-wrapper">
        {dbListing && dbListing?.length > 0 ? (
          dbListing
            .map((item, index) => {
              const isPremium = checkIsPremiumFeature(
                userConfig,
                "datasources",
                item.driver
              );

              if (mode === "schedule") {
                if (selectedItem?.pipeline === "read_tables") {
                  if (item.driver === "flat_files") return null;
                }
                if (selectedItem?.pipeline === "read_files") {
                  if (item.driver !== "flat_files") return null;
                }
              }

              return (
                <div
                  key={index}
                  style={{
                    margin: "10px",
                    position: "relative",
                  }}
                >
                  {(sourceType || destinationType) && (
                    <div
                      style={{
                        position: "absolute",
                        left: "4px",
                        zIndex: 10,
                        borderRadius: "12px",
                      }}
                    >
                      {/* <Switch
                        size="small"
                        checked={toggleStates[item.driver] || false}
                        onChange={(checked) =>
                          handleToggleChange(item.driver, checked)
                        }
                        style={{
                          transform: "scale(0.8)",
                        }}
                      /> */}
                    </div>
                  )}
                  <Badge.Ribbon
                    text={item.available ? "Enterprise" : "Coming Soon"}
                    color={item.available ? "#152A4F" : "rgb(242, 142, 30)"}
                    className={item.available && !isPremium && "d-none"}
                  >
                    <Tooltip title={item?.name} placement="bottom">
                      <Card
                        key={index}
                        hoverable={item?.available && !isPremium ? true : false}
                        onClick={() => {
                          if (!item?.available) return;
                          handleSelect(item);
                        }}
                        data-testid={`data-connector-id`}
                      >
                        {item?.verified && item?.available && !isPremium && (
                          <CheckCircleFilled
                            className="checked-icon"
                            data-testid="verified"
                          />
                        )}
                        <div className="db-icon">
                          <CustomIcon name={item?.name} />
                        </div>
                        <p className="text-ellipsis">{item?.name}</p>
                      </Card>
                    </Tooltip>
                  </Badge.Ribbon>
                </div>
              );
            })
            .filter(Boolean)
            .reverse()
        ) : (
          <Typography className="no-connectors">
            No Connectors Found !!
          </Typography>
        )}
      </div>
    </div>
  );
}

export default DbListing;
