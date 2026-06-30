import { Switch } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { setSelectedExtensions } from "../../../store/actions/appActions";
import { appSuggestionsData } from "../../../constants/appConstants";
import CustomIcon from "../../../components/ADIcons/custom-icon";
import "./Extensions.scss";

const Extensions = () => {
  const dispatch = useDispatch();
  const selectedExtensions = useSelector(
    (store) => store.app?.selectedExtensions
  );

  const handleToggleExntensions = (value, isSelected) => {
    dispatch(setSelectedExtensions({ value, isSelected }));
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100%",
      }}
      className="items-center"
    >
      {appSuggestionsData.map((eachData) => {
        const { extension, value, title, description } = eachData;
        return (
          <div className="extensions-conatiner" key={extension}>
            <div className="icons-container">
              <CustomIcon name={value} style={{ fontSize: "30px" }} />
              <Switch
                checked={selectedExtensions?.includes(value)}
                onChange={(e) => handleToggleExntensions(value, e)}
                data-testid="extension-switch"
              />
            </div>
            <span className="header">{title}</span>
            <p className="sub-header-db">{extension}</p>
            <p className="description-extensions">{description}</p>
          </div>
        );
      })}
    </div>
  );
};

export default Extensions;
