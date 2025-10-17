from rest_framework import serializers
from .models import Movie, Comment, Like, Rating
from django.contrib.contenttypes.models import ContentType


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model"""

    average_rating = serializers.FloatField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'year', 'genre',
            'duration', 'poster', 'average_rating', 'likes_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'average_rating', 
            'likes_count', 
            'created_at', 'updated_at'
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""

    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'movie', 'user', 'text', 'parent',
            'likes_count', 'replies',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'likes_count', 'replies',
            'created_at', 'updated_at'
        ]

    def get_replies(self, obj):
        """Return nested replies for a comment"""
        from rest_framework import serializers
        replies = obj.replies.all()
        # Create a simple serializer for replies to avoid circular reference
        return [
            {
                'id': reply.id,
                'user': str(reply.user),
                'text': reply.text,
                'parent': reply.parent_id,
                'likes_count': reply.likes_count,
                'created_at': reply.created_at,
                'updated_at': reply.updated_at
            }
            for reply in replies
        ]


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""

    user = serializers.StringRelatedField(read_only=True)
    content_type = serializers.SlugRelatedField(
        slug_field='model',
        queryset=ContentType.objects.all()
    )

    class Meta:
        model = Like
        fields = [
            'id', 'user', 
            'content_type', 'object_id', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for Rating model"""

    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)
    average_rating = serializers.FloatField(
        source='movie.average_rating', 
        read_only=True
    )

    class Meta:
        model = Rating
        fields = [
            'id', 'score', 
            'user', 'movie', 
            'average_rating', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 
            'movie', 'average_rating', 
            'created_at', 'updated_at'
        ]
