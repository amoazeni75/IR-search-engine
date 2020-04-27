from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from ir_core.models import News
from ir_core.serializer import UserSerializer, GroupSerializer, NewsSerializer
from django.http import HttpResponse, JsonResponse
import search_engine.query_processor_engine as engine
import search_engine.linguistic_tools as lin_tool


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = News.objects.all()
    serializer_class = NewsSerializer


def process_query(request):
    search = request.path[13:]
    if len(search) == 0:
        return [], []
    try:
        i = int(search)
        return get_similar_document(request, i)
    except ValueError:
        doc_list, simple_terms, phrase_terms = engine.process_query(search)
        doc_list = doc_list[:300]
        return prepare_json_object(doc_list, simple_terms, phrase_terms)


def prepare_json_object(doc_list, simple_terms, phrase_terms):
    objects = News.objects.filter(id__in=doc_list)
    objects = dict([(obj.id, obj) for obj in objects])
    sorted_objects = [objects[int(id)] for id in doc_list]

    result = []
    for index, item in enumerate(sorted_objects):
        result.append(create_object_dictionary(item, simple_terms, phrase_terms, (index + 1)))
    res = JsonResponse(result, safe=False)
    res['Access-Control-Allow-Credentials'] = 'true'
    res['Access-Control-Allow-Origin'] = '*'
    res['Access-Control-Allow-Headers'] = 'application/json'
    return res


def get_document(request, doc_id):
    doc_id = int(doc_id)
    return prepare_json_object([doc_id], [], [])


def get_similar_document(request, doc_id):
    doc_id = int(doc_id)
    doc_list = engine.get_similar_documents(doc_id)
    return prepare_json_object(doc_list, [], [])


def create_object_dictionary(news, simple_terms, phrase_terms, priority):
    highlighted = lin_tool.get_text_bolded(news.content, simple_terms, phrase_terms)
    dict = {
        'id': news.id,
        'publish_date': news.publish_date,
        'title': news.title,
        'url': news.url,
        'summary': news.summary,
        'meta_tags': news.meta_tags,
        'content': news.content,
        'thumbnail': news.thumbnail,
        'highlighted': highlighted,
        'priority': priority
    }
    return dict
