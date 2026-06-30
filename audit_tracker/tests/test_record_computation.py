import pytest
from unittest.mock import Mock

from audit_tracker.record_computation import (
    create_computation,
    ReadComputation,
    WriteComputation,
    AggregateComputation,
    ExpressionComputation,
    RenameColumnsComputation,
    _is_dict_of_dataframes,
    infer_rows_cols,
)

from audit_tracker.audit_tracker import AuditTracker
from audit_tracker.audit_tracker import ScheduleRunContext

def _maybe_import_pandas():
    try:
        import pandas as pd  # type: ignore
        return pd
    except Exception:
        return None


def test_read_uses_new_with_dict_and_list():
    comp = ReadComputation()
    # new is dict -> rows=len(dict), cols=1, cost=rows*cols
    res = comp.compute(old_df=None, new_df={"a": 1, "b": 2})
    assert (res.rows, res.cols, res.cost) == (2, 1, 2)

    # new is list -> rows=len(list), cols=1
    res = comp.compute(old_df={"x": 1}, new_df=[1, 2, 3])
    assert (res.rows, res.cols, res.cost) == (3, 1, 3)


def test_write_uses_old_with_none_safe():
    comp = WriteComputation()
    # old is None -> returns zeros
    res = comp.compute(old_df=None, new_df=[1, 2, 3])
    assert (res.rows, res.cols, res.cost) == (0, 0, 0)

    # old is dict
    res = comp.compute(old_df={"a": 1, "b": 2, "c": 3}, new_df=None)
    assert (res.rows, res.cols, res.cost) == (3, 1, 3)


def test_aggregate_uses_new_expression_uses_old_with_pandas_if_available():
    pd = _maybe_import_pandas()
    if pd is None:
        pytest.skip("pandas not available")

    new_df = pd.DataFrame({"c1": [1, 2, 3], "c2": [4, 5, 6]})  # 3x2
    old_df = pd.DataFrame({"x": [10, 20]})  # 2x1

    agg = AggregateComputation()
    res_new = agg.compute(old_df=old_df, new_df=new_df)
    assert (res_new.rows, res_new.cols, res_new.cost) == (3, 2, 6)

    expr = ExpressionComputation()
    res_old = expr.compute(old_df=old_df, new_df=new_df)
    assert (res_old.rows, res_old.cols, res_old.cost) == (2, 1, 2)


def test_rename_columns_reports_zero_cost_and_prefers_old_shape():
    comp = RenameColumnsComputation()

    # With old as dict and new as list
    res = comp.compute(old_df={"a": 1, "b": 2}, new_df=[1, 2, 3])
    assert (res.rows, res.cols, res.cost) == (2, 1, 0)

    # With old None, should fall back to new
    res = comp.compute(old_df=None, new_df=[1, 2, 3, 4])
    assert (res.rows, res.cols, res.cost) == (4, 1, 0)


@pytest.mark.parametrize(
    "op_key,uses_new",
    [
        ("read", True),
        ("write", False),
        ("add_columns", True),
        ("concat", True),
        ("correlation", False),
        ("date_format", False),
        ("deduplicate", True),
        ("drop_all_columns_except", False),
        ("drop_columns", False),
        ("drop_na", True),
        ("extract", False),
        ("fill_na", False),
        ("filter_value", True),
        ("joins", True),
        ("lower_case", False),
        ("pytool", False),
        ("rearrange_columns", False),
        ("replace_special_characters", False),
        ("sort", False),
        ("split", False),
        ("trim", False),
        ("union", True),
        ("upper_case", False),
        ("when_otherwise", False),
        ("aggregate", True),
        ("typecast", False),
        ("expression", False),
        ("sql", True),
    ],
)
def test_create_computation_and_shape_selection(op_key, uses_new):
    comp = create_computation(op_key)
    old_df = {"a": 1, "b": 2}
    new_df = [1, 2, 3]
    res = comp.compute(old_df=old_df, new_df=new_df)
    if op_key == "rename_columns":
        # Handled in dedicated test; skip here
        pytest.skip("rename_columns tested separately")
    if uses_new:
        assert (res.rows, res.cols, res.cost) == (3, 1, 3)
    else:
        assert (res.rows, res.cols, res.cost) == (2, 1, 2)



def test__is_dict_of_dataframes_true_when_any_value_contains_df_key():
    obj = {
        "first": {"df": [1, 2, 3]},
        "second": {"not_df": [4, 5]},
    }
    assert _is_dict_of_dataframes(obj) is True


def test__is_dict_of_dataframes_false_for_missing_df_key_and_non_dict_values():
    obj = {
        "first": {"data": 123},
        "second": 42,  # non-dict value; membership check should be guarded
    }
    assert _is_dict_of_dataframes(obj) is False


def test_infer_rows_cols_sums_shapes_for_dict_of_dataframes_without_pandas():
    class Dummy:
        def __init__(self, shape):
            self.shape = shape

    # Two entries: (3x2) and (5x1) -> rows 8, cols 3
    obj = {
        "a": {"df": Dummy((3, 2))},
        "b": {"df": Dummy((5, 1))},
    }
    rows, cols = infer_rows_cols(obj)
    assert (rows, cols) == (8, 3)

def test_record_decorator_with_new_df_as_dict():
    dummy_audit_runs_collection = Mock()
    dummy_audit_usage_collection = Mock()
    dummy_audit_runs_collection.insert_one.return_value = (True, "12345")
    dummy_audit_usage_collection.insert_one.return_value = (True, "12345")
    dummy_schedule_context = ScheduleRunContext(user_id="test_user", chat_id="test_chat", schedule_id="test_schedule", run_id="test_run", execution_type="test_execution_type")
    audit_tracker = AuditTracker(None, None, dummy_schedule_context)
    
    @audit_tracker.record
    def test_func(new_df):
        return new_df
    new_df = {"rows": 1, "cols": 2}
    res = test_func(new_df)
    assert res == new_df
    