import search_engine.words_lists as wl
import search_engine.configurations as config
import math
import search_engine.common_tools as c_tools


def prepare_document_term_vector(words):
    """
    This function will create a dictionary with the format of term:count for the terms in given documents
    :param words:
    :return:
    """
    doc_dic = {}
    for item in words:
        if item in doc_dic:
            term_freq = doc_dic.get(item)
            term_freq += 1
            doc_dic[item] = term_freq
        else:
            doc_dic[item] = 1
    return doc_dic


def prepare_frequency_vector(term_freq_dictionary, type_cal='None'):
    vector = [0] * config.dictionary_size
    for k, v in term_freq_dictionary.items():
        index = c_tools.get_inverted_index_keys().index(k)
        if type_cal == 'None':
            vector[index] = v
        elif type_cal == 'Log':
            if v == 0:
                vector[index] = 0
            else:
                vector[index] = 1 + math.log(v, 10)
    return vector


def prepare_one_document_vector(words):
    """
    This function will create a vector which each elements in it is 0 (the document does not have the element corresponding
     to its index in dictionary) or non-zero (the document has the element corresponding to its index in the dictionary)
    :param words: the list of words, which the document has them
    :return: a vector that its length is equal to dictionary size
    """
    vector = [0] * config.dictionary_size
    # vector = np.zeros(config.dictionary_size)
    for key in words:
        index = c_tools.get_inverted_index_keys().index(key)
        tf = 1 + math.log(words[key], 10)
        vector[index] = tf

    return vector


def prepare_documents_vector():
    """
    This function will prepare the vector of all documents
    :return:
    """
    for i in wl.documents_terms_frequency:
        vec = prepare_one_document_vector(i)
        wl.documents_terms_vectors.append(vec)


def get_avg_document_word_length():
    """
    This function calculate the average length of the documents words list
    :return:
    """
    sum = 0
    for i in wl.documents_terms_frequency:
        sum += len(i)
    return sum / len(wl.documents_terms_frequency)


def sort_posting_lists_depends_on_term_count():
    """
    sort each of posting list based on terms frequency
    :return:
    """
    for i in wl.inverted_index:
        new_value = sort_by_values_len(wl.inverted_index.get(i))
        wl.inverted_index[i] = new_value


def sort_by_values_len(dict):
    dict_len = {key: len(value) for key, value in dict.items()}
    import operator
    sorted_key_list = sorted(dict_len.items(), key=operator.itemgetter(1), reverse=True)
    result_dic = {}
    for item in sorted_key_list:
        result_dic[item[0]] = dict.get(item[0])
    return result_dic
