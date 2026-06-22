from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Project, Character, Place, TimelineEvent, Scene, SceneVersion, Conversation, Message
from .serializers import (
    ProjectSerializer,
    CharacterSerializer,
    PlaceSerializer,
    TimelineEventSerializer,
    SceneSerializer,
    SceneVersionSerializer,
    ConversationSerializer,
    MessageSerializer,
)
from .ai_service import get_ai_response, AIServiceNotConfigured, AIServiceError
from .export import generate_epub


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='export/epub')
    def export_epub(self, request, pk=None):
        project = self.get_object()
        scene_ids = request.data.get('scene_ids')
        if scene_ids:
            scenes = Scene.objects.filter(
                project=project, id__in=scene_ids
            ).order_by('order')
        else:
            scenes = project.scenes.all().order_by('order')

        if not scenes:
            return Response(
                {'error': 'No scenes to export.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buf = generate_epub(project, request.user, scenes)
        filename = f'{project.title}.epub'
        return FileResponse(
            buf,
            as_attachment=True,
            filename=filename,
            content_type='application/epub+zip',
        )


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

    def perform_update(self, serializer):
        scene = self.get_object()
        content_changed = 'content' in serializer.validated_data and serializer.validated_data['content'] != scene.content
        serializer.save()
        if content_changed:
            SceneVersion.objects.create(
                scene=scene,
                content=serializer.instance.content,
            )


class VersionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SceneVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SceneVersionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = VersionPagination

    def get_queryset(self):
        return SceneVersion.objects.filter(
            scene__project__owner=self.request.user,
            scene_id=self.kwargs['scene_pk'],
        )

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, project_pk=None, scene_pk=None, pk=None):
        password = request.data.get('password')
        if not password:
            return Response(
                {'error': 'Password is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(password):
            return Response(
                {'error': 'Incorrect password.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        version = self.get_object()
        scene = version.scene

        # Snapshot current scene content before restoring, so the "before restore"
        # state is preserved and can itself be restored later.
        SceneVersion.objects.create(
            scene=scene,
            content=scene.content,
        )

        scene.content = version.content
        scene.save(update_fields=['content'])

        serializer = SceneSerializer(scene, context={'project_id': project_pk})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Conversation.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )
        scene_id = self.request.query_params.get('scene')
        if scene_id is not None:
            qs = qs.filter(scene_id=scene_id)
        return qs

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

    def create(self, request, project_pk=None, conversation_pk=None):
        conversation = Conversation.objects.get(
            pk=conversation_pk,
            project__owner=request.user,
            project_id=project_pk,
        )

        user_content = request.data.get('content', '')
        if not user_content:
            return Response(
                {'error': 'Content is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_content,
        )

        try:
            result = get_ai_response(
                user=request.user,
                scene_id=conversation.scene_id,
                conversation_id=conversation.pk,
                new_message_content=user_content,
            )
        except AIServiceNotConfigured as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceError as e:
            msg = str(e)
            if 'quota' in msg.lower() or 'resource_exhausted' in msg.lower():
                msg = 'AI service quota exceeded. Try again later or use a different API key.'
            return Response(
                {'error': msg},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['reply'],
        )

        user_ser = MessageSerializer(user_message)
        assistant_ser = MessageSerializer(assistant_message)

        return Response({
            'user_message': user_ser.data,
            'assistant_message': assistant_ser.data,
            'is_free_tier': result['is_free_tier'],
        }, status=status.HTTP_201_CREATED)


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
            'has_gemini_key': bool(user.profile.gemini_api_key),
            'is_paid_tier': user.profile.is_paid_tier,
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
        'has_gemini_key': bool(request.user.profile.gemini_api_key),
        'is_paid_tier': request.user.profile.is_paid_tier,
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    if request.method == 'GET':
        return Response({
            'gemini_api_key_set': bool(request.user.profile.gemini_api_key),
            'is_paid_tier': request.user.profile.is_paid_tier,
        })

    # PATCH
    data = request.data
    if 'gemini_api_key' in data:
        request.user.profile.gemini_api_key = data['gemini_api_key']
    if 'is_paid_tier' in data:
        request.user.profile.is_paid_tier = bool(data['is_paid_tier'])
    request.user.profile.save()

    return Response({
        'gemini_api_key_set': bool(request.user.profile.gemini_api_key),
        'is_paid_tier': request.user.profile.is_paid_tier,
    })
