from django.db import migrations, models


def set_existing_users_verified(apps, schema_editor):
    UserProfile = apps.get_model('storybible', 'UserProfile')
    UserProfile.objects.update(is_email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('storybible', '0009_conversation_storybible__project_0de2ef_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_existing_users_verified, migrations.RunPython.noop),
    ]
