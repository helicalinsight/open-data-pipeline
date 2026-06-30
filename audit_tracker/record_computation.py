from dataclasses import dataclass
from typing import Tuple

@dataclass
class ComputationResult:
    """Result of record computation."""
    rows: int
    cols: int
    cost: float


class RecordComputationBase:
    """Base class for record computation."""
    
    def compute(self, old_df, new_df) -> ComputationResult:
        raise NotImplementedError("Subclasses must implement this method")

# -----------------------------
# Utilities for shape inference
# -----------------------------

def _try_imports():
    pandas_module = None
    pyspark_sql_module = None
    try:
        import pandas as pd  # type: ignore
        pandas_module = pd
    except Exception:
        pandas_module = None
    try:
        from pyspark.sql import DataFrame as SparkDataFrame  # type: ignore
        pyspark_sql_module = SparkDataFrame
    except Exception:
        pyspark_sql_module = None
    return pandas_module, pyspark_sql_module


_PD, _SPARK_DF = _try_imports()


def _is_pandas_dataframe(obj) -> bool:
    return _PD is not None and getattr(obj, "__class__", None) is not None and isinstance(obj, _PD.DataFrame)


def _is_pandas_series(obj) -> bool:
    return _PD is not None and getattr(obj, "__class__", None) is not None and isinstance(obj, _PD.Series)


def _is_spark_dataframe(obj) -> bool:
    return _SPARK_DF is not None and isinstance(obj, _SPARK_DF)

def _parse_rows_cols_single_dataframe(obj) -> Tuple[int, int]:
    if _is_pandas_dataframe(obj):
        # pandas DataFrame: shape is (rows, cols)
        rows, cols = int(obj.shape[0]), int(obj.shape[1])
        return rows, cols
    if _is_pandas_series(obj):
        # pandas Series: treat as single column table
        return int(len(obj)), 1
    if _is_spark_dataframe(obj):
        # Spark DataFrame: count() can be expensive; caller decides when to use it
        try:
            rows = int(obj.count())
        except Exception:
            # Fallback when Spark context isn't active; unknown rows
            rows = 0
        try:
            cols = int(len(obj.columns))
        except Exception:
            cols = 0
        return rows, cols
    # Numpy or array-like with shape
    shape = getattr(obj, "shape", None)
    if shape is not None:
        try:
            if len(shape) >= 2:
                return int(shape[0]), int(shape[1])
            if len(shape) == 1:
                return int(shape[0]), 1
        except Exception:
            pass
    # Generic size
    size = getattr(obj, "size", None)
    if isinstance(size, (int, float)):
        try:
            return int(size), 1
        except Exception:
            return 0, 0
    # Fallback to len
    try:
        return int(len(obj)), 1
    except Exception:
        return 0, 0
    
def _is_dict_of_dataframes(obj):
    any_dataframe_present = False
    if isinstance(obj, dict):
        try:
            for item in obj.items():
                _, v = item
                if "df" in v:
                    any_dataframe_present = True
        except:
            pass
                
    return any_dataframe_present

def infer_rows_cols(obj) -> Tuple[int, int]:
    """Infer (rows, cols) for supported inputs.

    - None -> (0, 0)
    - dict/list/tuple/set -> (len(obj), 1)
    - pandas.DataFrame -> obj.shape
    - pandas.Series -> (len(series), 1)
    - pyspark.sql.DataFrame -> (row_count, number_of_columns)
    - numpy-like with shape -> try to infer 2D, else treat as 1D
    - generic objects with __len__ -> (len(obj), 1)
    """
    if obj is None:
        return 0, 0
    if _is_dict_of_dataframes(obj):
        rows, cols = 0, 0
        for item in obj.items():
            _, v = item
            df = v.get("df", None)
            if df is None:
                continue
            r, c = _parse_rows_cols_single_dataframe(df)
            rows += r
            cols += c
        return rows, cols
    
    if isinstance(obj, tuple) and isinstance(obj[0], bool):
        return _parse_rows_cols_single_dataframe(obj[1])
    
    if isinstance(obj, (dict, list, tuple, set)):
        return len(obj), 1
    return _parse_rows_cols_single_dataframe(obj)
    

def infer_cost(obj) -> int:
    rows, cols = infer_rows_cols(obj)
    return int(rows * cols)


# ---------------------------------
# Computation classes (per operation)
# ---------------------------------

class _BaseSingleOperandComputation(RecordComputationBase):
    """Base for computations operating on either old_df or new_df."""

    use_new: bool = False  # if True -> use new_df, else old_df

    def compute(self, old_df, new_df) -> ComputationResult:
        target = new_df if self.use_new else old_df
        rows, cols = infer_rows_cols(target)
        cost = infer_cost(target)
        return ComputationResult(rows=rows, cols=cols, cost=cost)


# Operations that use new_df
class ReadComputation(_BaseSingleOperandComputation):
    use_new = True


class AddColumnsComputation(_BaseSingleOperandComputation):
    use_new = True


class ConcatComputation(_BaseSingleOperandComputation):
    use_new = True


class DeduplicateComputation(_BaseSingleOperandComputation):
    use_new = True


class DropNaComputation(_BaseSingleOperandComputation):
    use_new = True


class FilterValueComputation(_BaseSingleOperandComputation):
    use_new = True


class JoinsComputation(_BaseSingleOperandComputation):
    use_new = True


class UnionComputation(_BaseSingleOperandComputation):
    use_new = True


class AggregateComputation(_BaseSingleOperandComputation):
    use_new = True


class SqlComputation(_BaseSingleOperandComputation):
    use_new = True


# Operations that use old_df
class WriteComputation(_BaseSingleOperandComputation):
    use_new = False


class CorrelationComputation(_BaseSingleOperandComputation):
    use_new = False


class DateFormatComputation(_BaseSingleOperandComputation):
    use_new = False


class DropAllColumnsExceptComputation(_BaseSingleOperandComputation):
    use_new = False


class DropColumnsComputation(_BaseSingleOperandComputation):
    use_new = False


class ExtractComputation(_BaseSingleOperandComputation):
    use_new = False


class FillNaComputation(_BaseSingleOperandComputation):
    use_new = False


class LowerCaseComputation(_BaseSingleOperandComputation):
    use_new = False


class PytoolComputation(_BaseSingleOperandComputation):
    use_new = False


class RearrangeColumnsComputation(_BaseSingleOperandComputation):
    use_new = False


class ReplaceSpecialCharactersComputation(_BaseSingleOperandComputation):
    use_new = False


class SortComputation(_BaseSingleOperandComputation):
    use_new = False


class SplitComputation(_BaseSingleOperandComputation):
    use_new = False


class TrimComputation(_BaseSingleOperandComputation):
    use_new = False


class UpperCaseComputation(_BaseSingleOperandComputation):
    use_new = False


class WhenOtherwiseComputation(_BaseSingleOperandComputation):
    use_new = False


class TypecastComputation(_BaseSingleOperandComputation):
    use_new = False


class ExpressionComputation(_BaseSingleOperandComputation):
    use_new = False

   
class ExportComputation(_BaseSingleOperandComputation):
    use_new = False


# Special case: rename_columns cost is 0, but we still report shape based on available input
class RenameColumnsComputation(RecordComputationBase):
    def compute(self, old_df, new_df) -> ComputationResult:
        # Prefer shape from old_df; if missing, fallback to new_df; else zeros
        if old_df is not None:
            rows, cols = infer_rows_cols(old_df)
        elif new_df is not None:
            rows, cols = infer_rows_cols(new_df)
        else:
            rows, cols = 0, 0
        return ComputationResult(rows=rows, cols=cols, cost=0)


# Optional: registry mapping operation key -> class
OPERATION_TO_COMPUTATION_CLASS = {
    "read": ReadComputation(),
    "write": WriteComputation(),
    "add_columns": AddColumnsComputation(),
    "concat": ConcatComputation(),
    "correlation": CorrelationComputation(),
    "date_format": DateFormatComputation(),
    "deduplicate": DeduplicateComputation(),
    "drop_all_columns_except": DropAllColumnsExceptComputation(),
    "drop_columns": DropColumnsComputation(),
    "drop_na": DropNaComputation(),
    "extract": ExtractComputation(),
    "fill_na": FillNaComputation(),
    "filter_value": FilterValueComputation(),
    "joins": JoinsComputation(),
    "lower_case": LowerCaseComputation(),
    "pytool": PytoolComputation(),
    "rearrange_columns": RearrangeColumnsComputation(),
    "rename_columns": RenameColumnsComputation(),
    "replace_special_characters": ReplaceSpecialCharactersComputation(),
    "sort": SortComputation(),
    "split": SplitComputation(),
    "trim": TrimComputation(),
    "union": UnionComputation(),
    "upper_case": UpperCaseComputation(),
    "when_otherwise": WhenOtherwiseComputation(),
    "aggregate": AggregateComputation(),
    "typecast": TypecastComputation(),
    "expression": ExpressionComputation(),
    "sql": SqlComputation(),
    "export": ExportComputation()
}


def create_computation(operation_key: str) -> RecordComputationBase:
    cls = OPERATION_TO_COMPUTATION_CLASS.get(operation_key)
    if cls is None:
        raise KeyError(f"Unsupported operation key: {operation_key}")
    return cls