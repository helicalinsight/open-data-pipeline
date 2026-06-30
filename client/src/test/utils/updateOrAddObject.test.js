import { updateOrAddObject } from "../../utils/updateOrAddObject";

describe("updateOrAddObject function", () => {
  it("updates an existing object in the array based on condition", () => {
    const array = [
      { id: 1, name: "John" },
      { id: 2, name: "Jane" },
    ];

    const condition = (item) => item.id === 2;
    const newObject = { id: 2, name: "Updated Jane" };

    const result = updateOrAddObject(array, condition, newObject);

    expect(result).toEqual([
      { id: 1, name: "John" },
      { id: 2, name: "Updated Jane" },
    ]);
  });

  it("adds a new object to the array when condition is not met", () => {
    const array = [
      { id: 1, name: "John" },
      { id: 2, name: "Jane" },
    ];

    const condition = (item) => item.id === 3; // No object with id 3 exists
    const newObject = { id: 3, name: "New Person" };

    const result = updateOrAddObject(array, condition, newObject);

    expect(result).toEqual([
      { id: 1, name: "John" },
      { id: 2, name: "Jane" },
      { id: 3, name: "New Person" },
    ]);
  });

  it("returns the original array when condition is not met and no new object is provided", () => {
    const array = [
      { id: 1, name: "John" },
      { id: 2, name: "Jane" },
    ];

    const condition = (item) => item.id === 3; // No object with id 3 exists

    const result = updateOrAddObject(array, condition);

    expect(result).toEqual(array);
  });

  it("handles an empty array and adds a new object", () => {
    const array = [];
    const condition = () => true; // Condition always true
    const newObject = { id: 1, name: "New Person" };

    const result = updateOrAddObject(array, condition, newObject);

    expect(result).toEqual([{ id: 1, name: "New Person" }]);
  });
});
