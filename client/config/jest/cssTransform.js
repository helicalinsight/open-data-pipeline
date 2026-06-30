"use strict";

module.exports = {
  process(src, filename, config, options) {
    const transformedCode = "module.exports = {};";

    return {
      code: transformedCode,
    };
  },
  getCacheKey() {
    // The output is always the same.
    return "cssTransform";
  },
};
