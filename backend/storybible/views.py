import re
from datetime import date, timedelta
from collections import defaultdict

import dns.resolver
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.validators import EmailValidator
from django.db.models import Q
from django.http import FileResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django_ratelimit.core import is_ratelimited
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Project, Character, Place, TimelineEvent, Group, Item, Lore, Scene, SceneNote, SceneVersion, Conversation, Message, UserProfile
from .serializers import (
    ProjectSerializer,
    CharacterSerializer,
    PlaceSerializer,
    TimelineEventSerializer,
    GroupSerializer,
    ItemSerializer,
    LoreSerializer,
    SceneSerializer,
    SceneNoteSerializer,
    SceneVersionSerializer,
    ConversationSerializer,
    MessageSerializer,
)
from .ai_service import get_ai_response, check_contradictions, AIServiceNotConfigured, AIServiceError, resolve_key, GEMINI_MODEL, call_with_timeout
from .export import generate_epub


def strip_html(html):
    return re.sub(r'<[^>]+>', ' ', html or '').strip()


def extract_snippets(plain_text, query, max_snippets=3, context_chars=80):
    snippets = []
    text_lower = plain_text.lower()
    query_lower = query.lower()
    start = 0
    while len(snippets) < max_snippets:
        idx = text_lower.find(query_lower, start)
        if idx == -1:
            break
        snippet_start = max(0, idx - context_chars)
        snippet_end = min(len(plain_text), idx + len(query) + context_chars)
        snippet = plain_text[snippet_start:snippet_end].strip()
        if snippet_start > 0:
            snippet = '...' + snippet
        if snippet_end < len(plain_text):
            snippet = snippet + '...'
        snippets.append({
            'text': snippet,
            'match_start': idx - snippet_start + (3 if snippet_start > 0 else 0),
            'match_end': idx - snippet_start + len(query) + (3 if snippet_start > 0 else 0),
        })
        start = idx + len(query)
    return snippets


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user
        ).select_related('owner')

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

    @action(detail=True, methods=['get'], url_path='search')
    def search(self, request, pk=None):
        project = self.get_object()
        query = request.query_params.get('q', '').strip()

        if len(query) < 3:
            return Response({
                'query': query,
                'total_matches': 0,
                'total_scenes': 0,
                'results': [],
                'limit': int(request.query_params.get('limit', 20)),
                'offset': int(request.query_params.get('offset', 0)),
                'has_more': False,
            })

        limit = min(int(request.query_params.get('limit', 20)), 50)
        offset = int(request.query_params.get('offset', 0))

        scenes = Scene.objects.filter(
            project=project,
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('order')

        total_scenes = scenes.count()
        page = scenes[offset:offset + limit]

        results = []
        total_matches = 0
        for scene in page:
            plain_text = strip_html(scene.content)
            title_plain = strip_html(scene.title)
            # Count matches in title and content
            title_count = title_plain.lower().count(query.lower())
            content_count = plain_text.lower().count(query.lower())
            match_count = title_count + content_count
            total_matches += match_count

            # Get snippets from the combined text
            searchable_text = title_plain + ' ' + plain_text
            snippets = extract_snippets(searchable_text, query)

            results.append({
                'scene_id': scene.id,
                'scene_title': scene.title or 'Untitled Scene',
                'scene_order': scene.order,
                'match_count': match_count,
                'snippets': snippets,
            })

        return Response({
            'query': query,
            'total_matches': total_matches,
            'total_scenes': total_scenes,
            'results': results,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_scenes,
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


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class LoreViewSet(viewsets.ModelViewSet):
    serializer_class = LoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lore.objects.filter(
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
        ).prefetch_related('characters', 'places', 'timeline_events', 'groups', 'items', 'lore')

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
        if is_ratelimited(request, group='check_contradictions', key='user', rate='10/m', method='POST', increment=True):
            return Response(
                {'error': 'Too many requests. Please wait a moment before trying again.'},
                status=429,
            )

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

    @action(detail=True, methods=['post'], url_path='writing-prompt')
    def writing_prompt(self, request, project_pk=None, pk=None):
        if is_ratelimited(request, group='writing_prompt', key='user', rate='10/m', method='POST', increment=True):
            return Response(
                {'error': 'Too many requests. Please wait a moment before trying again.'},
                status=429,
            )

        scene = self.get_object()
        project = scene.project

        conversation = Conversation.objects.filter(
            project_id=project_pk,
            scene=scene,
        ).first()
        if not conversation:
            conversation = Conversation.objects.create(
                project_id=project_pk,
                scene=scene,
            )

        plain_content = re.sub(r'<[^>]+>', '', scene.content or '').strip()
        has_content = bool(plain_content)

        context_parts = []
        context_parts.append('Project: ' + project.title)

        characters = list(scene.characters.all())
        places = list(scene.places.all())
        timeline_events = list(scene.timeline_events.all())
        groups = list(scene.groups.all())
        items = list(scene.items.all())
        lore = list(scene.lore.all())

        has_tags = bool(characters or places or timeline_events or groups or items or lore)

        if characters:
            context_parts.append('CHARACTERS:')
            for c in characters:
                context_parts.append('- ' + c.name + ': ' + c.description)

        if places:
            context_parts.append('PLACES:')
            for p in places:
                context_parts.append('- ' + p.name + ': ' + p.description)

        if timeline_events:
            context_parts.append('TIMELINE EVENTS:')
            for e in timeline_events:
                context_parts.append('- ' + e.title + ': ' + e.description)

        if groups:
            context_parts.append('GROUPS:')
            for g in groups:
                context_parts.append('- ' + g.name + ' (' + g.group_type + '): ' + g.description)

        if items:
            context_parts.append('ITEMS:')
            for i in items:
                context_parts.append('- ' + i.name + ' (' + i.item_type + '): ' + i.description)

        if lore:
            context_parts.append('LORE:')
            for l in lore:
                context_parts.append('- ' + l.title + ' (' + l.lore_type + '): ' + l.description)

        assembled_context = '\n'.join(context_parts)

        content_text = plain_content if has_content else 'Scene is empty - no content yet.'

        system_prompt_template = (
            'You are a creative writing coach for a novelist.\n'
            'Your job is to generate ONE specific, actionable writing prompt\n'
            'that will help the writer continue this scene.\n\n'
            'Rules:\n'
            '- The prompt must be grounded in the Story Bible context provided.\n'
            '- Do NOT write prose for the writer. Give them a direction, not content.\n'
            '- Keep it to 2-4 sentences maximum.\n'
            '- Be specific - reference actual character names, places, items from the Story Bible.\n'
            '- Focus on: a character\'s internal reaction, a sensory detail, an unexpected action,\n'
            '  or a piece of dialogue that would move the scene forward.\n'
            '- If no Story Bible context exists, give a general craft-based prompt\n'
            '  about scene structure or character motivation.\n\n'
            'Story Bible context for this scene:\n'
            '{assembled_context}\n\n'
            'Current scene content (what is written so far):\n'
            '{content_text}\n\n'
            'Generate one writing prompt now.'
        )

        full_prompt = system_prompt_template.replace('{assembled_context}', assembled_context).replace('{content_text}', content_text)

        try:
            from .ai_service import resolve_key, GEMINI_MODEL, AIServiceNotConfigured, AIServiceError
            key, is_free = resolve_key(request.user)
        except AIServiceNotConfigured as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction='You are a creative writing coach. Generate one specific, actionable writing prompt.',
        )

        try:
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
            response = call_with_timeout(
                lambda: model.generate_content(full_prompt, safety_settings=safety_settings)
            )
        except Exception as e:
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
            content=response.text,
            metadata={'type': 'writing_prompt'},
        )

        serializer = MessageSerializer(assistant_message)
        return Response({'message': serializer.data}, status=status.HTTP_201_CREATED)


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


class SceneNoteViewSet(viewsets.ModelViewSet):
    serializer_class = SceneNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SceneNote.objects.filter(
            scene__project__owner=self.request.user,
            scene_id=self.kwargs['scene_pk'],
        )

    def perform_create(self, serializer):
        serializer.save(scene_id=self.kwargs['scene_pk'])


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Conversation.objects.filter(
            project__owner=self.request.user,
            project_id=self.kwargs['project_pk'],
        ).select_related('scene')
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
        ).select_related('conversation')

    def create(self, request, project_pk=None, conversation_pk=None):
        if is_ratelimited(request, group='create_message', key='user', rate='20/m', method='POST', increment=True):
            return Response(
                {'error': 'Too many requests. Please wait a moment before trying again.'},
                status=429,
            )

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


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    return Response({'csrfToken': get_token(request)})


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
    if not user.profile.is_email_verified:
        return Response(
            {'error': 'Please verify your email before logging in.', 'needs_verification': True, 'email': user.email},
            status=status.HTTP_403_FORBIDDEN,
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

    if not email:
        return Response(
            {'error': 'Email is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        EmailValidator()(email)
    except DjangoValidationError:
        return Response(
            {'error': 'Enter a valid email address.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    domain = email.split('@')[1].lower()
    try:
        dns.resolver.resolve(domain, 'MX')
    except Exception:
        return Response(
            {'error': 'Enter a valid email address.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    User = get_user_model()

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'A user with this username already exists.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'An account with this email already exists.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(password)
    except DjangoValidationError as e:
        return Response(
            {'error': e.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = False
        profile.save()

        signer = TimestampSigner(salt=settings.SIGNING_SALT)
        token = signer.sign(user.pk)

        verify_url = f"{request.scheme}://{request.get_host()}/api/auth/verify-email/?token={token}"

        if settings.RESEND_API_KEY:
            html_body = render_to_string('emails/verify_email.html', {
                'username': user.username,
                'verify_url': verify_url,
            })
            text_body = f'Welcome to Writer\'s Draft!\n\nPlease verify your email by clicking:\n{verify_url}'
            from anymail.message import AnymailMessage
            msg = AnymailMessage(
                subject='Verify your email — Writer\'s Draft',
                body=text_body,
                to=[user.email],
            )
            msg.attach_alternative(html_body, 'text/html')
            try:
                msg.send()
            except Exception:
                user.delete()
                return Response(
                    {'error': 'Could not send verification email to that address. Please use a different email.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {'message': 'Check your email to verify your account.', 'email': user.email},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email_view(request):
    token = request.query_params.get('token')
    if not token:
        return redirect(f"{settings.FRONTEND_URL}/verify-email?error=missing_token")

    try:
        signer = TimestampSigner(salt=settings.SIGNING_SALT)
        user_pk = signer.unsign(token, max_age=settings.SIGNING_MAX_AGE)
    except SignatureExpired:
        return redirect(f"{settings.FRONTEND_URL}/verify-email?error=expired")
    except BadSignature:
        return redirect(f"{settings.FRONTEND_URL}/verify-email?error=invalid")

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return redirect(f"{settings.FRONTEND_URL}/verify-email?error=not_found")

    if user.profile.is_email_verified:
        return redirect(f"{settings.FRONTEND_URL}/dashboard")

    user.profile.is_email_verified = True
    user.profile.save()

    login(request, user)

    return redirect(f"{settings.FRONTEND_URL}/dashboard")


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_view(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)

    if user.profile.is_email_verified:
        return Response({'message': 'Email already verified.'})

    try:
        signer = TimestampSigner(salt=settings.SIGNING_SALT)
        token = signer.sign(user.pk)
        verify_url = f"{request.scheme}://{request.get_host()}/api/auth/verify-email/?token={token}"

        html_body = render_to_string('emails/verify_email.html', {
            'username': user.username,
            'verify_url': verify_url,
        })
        text_body = f'Welcome to Writer\'s Draft!\n\nPlease verify your email by clicking:\n{verify_url}'
        from anymail.message import AnymailMessage
        msg = AnymailMessage(
            subject='Verify your email — Writer\'s Draft',
            body=text_body,
            to=[user.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()

        return Response({'message': 'Verification email sent.'})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to resend verification email to {user.email}: {e}")
        return Response({'error': 'Could not send verification email. The address may be invalid or the email service is unavailable.'}, status=status.HTTP_502_BAD_GATEWAY)


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
