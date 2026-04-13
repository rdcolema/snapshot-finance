import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create the initial superuser from environment variables"

    def handle(self, *args, **options):
        username = os.environ.get("INITIAL_USERNAME")
        password = os.environ.get("INITIAL_PASSWORD")

        if not username or not password:
            self.stderr.write(self.style.ERROR("INITIAL_USERNAME and INITIAL_PASSWORD must be set in environment."))
            raise SystemExit(1)

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists, skipping."))
            return

        User.objects.create_superuser(username=username, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
