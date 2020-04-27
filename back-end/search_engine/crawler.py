import requests
import search_engine.words_lists as wl
import search_engine.configurations as config
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import numpy as np
import math
import search_engine.common_tools as c_tools
import random
import re

seed = 7


def setup_crawler():
    print("Crawler started with thread")
    # 1: init front queues
    for i in range(0, config.number_of_front_queues):
        wl.front_queues.append([])
    # 2: load rss
    load_rss_from_file('RSS.json')

    # 3: getting all link from all rss
    dict_host_items = fetch_all_items_from_all_rss()

    # 4: add items to front queues
    add_extracted_items_from_rss_to_front_queue(dict_host_items)

    # 5: first initialization of back queue
    # add_item_to_back_queue_from_front_queue_directly()

    # 6: start crawling
    return star_crawling()


def get_html_page(url):
    """
    This function returns all contents of the given url
    :param url: the url of page
    :return: a soup which can access the data by their tags
    """
    try:
        code = requests.get(url)
        plain = code.text
        soup = BeautifulSoup(plain, "html.parser")
        # items = soup.findAll('item')
        # print(items[0].findChildren())
        return soup
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return -1


def extract_all_items_in_a_rss(soup):
    """
    This function extracts all link in a rss
    :param soup: html page soup
    :return: a list of items tag which their url does not seen yet
    """
    items = soup.findAll('item')
    item_should_fetch_content = []
    for i in items:
        url = get_url_from_item(i)
        if url != -1 and url not in wl.seen_urls:
            wl.seen_urls.append(url)
            item_should_fetch_content.append(i)
    return item_should_fetch_content


def add_extracted_items_from_rss_to_front_queue(dictionary_host_items):
    """
    This function will add  each item tag to a front queue based on its priority
    :param dictionary_host_items: list of the urls which are extracted from a rss
    :return:
    """
    counter = 0
    for item in dictionary_host_items:
        priority = get_host_priority(item.get('host_name'))
        # priority = np.random.randint(low=0, high=len(wl.front_queues), size=1)[0]
        wl.front_queues[priority].extend(item.get('items'))
        counter = counter + len(item.get('items'))
    print("Total number of item fetched: " + str(counter))


def get_url_from_item(item):
    """
    This function extracts the url from an item
    :param item: one item tag in a rss page
    :return: url
    """
    try:
        for i in item.contents:
            if 'http' in i:
                return i
        return -1
    except Exception as exception:
        return -1


def add_url_to_back_queue(url):
    """
    Add a new url to its corresponding queue, if it does not exist, create a new list for its host
    :param url:
    :return:
    """
    host_name = get_host_from_url(url)
    if host_name in wl.back_queues:
        wl.back_queues.get(host_name).append(url)
    else:
        wl.inverted_index[host_name] = [url]


def get_host_from_url(url):
    """
    Extracts the host name from the given url
    :param url:
    :return:
    """
    return urlparse(url).hostname


def get_a_item_tag_from_front_queue_round_robin():
    """
    This function will generate prioritized number based on round robin algorithm
    :return:
    """
    # temp_list = []
    # for i in wl.front_queues:
    #     if len(i) != 0:
    #         temp_list.append(i)
    #
    # priority = np.random.randint(low=1, high=((len(temp_list) + 1) * len(temp_list)) / 2,
    #                              size=1)
    # a = 1
    # b = 1
    # c = priority * (-2)
    # delta = b * b - 4 * a * c
    # x1 = -b + math.sqrt(delta)
    # x1 /= 2 * a
    # return temp_list[min(max(math.ceil(x1) - 1, 0), len(temp_list) - 1)]
    len_fronts = 0
    for f_list in wl.front_queues:
        len_fronts += len(f_list)

    if len_fronts == 0:
        return -1

    while True:
        num = np.random.randint(low=0, high=len(wl.front_queues), size=1)[0]
        if len(wl.front_queues[num]) != 0:
            return num


def biased_front_queue_selector():
    seen_front_queue = []
    print("Try to get a url from front queue")
    while True:
        front_queue_id = get_a_item_tag_from_front_queue_round_robin()
        if front_queue_id == -1:
            return -1
        if len(wl.front_queues[front_queue_id]) != 0:
            item_new = wl.front_queues[front_queue_id].pop(0)
            print("th url from front queue fetched successfully")
            return item_new
        else:
            seen_front_queue.append(front_queue_id)
            seen_front_queue = list(set(seen_front_queue))
            if len(seen_front_queue) == len(wl.front_queues):
                # This means there is not any links in none of the front queues
                return -1


def load_rss_from_file(address):
    if config.load_RSS:
        print("Loading RSS URLs from Disk")
        wl.rss_host_url_dictionary = c_tools.load_file(address)
        for item in wl.rss_host_url_dictionary:
            item['refresh_rate'] = int(item.get('refresh_rate'))
        print("Finish Loading RSS URLs from Disk")
    else:
        print("Start Preparing RSS URLs from Disk")
        # read lines from rss.txt
        file1 = open(config.prefix_path + 'rss.txt', 'r')
        Lines = file1.readlines()
        # create rss object
        for line in Lines:
            host_name = get_host_from_url(line)
            res = {}
            res['host_name'] = host_name
            res['refresh_rate'] = 10
            res['url'] = line.rstrip()
            wl.rss_host_url_dictionary.append(res)
        # save rss.json
        c_tools.save_to_file(wl.rss_host_url_dictionary, address)
        print("Finish Preparing RSS URLs from Disk")


def fetch_all_items_from_all_rss():
    print("Start Fetching all Links in all RSS")
    result = []
    for item in wl.rss_host_url_dictionary:
        print("Start Fetching  RSS Page of " + item.get('url'))
        rss_page_soup = get_html_page(item.get('url'))
        if rss_page_soup == -1:
            print("Fetching  RSS Page of " + item.get('url') + " Failed.")
        else:
            items_in_a_rss_page = extract_all_items_in_a_rss(rss_page_soup)
            res = {}
            res['host_name'] = item.get('host_name')
            res['items'] = items_in_a_rss_page
            result.append(res)

            wl.back_queues[item.get('host_name')] = []

            print("Fetching  RSS Page of " + item.get('url') + " Completed.")
    return result
    print("Finish Fetching all Links in all RSS")


def get_host_priority(host_name):
    return 0
    # sort hosts based on their refresh rate
    wl.rss_host_url_dictionary = c_tools.sort_a_list_of_dictionary(wl.rss_host_url_dictionary, 'refresh_rate')

    # find priority
    index = c_tools.get_index_of_an_object_by_attribute(wl.rss_host_url_dictionary, 'host_name', host_name)

    q = len(wl.rss_host_url_dictionary) // config.number_of_front_queues

    q = index // q

    q = min(max(0, q), config.number_of_front_queues - 1)

    return q


def get_an_item_to_crawl_from_back_queue():
    return get_item_from_front()
    print("Start getting an item from back queue")
    back_selection_index = np.random.randint(low=0, high=len(wl.back_queues), size=1)[0]

    host_name = list(wl.back_queues.keys())[back_selection_index]

    if len(wl.back_queues.get(host_name)) == 0:
        res = insert_item_to_back_queue(host_name)
        if res == -1:
            return -1

    ret_item = wl.back_queues.get(host_name).pop(0)

    if len(wl.back_queues.get(host_name)) == 0:
        res = insert_item_to_back_queue(host_name)
        if res == -1:
            return -1

    return ret_item


def get_item_from_front():
    if len(wl.front_queues[0]) == 0:
        return -1
    else:
        return wl.front_queues[0].pop(0)


def insert_item_to_back_queue(host_name):
    while True:
        item = biased_front_queue_selector()
        if item == -1:
            return -1
        else:
            host_name_item = get_host_from_url(get_url_from_item(item))
            if host_name_item in list(wl.back_queues.keys()):
                wl.back_queues.get(host_name_item).append(item)
                if host_name == host_name_item:
                    return 0


def star_crawling():
    counter = 0
    limit = 30
    list_fetched_documents = []
    while config.crawling:
        # 1: seeking a URL to crawl
        item = get_an_item_to_crawl_from_back_queue()
        if item == -1 or counter == limit:
            # should update refresh rate
            print("The crawler does not have any link to crawl")
            print("Total number of page crawled is: " + str(counter))
            return list_fetched_documents

        # 2: fetch content of the news page
        soup_news_page = get_html_page(get_url_from_item(item))
        if soup_news_page == -1:
            continue

        page = get_content_of_new_page(soup_news_page, item)
        if page == -1:
            continue

        # 3: indexing
        list_fetched_documents.append(page)
        counter += 1
        print("document " + str(counter) + " fetched : " + get_url_from_item(item))


def get_content_of_new_page(news_page_soup, item):
    try:
        new_news = {}
        content = get_content_page_from_soup(news_page_soup)
        if content == -1:
            return -1

        new_news['content'] = content
        new_news['publish_date'] = get_content_tag(item, 'pubDate')
        new_news['title'] = get_content_tag(item, 'title')
        new_news['url'] = get_url_from_item(item).rstrip()
        new_news['summary'] = get_content_tag(item, 'description')
        new_news['thumbnail'] = ' '

        return new_news
    except:
        return -1


def get_content_tag(item, parameter):
    try:
        val = item.find(re.compile("^" + parameter + "$", re.I)).text
        if val == -1:
            val = " "
        return val
    except:
        return " "


def get_content_page_from_soup(news_page_soup):
    try:
        return news_page_soup.find("div", {"class": "body"}).text
    except:
        return -1


def add_item_to_back_queue_from_front_queue_directly():
    for index, f_queue in enumerate(wl.front_queues):
        for item in f_queue:
            host_name = get_host_from_url(get_url_from_item(item))
            add_item_to_back_queue(host_name, item)
        wl.front_queues[index] = []


def add_item_to_back_queue(host_name, item):
    if host_name in list(wl.back_queues.keys()):
        wl.back_queues.get(host_name).append(item)
    else:
        wl.back_queues[host_name] = [item]
