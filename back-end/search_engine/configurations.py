pure_number_tokens = 0
after_removing_stop_words = 0
number_of_documents = 0
champion_list_size = 100
dictionary_size = 0

search_method = "ranked_base"  # "boolean"
classifier_mode = 'knn'
classifier_model = ""

log = True

min_k = 5
max_k = 40
best_k = 13
seed = 7

number_of_front_queues = 5  # levels of priority for front queue
number_of_cluster_for_comparing_with_query = 2  # This a parameter
min_number_of_result_show_to_user = 32  # Minimum number of news that should show to user

load_RSS = True  # default = true
load_classes = True  # default = true
labeling_dataset = False  # This cause to label data set by the help of 1000 labeled data by hand default = false
find_k_clustering = False  # default = false
use_champion_list = True  # default = true
load_classification = True  # This the list of 1000 labeled data by hand default = true
load_inverted_index = True  # default = true
load_documents_vector = True  # default = true
process_new_from_file = False  # default = false
affect_clustering_in_result = True  # This parameter would affect the result of clustering with tf-idf, default = false

prefix_path = 'resources/'
crawling = True

# 14k
