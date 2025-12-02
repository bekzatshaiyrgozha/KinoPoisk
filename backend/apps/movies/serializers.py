from rest_framework import serializers
from .models import Movie, Comment, Like, Rating,  Review, Favorite
from django.contrib.contenttypes.models import ContentType



class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model"""

    average_rating = serializers.FloatField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'year', 'genre',
            'duration', 'poster', 'average_rating', 'likes_count',
            'is_liked', 'user_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'average_rating', 
            'likes_count', 'is_liked', 'user_rating',
            'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Movie)
            # ActiveManager automatically filters deleted_at__isnull=True
            return Like.objects.filter(
                content_type=content_type,
                object_id=obj.id,
                user=user
            ).exists()
        return False
    
    def get_user_rating(self, obj):
        """Get the current user's rating for this movie"""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            rating = Rating.objects.filter(
                movie=obj,
                user=user
            ).first()
            return rating.score if rating else None
        return None


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""

    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'movie', 'user', 'text', 'parent',
            'likes_count', 'is_liked', 'replies',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'likes_count', 'is_liked', 'replies',
            'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Comment)
            # ActiveManager automatically filters deleted_at__isnull=True
            return Like.objects.filter(
                content_type=content_type,
                object_id=obj.id,
                user=user
            ).exists()
        return False

    def get_replies(self, obj):
        """Return nested replies for a comment"""
        from django.db.models import Count
        replies = obj.replies.annotate(
            likes_count=Count('likes', distinct=True)
        )
        
        user = self.context.get('request').user if self.context.get('request') else None
        content_type = ContentType.objects.get_for_model(Comment)
        
        return [
            {
                'id': reply.id,
                'user': str(reply.user),
                'text': reply.text,
                'parent': reply.parent_id,
                'likes_count': reply.likes_count,
                'is_liked': Like.objects.filter(
                    content_type=content_type,
                    object_id=reply.id,
                    user=user
                ).exists() if user and user.is_authenticated else False,
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

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""

    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)
    movie_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'movie', 'movie_id',
            'title', 'text', 'rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'movie',
            'created_at', 'updated_at'
        ]

    def validate_movie_id(self, value):
        """Validate that the movie exists"""
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie not found.")
        return value

    def create(self, validated_data):
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        validated_data['movie'] = movie

        user = self.context['request'].user
        if Review.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError({
                'detail': 'You have already reviewed this movie.'
            })

        return super().create(validated_data)



class RatingDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Rating model (for ViewSet)"""

    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Rating
        fields = [
            'id', 'user', 'movie', 'movie_id',
            'score',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'movie',
            'created_at', 'updated_at'
        ]

    def validate_movie_id(self, value):
        """Validate that the movie exists"""
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie not found.")
        return value

    def create(self, validated_data):
        """Create or update a rating"""
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        user = self.context['request'].user
        
        rating, created = Rating.objects.update_or_create(
            user=user,
            movie=movie,
            defaults={'score': validated_data['score']}
        )
        return rating


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for Favorite model"""

    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'movie', 'movie_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'movie',
            'created_at', 'updated_at'
        ]

    def validate_movie_id(self, value):
        """Validate that the movie exists"""
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie not found.")
        return value

    def create(self, validated_data):
        """Add movie to favorites"""
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        validated_data['movie'] = movie
        return super().create(validated_data)
    

class MovieSearchSerializer(serializers.Serializer):
    """
    Serializer for movie search parameters.
    All fields are optional to allow flexible search.
    """
    
    query = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search query for title and description"
    )
    genre = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Filter by genre (exact match)"
    )
    year_from = serializers.IntegerField(
        required=False,
        min_value=1900,
        help_text="Minimum release year"
    )
    year_to = serializers.IntegerField(
        required=False,
        max_value=2100,
        help_text="Maximum release year"
    )
    ordering = serializers.ChoiceField(
        choices=[
            'title', '-title',        
            'year', '-year',           
            'average_rating', '-average_rating',  
            'created_at', '-created_at'  
        ],
        required=False,
        default='-created_at',
        help_text="Sort order for results"
    )
    
    def validate(self, attrs):
        """Validate that year_from is not greater than year_to"""
        year_from = attrs.get('year_from')
        year_to = attrs.get('year_to')
        
        if year_from and year_to and year_from > year_to:
            raise serializers.ValidationError({
                'year_from': 'year_from cannot be greater than year_to'
            })
        
        return attrs