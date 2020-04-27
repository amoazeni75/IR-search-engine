from ir_core.models import News
import pandas as pd
import search_engine.configurations as config
import timeit


def insert_data_into_database(path):
    path = config.prefix_path + path
    if config.log:
        print("inserting data into database ... ")

    News.objects.all().delete()
    news_excel = []
    start = timeit.default_timer()
    # for i in range(0, 15):
    #     name = './IR-project-data-phase-3-100k/ir-news-' + str(counter) + '-' + str(counter + 2) + '.csv'
    #     news_excel.append(pd.read_csv(name, encoding='utf-8', skiprows=0))
    # news_excel = pd.concat(news_excel)

    news_excel = pd.read_excel(path)
    end = timeit.default_timer()
    print("Loading CSV files time: " + str(end - start))

    # TODO we should process meta-tags
    start = timeit.default_timer()
    counter = 0
    for index, row in news_excel.iterrows():
        meta_tag = row['meta_tags']
        if len(str(row['content'])) < 45 or len(str(row['title'])) < 5 or row['publish_date'] is None or str(
                row['publish_date']) == "":
            continue
        new_news = News(id=counter, publish_date=row['publish_date'], title=row['title'], url=row['url'],
                        summary=row['summary'], meta_tags=meta_tag, content=row['content'], thumbnail=row['thumbnail'],
                        category=row['class_label'])
        counter += 1
        new_news.save()
    end = timeit.default_timer()
    print("Saving Rows to database: " + str(end - start))

    if config.log:
        print("inserting data into the database successfully finished...")
        print("Total number of documents is: " + str(len(news_excel)))
