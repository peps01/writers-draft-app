from datetime import date, timedelta
from collections import defaultdict

import google.generativeai as genai

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
from .ai_service import get_ai_response, check_contradictions, AIServiceNotConfigured, AIServiceError, resolve_key, GEMINI_MODEL
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

    @action(detail=True, methods=['get'], url_path='statistics')
    def statistics(self, request, pk=None):
        project = self.get_object()
        scenes = list(project.scenes.all())

        total_scenes = len(scenes)
        total_words = sum(len(s.content.split()) for s in scenes)

        if total_scenes > 0:
            longest = max(scenes, key=lambda s: len(s.content.split()))
            shortest = min(scenes, key=lambda s: len(s.content.split()))
            longest_scene = {
                'id': longest.id,
                'title': longest.title or 'Untitled',
                'word_count': len(longest.content.split()),
            }
            shortest_scene = {
                'id': shortest.id,
                'title': shortest.title or 'Untitled',
                'word_count': len(shortest.content.split()),
            }
            avg_words = total_words // total_scenes
        else:
            longest_scene = None
            shortest_scene = None
            avg_words = 0

        versions = SceneVersion.objects.filter(
            scene__project=project
        ).select_related('scene').order_by('scene_id', 'created_at')

        scene_date_counts = defaultdict(dict)
        for v in versions:
            d = v.created_at.date()
            wc = len(v.content.split())
            scene_date_counts[v.scene_id][d] = wc

        daily_deltas = defaultdict(int)
        for scene_id, date_counts in scene_date_counts.items():
            sorted_dates = sorted(date_counts.keys())
            prev_count = 0
            for d in sorted_dates:
                count = date_counts[d]
                delta = max(0, count - prev_count)
                daily_deltas[d] += delta
                prev_count = count

        if versions:
            first_date = versions.earliest('created_at').created_at.date()
        else:
            first_date = date.today()

        all_daily = []
        current = first_date
        today = date.today()
        while current <= today:
            words = daily_deltas.get(current, 0)
            all_daily.append({'date': current.isoformat(), 'words': words})
            current += timedelta(days=1)

        total_days_written = sum(1 for d in all_daily if d['words'] > 0)

        streak = 0
        idx = len(all_daily) - 1
        if all_daily and all_daily[idx]['words'] == 0:
            idx -= 1
        while idx >= 0 and all_daily[idx]['words'] > 0:
            streak += 1
            idx -= 1

        daily_words = all_daily[-90:]

        return Response({
            'total_words': total_words,
            'total_scenes': total_scenes,
            'average_words_per_scene': avg_words,
            'longest_scene': longest_scene,
            'shortest_scene': shortest_scene,
            'daily_words': daily_words,
            'writing_streak': streak,
            'total_days_written': total_days_written,
        })


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

    @action(detail=True, methods=['post'], url_path='check-contradictions')
    def check_contradictions(self, request, project_pk=None, pk=None):
        scene = self.get_object()

        conversation = Conversation.objects.filter(
            project_id=project_pk,
            scene=scene,
        ).first()
        if not conversation:
            conversation = Conversation.objects.create(
                project_id=project_pk,
                scene=scene,
            )

        try:
            result = check_contradictions(
                user=request.user,
                scene=scene,
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
            metadata=result['parsed'],
        )

        serializer = MessageSerializer(assistant_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
            'daily_word_goal': user.profile.daily_word_goal,
            'show_word_goal': user.profile.show_word_goal,
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
    key = request.user.profile.gemini_api_key
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'has_gemini_key': bool(key),
        'gemini_api_key_preview': key[-4:] if key else None,
        'is_paid_tier': request.user.profile.is_paid_tier,
        'daily_word_goal': request.user.profile.daily_word_goal,
        'show_word_goal': request.user.profile.show_word_goal,
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    if request.method == 'GET':
        key = request.user.profile.gemini_api_key
        return Response({
            'gemini_api_key_set': bool(key),
            'gemini_api_key_preview': key[-4:] if key else None,
            'is_paid_tier': request.user.profile.is_paid_tier,
            'daily_word_goal': request.user.profile.daily_word_goal,
            'show_word_goal': request.user.profile.show_word_goal,
        })

    # PATCH
    data = request.data
    if 'gemini_api_key' in data:
        val = data['gemini_api_key']
        request.user.profile.gemini_api_key = val
    if 'is_paid_tier' in data:
        request.user.profile.is_paid_tier = bool(data['is_paid_tier'])
    if 'daily_word_goal' in data:
        val = data['daily_word_goal']
        request.user.profile.daily_word_goal = int(val) if val is not None else None
    if 'show_word_goal' in data:
        request.user.profile.show_word_goal = bool(data['show_word_goal'])
    request.user.profile.save()

    key = request.user.profile.gemini_api_key
    return Response({
        'gemini_api_key_set': bool(key),
        'gemini_api_key_preview': key[-4:] if key else None,
        'is_paid_tier': request.user.profile.is_paid_tier,
        'daily_word_goal': request.user.profile.daily_word_goal,
        'show_word_goal': request.user.profile.show_word_goal,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_key_view(request):
    try:
        key, is_paid = resolve_key(request.user)
    except AIServiceNotConfigured:
        return Response({'status': 'not_configured'})

    using = 'custom' if request.user.profile.gemini_api_key else 'default'
    genai.configure(api_key=key)
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        model.generate_content(
            'Hello',
            generation_config=genai.types.GenerationConfig(max_output_tokens=5),
        )
        return Response({'status': 'ok', 'using': using})
    except Exception as e:
        err = str(e).lower()
        if any(x in err for x in ('quota', 'resource_exhausted', '429')):
            return Response({'status': 'quota_exceeded', 'using': using})
        return Response({'status': 'invalid_key', 'using': using})
