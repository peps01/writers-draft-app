from django.db import migrations, models


def fix_null_is_email_verified(apps, schema_editor):
    UserProfile = apps.get_model('storybible', 'UserProfile')
    UserProfile.objects.filter(is_email_verified__isnull=True).update(is_email_verified=False)


class Migration(migrations.Migration):

    dependencies = [
        ('storybible', '0010_userprofile_is_email_verified'),
    ]

    operations = [
        migrations.RunPython(fix_null_is_email_verified, migrations.RunPython.noop),
    ]
