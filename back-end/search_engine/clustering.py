import numpy as np
from sklearn.cluster import KMeans
import search_engine.configurations as config
import search_engine.words_lists as wl
import timeit
from kneed import KneeLocator
import matplotlib.pyplot as plt
from scipy.spatial import distance
import search_engine.rank as rank_tools
import json
import search_engine.common_tools as c_tools

plt.style.use('ggplot')


def finding_best_k_for_clustering():
    """
    This function runs k time the k-means algorithm
    :return:
    """
    print("Finding clustering")
    seed = 7
    wcss = []
    for i in range(config.min_k, config.max_k):
        start = timeit.default_timer()
        kmeans = cluster_data_with_specific_k(i, 300, 2, wl.documents_terms_vectors)
        wcss.append(kmeans.inertia_)
        print(str(i) + "," + str(kmeans.inertia_))
        stop = timeit.default_timer()
        print('Time: ', stop - start)
    calculate_best_k_clustering(wcss)


def calculate_best_k_clustering(wcss):
    """
    Finds the best k based on MSS
    :param wcss:
    :return:
    """
    x = range(config.min_k, config.min_k + len(wcss))
    y = wcss
    sensitivity = [1, 3, 5, 10, 100, 200, 400]
    knees = []
    norm_knees = []
    for s in sensitivity:
        kl = KneeLocator(x, y, curve='convex', direction='decreasing', S=s)
        knees.append(kl.knee)
        norm_knees.append(kl.norm_knee)

    print("knees")
    print(knees)
    plt.plot(range(config.min_k, config.min_k + len(wcss)), wcss)

    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.show()
    print("Errors: ")
    print(wcss)


def cluster_data_with_specific_k(k, max_iteration, n_init, data):
    """
    This function will clusters the data
    :param k:
    :param max_iteration:
    :param n_init:
    :param data:
    :return:
    """
    start = timeit.default_timer()
    print("Clustering with K = " + str(k) + ", Started")
    kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=max_iteration, n_init=n_init, random_state=0)
    kmeans.fit(data)
    print("Clustering with K = " + str(k) + " Finished, time: " + str(timeit.default_timer() - start))
    return kmeans


def save_clusters_to_file_as_json(kmeans):
    """
    This functions will create a json file which contains information about every cluster
    such as their centroids, documents in the classes, length of centroids' vector, labels
    :param kmeans: the object of class k-means
    :return: save .json file in disk
    """
    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_

    data_before_save = {}
    for i in range(0, config.best_k):
        data_before_save[i] = {}
        data_before_save[i]['centroid'] = centroids[i].tolist()
        data_before_save[i]['label'] = str(i)
        data_before_save[i]['documents'] = []

    for index, item in enumerate(labels):
        c = data_before_save.get(item)
        c.get('documents').append(index)

    for i in range(0, config.best_k):
        data_before_save[i]['length'] = rank_tools.calculate_vector_length(data_before_save[i].get('documents'))

    list_out_put = list(data_before_save.values())
    with open('clusters.json', 'w') as fp:
        json.dump(list_out_put, fp)


def find_nearest_clusters_to_query(centroids, query_dict):
    dists = []
    for center in centroids:
        dist = calculate_cosine_similarity_cluster_query(query_dict, center)
        res = center
        res['distance'] = dist
        dists.append(res)
    return dists, 'distance'


def eucl_dist(a, b, f_size):
    esum = 0
    for i in range(f_size):
        if a[i] and b[i]:
            esum += (a[i] - b[i]) ** 2
    return np.sqrt(esum)


def get_diff(c1, c2):
    row, col = c1.shape
    csum = 0
    for i in row:
        csum += np.linalg.norm(c1[i], c2[i])
    return csum


def get_min(X, f_size):
    vmin = np.zeros(f_size)
    for x in X:
        for j in x:
            j = int(j)
            if vmin[j] > x[j]:
                vmin[j] = x[j]
    return vmin


def get_max(X, f_size):
    vmax = np.zeros(f_size)
    for x in X:
        for j in x:
            j = int(j)
            if vmax[j] < x[j]:
                vmax[j] = x[j]
    return vmax


def get_mean(points, f_size):
    cmean = np.zeros(f_size)
    for i in points:
        for j in range(f_size):
            if j in points[i]:
                cmean += points[i][j]
    cmean = cmean / len(points)
    return cmean


def k_mean(x, d_size, f_size, k):
    # initalizing cluster variable
    cluster = np.zeros(d_size)

    # calculation min and max for every dimension of data
    minv = get_min(x, f_size)
    maxv = get_max(x, f_size)

    # for k in range(2,11):
    error = 0

    # initalizing centroids of k clusters
    center = np.zeros((k, f_size))
    for i in range(k):
        for j in range(f_size):
            center[i, j] = minv[j] + np.random.random() * (maxv[j] - minv[j])

    # assigining zeros to old centroids value
    center_old = np.zeros(center.shape)

    # initial error
    err = get_diff(center, center_old)

    while err != 0:

        # calculatin distance of data points from centroids and assiging min distance cluster centroid as data point cluster
        for i in range(len(x)):
            distances = []
            for c in range(center.shape[0]):
                distances.append(eucl_dist(x[i], center[c], f_size))
            clust = np.argmin(distances)
            cluster[i] = clust

        # changing old centroids value
        center_old = np.copy(center)

        # Finding the new centroids by taking the average value
        for i in range(k):
            points = [x[j] for j in range(len(x)) if cluster[j] == i]
            if points:
                center[i] = get_mean(points, f_size)

        # calculation difference between new centroid and old centroid values
        err = get_diff(center, center_old)

    # calculation total difference between cluster centroids and cluster data points
    for i in range(k):
        d = [eucl_dist(x[j], center[i], f_size) for j in range(len(x)) if cluster[j] == i]
        error += np.sum(d)

    # counting data points in all clusters
    count = {key: 0.0 for key in range(k)}
    for i in range(len(x)):
        count[cluster[i]] += 1

    # displaying cluster number, average distance between centroids and data points and cluster count
    print(k, error / len(x), count)

    return cluster


def get_initial_center_k_mean_plus(data, k):
    first = data[0]
    centers = []
    centers.append(first)
    for i in data:
        index, should_add = get_max_distance_from_centers(i, centers)
        if len(centers) <= k and should_add:
            centers.append(i)


def get_max_distance_from_centers(data, list_data):
    dista_max = -1
    for i in list_data:
        if eucl_dist(data, i, 2) < dista_max:
            dista_max = eucl_dist(data, i, 2)
    return dista_max, True


def calculate_cosine_similarity_cluster_query(query_dict, centroid):
    numerator = 0
    query_vector_length = rank_tools.calculate_vector_length(list(query_dict.values()))
    for k, v in query_dict.items():
        index = c_tools.get_inverted_index_keys().index(k)
        numerator += v * centroid['centroid'][index]

    denumerator = centroid['length'] * query_vector_length
    if denumerator == 0:
        return 0
    else:
        return numerator / denumerator


#
# def calculate_cosine_similarity_between_query_cluster_members(query_vector, cluster_members_vector):
#     """
#     This function calculates the cosine similarity between members of a cluster and query vector
#     :param query_vector: is the vector of query (ndarray)
#     :param cluster_members_vector: is a list of doc_ids
#     :return: a list of dictionaries which key is doc_id and value is distance (1 - cosine)
#     """
#     # @TEST
#     distances = []
#     for doc_id in cluster_members_vector:
#         dist = get_cosine_distance_vector_to_doc_id(doc1_vector=query_vector, doc2_id=doc_id)
#         res = {}
#         res['doc_id'] = doc_id
#         res['distance'] = dist
#         distances.extend(res)
#     return distances, 'distance'
#

def get_nearest_cluster_to_given_document(centroids, document_id):
    dists = []
    for center in centroids:
        dist = get_cosine_distance_vector_to_doc_id(doc1_vector=center['centroid'], doc2_id=document_id)
        res = center
        res['distance'] = dist
        dists.append(res)

    dists = c_tools.sort_a_list_of_dictionary(dists, 'distance')
    return dists[0]


def add_document_to_nearest_cluster(centroids, document_id):
    min_dis = 1000000000000000000
    index = -1
    for i, center in enumerate(centroids):
        dist = get_cosine_distance_vector_to_doc_id(doc1_vector=center['centroid'], doc2_id=document_id)
        if dist < min_dis:
            min_dis = dist
            index = i
    wl.clusters[index].get('documents').append(document_id)


def sort_similar_document_based_on_cosine(doc_id, target_documents):
    document_vector = wl.documents_terms_vectors[doc_id]
    distances = {}
    for doc in target_documents:
        if doc == doc_id:
            continue
        similarity = get_cosine_distance_vector_to_doc_id(doc1_vector=document_vector, doc2_id=doc)
        distances[doc] = similarity

    distances = c_tools.sort_dictionary_by_value(distances)
    return list(distances.keys())


def get_cosine_distance_vector_to_doc_id(doc1_vector, doc2_id):
    return distance.cosine(wl.documents_terms_vectors[doc2_id], doc1_vector)
