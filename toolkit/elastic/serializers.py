import json
from rest_framework import serializers

from toolkit.elastic.models import Reindexer
from toolkit.core.task.serializers import TaskSerializer
from toolkit.serializer_constants import ProjectResourceUrlSerializer, FieldParseSerializer


class ReindexerCreateSerializer(FieldParseSerializer, serializers.HyperlinkedModelSerializer, ProjectResourceUrlSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    url = serializers.SerializerMethodField()
    description = serializers.CharField(help_text='Describe your re-indexing task', required=True, allow_blank=False)
    indices = serializers.ListField(child=serializers.CharField(), help_text=f'Add the indices, you wish to reindex into a new index.', write_only=True, required=True)
    fields = serializers.ListField(child=serializers.CharField(),
                                   help_text=f'Empty fields chooses all posted indices fields. Fields content adds custom field content to the new index.',)
    query = serializers.JSONField(help_text='Add a query, if you wish to filter the new reindexed index.', required=False)
    new_index = serializers.CharField(help_text='Your new re-indexed index name', allow_blank=False, required=True)
    random_size = serializers.IntegerField(help_text='Picks a subset of documents of chosen size at random. Disabled by default.',
                                           required=False)
    field_type = serializers.ListField(help_text=f'Used to update the fieldname and the field type of chosen paths.',
                                       required=False,)
    task = TaskSerializer(read_only=True)

    class Meta:
        model = Reindexer
        fields = ('id', 'url', 'author_username', 'description', 'indices', 'fields', 'query', 'new_index', 'random_size', 'field_type', 'task')
        fields_to_parse = ('fields', 'field_type')
