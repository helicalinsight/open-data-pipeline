export const checkIsPremiumFeature = (config, module, name) => {
  if (!config || !module || !name || !config[module]) return false;
  return !config[module].includes(name);
};
