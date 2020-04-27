"""
WSGI config for ir_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import search_engine.configurations as config
import search_engine.words_lists as wl
from django.core.wsgi import get_wsgi_application
import search_engine.query_processor_engine as query_engine

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ir_project.settings')

application = get_wsgi_application()
print("server started")

query_engine.start_search_engine()
if config.log:
    print("############################")
    print("Total number of words in all documents without any processing : " + str(config.pure_number_tokens))
    words = list(wl.inverted_index.keys())
    print(words)
    print("Total number of words in Dictionary : " + str(config.dictionary_size))
    print("############################")

print("ready for processing the queries...")
