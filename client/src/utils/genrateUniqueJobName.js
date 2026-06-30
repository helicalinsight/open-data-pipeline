const genrateUniqueJobName = (allJobs) => {
  const numbers = allJobs
    .map(({ chat_name }) => chat_name.match(/^Job\s(\d+)$/))
    .filter((match) => match !== null)
    .map((match) => parseInt(match[1]));

  numbers.sort((a, z) => a - z);
  let jobName = "Job";
  if (numbers.at(-1)) {
    jobName = `${jobName} ${numbers.at(-1) + 1}`;
  } else if (jobName === "Job") {
    jobName = `${jobName} 1`;
  }
  return jobName;
};
export default genrateUniqueJobName;
