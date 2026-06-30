import difflib
import re
from .........logger.logger import logger, Logger


def find_closest_match(name, d, n=1, cutoff=0.7):
    """
    Find the closest match to a given name in a dictionary and return the corresponding key-value pair.

    This function uses the `difflib.get_close_matches` method to find the closest match to the provided name
    from the values in the dictionary. It then returns the key and value of the closest match.

    :param name: The name or string to find the closest match for.
    :type name: str
    :param d: The dictionary to search for the closest match. The function searches within the values of this dictionary.
    :type d: dict
    :param n: The maximum number of closest matches to return. Defaults to 1.
    :type n: int, optional
    :param cutoff: A float in the range [0.0, 1.0] that specifies the similarity threshold for the matches. Defaults to 0.7.
    :type cutoff: float, optional
    :return: A tuple containing the key and value of the closest match, or None if no match is found.
    :rtype: tuple or None
    """
    # Get the values from the dictionary
    values = list(d.values())
    
    # Find the closest match to the given name
    closest_matches = difflib.get_close_matches(name, values, n=1, cutoff=0.7)
    
    # If there is a closest match, return the key-value pair
    if closest_matches:
        closest_value = closest_matches[0]
        for key, value in d.items():
            if value == closest_value:
                return key, value
    else:
        return None
    
def extract_code(text):
    """Extracts code blocks from the given text, prioritizing Python code."""

    # Function to search for generic <code> block
    def find_generic_code_block(text):
        generic_pattern = r'<code>(.*?)</code>'
        generic_match = re.search(generic_pattern, text, re.DOTALL)
        return generic_match.group(1).strip() if generic_match else None
    
    # Try Python code block extraction first (more specific)
    python_pattern = r'```python\s+(.*?)\s+```'
    python_match = re.search(python_pattern, text, re.DOTALL)
    if python_match:
        # Check if there's a generic <code> block after the Python code block
        generic_code = find_generic_code_block(text)
        return generic_code if generic_code else python_match.group(1).strip()
    
    # Fallback to generic <code> block extraction if no Python block is found
    return find_generic_code_block(text)

    
def match_aliases(python_code, spark_code):
    # Extract aliases from the Python code using regex
    python_aliases = re.findall(r'alias="([^"]+)"', python_code)

    # Extract aliases from the Spark code using regex
    spark_aliases = re.findall(r'alias="([^"]+)"', spark_code)

    # Function to fix spark code if aliases don't match
    def fix_spark_aliases(python_aliases, spark_code):
        # If the alias names are not the same, update the spark code
        for i, alias in enumerate(python_aliases):
            if i < len(spark_aliases):
                spark_code = spark_code.replace(spark_aliases[i], alias)
        return spark_code

    # Check if aliases in both codes are the same
    if python_aliases != spark_aliases:
        spark_code = fix_spark_aliases(python_aliases, spark_code)
        logger.info("The spark_code has been updated to match the aliases in python_code:")
        logger.info(f"spark_code {spark_code}")
    else:
        logger.info("The aliases in both codes are the same.")
    return spark_code
