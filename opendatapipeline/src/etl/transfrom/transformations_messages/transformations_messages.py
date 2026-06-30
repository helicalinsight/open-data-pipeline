from ....logger.logger import Logger, logger

class Messages:
    """
    This is the class for generating messages
    This class provides methods for generating messages based on different transformations
    such as add_columns, concat, correlation, date_format, deduplicate, drop_all_columns_except, drop_columns, drop_na, extract, fill_na, filter_value, joins, lower_case, pytool, rearrange_columns, rename_columns, replace_special_characters, 
    sort, split, trim, union, upper_case, when_otherwise, aggregate, typecast, expression, sql

    """
    @staticmethod
    @Logger.generate
    def add_columns(parameters, success):
        """
        Generates message for add_columns transformation

        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        groups = parameters['groups']       
        # removing prefix for failed because we are calling this only if the success is true , 
        # if it is false it is being handled in transformations itself
        try:
            if success:
                prefix = f"Successfully added column(s)"
                if len(groups) == 1:
                    message = f"{prefix} {' and '.join(groups[0]['columns'])} with default value {groups[0].get('default', 'None')}."
                else:
                    message = prefix + " " + ", ".join(
                        map(lambda
                                group: f"{' and '.join(group['columns'])} with default value {group.get('default', 'None')}",
                            groups[:-1]))
                    message += " and " + f"{' and '.join(groups[-1]['columns'])} with default value {groups[-1].get('default', 'None')}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def rename_columns(parameters, success):
        """
        Generates message for rename_columns transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """        
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully renamed column(s) "
                message = prefix + ", ".join(
                    [f"{item['old_name']} with {item['new_name']}" for item in groups[:-1]]) + (
                              " and " if len(
                                  groups) > 1 else "") + f"{groups[-1]['old_name']} with {groups[-1]['new_name']}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def sort(parameters, success):
        """
        Generates message for sort transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']        
                prefix = f"Successfully sorted column(s) "
                if len(groups) == 1:
                    message = f"{prefix} {' and '.join(groups[0]['columns'])}."
                else:
                    message = prefix + ", ".join(
                        map(lambda group: f"{' and '.join(group['columns'])}",
                            groups[:-1]))
                    message += " and " + f"{' and '.join(groups[-1]['columns'])}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def drop_columns(parameters, success):
        """
        Generates message for drop_columns transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully dropped column(s)"
                if len(groups) == 1:
                    message = f"{prefix} {' and '.join(groups[0]['columns'])}."
                else:
                    message = prefix + " "+ ", ".join(
                        map(lambda group: f"{' and '.join(group['columns'])}",
                            groups[:-1]))
                    message += " and " + f"{' and '.join(groups[-1]['columns'])}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def drop_all_columns_except(parameters, success):
        """
        Generates message for drop_all_columns_except transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully dropped all column(s) except"
                if len(groups) == 1:
                    message = f"{prefix} {' and '.join(groups[0]['columns'])}."
                else:
                    message = prefix + " " + ", ".join(
                        map(lambda group: f"{' and '.join(group['columns'])}",
                            groups[:-1]))
                    message += " and " + f"{' and '.join(groups[-1]['columns'])}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def deduplicate(parameters, success):
        """
        Generates message for deduplicate transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully deduplicated column(s)" if success else f"Failed to deduplicate column(s) "
                if len(groups) == 1:
                    message = f"{prefix} {' and '.join(groups[0]['columns'])}."
                else:
                    message = prefix +" "+ ", ".join(
                        map(lambda group: f"{' and '.join(group['columns'])}",
                            groups[:-1]))
                    message += " and " + f"{' and '.join(groups[-1]['columns'])}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def split(parameters, success):
        """
        Generates message for split transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully splitted column(s) "
                message = prefix + ", ".join([
                                                 f"'{item['column']}' into {', '.join(item['destination_columns'])} at the delimiter {item['delimiter']}"
                                                 for item in groups[:-1]]) + (" and " if len(groups) > 1 else "") + \
                          f"{groups[-1]['column']} into {', '.join(groups[-1]['destination_columns'])} " \
                          f"at the delimiter '{groups[-1]['delimiter']}'."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def replace_special_characters(parameters, success):
        """
        Generates message for replace_special_characters transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                if parameters["delimiter"] == False:
                    message = f"The target character does not exist in the given column."
                else:
                    prefix = f"Successfully replaced special characters in column(s) "
                    message = prefix + (", ".join([
                                                      f"{', '.join(group['columns'])}: {group['target_character']} to {group['replacement_character']}"
                                                      for group in groups[:-1]]) + (
                                            ", and " if len(groups) > 1 else "") + ", ".join([
                        f"{', '.join(groups[-1]['columns'])}: {groups[-1]['target_character']} to {groups[-1]['replacement_character']}"])) + "."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def concat(parameters, success):
        """
        Generates message for concat transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully concatenated column(s) "
                message = prefix + (", ".join([
                                                  f"{', '.join(group['columns'])} with '{group['separator']}' to the column '{group['destination_column']}'"
                                                  for group in groups[:-1]]) + (
                                        " and " if len(groups) > 1 else "") + ", ".join([
                    f"{', '.join(groups[-1]['columns'])} with '{groups[-1]['separator']}' to the column '{groups[-1]['destination_column']}'"])) + "."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def when_otherwise(parameters, success):
        """
        Generates message for when_otherwise transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                message = ("When otherwise query executed and stored in " + ", ".join(
                    "".join(group['destination_column']) for group in
                    groups) + " successfully.")
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def filter_value(parameters, success):
        """
        Generates message for filter_value transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully filtered column(s) "
                if len(groups) == 1:
                    message = prefix + ", ".join([f"'{column}'" for column in groups[0]['columns']]) + " based on the given criteria."
                else:
                    column_names = ", ".join(
                        [", ".join([f"'{info['columns'][i]}'" for i in range(len(info['columns']))]) for info in
                         groups[:-1]])
                    last_column = ", ".join(
                        [f"'{groups[-1]['columns'][i]}'" for i in range(len(groups[-1]['columns']))])
                    message = prefix + f"{column_names} and {last_column} based on the given criteria."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def date_format(parameters, success):
        """
        Generates message for date_format transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully updated the format of the date for the column(s) "
                message = prefix + (
                    ", ".join([f"{', '.join(group['columns'])} to '{group['format']}'" for group in groups[:-1]])) + (
                              " and " if len(
                                  groups) > 1 else "") + f"{', '.join(groups[-1]['columns'])} to '{groups[-1]['format']}'."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def correlation(parameters, success):
        """
        Generates message for correlation transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully calculated correlation for the column(s) "
                message = prefix + (
                    ", ".join([f"{', '.join(group['columns'])} to {group['destination_column']}" for group in groups[:-1]])) + (
                              " and " if len(
                                  groups) > 1 else "") + f"{', '.join(groups[-1]['columns'])} to {groups[-1]['destination_column']}."

                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def trim(parameters, success):
        """
        Generates message for trim transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully trimmed column(s) "
                message = prefix + (", ".join([f"{', '.join(group['columns'])} to '{group['number_of_characters']}' "
                                               f"character(s) to its {group['location']}" for group in groups])) + "."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def upper_case(parameters, success):
        """
        Generates message for upper_case transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully updated column(s) "
                message = prefix + (
                    ", ".join([f"{', '.join(group['columns'])} to uppercase" for group in groups])) + "."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def lower_case(parameters, success):
        """
        Generates message for lower_case transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully updated column(s) " if success else f"Failed to update column(s) "
                message = prefix + (
                    ", ".join([f"{', '.join(group['columns'])} to lowercase" for group in groups])) + "."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def union(parameters, success):
        """
        Generates message for union transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                if parameters is not None:
                    groups = parameters.get('groups')
                    prefix = f"Successfully performed union based on column(s) "
                    column_names = []
                    file_names = parameters.get("file_names", [])
                    if groups:
                        for group in groups:
                            if group.get('columns') and None not in group['columns']:
                                column_names.extend(group['columns'])
                    if column_names:
                        message = prefix + ", ".join(column_names) + f" for {', '.join(file_names)}."
                    else:
                        message = f"Union performed successfully for {', '.join(file_names)}."
                else:
                    message = f"Union performed successfully."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def joins(parameters, success):
        """
        Generates message for joins transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully performed joins "
                message = prefix + (", ".join([
                    f"on files {', '.join(parameters['file_names'])} on columns {', '.join(group['left_on'])} and {', '.join(group['right_on'])} with the type {group['join_type']}"
                    for group in groups])) + "."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def rearrange_columns(parameters, success):
        """
        Generates message for rearrange_columns transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Successfully rearranged column(s) in the given order "
                message = prefix
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def cast(parameters, success):
        """
        Generates message for cast transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                prefix = f"Updated data type of the given column(s) "
                message_parts = []
                for group in groups:
                    column_names = ', '.join(group['columns'])
                    new_type = group['new_type'].get(group['columns'][0]) if group['new_type'] not in ["date", "timestamp"] else group['new_type']
                    if new_type in ['float32','float64','float8','float16']:
                        group['new_type'] = 'float'
                        new_type = 'float'
                    if new_type in ['int32', 'int64','int8','int16']:
                        group['new_type'] = 'integer'
                        new_type = 'integer'
                    if new_type in ['bool', 'boolean']:
                        group['new_type'] = new_type
                        new_type = 'boolean'
                    if new_type in ['string']:
                        group['new_type'] = new_type
                        new_type = 'string'
                    if new_type in ['object']:
                        group['new_type'] = new_type
                        new_type = 'object'
                    message_parts.append(f"{column_names} to '{new_type}'")
                message = ', '.join(message_parts)
                if len(groups) > 1:
                    message = ', '.join(message_parts[:-1]) + " and " + message_parts[-1]
                message = prefix + message + "."
                return message, group
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def aggregations(parameters, success):
        """
        Generates message for aggregations transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters["groups"]
                prefix = "Successfully performed aggregations "
                message = (
                    prefix
                    + ", ".join(
                        [
                            f"on '{', '.join(group['columns'])}' grouped by '{', '.join(group['group_by'])}'"
                            for group in groups
                        ]
                    )
                    + "."
                )
                return message
        except Exception as e:  # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def arithmetic_operations(parameters, success):
        """
        Generates message for arithmetic_operations transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            if success:
                groups = parameters['groups']
                query = ','.join([f"'{group['query']}'" for group in groups])
                destination_column = ','.join([f"'{group['destination_column']}'" for group in groups])
                message = f"Arithmetic operation performed on the given query {query} and stored to {destination_column}."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @staticmethod
    @Logger.generate
    def sql_operations(parameters, success):
        """
        Generates message for sql operation transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :type success: bool
        :return: message
        :rtype: str
        """ 
        try:
            if success:
                groups = parameters['groups']
                query = ','.join([f"'{group['query']}'" for group in groups])
                message = f"Executed the given query {query} successfully."
                return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @Logger.generate
    def drop_na(self, parameters, success, exception=None, error_msg=None):
        """
        Generates message for drop_na transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :param exception: Contains type of exception if occurred
        :param error_msg: Error message occurred in case of exception
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            prefix = f"Dropped NaN values" if success else f"Failed to drop NaN values"
            if parameters is None:
                message = prefix
            else:
                groups = parameters['groups']
                if groups[0] == {}:
                    message = f"{prefix}"
                elif "subset" in groups[0]:
                    message = f"{prefix} for {groups[0]['subset']} columns"
            return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"
        
    @Logger.generate
    def extract(self, parameters, success, exception=None, error_msg=None):
        """
        Generates message for extract transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :param exception: Contains type of exception if occurred
        :param error_msg: Error message occurred in case of exception
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            groups = parameters['groups'][0]
            prefix = f"Extracted '{groups['component']}' from '{groups['column']}' column" if success else f"Failed to extract '{groups['component']}' from '{groups['column']}' column"
            # message = f"{prefix} to '{groups['destination_column']}' column"
            message = f"{prefix}"
            return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"

    @Logger.generate
    def fill_na(self, parameters, success, exception=None, error_msg=None):
        """
        Generates message for fill_na transformation
        :param parameters: The input parameters
        :type parameters: dict
        :param success: Boolean value to determine if the transformation is succeeded or not
        :param exception: Contains type of exception if occurred
        :param error_msg: Error message occurred in case of exception
        :type success: bool
        :return: message
        :rtype: str
        """
        try:
            groups = parameters['groups']
            if "column" in groups[0] and groups[0]["column"] != None:
                prefix = f"Filled NaN values in column '{groups[0]['column']}'" if success else f"Failed to fill NaN values in column '{groups[0]['column']}'"
            else:
                prefix = f"Filled NaN values" if success else f"Failed to fill NaN values"
            if "value" and "axis" in groups[0] and groups[0]["value"] != None and groups[0]["axis"] != None:
                message = f"{prefix} with '{groups[0]['value']}' along the {groups[0]['axis']}"
            elif "method" and "limit" in groups[0] and groups[0]["method"] != None and groups[0]["limit"] != None:
                message = f"{prefix} using {groups[0]['method']} method with limit {groups[0]['limit']}"
            elif "value" in groups[0] and groups[0]["value"] != None:
                message = f"{prefix} with '{groups[0]['value']}' value"
            elif "method" in groups[0] and groups[0]["method"] != None:
                message = f"{prefix} using {groups[0]['method']} method"
            return message
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return f"Operation completed with exception: {str(e)}"
