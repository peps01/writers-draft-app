from rest_framework import serializers

from .models import Project, Character, Place, TimelineEvent, Group, Item, Lore, Scene, SceneVersion, Conversation, Message


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['owner', 'created_at', 'updated_at']


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class LoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lore
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_id = self.context.get('project_id')
        qs = Character.objects.filter(project_id=project_id) if project_id is not None else Character.objects.none()
        self.fields['characters'].child_relation.queryset = qs
        qs = Place.objects.filter(project_id=project_id) if project_id is not None else Place.objects.none()
        self.fields['places'].child_relation.queryset = qs
        qs = TimelineEvent.objects.filter(project_id=project_id) if project_id is not None else TimelineEvent.objects.none()
        self.fields['timeline_events'].child_relation.queryset = qs
        qs = Group.objects.filter(project_id=project_id) if project_id is not None else Group.objects.none()
        self.fields['groups'].child_relation.queryset = qs
        qs = Item.objects.filter(project_id=project_id) if project_id is not None else Item.objects.none()
        self.fields['items'].child_relation.queryset = qs
        qs = Lore.objects.filter(project_id=project_id) if project_id is not None else Lore.objects.none()
        self.fields['lore'].child_relation.queryset = qs


class SceneVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SceneVersion
        fields = ['id', 'content', 'created_at']
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ['project', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['conversation', 'created_at']
