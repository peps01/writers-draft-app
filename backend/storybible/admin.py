from django.contrib import admin

from .models import Project, Character, Place, TimelineEvent, Scene, SceneVersion, Conversation, Message

admin.site.register(Project)
admin.site.register(Character)
admin.site.register(Place)
admin.site.register(TimelineEvent)
admin.site.register(Scene)
admin.site.register(SceneVersion)
admin.site.register(Conversation)
admin.site.register(Message)
