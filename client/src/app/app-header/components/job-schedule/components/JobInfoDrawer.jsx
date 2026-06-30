import { Drawer, Segmented } from "antd";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import RenderMarkDown from "../../../../database-module/components/RenderMarkDown";

const defaultOptions = [
  { label: "Python", value: "python" },
  { label: "YAML", value: "yaml" },
  { label: "Job Arguments", value: "job_arguments"}
];

const JobInfoDrawer = ({ open, setOpenInfo, mode }) => {
  const [value, setValue] = useState(mode);
  const [options, setOptions] = useState(defaultOptions);
  const [description, setDescription] = useState("");
  const jobHelpInfo = useSelector((store) => store.app.jobHelpInfo);
  useEffect(() => {
    setDescription(jobHelpInfo[value]);
  }, [value]);

  useEffect(() => {
    if (mode) {
      const filteredOptions = defaultOptions.filter(
        ({ value }) => value === mode
      );
      setOptions(filteredOptions);
      setValue(mode)
    }
  }, [mode]);

  return (
    <Drawer
      open={open}
      onClose={() => setOpenInfo(false)}
      destroyOnClose={true}
      width={"54%"}
      title={
        <Segmented
          options={options}
          value={value}
          onChange={setValue}
          size="small"
        />
      }
    >
      <div>
        <RenderMarkDown description={description} />
      </div>
    </Drawer>
  );
};

export default JobInfoDrawer;
