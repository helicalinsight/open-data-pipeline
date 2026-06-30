
import time


def get_unique_name(name, data):
        try:
            aliases = [value['alias'] for key, value in data.items()]
            while name in aliases:
                    name=f"{name}_copy"
            return name
        except Exception as e:
            return name
    # List of words to choose from
   