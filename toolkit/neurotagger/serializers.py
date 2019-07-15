import json
import re

from rest_framework import serializers
from django.db.models import Avg

from . import choices
from .models import Neurotagger
from toolkit.constants import get_field_choices
from toolkit.core.task.serializers import TaskSerializer
from toolkit.settings import URL_PREFIX



class NeurotaggerSerializer(serializers.HyperlinkedModelSerializer):
    fields = serializers.ListField(child=serializers.CharField(), help_text=f'Fields used to build the model.', write_only=True)
    fields_parsed = serializers.SerializerMethodField()
    model_architecture = serializers.ChoiceField(choices=choices.model_arch_choices)
    seq_len = serializers.IntegerField(default=choices.DEFAULT_SEQ_LEN, help_text=f'Default: {choices.DEFAULT_SEQ_LEN}')
    vocab_size = serializers.IntegerField(default=choices.DEFAULT_VOCAB_SIZE, help_text=f'Default: {choices.DEFAULT_VOCAB_SIZE}')
    num_epochs = serializers.IntegerField(default=choices.DEFAULT_NUM_EPOCHS, help_text=f'Default: {choices.DEFAULT_NUM_EPOCHS}')
    validation_split = serializers.IntegerField(default=choices.DEFAULT_VALIDATION_SPLIT, help_text=f'Default: {choices.DEFAULT_VALIDATION_SPLIT}')
    score_threshold = serializers.IntegerField(default=choices.DEFAULT_SCORE_THRESHOLD, help_text=f'Default: {choices.DEFAULT_SCORE_THRESHOLD}')

    negative_multiplier = serializers.IntegerField(default=choices.DEFAULT_NEGATIVE_MULTIPLIER, help_text=f'Default: {choices.DEFAULT_NEGATIVE_MULTIPLIER}')
    maximum_sample_size = serializers.IntegerField(default=choices.DEFAULT_MAX_SAMPLE_SIZE,help_text=f'Default: {choices.DEFAULT_MAX_SAMPLE_SIZE}')

    task = TaskSerializer(read_only=True)
    plot = serializers.SerializerMethodField()
    model_plot = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()


    class Meta:
        model = Neurotagger
        fields = ('url', 'id', 'description', 'project', 'author', 'queries', 'validation_split', 'score_threshold',
                  'fields', 'fields_parsed', 'embedding', 'model_architecture', 'seq_len', 'maximum_sample_size', 'negative_multiplier',
                  'location', 'num_epochs', 'vocab_size', 'plot', 'task', 'validation_accuracy', 'training_accuracy',
                  'training_loss', 'validation_loss', 'model_plot', 'result_json')

        read_only_fields = ('author', 'project', 'location', 'accuracy', 'loss', 'plot',
                            'model_plot', 'result_json', 'validation_accuracy', 'training_accuracy',
                            'training_loss', 'validation_loss',
                            )

    def __init__(self, *args, **kwargs):
        '''
        Add the ability to pass extra arguments such as "remove_fields".
        Useful for the Serializer eg in another Serializer, without making a new one.
        '''
        remove_fields = kwargs.pop('remove_fields', None)
        super(NeurotaggerSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)
    

    def get_plot(self, obj):
        if obj.plot:
            return '{0}/{1}'.format(URL_PREFIX, obj.plot)
        else:
            return None

    def get_model_plot(self, obj):
        if obj.model_plot:
            return '{0}/{1}'.format(URL_PREFIX, obj.model_plot)
        else:
            return None

    def get_fields_parsed(self, obj):
        if obj.fields:
            return json.loads(obj.fields)
        return None

    def get_url(self, obj):
        request = self.context['request']
        path = re.sub(r'\d+\/*$', '', request.path)
        resource_url = request.build_absolute_uri(f'{path}{obj.id}/')
        return resource_url 
