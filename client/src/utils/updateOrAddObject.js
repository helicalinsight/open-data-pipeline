export const updateOrAddObject = (array, condition, newObject) => {
  let found = false;

  // Iterate through the array to find and update the object
  array.forEach((item, index) => {
    if (condition(item)) {
      array[index] = { ...item, ...newObject };
      found = true;
    }
  });

  // If condition didn't match, add the new object to the array
  if (!found) {
    array.push(newObject);
  }

  return array;
};
