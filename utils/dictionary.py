def get_dict_key_by_index(dictionary, key_index):
    return list(dictionary)[key_index]


def get_dict_value_by_index(dictionary, key_index):
    key = get_dict_key_by_index(dictionary, key_index)
    return dictionary[key]
