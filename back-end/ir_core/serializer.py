from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ir_core.models import News


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class NewsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = News
        fields = ['publish_date',	'title', 'url',	'summary', 'meta_tags',	'content', 'thumbnail']


