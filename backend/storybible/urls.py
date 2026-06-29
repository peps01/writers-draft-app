from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

router = DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='project')

projects_router = routers.NestedSimpleRouter(router, 'projects', lookup='project')
projects_router.register('characters', views.CharacterViewSet, basename='project-characters')
projects_router.register('places', views.PlaceViewSet, basename='project-places')
projects_router.register('timeline-events', views.TimelineEventViewSet, basename='project-timeline-events')
projects_router.register('groups', views.GroupViewSet, basename='project-groups')
projects_router.register('items', views.ItemViewSet, basename='project-items')
projects_router.register('lore', views.LoreViewSet, basename='project-lore')
projects_router.register('scenes', views.SceneViewSet, basename='project-scenes')
projects_router.register('conversations', views.ConversationViewSet, basename='project-conversations')

scenes_router = routers.NestedSimpleRouter(
    projects_router, 'scenes', lookup='scene'
)
scenes_router.register('versions', views.SceneVersionViewSet, basename='project-scene-versions')
scenes_router.register('notes', views.SceneNoteViewSet, basename='project-scene-notes')

conversations_router = routers.NestedSimpleRouter(
    projects_router, 'conversations', lookup='conversation'
)
conversations_router.register('messages', views.MessageViewSet, basename='project-conversation-messages')

auth_urls = [
    path('auth/csrf/', views.csrf_token_view, name='auth-csrf'),
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/logout/', views.logout_view, name='auth-logout'),
    path('auth/user/', views.user_view, name='auth-user'),
    path('auth/register/', views.register_view, name='auth-register'),
    path('auth/profile/', views.profile_view, name='auth-profile'),
    path('auth/profile/test-key/', views.test_key_view, name='auth-profile-test-key'),
]

urlpatterns = [
    *auth_urls,
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(scenes_router.urls)),
    path('', include(conversations_router.urls)),
]
