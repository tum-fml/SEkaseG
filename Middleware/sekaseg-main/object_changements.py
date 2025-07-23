'''
Get object changements by comparing the old dict to the new dict
Returns a dictionary containing the differences of old and new dict
'''

import json
import os

def object_changements(object_name, directory):
    # directory: path to object folder
    filepath = os.path.join(directory, f"{object_name}.object.txt")
    with open(filepath, "r") as f:
        object_info = f.read()
        object_info = object_info.replace("'", "\"")
        object_info = object_info.replace("(", "[")
        object_info = object_info.replace(")", "]")
        json_dict = json.loads(object_info)
        new_dict = json_dict["new_dict"]
        old_dict = json_dict["old_dict"]

        # changes in position on canvas are not published
        new_dict.pop("position")
        old_dict.pop("position")
        new_dict.pop("subscribers")
        old_dict.pop("subscribers")
        new_dict.pop("references")
        old_dict.pop("references")
        new_dict.pop("folder")
        old_dict.pop("folder")

        # Find keys that are in both dict1 and dict2 but have different values
        keys_with_different_values = set(k for k in new_dict.keys() & old_dict.keys() if new_dict[k] != old_dict[k])

        # Find new keys or if keys got deleted
        new_keys = set(k for k in new_dict.keys() if k not in old_dict.keys())
        deleted_keys = set(k for k in old_dict.keys() if k not in new_dict.keys())

        # Combine the above differences into a single dictionary
        # the differences dictionary consists of a key and value tuple (old and new value)
        differences = {}
        if keys_with_different_values or new_keys or deleted_keys:
            for key in keys_with_different_values:
                differences[key] = (new_dict[key], old_dict[key])
            for key in new_keys:
                differences[key] = (new_dict[key], None)
            for key in deleted_keys:
                differences[key] = (None, new_dict[key])
        else:
            differences = None

    # Return the differences
    return differences
