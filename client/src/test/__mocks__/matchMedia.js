global.matchMedia =
  global.matchMedia ||
  function () {
    return {
      matches: true,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
    };
  };
