import search_engine.words_lists as wl
import math
from numpy import linalg as LA
import search_engine.linguistic_tools as lin_tools
import search_engine.common_tools as c_tools


def get_tf_idf_query_ltc(words):
    """
    This function will calculate tf_idf based on ltc method for the words in the query
    :param words: The words in the query
    :return: A dictionary which contains term:tf_idf
    """
    tf_idf_dic = {}
    distinct_words = set(words)
    length_inverted_index = len(wl.inverted_index)
    for word in distinct_words:
        word_dict = lin_tools.preprocess_single_word_in_query(word)
        if word_dict == -1:
            continue
        if word_dict not in wl.inverted_index:
            continue
        tf = words.count(word)
        tf = 1 + math.log(tf, 10)
        idf = get_df_word(word_dict)
        idf = math.log(length_inverted_index / idf, 10)
        tf_idf_dic[word_dict] = tf * idf
    return tf_idf_dic, distinct_words


def get_tf_idf_query_lnn(words):
    """
        Calculate tf_idf based on lnn
    """
    tf_idf_dic = {}
    distinct_words = set(words)
    length_inverted_index = len(wl.inverted_index)
    for word in distinct_words:
        word_dict = lin_tools.preprocess_single_word_in_query(word)
        if word_dict == -1:
            continue
        if word_dict not in wl.inverted_index:
            continue
        idf = get_df_word(word_dict)
        idf = math.log(1 + (length_inverted_index / idf), 10)
        tf_idf_dic[word_dict] = idf
    return tf_idf_dic, distinct_words


def get_tf_idf_query_aln(words):
    """
    Calculate tf_idf based on aln
    """
    tf_idf_dic = {}
    distinct_words = set(words)
    length_inverted_index = len(wl.inverted_index)
    max_tf = 0
    for i in distinct_words:
        if max_tf < words.count(i):
            max_tf = words.count(i)

    for word in distinct_words:
        word_dict = lin_tools.preprocess_single_word_in_query(word)
        if word_dict == -1:
            continue
        if word_dict not in wl.inverted_index:
            continue
        tf = words.count(word)
        tf = (0.5 + 0.5 * (tf / max_tf))
        idf = get_df_word(word_dict)
        idf = math.log(1 + (length_inverted_index / idf), 10)
        tf_idf_dic[word_dict] = tf * idf
    return tf_idf_dic, distinct_words


def get_tf_idf_documents_lnc(documents_ids, query_words, centroid=[]):
    """
    This function will calculate tf_idf based on lnc method for documents
    :param centroid:
    :param documents_ids: union of the documents which contains any words of the given query
    :param query_words: the words in the given query
    :return: a list of tuples, each tuple contains document id and a dictionary which contains term and tf_idf based on lnc
    """
    document_term_tf_idf = []
    for doc_id in documents_ids:
        doc_id = int(doc_id)
        doc_dic = {}
        for word in query_words:
            if word in wl.documents_terms_frequency[doc_id]:
                tf = 1 + math.log(wl.documents_terms_frequency[doc_id].get(word), 10)
                doc_dic[word] = tf
            elif len(centroid) != 0:
                doc_dic[word] = centroid[c_tools.get_inverted_index_keys().index(word)]

        document_term_tf_idf.append([doc_id, doc_dic])
    return document_term_tf_idf


def get_tf_idf_documents_ntc(documents_ids, query_words, centroid=[]):
    """
    This function will calculate tf_idf based on lnc method for documents
    :param centroid:
    :param documents_ids: union of the documents which contains any words of the given query
    :param query_words: the words in the given query
    :return: a list of tuples, each tuple contains document id and a dictionary which contains term and tf_idf based on lnc
    """
    document_term_tf_idf = []
    length_inverted_index = len(wl.inverted_index)
    for doc_id in documents_ids:
        doc_id = int(doc_id)
        doc_dic = {}
        for word in query_words:
            if word in wl.documents_terms_frequency[doc_id]:
                tf = wl.documents_terms_frequency[doc_id].get(word)
                idf = get_df_word(word)
                idf = math.log(length_inverted_index / idf, 10)
                doc_dic[word] = tf * idf
            elif len(centroid) != 0:
                doc_dic[word] = centroid[c_tools.get_inverted_index_keys().index(word)]

        document_term_tf_idf.append([doc_id, doc_dic])
    return document_term_tf_idf


def get_tf_idf_documents_ltn(documents_ids, query_words, centroid=[]):
    document_term_tf_idf = []
    length_inverted_index = len(wl.inverted_index)
    for doc_id in documents_ids:
        doc_id = int(doc_id)
        doc_dic = {}
        for word in query_words:
            if word in wl.documents_terms_frequency[doc_id]:
                tf = 1 + math.log(wl.documents_terms_frequency[doc_id].get(word), 10)
                idf = get_df_word(word)
                idf = math.log(length_inverted_index / idf, 10)
                doc_dic[word] = tf * idf
            elif len(centroid) != 0:
                doc_dic[word] = centroid[c_tools.get_inverted_index_keys().index(word)]

        document_term_tf_idf.append([doc_id, doc_dic])
    return document_term_tf_idf


def get_df_word(word):
    return len(wl.inverted_index.get(word))


def calculate_cosine_similarity(documents_vector, query_vector):
    """
    This function will calculate cosine similarity of documents tf_idf and query tf_idf
    :param documents_vector: list of tuples, each tuples is in the format of doc_id: dictionary{terms:tf_idf}
    :param query_vector: A dictionary of words: tf_idf
    :return: List of tuples in the format of doc_id: score
    """
    query_vector_length = calculate_vector_length(list(query_vector.values()))

    for d_tf in documents_vector:
        numerator = 0
        for q_tf in query_vector:
            if q_tf in d_tf[1]:
                numerator += query_vector.get(q_tf) * d_tf[1].get(q_tf)
        denumerator = calculate_vector_length(list(d_tf[1].values())) * query_vector_length
        if denumerator == 0:
            d_tf[1] = 0
        else:
            d_tf[1] = numerator / denumerator


def calculate_vector_length(number_list):
    return LA.norm(number_list, 2)


def calculate_score_document_query(document_list, tf_idf_query_dic_ltc, centroid=[]):
    """
    This function will calculate score for the documents
    :param centroid:
    :param document_list:
    :param tf_idf_query_dic_ltc:
    :return:
    """
    # depends on selection of method for calculating score, we choose the tf-idf variant
    doc_terms_lnc = get_tf_idf_documents_lnc(document_list, tf_idf_query_dic_ltc, centroid)

    # calculate the scores based on cosine similarity
    calculate_cosine_similarity(doc_terms_lnc, tf_idf_query_dic_ltc)
    sorted_document = sort_documents_depends_on_relativity_to_query(doc_terms_lnc)

    doc_id_sorted = [item[0] for item in sorted_document]
    return doc_id_sorted


def sort_documents_depends_on_relativity_to_query(sub_li):
    sub_li.sort(key=lambda x: x[1], reverse=True)
    return sub_li
