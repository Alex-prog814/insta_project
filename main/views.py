from django.db.models import Q

from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Post, Comment
from .permissions import IsPostAuthor
from .serializers import PostSerializer, CommentSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        if self.action in ['create', 'own']:
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthenticated, IsPostAuthor]
        else:
            permissions = []
        return[permission() for permission in permissions]

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        if self.action in ['create', 'own']:
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthenticated, IsPostAuthor]
        else:
            permissions = []
        return [permission() for permission in permissions]

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)