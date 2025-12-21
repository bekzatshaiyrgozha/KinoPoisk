# Django modules
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Movie search request",
            request_only=True,
            value={
                "query": "Inception",
                "genre": "Action",
                "year_from": 2010,
                "year_to": 2020,
                "ordering": "-average_rating",
            },
        )
    ]
)
class MovieSearchRequestSerializer(serializers.Serializer):
    """Serializer for movie search requests."""

    query = serializers.CharField(required=False, allow_blank=True)
    genre = serializers.CharField(required=False, allow_blank=True)
    year_from = serializers.IntegerField(required=False, min_value=1900)
    year_to = serializers.IntegerField(required=False, max_value=2100)
    ordering = serializers.ChoiceField(
        choices=[
            "title",
            "-title",
            "year",
            "-year",
            "average_rating",
            "-average_rating",
            "created_at",
            "-created_at",
        ],
        required=False,
        default="-created_at",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Comment request",
            request_only=True,
            value={
                "text": "Great movie!",
                "parent": None,
            },
        )
    ]
)
class CommentRequestSerializer(serializers.Serializer):
    """Serializer for comment requests."""

    text = serializers.CharField()
    parent = serializers.IntegerField(required=False, allow_null=True)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Rating request",
            request_only=True,
            value={
                "score": 5,
            },
        )
    ]
)
class RatingRequestSerializer(serializers.Serializer):
    """Serializer for rating requests."""

    score = serializers.IntegerField(min_value=1, max_value=5)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Like toggle request",
            request_only=True,
            value={
                "content_type": "movie",
                "object_id": 1,
            },
        )
    ]
)
class LikeToggleRequestSerializer(serializers.Serializer):
    """Serializer for like toggle requests."""

    content_type = serializers.CharField()
    object_id = serializers.IntegerField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Review request",
            request_only=True,
            value={
                "movie_id": 1,
                "title": "Amazing!",
                "text": "This is an excellent movie with great acting.",
                "rating": 5,
            },
        )
    ]
)
class ReviewRequestSerializer(serializers.Serializer):
    """Serializer for review requests."""

    movie_id = serializers.IntegerField()
    title = serializers.CharField()
    text = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Rating detail request",
            request_only=True,
            value={
                "movie_id": 1,
                "score": 4,
            },
        )
    ]
)
class RatingDetailRequestSerializer(serializers.Serializer):
    """Serializer for rating detail requests."""

    movie_id = serializers.IntegerField()
    score = serializers.IntegerField(min_value=1, max_value=5)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Favorite request",
            request_only=True,
            value={
                "movie_id": 1,
            },
        )
    ]
)
class FavoriteRequestSerializer(serializers.Serializer):
    """Serializer for favorite requests."""

    movie_id = serializers.IntegerField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Video upload request",
            request_only=True,
            value={
                "video": "movie.mp4",
            },
        )
    ]
)
class VideoUploadRequestSerializer(serializers.Serializer):
    """Serializer for video upload requests."""

    video = serializers.FileField()


class MovieFilterRequestSerializer(serializers.Serializer):
    """Serializer for filtering by movie_id in query params."""

    movie_id = serializers.IntegerField(required=False, help_text="Filter by movie ID")
