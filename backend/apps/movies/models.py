# Django modules
from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Project modules
from apps.abstracts.models import AbstractBaseModel


class ActiveManager(models.Manager):
    """Manager that filters out soft-deleted records"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


NAME_MAX_LENGTH = 255
GENRE_MAX_LENGTH = 100
MIN_YEAR = 1900
MAX_YEAR = 2100
MIN_RATING = 1
MAX_RATING = 5


class Movie(AbstractBaseModel):
    """
    Movie model representing a film.

    Fields:
        - title: Title of the movie
        - description: Description of the movie
        - year: Release year of the movie
        - genre: Genre of the movie
        - duration: Duration of the movie in minutes
        - poster: File path to the movie poster
        - average_rating: Average rating of the movie (calculated)
        - likes_count: Total number of likes for the movie (calculated)
    """

    title = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    year = models.IntegerField(
        validators=[MinValueValidator(MIN_YEAR), MaxValueValidator(MAX_YEAR)],
        help_text="Movie release year",
    )
    genre = models.CharField(max_length=GENRE_MAX_LENGTH, help_text="Movie genre")
    duration = models.IntegerField(help_text="Duration in minutes")
    poster = models.FileField(
        upload_to="posters/", blank=True, null=True, help_text="Movie poster file path"
    )
    video = models.FileField(
        upload_to="videos/", blank=True, null=True, help_text="Movie video file"
    )
    likes = GenericRelation("Like", related_query_name="movie")

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["genre"], name="movie_genre_idx"),
            models.Index(fields=["year"], name="movie_year_idx"),
            models.Index(fields=["-created_at"], name="movie_created_idx"),
            models.Index(fields=["genre", "year"], name="movie_genre_year_idx"),
        ]

    @property
    def average_rating(self):
        """Average rating value for this movie."""
        if hasattr(self, "_average_rating_cache"):
            return self._average_rating_cache or 0
        return self.ratings.aggregate(avg=Avg("score")).get("avg") or 0

    @average_rating.setter
    def average_rating(self, value):
        # Allow annotate(...) to set this value without error
        self._average_rating_cache = value

    @property
    def likes_count(self):
        """Total likes for this movie."""
        if hasattr(self, "_likes_count_cache"):
            return self._likes_count_cache or 0
        return self.likes.count()

    @likes_count.setter
    def likes_count(self, value):
        # Allow annotate(...) to set this value without error
        self._likes_count_cache = value


class Comment(AbstractBaseModel):
    """
    Comment model representing a user's comment on a movie.

    Fields:
        - movie: ForeignKey to the Movie model
        - user: ForeignKey to the User model
        - text: Text content of the comment
        - parent: Optional ForeignKey to self for nested comments
        - likes_count: Total number of likes for the comment (calculated)
    """

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    likes = GenericRelation("Like", related_query_name="comment")

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.movie.title}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["movie"], name="comment_movie_idx"),
            models.Index(fields=["parent"], name="comment_parent_idx"),
            models.Index(fields=["-created_at"], name="comment_created_idx"),
        ]

    @property
    def likes_count(self):
        """Total likes for this comment."""
        if hasattr(self, "_likes_count_cache"):
            return self._likes_count_cache or 0
        return self.likes.count()

    @likes_count.setter
    def likes_count(self, value):
        # Allow annotate(...) to set this value without error
        self._likes_count_cache = value


class Rating(AbstractBaseModel):
    """
    Rating model representing a user's rating for a movie.

    Fields:
        - user: ForeignKey to the User model
        - movie: ForeignKey to the Movie model
        - score: Rating score (1-5)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings"
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_RATING), MaxValueValidator(MAX_RATING)]
    )

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["movie"], name="rating_movie_idx"),
            models.Index(fields=["user", "movie"], name="rating_user_movie_idx"),
        ]

    def __str__(self):
        return f"{self.score} for {self.movie.title} by {self.user.username}"


class Like(AbstractBaseModel):
    """
    Universal Like model — works for both Movie and Comment.

    Fields:
        - user: ForeignKey to the User model
        - content_type: ForeignKey to ContentType for generic relation
        - object_id: ID of the liked object
        - content_object: GenericForeignKey to the liked object
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.content_object}"


class Review(AbstractBaseModel):
    """
    Review model representing a user's detailed review of a movie.

    Fields:
        - user: ForeignKey to the User model
        - movie: ForeignKey to the Movie model
        - title: Title of the review
        - text: Detailed review text
        - rating: Rating score (1-5) associated with this review
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=NAME_MAX_LENGTH, help_text="Review title")
    text = models.TextField(help_text="Detailed review content")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_RATING), MaxValueValidator(MAX_RATING)],
        help_text="Rating score (1-5)",
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["movie"], name="review_movie_idx"),
            models.Index(fields=["user"], name="review_user_idx"),
            models.Index(fields=["-created_at"], name="review_created_idx"),
        ]

    def __str__(self):
        return f"Review by {self.user.username} for {self.movie.title}"


class Favorite(AbstractBaseModel):
    """
    Favorite model representing a user's favorite movies.

    Fields:
        - user: ForeignKey to the User model
        - movie: ForeignKey to the Movie model
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="favorited_by"
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} favorited {self.movie.title}"
