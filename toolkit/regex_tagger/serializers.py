import json

from rest_framework import serializers
from texta_lexicon_matcher.lexicon_matcher import SUPPORTED_MATCH_TYPES, SUPPORTED_OPERATORS

from toolkit.serializer_constants import FieldParseSerializer, ProjectResourceUrlSerializer
from .models import RegexTagger, RegexTaggerGroup
from ..core.task.serializers import TaskSerializer
from ..elastic.searcher import EMPTY_QUERY
from ..elastic.serializers import IndexSerializer


PRIORITY_CHOICES = (
    ("first_span", "first_span"),
    ("last_span", "last_span"),
)


class RegexTaggerSerializer(FieldParseSerializer, serializers.ModelSerializer, ProjectResourceUrlSerializer):
    description = serializers.CharField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    lexicon = serializers.ListField(child=serializers.CharField(required=True))
    counter_lexicon = serializers.ListField(child=serializers.CharField(required=False), default=[])

    operator = serializers.CharField(default=SUPPORTED_OPERATORS[0], required=False)
    match_type = serializers.CharField(default=SUPPORTED_MATCH_TYPES[0], required=False)
    required_words = serializers.FloatField(default=1.0, required=False)
    phrase_slop = serializers.IntegerField(default=0, required=False)
    counter_slop = serializers.IntegerField(default=0, required=False)
    n_allowed_edits = serializers.IntegerField(default=0, required=False)
    return_fuzzy_match = serializers.BooleanField(default=True, required=False)
    ignore_case = serializers.BooleanField(default=True, required=False)
    ignore_punctuation = serializers.BooleanField(default=True, required=False)
    url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    tagger_groups = serializers.SerializerMethodField(read_only=True)


    def get_tagger_groups(self, value: RegexTagger):
        tgs = RegexTaggerGroup.objects.filter(regex_taggers__project_id=value.project.pk, regex_taggers__id=value.pk)
        descriptions = [{"tagger_group_id": tagger.pk, "description": tagger.description} for tagger in tgs]
        return descriptions


    def to_representation(self, instance):
        data = super(RegexTaggerSerializer, self).to_representation(instance)
        data["lexicon"] = json.loads(instance.lexicon)
        data["counter_lexicon"] = json.loads(instance.counter_lexicon)
        return data


    class Meta:
        model = RegexTagger
        fields = ('id', 'url', 'author_username',
                  'description', 'lexicon', 'counter_lexicon', 'operator', 'match_type', 'required_words',
                  'phrase_slop', 'counter_slop', 'n_allowed_edits', 'return_fuzzy_match', 'ignore_case',
                  'ignore_punctuation')
        fields_to_parse = ('lexicon', 'counter_lexicon')
                  'phrase_slop', 'counter_slop', 'n_allowed_edits', 'return_fuzzy_match', 'ignore_case', 'ignore_punctuation', 'tagger_groups')


class RegexTaggerTagTextsSerializer(serializers.Serializer):
    texts = serializers.ListField(child=serializers.CharField(required=True))


class TagRandomDocSerializer(serializers.Serializer):
    indices = IndexSerializer(many=True, default=[])
    fields = serializers.ListField(child=serializers.CharField(), required=True, allow_empty=False)


class RegexTaggerGroupTagDocumentSerializer(serializers.Serializer):
    doc = serializers.JSONField(help_text=f'Document in JSON format.')
    fields = serializers.ListField(child=serializers.CharField(), required=True, allow_empty=False)


class RegexGroupTaggerTagTextSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)


class RegexMultitagTextSerializer(serializers.Serializer):
    text = serializers.CharField()
    taggers = serializers.ListField(help_text='List of RegexTagger IDs to be used. Default: [] (uses all).',
                                    child=serializers.IntegerField(),
                                    default=[])


class RegexTaggerGroupSerializer(serializers.ModelSerializer, ProjectResourceUrlSerializer):
    description = serializers.CharField()
    url = serializers.SerializerMethodField()
    task = TaskSerializer(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    tagger_info = serializers.SerializerMethodField(read_only=True)  # Helper field for displaying tagger info in a friendly manner.

    def get_tagger_info(self, value: RegexTaggerGroup):
        return [tagger.get_description() for tagger in value.regex_taggers.all()]

    class Meta:
        model = RegexTaggerGroup
        # regex_taggers is the field which to use to manipulate the related RegexTagger model objects.
        fields = ('id', 'url', 'regex_taggers', 'author_username', 'task', 'description', 'tagger_info')


class RegexTaggerGroupMultitagTextSerializer(serializers.Serializer):
    text = serializers.CharField()
    tagger_groups = serializers.ListField(
        help_text='List of RegexTaggerGroup IDs to be used. Default: [] (uses all).',
        child=serializers.IntegerField(),
        default=[]
    )


class ApplyRegexTaggerGroupSerializer(serializers.Serializer):
    description = serializers.CharField(required=True, help_text="Text for distinguishing this task from others.")
    # priority = serializers.ChoiceField(default=None, choices=PRIORITY_CHOICES)
    indices = IndexSerializer(many=True, default=[], help_text="Which indices in the project to apply this to.")
    fields = serializers.ListField(required=True, child=serializers.CharField(), help_text="Which fields to extract the text from.")
    query = serializers.JSONField(help_text='Filter the documents which to scroll and apply to.', default=EMPTY_QUERY)
