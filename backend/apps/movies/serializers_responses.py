# Django modules
from apps.abstracts.serializers import SuccessResponseSerializer
from apps.movies.serializers import (
    MovieSerializer,
    CommentSerializer,
    RatingSerializer,
    ReviewSerializer,
    RatingDetailSerializer,
    FavoriteSerializer,
)


class MovieSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful movie responses."""

    data = MovieSerializer()


class MovieListSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful movie list responses."""

    data = MovieSerializer(many=True)


class CommentSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful comment responses."""

    data = CommentSerializer()


class CommentListSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful comment list responses."""

    data = CommentSerializer(many=True)


class RatingSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful rating responses."""

    data = RatingSerializer()


class ReviewSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful review responses."""

    data = ReviewSerializer()


class ReviewListSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful review list responses."""

    data = ReviewSerializer(many=True)


class RatingDetailSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful rating detail responses."""

    data = RatingDetailSerializer()


class RatingDetailListSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful rating detail list responses."""

    data = RatingDetailSerializer(many=True)


class FavoriteSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful favorite responses."""

    data = FavoriteSerializer()


class FavoriteListSuccessResponseSerializer(SuccessResponseSerializer):
    """Serializer for successful favorite list responses."""

    data = FavoriteSerializer(many=True)
