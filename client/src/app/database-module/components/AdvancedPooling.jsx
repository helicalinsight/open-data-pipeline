import { Divider } from "antd";

import KeyValueForm from "../../app-header/components/key-value/KeyValueForm";
import KeyValueTable from "../../app-header/components/key-value/KeyValueTable";

const AdvancedPooling = ({ poolingData, setPoolingData, poolingOn ,handleFinish,loading,values}) => {  
  const onAdd = (data) => {
    setPoolingData((prev) => {
      return {
        ...prev,
        [poolingOn]: [...prev[poolingOn], data],
      };
    });
  };

  const onDelete = (record) => {
    setPoolingData((prev) => {
      const updated = prev[poolingOn].filter((data) => data.key !== record.key);

      return {
        ...prev,
        [poolingOn]: updated,
      };
    });
  };

  const onEdit = (data) => {
    setPoolingData((prev) => {
      return {
        ...prev,
        [poolingOn]: data,
      };
    });
  };

  return (
    <>
      <Divider />
      <KeyValueForm keyValueData={poolingData[poolingOn]} onAdd={onAdd} />
      <KeyValueTable
        dataSource={poolingData[poolingOn]}
        onDelete={onDelete}
        onEdit={onEdit}
        handleFinish={handleFinish}
        loading={loading}
        values={values}
        visible="true"
      />
    </>
  );
};

export default AdvancedPooling;
