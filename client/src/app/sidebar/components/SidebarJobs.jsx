import { memo, useMemo, useState } from "react";
import { ADSpace } from "../../../components/";
import SidebarEachJob from "./SidebarEachJob";
import { FixedSizeList, areEqual } from "react-window";
import memoize from "memoize-one";
import { setOpenInfo } from "../../../store/actions/chatAction";
import { useDispatch } from "react-redux";

const createItemData = memoize(
  (searchResults, handleChatClick, setAllJobs, allJobs, isDmsMode) => ({
    searchResults,
    handleChatClick,
    setAllJobs,
    allJobs,
    isDmsMode,
  })
);

const Row = memo(({ index, style, data }) => {
  const [isHovered, setIsHovered] = useState(false);
  const { searchResults, handleChatClick, setAllJobs, allJobs, isDmsMode } = data;
  const dispatch = useDispatch();

  return (
    <div
      style={style}
      onClick={() => {
        handleChatClick(searchResults[index]);
        dispatch(setOpenInfo(false));
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      data-testid={`job-item-id-${index}`}
      key={index}
    >
      <SidebarEachJob
        key={index}
        eachJob={searchResults[index]}
        setAllJobs={setAllJobs}
        allJobs={allJobs}
        isHovered={isHovered}
        isDmsMode={isDmsMode}
      />
    </div>
  );
}, areEqual);

const SidebarJobs = ({
  searchResults,
  handleChatClick,
  allJobs,
  setAllJobs,
  isSidebarCollapsed,
  isDmsMode = false,
}) => {
  const itemData = createItemData(
    searchResults,
    handleChatClick,
    setAllJobs,
    allJobs,
    isDmsMode
  );

  return (
    <div className="jobs-container dFlex flexColumn">
      {searchResults?.length > 0 ? (
        <FixedSizeList
          height={500}
          width={isSidebarCollapsed ? 60 : 275}
          itemSize={60}
          itemCount={searchResults.length}
          style={{ paddingBottom: "20px" }}
          itemData={itemData}
        >
          {Row}
        </FixedSizeList>
      ) : allJobs.length > 0 ? (
        <ADSpace justifyContent="center">
          <p className="no-results">No Results Found!!</p>
        </ADSpace>
      ) : (
        <ADSpace justifyContent="center">
          <p className="no-results">No Jobs Found!!</p>
        </ADSpace>
      )}
    </div>
  );
};

export default SidebarJobs;
