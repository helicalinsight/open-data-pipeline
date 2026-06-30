import { useDispatch, useSelector } from "react-redux";
import CloseButton from "./CloseButton";
import handleBackClick from "../../../utils/handleClick";

function DbStepper({ current, items, steps, setCurrent, showCloseButton }) {
  const dispatch = useDispatch();
  const editConnection = useSelector((store) => store.database.editConnection);
  return (
    <>
      <div className="content-wrapper">{steps[current].content}</div>
    </>
  );
}

export default DbStepper;
