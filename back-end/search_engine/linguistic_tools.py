import hazm as hz
from PersianStemmer import PersianStemmer
import search_engine.words_lists as wl
from itertools import combinations
import re
import string
import search_engine.configurations as config

ps = PersianStemmer()
stop_words = hz.stopwords_list()
normalizer = hz.Normalizer()
stemmer = hz.Stemmer()
lemmatizer = hz.Lemmatizer()


def process_single_document(doc_content):
    # 1: remove html tags and irrelevant contents
    cleaned_content_from_tag = remove_tags(doc_content)
    # 2: normalize text
    normalize_text = normalizer.normalize(cleaned_content_from_tag)
    # 3: tokenize
    words_token = hz.word_tokenize(normalize_text)
    config.pure_number_tokens += len(words_token)
    return words_token


def preprocess_single_word_in_query(word):
    # 1: normalized
    word = normalizer.normalize(word)
    # 2: lemmatized and stemmer
    word_lemmatized = lemmatizer.lemmatize(word)
    if '#' in word_lemmatized:
        word = word_lemmatized.split('#')[-1]
    else:
        word = ps.run(word)
    # 3: combine different style of words
    temp_word, temp_word2 = get_same_words(word)
    if temp_word != -1:
        word = temp_word
    # 4: stop word check
    if word in stop_words or len(word) == 1:
        return -1
    # 5: check in dictionary
    if word in wl.inverted_index:
        return word
    else:
        return -1


def get_same_words(word):
    for item in wl.words_same_view:
        if word in item:
            return item[0], item[1]
    return -1, -1


def get_phrase_probable(query):
    result_phrase = []
    new_simple_query = query

    mixing_words = list(combinations(query, 2))
    mixing_words.extend(list(combinations(query, 3)))
    for item in mixing_words:
        str_mix = ""
        for index, word in enumerate(item):
            if index != len(item) - 1:
                str_mix += word + " "
            else:
                str_mix += word
        if str_mix in wl.proximity_phrases:
            result_phrase.append(str_mix)
            new_simple_query = list(set(new_simple_query).difference(set(item)))

    for index, i in enumerate(result_phrase):
        new_word = normalizer.normalize(i)
        if new_word == 'چنان چه':
            new_word = 'چنانچه'
        result_phrase[index] = new_word
    return result_phrase, new_simple_query


def get_text_bolded(content, simple_terms, phrase_terms):
    result = "<p>"
    content = normalizer.normalize(content)
    cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    clear_content = re.sub(cleaner, '', content)
    combined_list = []
    if len(simple_terms) != 0:
        combined_list.extend(simple_terms)
    if len(phrase_terms) != 0:
        combined_list.extend(phrase_terms)

    for item in combined_list:
        item = normalizer.normalize(item)
        index_term = clear_content.find(' ' + item + ' ')
        if index_term == -1:
            same1, same2 = get_same_words(item)
            if same1 != -1:
                index_term = clear_content.find(same1)
                if index_term == -1:
                    index_term = clear_content.find(same2)
                    if index_term == -1:
                        continue
                    else:
                        item = same2
                else:
                    item = same1
            else:
                continue

        index_start = clear_content.find(" ", max(index_term - 30, 0))
        index_end = clear_content.find(" ", min(index_term + 35, len(clear_content) - 1))
        part1 = clear_content[index_start:index_term]
        part2 = clear_content[index_term + 1 + len(item):index_end]
        temp_res = "..." + part1 + " " + "<b style=\"color:red\">" + item + "</b>" + part2 + "..."
        result += temp_res

    result += "</p>"
    return result


def tokenize(content_text):
    words = re.findall(r"[\w']+", content_text)
    return words


def remove_tags(content_text):
    # remove all html tags
    content_text = content_text.replace("&nbsp;", ' ')
    cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    clean_text = re.sub(cleaner, '', content_text)

    # remove english punctuation signs
    replace_punctuation = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    clean_text = clean_text.translate(replace_punctuation)

    # remove persian punctuation signs and numbers
    cleaner = re.compile('[a-zA-Z]|[۰-۹]|١|٥|٨|٠|٤|٣|٢|[0-9]|؟|/|:|–|!|،|؛')
    clean_text = re.sub(cleaner, ' ', clean_text)

    return clean_text


def adding_words_to_dictionary(words, doc_id, add_to_inverted_index, is_crawling=False):
    document_proceeds_words = []
    for position, word in enumerate(words):

        # verb: get root and noun: get stem
        word_lemmatized = lemmatizer.lemmatize(word)
        if '#' in word_lemmatized:
            word = word_lemmatized.split('#')[-1]
        else:
            word = ps.run(word)

        # remove stop words
        if word in stop_words or len(word) == 1:
            continue

        # add to inverted index
        if is_crawling:
            add_cleaned_word_to_dictionary_crawling(word, position, doc_id,
                                                    document_proceeds_words)
        else:
            add_cleaned_word_to_dictionary_common(word, add_to_inverted_index, position, doc_id,
                                                  document_proceeds_words)

        # if word in wl.inverted_index:
        #     if add_to_inverted_index:
        #         add_word_into_dictionary(word, position, doc_id, True)
        #     document_proceeds_words.append(word)
        # else:
        #     same_word, same_word2 = get_same_words(word)
        #     if same_word == -1:
        #         if add_to_inverted_index:
        #             # this word is not in the dictionary and it is not in same words list
        #             add_word_into_dictionary(word, position, doc_id, False)
        #             document_proceeds_words.append(word)
        #     else:
        #         if add_to_inverted_index:
        #             document_proceeds_words.append(same_word)
        #         if add_to_inverted_index:
        #             if same_word in wl.inverted_index:
        #                 add_word_into_dictionary(same_word, position, doc_id, True)
        #                 if not add_to_inverted_index:
        #                     document_proceeds_words.append(same_word)
        #             else:
        #                 add_word_into_dictionary(same_word, position, doc_id, False)

    return document_proceeds_words


def add_cleaned_word_to_dictionary_common(word, add_to_inverted_index, position, doc_id, document_proceeds_words):
    # add to inverted index
    if word in wl.inverted_index:
        if add_to_inverted_index:
            add_word_into_dictionary(word, position, doc_id, True)
        document_proceeds_words.append(word)
    else:
        same_word, same_word2 = get_same_words(word)
        if same_word == -1:
            if add_to_inverted_index:
                # this word is not in the dictionary and it is not in same words list
                add_word_into_dictionary(word, position, doc_id, False)
                document_proceeds_words.append(word)
        else:
            if add_to_inverted_index:
                document_proceeds_words.append(same_word)
            if add_to_inverted_index:
                if same_word in wl.inverted_index:
                    add_word_into_dictionary(same_word, position, doc_id, True)
                    if not add_to_inverted_index:
                        document_proceeds_words.append(same_word)
                else:
                    add_word_into_dictionary(same_word, position, doc_id, False)


def add_cleaned_word_to_dictionary_crawling(word, position, doc_id, document_proceeds_words):
    # add to inverted index
    if word in wl.inverted_index:
        add_word_into_dictionary(word, position, doc_id, True, True)
        document_proceeds_words.append(word)
    else:
        same_word, same_word2 = get_same_words(word)
        if same_word != -1:
            document_proceeds_words.append(same_word)
            if same_word in wl.inverted_index:
                add_word_into_dictionary(same_word, position, doc_id, True, True)


def add_word_into_dictionary(word, position, doc_id, is_exist, reorder=False):
    if is_exist:
        posting_list = wl.inverted_index.get(word)
        if doc_id in posting_list:
            posting_list.get(doc_id).append(position)
        else:
            if reorder:
                d1 = {}
                d1[str(doc_id)] = [position]
                d1.update(posting_list)
                wl.inverted_index[word] = d1
            else:
                posting_list[doc_id] = [position]

    else:
        wl.inverted_index[word] = {doc_id: [position]}
