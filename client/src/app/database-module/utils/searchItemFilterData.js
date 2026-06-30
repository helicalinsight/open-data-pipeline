export const searchItemFilterData = (data, searchTerm = "") => {
  if (!searchTerm) return data;
  return data.filter((eachData) =>
    eachData.alias?.toLowerCase().includes(searchTerm.toLowerCase())
  );
};
