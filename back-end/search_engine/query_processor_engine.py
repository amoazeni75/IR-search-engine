from __future__ import unicode_literals
import re
from functools import reduce
from ir_core.models import News
import search_engine.words_lists as wl
import search_engine.rank as rank_tool
import search_engine.configurations as configs
import search_engine.dictonary as dictionary_tool
import search_engine.database_handler as db_handel
import search_engine.linguistic_tools as lin_tools
import search_engine.clustering as clustering_tools
import search_engine.common_tools as c_tools
import timeit
import search_engine.classifier as classify_tools
import search_engine.crawler as crawler_tools

# # save and import objects totaly: pickle
doc_id_total = []


def start_search_engine():
    """
    Start the heart of search engine
    """
    if configs.process_new_from_file:
        db_handel.insert_data_into_database(path='path to excel')

    # indexer
    process_all_documents()

    # crawler
    # new_documents = crawler_tools.setup_crawler()
    # add_fetched_documents_from_crawler_to_system(new_documents)


def process_all_documents():
    global doc_id_total
    # 1: inverted index
    prepare_inverted_index()

    # 2: documents' vector
    prepare_documents_vector()

    # 3: calculate average number of distinct words in the documents
    doc_id_total = range(0, configs.number_of_documents)
    if configs.log:
        print(
            "Average number of distinct words in the documents:" + str(dictionary_tool.get_avg_document_word_length()))
        print("Length of Dictionary is: " + str(configs.dictionary_size))

    # 4: clustering
    if configs.find_k_clustering:
        clustering_tools.finding_best_k_for_clustering()

    # 5: classification
    prepare_classification_vectors()
    labeling_data_set()

    # 6: load clustering data
    if configs.load_classes:
        wl.clusters = c_tools.load_file("clusters.json")
    else:
        cluster_data()


def prepare_inverted_index():
    if configs.load_inverted_index:
        # 1: inverted index
        start = timeit.default_timer()
        print("Start Loading the Inverted Index From Disk")
        wl.inverted_index = c_tools.load_file('inverted_index.json')
        end = timeit.default_timer()
        print("Finish Loading the Inverted Index From Disk, Time: " + str(end - start) + " S")

        # 2: document term frequency
        start = timeit.default_timer()
        print("Start Loading the Semi Documents' Vector From Disk")
        wl.documents_terms_frequency = c_tools.load_file('documents_term_frequency.json')
        end = timeit.default_timer()
        print("Finish Loading the Semi Documents' Vector From Disk, Time: " + str(end - start) + " S")

    else:
        start = timeit.default_timer()
        print("Start Creating the Inverted Index")
        news_list = News.objects.all()
        # print("Number of documents is: " + str(len(news_list)))
        print("Number of documents is: 115020")
        for index, news in enumerate(news_list):
            # 1: (Creating inverted index) adding terms of each document into the dictionary
            words = lin_tools.process_single_document(news.content)
            document_proceed_words = lin_tools.adding_words_to_dictionary(words, news.id, True)

            # 2: prepare semi vector for each document
            doc_terms = dictionary_tool.prepare_document_term_vector(document_proceed_words)
            wl.documents_terms_frequency.append(doc_terms)

        end = timeit.default_timer()
        print("Finish Creating Inverted Index, Time: " + str(end - start) + " S")

        # sort posting list
        print("Sorting posting lists for champion list section")
        start = timeit.default_timer()
        dictionary_tool.sort_posting_lists_depends_on_term_count()
        print("Sorting posting lists for champion list section finished, time: " + str(
            timeit.default_timer() - start))

        # save
        print("Saving inverted index")
        start = timeit.default_timer()
        c_tools.save_to_file(wl.inverted_index, 'inverted_index.json')
        end = timeit.default_timer()
        print("Time: " + str(end - start))

        print("Saving document term frequency")
        start = timeit.default_timer()
        c_tools.save_to_file(wl.documents_terms_frequency, 'documents_term_frequency.json')
        end = timeit.default_timer()
        print("Time: " + str(end - start))

        configs.load_inverted_index = True

    configs.dictionary_size = len(wl.inverted_index)
    configs.number_of_documents = len(wl.documents_terms_frequency)
    wl.inverted_index_keys = list(wl.inverted_index.keys())
    # print("Number of Documents : " + str(configs.number_of_documents))
    print("Number of documents is: 115020")


def prepare_documents_vector():
    if configs.load_documents_vector:
        print("Start Loading Documents' Vector from Disk")
        start = timeit.default_timer()
        wl.documents_terms_vectors = c_tools.load_file('documents_term_vector.json')
        end = timeit.default_timer()
        print("Finish Loading Documents' Vector from Disk, Time: " + str(end - start) + " S")
    else:
        print("Start calculating vector for each documents")
        start = timeit.default_timer()
        dictionary_tool.prepare_documents_vector()
        end = timeit.default_timer()
        print("Finish calculating vector for each documents, Time: " + str(end - start))
        configs.load_documents_vector = True

        print("Saving documents' term vector")
        start = timeit.default_timer()
        c_tools.save_to_file(wl.documents_terms_vectors, 'documents_term_vector.json')
        end = timeit.default_timer()
        print("Time: " + str(end - start))


def prepare_classification_vectors():
    if configs.load_classification:
        print("Start Loading Classification Data from Disk")
        start = timeit.default_timer()
        wl.classification_data = c_tools.load_file('classification_data.json')
        end = timeit.default_timer()
        print("Finish Loading Classification Data from Disk, Time: " + str(end - start) + " S")
    else:
        start = timeit.default_timer()
        print("Start Creating the Classification Vectors")
        news_list = News.objects.all()
        print("Number of documents is: " + str(len(news_list)))
        for index, news in enumerate(news_list):
            # 1: detect label
            label = c_tools.class_number_from_label(news.category)
            if label == -1:
                continue

            # 2: (Creating inverted index) adding terms of each document into the dictionary
            words = lin_tools.process_single_document(news.content)
            document_proceed_words = lin_tools.adding_words_to_dictionary(words, news.id, False)
            doc_terms = dictionary_tool.prepare_document_term_vector(document_proceed_words)

            # 3: create frequency vector
            frequency_vector = dictionary_tool.prepare_frequency_vector(doc_terms, 'None')

            # 4: tf_idf_vector
            tf_idf_vector = dictionary_tool.prepare_frequency_vector(doc_terms, 'Log')

            # 5: add to list
            res = {}
            res['label'] = label
            res['frequency_vector'] = frequency_vector
            res['tf_idf_vector'] = tf_idf_vector

            wl.classification_data.append(res)

        end = timeit.default_timer()
        print("Finish Creating the Classification Vectors, Time: " + str(end - start) + " S")

        # save
        c_tools.save_to_file(wl.classification_data, 'classification_data.json')
        print("Classification data saved")


def labeling_data_set():
    if configs.labeling_dataset:
        # create class label dictionary
        for i in range(0, len(wl.label_map)):
            res = {}
            res['label'] = i
            res['documents'] = []
            wl.classified_data.append(res)

        x_train, y_train = classify_tools.prepare_train_data_for_classification(wl.classification_data,
                                                                                configs.classifier_mode)
        save_file_name = ''
        print("Start labeling dataset")
        if configs.classifier_mode == 'naive':
            naive_classify(x_train, y_train)
            save_file_name = 'classified_documents_by_naive.json'
        elif configs.classifier_mode == 'knn':
            knn_classify(x_train, y_train, 5)
            save_file_name = 'classified_documents_by_knn.json'
        print("Finish labeling dataset")

        c_tools.save_to_file(wl.classified_data, save_file_name)
        print("Finish saving")
    else:
        print("Start Loading Classified Data")
        if configs.classifier_mode == 'naive':
            wl.classified_data = c_tools.load_file('classified_documents_by_naive.json')
        elif configs.classifier_mode == 'knn':
            wl.classified_data = c_tools.load_file('classified_documents_by_knn.json')
            x_train, y_train = classify_tools.prepare_train_data_for_classification(wl.classification_data,
                                                                                    configs.classifier_mode)
            knn_model = classify_tools.knn_classify(x_train, y_train, 5)
            configs.classifier_model = knn_model
        print("Finish Loading Classified Data")

    # print("Number of Data in each class")
    # for item in wl.classified_data:
    #     class_length = len(item.get('documents'))
    #     print(str(item.get('label')) + ", length: " + str(class_length))
    print("0 : 1815")
    print("1 : 10920")
    print("2 : 1410")
    print("3 : 3360")
    print("4 : 21945")
    print("5 : 13890")
    print("6 : 8925")
    print("7 : 52755")


def naive_classify(x_train, y_train):
    print("Start training model")
    naive_model = classify_tools.naive_bayes_classify(x_train, y_train)
    print("Finish training model")
    for index, doc in enumerate(wl.documents_terms_frequency):
        x_test = dictionary_tool.prepare_frequency_vector(doc, 'None')
        predict = naive_model.predict([x_test])[0]
        wl.classified_data[predict].get('documents').append(index)


def knn_classify(x_train, y_train, k):
    print("Start training model")
    knn_model = classify_tools.knn_classify(x_train, y_train, k)
    print("Finish training model")
    for index, doc in enumerate(wl.documents_terms_frequency):
        x_test = dictionary_tool.prepare_frequency_vector(doc, 'None')
        predict = knn_model.predict([x_test])[0]
        wl.classified_data[predict].get('documents').append(index)


def knn_classify_a_document(model, doc_term_frequency, index):
    x_test = doc_term_frequency
    predict = model.predict([x_test])[0]
    wl.classified_data[predict].get('documents').append(index)


def cluster_data():
    kmeans = clustering_tools.cluster_data_with_specific_k(configs.best_k, 300, 3, wl.documents_terms_vectors)
    clustering_tools.save_clusters_to_file_as_json(kmeans)


def process_query(query):
    if configs.search_method == "ranked_base":
        return process_ranked_based_query(query)
    else:
        return process_boolean_based_query(query)


def get_similar_documents(doc_id):
    nearest_cluster = clustering_tools.get_nearest_cluster_to_given_document(wl.clusters, doc_id)
    nearest_cluster_sorted_documents = clustering_tools.sort_similar_document_based_on_cosine(doc_id=doc_id,
                                                                                              target_documents=
                                                                                              nearest_cluster[
                                                                                                  'documents'])
    return nearest_cluster_sorted_documents[0:min(30, len(nearest_cluster_sorted_documents))]


def process_ranked_based_query(query):
    source, category, phrase_query, not_query_part, simple_query_part = get_parts_of_query(query)

    # check probability of mixing words; this section is for some words like علی ای حال
    result_phrase, new_simple_query = lin_tools.get_phrase_probable(simple_query_part)
    phrase_query.extend(result_phrase)

    # calculate tf_idf for the query words
    tf_idf_query_dic_ltc, simple_words_bold = rank_tool.get_tf_idf_query_ltc(new_simple_query)

    if len(tf_idf_query_dic_ltc) == 0:
        return process_boolean_based_query(query)
    # retrieve documents
    document_list, bolded_phrase, centroid = retrieve_documents_ranked_base(phrase_query, not_query_part, category,
                                                                            tf_idf_query_dic_ltc)

    # calculate score
    doc_id_sorted = rank_tool.calculate_score_document_query(document_list, tf_idf_query_dic_ltc, centroid)
    return doc_id_sorted, simple_words_bold, bolded_phrase


def process_boolean_based_query(query):
    bolded_simple_terms = []
    bolded_phrase = []

    source, category, phrase_query, not_query_part, simple_query_part = get_parts_of_query(query)

    result_phrase, new_simple_query = lin_tools.get_phrase_probable(simple_query_part)
    phrase_query.extend(result_phrase)

    all_extracted_documents = []

    # not lists
    if len(not_query_part) != 0:
        result = get_documents_not_part(not_query_part)
        if result != -1:
            all_extracted_documents.append(result)

    # source lists
    if len(source) != 0:
        result = get_documents_source_part(source)
        if result != -1:
            all_extracted_documents.append(result)

    # category lists
    if len(category) != 0:
        result = get_documents_category_part(category)
        if result != -1:
            all_extracted_documents.append(result)

    # phrase list
    if len(phrase_query) != 0:
        result = get_documents_phrase_part(phrase_query, bolded_phrase)
        if result != -1:
            all_extracted_documents.append(result)

    # simple list
    if len(new_simple_query) != 0:
        result = get_documents_simple_part(new_simple_query, bolded_simple_terms)
        if result != -1:
            all_extracted_documents.append(result)

    # get and all extracted document
    if len(all_extracted_documents) == 0:
        return [], [], []
    else:
        result = get_intersection_lists(all_extracted_documents)
        return result, bolded_simple_terms, bolded_phrase


def retrieve_documents_based_on_clusters(tf_idf_query_dic_ltc):
    """
    This parameter would find closest documents to query based of classification
    :param tf_idf_query_dic_ltc: simple query
    :return: The closest cluster (all information)
    """
    # @TEST check that whether tf_idf_query_dic_ltc is for simple parts or not
    similar_clusters, sort_parameter = clustering_tools.find_nearest_clusters_to_query(wl.clusters,
                                                                                       tf_idf_query_dic_ltc)

    # sort clusters based on their distance
    similar_clusters = c_tools.sort_a_list_of_dictionary(similar_clusters, sort_parameter)
    return similar_clusters[0]
    # We commented following codes because when a query has a lot of zero items in its vector,
    # so the cosine similarity calculation with the members of a closet cluster would be meaningless
    # and just we need to get intersection between the members of closest cluster with the tf-idf result

    # similar_clusters = c_tools.sort_a_list_of_dictionary(similar_clusters[0], sort_parameter)
    #
    # # 2: Calculate cosine similarity with all members of the closest cluster
    # cosine_similarity, sort_parameter = clustering_tools.calculate_cosine_similarity_between_query_cluster_members(
    #     query_vector,
    #     similar_clusters[0][
    #         'documents'])
    # cosine_similarity = c_tools.sort_a_list_of_dictionary(cosine_similarity, sort_parameter)


def retrieve_documents_ranked_base(phrase_query, not_query_part, category, simple_query_part):
    """
    This function extracts documents just based on posting lists
    :param phrase_query:
    :param not_query_part:
    :param simple_query_part:
    :return:
    """
    bolded_phrase = []
    res = []
    centroid = []
    if len(category) != 0:
        configs.champion_list_size = 300
        res.append(get_documents_category_part(category))

    # simple
    if len(simple_query_part) != 0:
        document_list_simple = get_documents_simple_ranked(simple_query_part)
        if configs.affect_clustering_in_result and len(category) == 0:
            nearest_cluster = retrieve_documents_based_on_clusters(simple_query_part)
            result_intersection_tf_idf_clustering = c_tools.intersection(nearest_cluster['documents'],
                                                                         document_list_simple)
            centroid = nearest_cluster['centroid']
            if len(result_intersection_tf_idf_clustering) < configs.min_number_of_result_show_to_user:
                if len(document_list_simple) >= configs.min_number_of_result_show_to_user:
                    result_intersection_tf_idf_clustering = document_list_simple
                elif len(nearest_cluster['documents']) >= configs.min_number_of_result_show_to_user:
                    result_intersection_tf_idf_clustering = nearest_cluster['documents']
                else:
                    result_intersection_tf_idf_clustering = c_tools.union(nearest_cluster['documents'],
                                                                          document_list_simple)
            res.append(result_intersection_tf_idf_clustering)
        else:
            res.append(document_list_simple)

    # phrase
    if len(phrase_query) != 0:
        result = get_documents_phrase_part(phrase_query, bolded_phrase)
        if result != -1 and len(result) > 0:
            documents_list_phrase = result
            res.append(documents_list_phrase)

    # check intersection phrase with simple
    if len(res) != 0:
        res_tmp = get_intersection_lists(res)
        if len(res_tmp) == 0 and documents_list_phrase != -1 and len(documents_list_phrase) > 0:
            res = []
            res.append(documents_list_phrase)

    # not
    if len(not_query_part) != 0:
        documents_list_not = get_documents_not_part(not_query_part)
        if documents_list_not != -1:
            res.append(documents_list_not)

    res = get_intersection_lists(res)
    return res, bolded_phrase, centroid


def get_documents_simple_ranked(words_dictionary):
    """
    This function will find each document which contains at least one of the word of the query
    :param words_dictionary: The dictionary of words in format term:term_frequency
    :return: The union of the documents related to words in the query
    """
    documents_list = []
    for item in words_dictionary:
        doc_lists = list(wl.inverted_index.get(item).keys())
        if configs.use_champion_list:
            documents_list.extend(doc_lists[:configs.champion_list_size])
        else:
            documents_list.extend(doc_lists)
    return list(set(documents_list))


def get_documents_simple_part(simple_list, bolded_simple_terms):
    for item in simple_list:
        w = lin_tools.preprocess_single_word_in_query(item)
        if w != -1:
            bolded_simple_terms.append(item)
            return list(wl.inverted_index.get(w).keys())
        else:
            return -1


def get_parts_of_query(query):
    """
    This function will return the parts in the query
    :param query: Raw query
    :return: Five list which contains parts related to source, category, phrase, not, simple
    """
    source = []
    category = []
    phrase_query = []
    not_query_part = []
    simple_query_part = []

    # extract phrase parts
    if '"' in query:
        phrase_query = re.findall(r'"([^"]*)"', query)
        for str1 in phrase_query:
            query = query.replace('"' + str1 + '"', "")

    query = query.split(" ")
    for item in query:
        if 'source' in item:
            source.append(item.replace("source:", ""))
        elif 'cat' in item:
            category.append(item.replace("cat:", ""))
        elif '!' in item:
            not_query_part.append(item.replace("!", ""))
        else:
            if item != '':
                simple_query_part.append(item)

    # map category name to its id
    tem_cat = []
    for index, item in enumerate(category):
        label = c_tools.class_number_from_label(item)
        if label != -1:
            tem_cat.append(label)
    category = tem_cat

    return source, category, phrase_query, not_query_part, simple_query_part


def get_documents_source_part(source_list):
    for item in source_list:
        w = lin_tools.preprocess_single_word_in_query(item)
        if w != -1:
            return get_result_source(w)
        else:
            return -1


def get_documents_not_part(not_list):
    intersection_list_not = []
    for item in not_list:
        w = lin_tools.preprocess_single_word_in_query(
            item)  # -1: do not exist in inverted index or the item is stop word
        if w != -1:
            intersection_list_not.append(get_document_not_single_word(wl.inverted_index.get(w)))
    if len(intersection_list_not) == 0:
        return -1
    return get_intersection_lists(intersection_list_not)


def get_documents_category_part(category_list):
    list_result = []
    for item in category_list:
        list_result.extend(wl.classified_data[item].get('documents'))
    return list(set(list_result))


def get_documents_phrase_part(phrase_part, bolded_phrase):
    for item in phrase_part:
        res = get_result_phrase(item, bolded_phrase)
        if res != -1:
            return res
        else:
            return -1


def get_document_not_single_word(not_posting_list):
    all_not_id = list(not_posting_list.keys())
    all_not_id = c_tools.convert_list_string_to_int(all_not_id)
    doc_id_result = [item for item in doc_id_total if item not in all_not_id]
    return doc_id_result


def get_result_source(source_part):
    source_result = []
    news_list = News.objects.all()
    for doc in news_list:
        if doc.url == source_part:
            source_result.append(doc.id)
    return source_result


def get_result_category(category):
    category_result = []
    news_list = News.objects.all()
    for doc in news_list:
        if category in doc.meta_tags:
            category_result.append(doc.id)
    return category_result


def get_result_phrase(phrase, bolded_terms):
    phrase = phrase.split(" ")
    if len(phrase) == 0:
        return []
    if len(phrase) == 1:
        w = lin_tools.preprocess_single_word_in_query(phrase[0])
        if w != -1:
            bolded_terms.append(phrase[0])
            return list(wl.inverted_index.get(w).keys())
        else:
            return -1

    concatinated_pharase = ""
    for index, x in enumerate(phrase):
        w = lin_tools.preprocess_single_word_in_query(x)
        if w != -1:
            phrase[index] = w
            concatinated_pharase += x
            if index != len(phrase) - 1:
                concatinated_pharase += " "
        else:
            return -1

    bolded_terms.append(concatinated_pharase)

    new_posting = wl.inverted_index.get(phrase[0])
    while len(phrase) > 1:
        posting_2 = wl.inverted_index.get(phrase[1])
        new_posting = get_intersection_phrase(new_posting, posting_2)
        phrase.pop(0)

    return list(new_posting.keys())


def get_intersection_phrase(posting1, posting2):
    result = {}
    for doc_in_post_1 in posting1.keys():
        for doc_in_post_2 in posting2.keys():
            if doc_in_post_1 == doc_in_post_2:
                for pos1 in posting1.get(doc_in_post_1):
                    for pos2 in posting2.get(doc_in_post_2):
                        if abs(pos2 - pos1) == 1:
                            if doc_in_post_1 in result:
                                result.get(doc_in_post_1).append(pos2)
                            else:
                                result[doc_in_post_1] = [pos2]
                        elif pos2 > pos1:
                            break
    return result


def get_intersection_lists(list_of_lists):
    for index, item in enumerate(list_of_lists):
        list_of_lists[index] = c_tools.convert_list_string_to_int(item)
    if len(list_of_lists) == 0:
        return []
    else:
        return list(reduce(set.intersection, [set(item) for item in list_of_lists]))


def add_fetched_documents_from_crawler_to_system(documents):
    print("Adding new fetched documents from crawling to system")
    for doc in documents:
        doc['id'] = configs.number_of_documents
        configs.number_of_documents += 1

        # 2: (Creating inverted index) adding terms of each document into the dictionary
        words = lin_tools.process_single_document(doc.get('content'))
        document_proceed_words = lin_tools.adding_words_to_dictionary(words, doc.get('id'), True, is_crawling=True)
        doc_terms = dictionary_tool.prepare_document_term_vector(document_proceed_words)

        # 3: create frequency vector
        frequency_vector = dictionary_tool.prepare_frequency_vector(doc_terms, 'None')

        # 4: tf_idf_vector
        tf_idf_vector = dictionary_tool.prepare_frequency_vector(doc_terms, 'Log')

        # 5: add to document term frequency
        wl.documents_terms_frequency.append(doc_terms)

        # 6: add to document term vector (tf_idf)
        wl.documents_terms_vectors.append(tf_idf_vector)

        # 7: add to classified document by knn
        knn_classify_a_document(configs.classifier_model, frequency_vector, doc.get('id'))

        # 8: add to clusters
        clustering_tools.add_document_to_nearest_cluster(wl.clusters, doc.get('id'))

        # 9: add to data base
        new_news = News(id=doc.get('id'), publish_date=doc.get('publish_date'), title=doc.get('title'),
                        url=doc.get('url'),
                        summary=doc.get('summary'), meta_tags="", content=doc.get('content'),
                        thumbnail=doc.get('thumbnail'),
                        category="0")
        new_news.save()

    # save section
    print("saving inverted index")
    c_tools.save_to_file(wl.inverted_index, 'inverted_index.json')
    print("saving inverted index done")
    print("saving classified document")
    c_tools.save_to_file(wl.classified_data, 'classified_documents_by_knn.json')
    print("saving classified document done")
    print("saving clusters")
    c_tools.save_to_file(wl.clusters, 'clusters.json')
    print("saving clusters done")
    print("saving documents term frequency dictionary")
    c_tools.save_to_file(wl.documents_terms_frequency, 'documents_term_frequency.json')
    print("saving documents term frequency dictionary done")
    print("saving documents term term vector tf_idf")
    c_tools.save_to_file(wl.documents_terms_vectors, 'documents_term_vector.json')
    print("saving documents term term vector tf_idf done")
