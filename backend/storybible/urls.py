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
projects_router.register('scenes', views.SceneViewSet, basename='project-scenes')
projects_router.register('conversations', views.ConversationViewSet, basename='project-conversations')

conversations_router = routers.NestedSimpleRouter(
    projects_router, 'conversations', lookup='conversation'
)
conversations_router.register('messages', views.MessageViewSet, basename='project-conversation-messages')

auth_urls = [
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/logout/', views.logout_view, name='auth-logout'),
    path('auth/user/', views.user_view, name='auth-user'),
    path('auth/register/', views.register_view, name='auth-register'),
]

urlpatterns = [
    *auth_urls,
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(conversations_router.urls)),
]
