from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
import search_engine.configurations as configs


def naive_bayes_classify(x_train, y_train):
    clf = MultinomialNB(alpha=1)
    clf = clf.fit(x_train, y_train)
    return clf


def knn_classify(x_train, y_train, k):
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(x_train, y_train)
    return model


def prepare_train_data_for_classification(classification_data, classifier):
    x_train = []
    y_train = []
    for item in classification_data:
        if classifier == 'naive':
            x_train.append(item.get('frequency_vector'))
        elif classifier == 'knn':
            x_train.append(item.get('tf_idf_vector'))
        y_train.append(int(item.get('label')))
    return x_train, y_train
