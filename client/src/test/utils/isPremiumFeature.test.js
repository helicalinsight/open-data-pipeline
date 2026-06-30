import { checkIsPremiumFeature } from "../../utils/isPremiumFeature";

describe("checkIsPremiumFeature", () => {
  test("returns false when config is not provided", () => {
    const result = checkIsPremiumFeature(null, "module1", "feature1");
    expect(result).toBe(false);
  });

  test("returns false when module is not provided", () => {
    const result = checkIsPremiumFeature(
      { module1: ["feature1"] },
      null,
      "feature1"
    );
    expect(result).toBe(false);
  });

  test("returns false when name is not provided", () => {
    const result = checkIsPremiumFeature(
      { module1: ["feature1"] },
      "module1",
      null
    );
    expect(result).toBe(false);
  });

  test("returns false when module is not in the config", () => {
    const result = checkIsPremiumFeature(
      { module2: ["feature1"] },
      "module1",
      "feature1"
    );
    expect(result).toBe(false);
  });

  test("returns true when name is not in the module", () => {
    const result = checkIsPremiumFeature(
      { module1: ["feature2"] },
      "module1",
      "feature1"
    );
    expect(result).toBe(true);
  });

  test("returns false when all conditions are met", () => {
    const result = checkIsPremiumFeature(
      { module1: ["feature1"] },
      "module1",
      "feature1"
    );
    expect(result).toBe(false);
  });

  test("returns true when config, module, and name are valid but module has no features", () => {
    const result = checkIsPremiumFeature(
      { module1: [] },
      "module1",
      "feature1"
    );
    expect(result).toBe(true);
  });

  test("returns false when config, module, and name are valid but module features are undefined", () => {
    const result = checkIsPremiumFeature(
      { module1: undefined },
      "module1",
      "feature1"
    );
    expect(result).toBe(false);
  });
});
