import json

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from toolkit.embedding.models import Embedding, EmbeddingCluster
from toolkit.embedding.serializers import (EmbeddingSerializer, EmbeddingPredictSimilarWordsSerializer,
                                           EmbeddingClusterSerializer, EmbeddingClusterBrowserSerializer)
from toolkit.serializer_constants import GeneralTextSerializer
from toolkit.embedding.embedding import W2VEmbedding
from toolkit.embedding.phraser import Phraser
from toolkit.embedding.word_cluster import WordCluster
from toolkit.core.project.models import Project
from toolkit.tools.model_cache import ModelCache
from toolkit.permissions.project_permissions import ProjectResourceAllowed
from toolkit.tools.text_processor import TextProcessor
from toolkit.view_constants import BulkDelete, ExportModel

global_w2v_cache = ModelCache(W2VEmbedding)
global_phraser_cache = ModelCache(Phraser)
global_cluster_cache = ModelCache(WordCluster)


class EmbeddingViewSet(viewsets.ModelViewSet, BulkDelete, ExportModel):
    """
    API endpoint that allows TEXTA models to be viewed or edited.
    Only include the embeddings that are related to the request UserProfile's active_project
    """
    queryset = Embedding.objects.all()
    serializer_class = EmbeddingSerializer
    permission_classes = (
        ProjectResourceAllowed,
        permissions.IsAuthenticated,
        )

    def get_queryset(self):
        return Embedding.objects.filter(project=self.kwargs['project_pk'])


    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        project=Project.objects.get(id=self.kwargs['project_pk']),
                        fields=json.dumps(serializer.validated_data['fields']))


    @action(detail=True, methods=['post'],serializer_class=EmbeddingPredictSimilarWordsSerializer)
    def predict_similar(self, request, pk=None, project_pk=None):
        data = request.data
        serializer = EmbeddingPredictSimilarWordsSerializer(data=data)
        if serializer.is_valid():
            embedding_object = self.get_object()
            if not embedding_object.location:
                return Response({'error': 'model does not exist (yet?)'}, status=status.HTTP_400_BAD_REQUEST)

            embedding = global_w2v_cache.get_model(embedding_object)

            predictions = embedding.get_similar(serializer.validated_data['positives'],
                negatives=serializer.validated_data['negatives'],
                n=serializer.validated_data['output_size']
            )

            return Response(predictions, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], serializer_class=GeneralTextSerializer)
    def phrase_text(self, request, pk=None, project_pk=None):
        data = request.data
        serializer = GeneralTextSerializer(data=data)
        if serializer.is_valid():
            embedding_object = self.get_object()
            if not embedding_object.location:
                return Response({'error': 'model does not exist (yet?)'}, status=status.HTTP_400_BAD_REQUEST)

            phraser = global_phraser_cache.get_model(embedding_object)
            text_processor = TextProcessor(phraser=phraser, sentences=False, remove_stop_words=False, tokenize=False)
            phrased_text = text_processor.process(serializer.validated_data['text'])[0]

            return Response(phrased_text, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EmbeddingClusterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TEXTA embedding clusterings to be viewed or edited.
    Only include embedding clusterings that are related to the request UserProfile's active_project
    """
    serializer_class = EmbeddingClusterSerializer
    permission_classes = (
        ProjectResourceAllowed,
        permissions.IsAuthenticated,
        )

    def get_queryset(self):
        return EmbeddingCluster.objects.filter(project=self.kwargs['project_pk'])


    def perform_create(self, serializer):
        serializer.save(author=self.request.user,  project=Project.objects.get(id=self.kwargs['project_pk']))


    @action(detail=True, methods=['post'], serializer_class=EmbeddingClusterBrowserSerializer)
    def browse_clusters(self, request, pk=None, project_pk=None):
        """
        API endpoint for browsing clustering results.
        """
        data = request.data
        serializer = EmbeddingClusterBrowserSerializer(data=data)

        # check if valid request
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        clustering_object = self.get_object()
        # check if clustering ready
        if not clustering_object.location:
            return Response({'error': 'model does not exist (yet?)'}, status=status.HTTP_400_BAD_REQUEST)

        # load cluster model
        clusterer = global_cluster_cache.get_model(clustering_object)


        clustering_result = clusterer.browse(max_examples_per_cluster=serializer.validated_data['max_examples_per_cluster'],
                                             number_of_clusters=serializer.validated_data['number_of_clusters'],
                                             sort_reverse=serializer.validated_data['cluster_order'])

        return Response(clustering_result, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], serializer_class=GeneralTextSerializer)
    def find_cluster_by_word(self, request, pk=None, project_pk=None):
        """
        API endpoint for finding a cluster for any word in model.
        """
        data = request.data
        serializer = GeneralTextSerializer(data=data)

        # check if valid request
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        clustering_object = self.get_object()
        # check if clustering ready
        if not clustering_object.location:
            return Response({'error': 'model does not exist (yet?)'}, status=status.HTTP_400_BAD_REQUEST)

        # load cluster model
        clusterer = global_cluster_cache.get_model(clustering_object)

        clustering_result = clusterer.query(serializer.validated_data['text'])
        return Response(clustering_result, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], serializer_class=GeneralTextSerializer)
    def cluster_text(self, request, pk=None, project_pk=None):
        """
        API endpoint for clustering raw text.
        """
        data = request.data
        serializer = GeneralTextSerializer(data=data)

        # check if valid request
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        clustering_object = self.get_object()
        # check if clustering ready
        if not clustering_object.location:
            return Response({'error': 'model does not exist (yet?)'}, status=status.HTTP_400_BAD_REQUEST)

        # load cluster model
        clusterer = global_cluster_cache.get_model(clustering_object)

        clustered_text = clusterer.text_to_clusters(serializer.validated_data['text'])
        return Response(clustered_text, status=status.HTTP_200_OK)
