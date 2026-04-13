from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Create the initial superuser from environment variables"

    def handle(self, *args, **options):
        username = settings.INITIAL_USERNAME
        password = settings.INITIAL_PASSWORD

        if not username or not password:
            raise CommandError("INITIAL_USERNAME and INITIAL_PASSWORD must be set in environment.")

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists, skipping."))
            return

        try:
            validate_password(password)
        except ValidationError as e:
            raise CommandError(f"Password rejected: {'; '.join(e.messages)}")

        User.objects.create_superuser(username=username, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
