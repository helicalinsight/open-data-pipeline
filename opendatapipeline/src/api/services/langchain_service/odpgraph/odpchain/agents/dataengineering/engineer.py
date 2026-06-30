from .tools.add_columns.main import AddColumnsAgent
from .tools.aggregations.main import AggregationsAgent
from .tools.arithmetic_operations.main import ArithmeticOperationsAgent
from .tools.cast.main import CastAgent
from .tools.concat.main import ConcatAgent
from .tools.correlation.main import CorrelationAgent
from .tools.date_format.main import DateFormatAgent
from .tools.deduplicate.main import DeduplicateAgent
from .tools.drop_all_except_columns.main import DropAllExceptColumnsAgent
from .tools.drop_columns.main import DropColumnsAgent
from .tools.export.main import ExportAgent
from .tools.extract.main import ExtractAgent
from .tools.fill_na.main import FillNaAgent
from .tools.filter.main import FilterAgent
from .tools.joins.main import JoinsAgent
from .tools.lowercase.main import LowerCaseAgent
from .tools.rearrange_columns.main import RearrangeColumnsAgent
from .tools.rename_columns.main import RenameColumnsAgent
from .tools.replace_special_characters.main import ReplaceSpecialCharactersAgent
from .tools.sort.main import SortAgent
from .tools.split.main import SplitAgent
from .tools.sql_operations.main import SQLOperationsAgent
from .tools.trim.main import TrimAgent
from .tools.union.main import UnionAgent
from .tools.uppercase.main import UpperCaseAgent
from .tools.when_otherwise.main import WhenOtherwiseAgent
from .tools.cwf.main import CurrentWorkingFileAgent
from .tools.dropna.main import DropNaAgent
from .tools.extract.main import ExtractAgent
from .tools.pytool.main import PyToolAgent
from .tools.sparktool.main import SaprkToolAgent
import logging


class DataEngineer:
    """This class provides functionalities for managing and creating data processing
    agents. It maintains a mapping of different agent types to their corresponding
    agent classes and provides a method to instantiate these agents.

    The class maintains a dictionary, `agent_mapping`, where keys are strings
    representing different data processing tasks and values are classes implementing
    those tasks. This allows for flexible and dynamic creation of agent instances
    based on the required data processing functionality.

    :param agent_mapping: A dictionary mapping task names (strings) to their
        corresponding agent classes.
    :type agent_mapping: dict
    """
    agent_mapping = {
        "add_columns": AddColumnsAgent,
        "aggregations": AggregationsAgent,
        "arithmetic_operations": ArithmeticOperationsAgent,
        "cast": CastAgent,
        "concat": ConcatAgent,
        "correlation": CorrelationAgent,
        "date_format": DateFormatAgent,
        "deduplicate": DeduplicateAgent,
        "drop_all_except_columns": DropAllExceptColumnsAgent,
        "drop_columns": DropColumnsAgent,
        "drop_null":DropNaAgent,
        "export": ExportAgent,
        "extract": ExtractAgent,
        "fill_na": FillNaAgent,
        "filter": FilterAgent,
        "joins": JoinsAgent,
        "lowercase": LowerCaseAgent,
        "rearrange_columns": RearrangeColumnsAgent,
        "rename_columns": RenameColumnsAgent,
        "replace_special_characters": ReplaceSpecialCharactersAgent,
        "sort": SortAgent,
        "split": SplitAgent,
        "sql_operations": SQLOperationsAgent,
        "trim": TrimAgent,
        "union": UnionAgent,
        "uppercase": UpperCaseAgent,
        "when_otherwise": WhenOtherwiseAgent,
        "cwf" : CurrentWorkingFileAgent,
        "pytool" : PyToolAgent,
        "sparktool": SaprkToolAgent
    }

    @staticmethod
    def create_agent(agent):
        try:
            agent = DataEngineer.agent_mapping.get(agent)
            return agent
        except Exception as e:
            logging.error("error while creating object", str(e), exc_info=True)
            return None
