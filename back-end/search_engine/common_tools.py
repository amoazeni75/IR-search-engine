import json
import search_engine.words_lists as wl
import search_engine.configurations as configs


def sort_a_list_of_dictionary(dict, parameter):
    return sorted(dict, key=lambda i: i[parameter])


def intersection(lst1, lst2):
    return list(set(lst1).intersection(set(lst2)))


def union(lst1, lst2):
    return list(set(lst1).union(set(lst2)))


def save_to_file(data, file_name):
    file_name = configs.prefix_path + file_name
    with open(file_name, 'w') as fp:
        json.dump(data, fp)


def load_file(file_name):
    file_name = configs.prefix_path + file_name
    data = ''
    with open(file_name, 'r') as fp:
        data = json.load(fp)
    return data


def convert_list_string_to_int(l_input):
    return list(map(int, l_input))


def get_inverted_index_keys():
    return wl.inverted_index_keys


def class_number_from_label(label):
    label = label.title()
    if label in wl.label_map:
        return wl.label_map.get(label)
    else:
        return -1


def sort_dictionary_by_value(dict):
    return {k: v for k, v in sorted(dict.items(), key=lambda item: item[1])}


def get_index_of_an_object_by_attribute(list_objs, key, value):
    return next((i for i, item in enumerate(list_objs) if item.get(key) == value), -1)
