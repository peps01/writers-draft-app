from django.contrib import admin

from .models import Project, Character, Place, TimelineEvent, Group, Item, Lore, Scene, SceneNote, SceneVersion, Conversation, Message, UserProfile

admin.site.register(Project)
admin.site.register(Character)
admin.site.register(Place)
admin.site.register(TimelineEvent)
admin.site.register(Group)
admin.site.register(Item)
admin.site.register(Lore)
admin.site.register(Scene)
admin.site.register(SceneNote)
admin.site.register(SceneVersion)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(UserProfile)
