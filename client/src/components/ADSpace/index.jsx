import React from "react";
import cx from "classnames";
import "./styles.scss";

const ADSpace = ({
  children,
  space = "0",
  as: Component = "div",
  stack = "horizontal",
  alignItem,
  flexWrap = "nowrap",
  justifyContent,
  flexDirection = stack === "horizontal" ? "row" : "column",
  className,
  ...rest
}) => {
  const spaceClassname = cx({
    "ad-space": true,
    [`ad-space__${stack}`]: true,
    [`ad-space__${stack}__${flexDirection}`]: true,
    [`ad-space__${stack}__${flexDirection}__${space}`]: true,
    [`ad-space__align-item--${alignItem}`]: Boolean(alignItem),
    [`ad-space__justify-content--${justifyContent}`]: Boolean(justifyContent),
    [`ad-space__flex-wrap--${flexWrap}`]: true,
    [className]: Boolean(className),
  });

  return (
    <Component className={spaceClassname} {...rest}>
      {children}
    </Component>
  );
};

export default ADSpace;
