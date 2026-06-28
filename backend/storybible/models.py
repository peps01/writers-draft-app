from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True, default='')
    synopsis = models.TextField(blank=True, default='')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
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


class Group(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=100, blank=True,
        help_text="e.g. Faction, Organization, Guild, Family, Religion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Item(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=100, blank=True,
        help_text="e.g. Weapon, Artifact, Relic, Tool, MacGuffin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Lore(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='lore')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    lore_type = models.CharField(max_length=100, blank=True,
        help_text="e.g. Magic System, Religion, Language, History, Law, Geography")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Scene(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scenes')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    characters = models.ManyToManyField(Character, blank=True)
    places = models.ManyToManyField(Place, blank=True)
    timeline_events = models.ManyToManyField(TimelineEvent, blank=True, related_name='scenes')
    groups = models.ManyToManyField(Group, blank=True, related_name='scenes')
    items = models.ManyToManyField(Item, blank=True, related_name='scenes')
    lore = models.ManyToManyField(Lore, blank=True, related_name='scenes')
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


class SceneNote(models.Model):
    NOTE_TYPES = [
        ('general', 'General'),
        ('todo', 'To-Do'),
        ('research', 'Research'),
        ('warning', 'Warning'),
        ('idea', 'Idea'),
    ]
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.note_type} note on {self.scene}'

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    # NOTE: API key stored as plaintext in Postgres for MVP.
    # Before any multi-user cloud deployment, add encryption via
    # django-encrypted-model-fields or a similar solution.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    gemini_api_key = models.CharField(max_length=200, blank=True, default='')
    is_paid_tier = models.BooleanField(default=False)
    daily_word_goal = models.PositiveIntegerField(null=True, blank=True, default=None)
    show_word_goal = models.BooleanField(default=False)

    def __str__(self):
        return f'Profile for {self.user.username}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


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
    metadata = models.JSONField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.role} @ {self.created_at}'

    class Meta:
        ordering = ['created_at']
