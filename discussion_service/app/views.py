import requests
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from .models import Discussion, Comment
from .serializers import DiscussionSerializer, CommentSerializer

# URL of the user_service
USER_SERVICE_URL = 'http://localhost:8000/api/api/users/'

class DiscussionViewSet(viewsets.ModelViewSet):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]

    def perform_create(self, serializer):
        # Validate user with user_service
        user_id = self.request.user.id
        response = requests.get(f'{USER_SERVICE_URL}{user_id}/')

        if response.status_code != 200:
            raise serializers.ValidationError('User validation failed')

        # If user is valid, save the discussion
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Discussion.objects.all()
        tags = self.request.query_params.get('tags')
        text = self.request.query_params.get('text')
        
        if tags:
            queryset = queryset.filter(hashtags__icontains=tags)
        if text:
            queryset = queryset.filter(text__icontains=text)
            
        return queryset

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        discussion = self.get_object()
        discussion.likes += 1
        discussion.save()
        return Response({'status': 'discussion liked'})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        discussion = self.get_object()
        comment_text = request.data.get('text')
        if not comment_text:
            return Response({'error': 'Comment text is required'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(discussion=discussion, user=request.user, text=comment_text)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        discussion = self.get_object()
        discussion.views += 1
        discussion.save()
        return Response({'status': 'discussion viewed'})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
