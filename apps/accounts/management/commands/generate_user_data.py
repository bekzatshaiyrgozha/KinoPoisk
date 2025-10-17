# Python modules
from typing import Any
from datetime import datetime

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction

# Third-party modules
from faker import Faker

fake = Faker()
Faker.seed(42)

class Command(BaseCommand):
    help = "Generate fake data for movies, users, comments, ratings, and likes."

    USER_COUNT = 20
    
    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        start = datetime.now()
        self.stdout.write(self.style.NOTICE("Generating fake data..."))

        users = self._generate_users()

        elapsed = (datetime.now() - start).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(f"\n Done in {elapsed:.2f} seconds.")
        )
    def _generate_users(self):
        self.stdout.write("Creating users...")
        users = [
            User(
                username=f"user{i}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password=make_password("password123"),
            )
            for i in range(self.USER_COUNT)
        ]
        User.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS(f"→ {len(users)} users created."))
        return list(User.objects.all())
        


