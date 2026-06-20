from django.db import models
from django.conf import settings


class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Character(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Place(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class TimelineEvent(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timeline_events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']


class Scene(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scenes')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    characters = models.ManyToManyField(Character, blank=True)
    places = models.ManyToManyField(Place, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f'Scene {self.order}'

    class Meta:
        ordering = ['order']


class SceneVersion(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'v{self.pk} of {self.scene}'

    class Meta:
        ordering = ['-created_at']


class Conversation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='conversations')
    scene = models.ForeignKey(Scene, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Conversation {self.pk} -- {self.project}'

    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.role} @ {self.created_at}'

    class Meta:
        ordering = ['created_at']
