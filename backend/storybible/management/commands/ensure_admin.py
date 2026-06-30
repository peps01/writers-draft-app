from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Ensure the admin superuser exists'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'pepep'
        password = 'markjohn123'
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, 'pepep@admin.com', password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created'))
        else:
            self.stdout.write(f'Superuser "{username}" already exists')
