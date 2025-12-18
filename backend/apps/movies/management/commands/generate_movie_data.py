# Python modules
from typing import Any
from random import choice, randint
from datetime import datetime

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

# Third-party modules
from faker import Faker

# Project modules
from apps.movies.models import Movie, Comment, Rating, Like, Review, Favorite


User = get_user_model()


fake = Faker()
Faker.seed(42)


class Command(BaseCommand):
    help = "Generate fake data for movies, users, comments, ratings, and likes."

    USER_COUNT = 20
    MOVIE_COUNT = 15
    MAX_COMMENTS = 60
    MAX_LIKES = 100
    MAX_RATINGS = 40

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        start = datetime.now()
        self.stdout.write(self.style.NOTICE("Clearing old data..."))
        self._clear_old_data()

        self.stdout.write(self.style.NOTICE("Generating fake data..."))

        users = self._generate_users()
        movies = self._generate_movies()
        comments = self._generate_comments(users, movies)
        self._generate_ratings(users, movies)
        self._generate_likes(users, movies, comments)
        self._generate_reviews(users, movies)
        self._generate_favorites(users, movies)

        elapsed = (datetime.now() - start).total_seconds()
        self.stdout.write(self.style.SUCCESS(f"\n Done in {elapsed:.2f} seconds."))

    def _clear_old_data(self):
        Review.objects.all().delete()
        Favorite.objects.all().delete()
        Like.objects.all().delete()
        Comment.objects.all().delete()
        Rating.objects.all().delete()
        Movie.objects.all().delete()
        User.objects.filter(is_superuser=False, is_staff=False).delete()

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
        return list(User.objects.filter(is_superuser=False, is_staff=False))

    def _generate_movies(self):
        self.stdout.write("Creating movies...")
        movies = []
        for _ in range(self.MOVIE_COUNT):
            title = fake.sentence(nb_words=3).replace(".", "")
            description = fake.paragraph(nb_sentences=6)
            genre = choice(
                ["Action", "Drama", "Comedy", "Sci-Fi", "Thriller", "Romance"]
            )
            duration = randint(60, 180)
            year = randint(1980, 2025)
            movies.append(
                Movie(
                    title=title,
                    description=description,
                    genre=genre,
                    duration=duration,
                    year=year,
                )
            )
        Movie.objects.bulk_create(movies)
        self.stdout.write(self.style.SUCCESS(f"→ {len(movies)} movies created."))
        return list(Movie.objects.all())

    def _generate_comments(self, users, movies):
        self.stdout.write("Creating comments...")
        comments = []
        for _ in range(randint(self.MAX_COMMENTS // 2, self.MAX_COMMENTS)):
            user = choice(users)
            movie = choice(movies)
            text = fake.sentence(nb_words=20)
            comments.append(Comment(movie=movie, user=user, text=text))
        Comment.objects.bulk_create(comments)
        self.stdout.write(self.style.SUCCESS(f"→ {len(comments)} comments created."))
        return list(Comment.objects.all())

    def _generate_ratings(self, users, movies):
        self.stdout.write("Creating ratings...")
        ratings = []
        created_pairs = set()

        target_count = randint(self.MAX_RATINGS // 2, self.MAX_RATINGS)
        attempts = 0
        max_attempts = target_count * 3

        while len(ratings) < target_count and attempts < max_attempts:
            user = choice(users)
            movie = choice(movies)
            pair = (user.id, movie.id)

            if pair not in created_pairs:
                score = randint(1, 5)
                ratings.append(Rating(user=user, movie=movie, score=score))
                created_pairs.add(pair)
            attempts += 1

        Rating.objects.bulk_create(ratings)
        self.stdout.write(self.style.SUCCESS(f"→ {len(ratings)} ratings created."))

    def _generate_likes(self, users, movies, comments):
        self.stdout.write("Creating likes...")

        like_objects = []
        created_triplets = set()
        movie_ct = ContentType.objects.get_for_model(Movie)
        comment_ct = ContentType.objects.get_for_model(Comment)

        target_count = randint(self.MAX_LIKES // 2, self.MAX_LIKES)
        attempts = 0
        max_attempts = target_count * 3

        while len(like_objects) < target_count and attempts < max_attempts:
            user = choice(users)
            if choice([True, False]):
                obj = choice(movies)
                ct = movie_ct
            else:
                obj = choice(comments)
                ct = comment_ct

            triplet = (user.id, ct.id, obj.id)
            if triplet not in created_triplets:
                like_objects.append(Like(user=user, content_type=ct, object_id=obj.id))
                created_triplets.add(triplet)
            attempts += 1

        Like.objects.bulk_create(like_objects, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"→ {len(like_objects)} likes created."))

    def _generate_reviews(self, users, movies):
        self.stdout.write("Creating reviews...")
        reviews = []
        created_pairs = set()
        target_count = 50
        attempts = 0
        max_attempts = target_count * 3

        while len(reviews) < target_count and attempts < max_attempts:
            user = choice(users)
            movie = choice(movies)
            pair = (user.id, movie.id)

            if pair not in created_pairs:
                reviews.append(
                    Review(
                        user=user,
                        movie=movie,
                        title=fake.sentence(nb_words=5),
                        text=fake.paragraph(nb_sentences=3),
                        rating=randint(1, 5),
                    )
                )
                created_pairs.add(pair)
            attempts += 1

        Review.objects.bulk_create(reviews, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"→ {len(reviews)} reviews created."))

    def _generate_favorites(self, users, movies):
        self.stdout.write("Creating favorites...")
        favorites = []
        created_pairs = set()
        target_count = 30
        attempts = 0
        max_attempts = target_count * 3

        while len(favorites) < target_count and attempts < max_attempts:
            user = choice(users)
            movie = choice(movies)
            pair = (user.id, movie.id)

            if pair not in created_pairs:
                favorites.append(Favorite(user=user, movie=movie))
                created_pairs.add(pair)
            attempts += 1

        Favorite.objects.bulk_create(favorites, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"→ {len(favorites)} favorites created."))
