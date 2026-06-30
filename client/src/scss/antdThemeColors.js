// REFER: https://ant.design/docs/react/migrate-less-variables
import { theme } from "antd";
const customTheme = {
  light: {
    algorithm: theme.defaultAlgorithm,
    token: {
      colorPrimary: "#152A4F",
      colorLink: "#152A4F", 
    },
    inherit: false,
    components: {
      Layout: {
        siderBg: "#152A4F",
      },
      Spin: {
        colorPrimary: "#F28E1E",
      },
      Button: {
        colorPrimary: "#152A4F",
      },
      Input: {
        colorPrimary: "#152A4F",
        colorPrimaryHover: "#152A4F",
        colorPrimaryActive: "#152A4F",
        controlOutline: "#ffffff",
      },
      Pagination: {
        itemSizeSM: 16,
        fontSize: 10,
        fontWeightStrong: 400,
        colorText: "#687182",
      },
      Result: {
        iconFontSize: 35,
        titleFontSize: 16,
      },
    },
  },
  dark: {
    algorithm: theme.darkAlgorithm,
    token: {
      // colorPrimary: "",
      // colorPrimaryBg: "",
    },
  },
};

export default customTheme;
