import genrateUniqueJobName from "../../utils/genrateUniqueJobName";

describe("genrateUniqueJobName", () => {
  it("should generate a unique job name when allJobs is empty", () => {
    const result = genrateUniqueJobName([]);
    expect(result).toBe("Job 1");
  });

  it("should generate a unique job name when allJobs contains non-matching names", () => {
    const allJobs = [
      { chat_name: "Not a Job" },
      { chat_name: "Task 1" },
      { chat_name: "Job 2" },
    ];
    const result = genrateUniqueJobName(allJobs);
    expect(result).toBe("Job 3");
  });

  it("should generate a unique job name when allJobs contains matching names", () => {
    const allJobs = [{ chat_name: "Job 1" }, { chat_name: "Job 3" }];
    const result = genrateUniqueJobName(allJobs);
    expect(result).toBe("Job 4");
  });

  it("should generate a unique job name when allJobs contains mixed names", () => {
    const allJobs = [
      { chat_name: "Job 1" },
      { chat_name: "Task 2" },
      { chat_name: "Job 3" },
      { chat_name: "Job 5" },
    ];
    const result = genrateUniqueJobName(allJobs);
    expect(result).toBe("Job 6");
  });

  it("should generate a unique job name when allJobs contains improperly formatted names", () => {
    const allJobs = [{ chat_name: "Job 1" }, { chat_name: "Job ABC" }];
    const result = genrateUniqueJobName(allJobs);
    expect(result).toBe("Job 2");
  });
});
