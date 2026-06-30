import React from "react";
import { Tooltip } from "antd";
import { useSelector } from "react-redux";
import { checkIsPremiumFeature } from "../../utils/isPremiumFeature";
import "./index.scss";

const PremiumFeatureWrapper = (props) => {
  const { children, module, feature, tooltip } = props;
  const userConfig = useSelector((state) => state?.app?.userConfig);
  const isPremium = checkIsPremiumFeature(userConfig, module, feature);

  if (isPremium) {
    const enhancedChildren = React.Children.map(children, (child) => {
      return React.cloneElement(child, {
        disabled: true,
        className: `${child.props.className || ""} ${
          "blurred-icon items-center" || ""
        }`.trim(),
        onClick: (e) => {
          e.stopPropagation();
          e.preventDefault();
        },
      });
    });

    return (
      <div className="items-center" data-testid="premium">
        <Tooltip
          title={`${tooltip?.title} : Upgrade to use this feature`}
          placement={tooltip?.placement && tooltip.placement}
          data-testid="premium"
          fresh={true}
        >
          {enhancedChildren}
        </Tooltip>
      </div>
    );
  }

  return (
    <div className="items-center" data-testid="children">
      {tooltip?.title === "File Size" ? (
        children
      ) : (
        <Tooltip
          title={tooltip?.title}
          placement={tooltip?.placement}
          fresh={true}
        >
          {children}
        </Tooltip>
      )}
    </div>
  );
};

export default PremiumFeatureWrapper;
