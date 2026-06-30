import { useEffect, useState, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setCurrentPage } from "../../store/actions/jobScheduleActions";
import { getLocalStorageItem } from "../../utils/userData";
import { fetchDagListUtil } from "../../utils/appUtils";
import JobScheduleList from "./components/JobScheduleList";
import IndividualJob from "./components/IndividualJob";
import ErrorFallback from "../error-boundry/ErrorFallback";
import "./style.scss";

function JobScheduleModule() {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const { user } = getLocalStorageItem() || {};
  const { dagTotal, individualJob, dagInfo, currentPageInfo, pageSizeInfo } =
    useSelector((state) => state.jobSchedule);
  const [current, setCurrent] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState({});

  const fetchDagList = (resetPagination = false, newFilters = filters) => {
    if (loading && !resetPagination) return;
    const targetPage = resetPagination ? 1 : current;
    const targetPageSize = resetPagination ? 10 : pageSize;
    fetchDagListUtil({
      dispatch,
      setLoading,
      user,
      current: targetPage,
      pageSize: targetPageSize,
      filters: newFilters,
    });
    if (resetPagination) {
      setCurrent(1);
      setPageSize(10);
    }
  };
  useEffect(() => {
    fetchDagList();
  }, [current, pageSize, filters]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setCurrent(1);
  };
  useEffect(() => {
    document.addEventListener("mouseover", (e) => {
      if (e.target?.title) e.target.removeAttribute("title");
    });
  }, []);
  const paginationData = useMemo(
    () => ({
      showSizeChanger: true,
      pageSizeOptions: ["10", "20", "50", "100"],
      onChange: (page) => setCurrent(page),
      onShowSizeChange: (_, newPageSize) => {
        setPageSize(newPageSize);
        setCurrent(1);
      },
      showTitle: false,
      current,
      pageSize,
      total: individualJob ? undefined : dagTotal,
      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
    }),
    [current, pageSize, dagTotal, individualJob]
  );
  // pagination  for individual job
  const paginationInfoData = useMemo(
    () => ({
      showSizeChanger: true,
      pageSizeOptions: ["10", "20", "50", "100"],
      onChange: (page, pageSize) => {
        dispatch(setCurrentPage(page));
        dispatch(setPageSize(pageSize));
      },
      onShowSizeChange: (_, newPageSize) => {
        dispatch(setCurrentPage(1));
        dispatch(setPageSize(newPageSize));
      },
      current: currentPageInfo,
      pageSize: pageSizeInfo,
      showTitle: false,
      total: dagInfo?.dag_runs?.total_entries,
      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
    }),
    [currentPageInfo, pageSizeInfo, dagInfo?.dag_runs?.total_entries]
  );

  return (
    <ErrorFallback>
      {individualJob ? (
        <IndividualJob paginationInfoData={paginationInfoData} />
      ) : (
        <JobScheduleList
          paginationData={paginationData}
          fetchDagList={fetchDagList}
          loading={loading}
          onFilterChange={handleFilterChange}
        />
      )}
    </ErrorFallback>
  );
}
export default JobScheduleModule;
