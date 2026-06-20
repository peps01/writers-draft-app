from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Project, Character, Place, TimelineEvent, Scene, Conversation, Message
from .serializers import (
    ProjectSerializer,
    CharacterSerializer,
    PlaceSerializer,
    TimelineEventSerializer,
    SceneSerializer,
    ConversationSerializer,
    MessageSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CharacterViewSet(viewsets.ModelViewSet):
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Character.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class PlaceViewSet(viewsets.ModelViewSet):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Place.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class TimelineEventViewSet(viewsets.ModelViewSet):
    serializer_class = TimelineEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimelineEvent.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class SceneViewSet(viewsets.ModelViewSet):
    serializer_class = SceneSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_id'] = self.kwargs['project_pk']
        return context

    def get_queryset(self):
        return Scene.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__project__owner=self.request.user,
            conversation_id=self.kwargs['conversation_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(conversation_id=self.kwargs['conversation_pk'])


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid username or password.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    login(request, user)
    return Response({
        'id': user.id,
        'username': user.username,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email', '')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    User = get_user_model()

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'A user with this username already exists.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(password)
    except ValidationError as e:
        return Response(
            {'error': e.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    return Response(
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'detail': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_view(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
    })
