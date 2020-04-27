from django.db import models


class News(models.Model):
    publish_date = models.TextField()
    title = models.TextField()
    url = models.TextField()
    summary = models.TextField()
    meta_tags = models.TextField()
    content = models.TextField()
    thumbnail = models.TextField()
    # category = models.TextField()
