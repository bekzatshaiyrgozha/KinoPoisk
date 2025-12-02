# Third-party modules
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# Django modules
from django.http import HttpRequest
from django.db.models import Avg, Count
from django.contrib.contenttypes.models import ContentType


# Project modules
from .models import Movie, Comment, Like, Rating
from .serializers import (
    MovieSerializer,
    CommentSerializer,
    RatingSerializer,
    MovieSearchSerializer,
    MovieVideoUploadSerializer,
)
from apps.abstracts.serializers import (
    ErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)
from apps.abstracts.permissions import IsOwnerOrAdmin

# Typing imports
from typing import Optional, Type
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.contenttypes.models import ContentType as ContentTypeModel
from django.db.models.base import ModelBase


class MovieListView(APIView):
    """
    View to list all movies.
    Only authenticated users can access.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get list of all movies",
        description="Returns a list of all movies with average rating and likes count",
        tags=['Movies'],
        responses={
            200: MovieSerializer(many=True),
        }
    )
    def get(
            self, request: HttpRequest,
            *args, **kwargs
        ) -> Response:
        """
        Return all movies with average rating and like count.

        Params:
            - request: HttpRequest
            - *args
            - **kwargs
        Return:
            - response: Response
        """
        from .pagination import StandardResultsSetPagination
        
        movies: QuerySet[Movie] = Movie.objects.annotate(
            average_rating=Avg('ratings__score'),
            likes_count=Count('likes', distinct=True)
        )
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_movies = paginator.paginate_queryset(movies, request)
        
        serializer: MovieSerializer = MovieSerializer(
            paginated_movies, many=True, context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)


class MovieDetailView(APIView):
    """
    View to retrieve a specific movie.
    Only authenticated users can access.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get movie details",
        description="Returns detailed information about a specific movie by ID",
        tags=['Movies'],
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Movie ID',
                required=True
            ),
        ],
        responses={
            200: MovieSerializer,
            404: ErrorResponseSerializer,
        }
    )
    def get(
            self, request: HttpRequest,
            movie_id: int,
            *args, **kwargs
        ) -> Response:
        """
        Return a specific movie with average rating and like count.

        Params:
            - request: HttpRequest
            - movie_id: int - specific movie ID
            - *args
            - **kwargs
        Return:
            - response: Response
        """
        try:
            movie: Movie = Movie.objects.annotate(
                average_rating=Avg('ratings__score'),
                likes_count=Count('likes', distinct=True)
            ).get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Movie not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer: MovieSerializer = MovieSerializer(
            movie, context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class MovieVideoUploadView(APIView):
    """
    Admin-only endpoint to upload/replace a movie video file.
    """

    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload/replace movie video",
        description="Uploads or replaces the video file for the given movie. Admin/staff only.",
        tags=['Movies'],
        request=MovieVideoUploadSerializer,
        responses={
            200: MovieSerializer,
            400: ValidationErrorResponseSerializer,
            404: ErrorResponseSerializer,
        }
    )
    def put(
            self, request: HttpRequest,
            movie_id: int,
            *args, **kwargs
        ) -> Response:
        try:
            movie: Movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Movie not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MovieVideoUploadSerializer(
            movie,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                MovieSerializer(movie, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(
            self, request: HttpRequest,
            movie_id: int,
            *args, **kwargs
        ) -> Response:
        """Allow POST as alias for upload."""
        return self.put(request, movie_id, *args, **kwargs)


class CommentView(APIView):
    """
    View for listing and creating comments under a specific movie.
    Only authenticated users can access.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get movie comments",
        description="Returns a list of all comments for a movie (including replies)",
        tags=['Comments'],
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Movie ID',
                required=True
            ),
        ],
        responses={
            200: CommentSerializer(many=True),
        }
    )
    def get(
            self, request: HttpRequest, 
            movie_id: int, 
            *args, **kwargs
        ) -> Response:
        """
        List all comments for a movie (including replies).
        
        Params:
            - request: HttpRequest
            - movie_id: int
            - *args
            - **kwargs
        Return:
            - response: Response    
        """
        from .pagination import StandardResultsSetPagination
        
        comments: QuerySet[Comment] = Comment.objects.filter(
            movie_id=movie_id, parent=None
        ).select_related(
            'user', 'movie'
        ).prefetch_related(
            'replies__user'
        ).annotate(
            likes_count=Count('likes', distinct=True)
        )
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)
        
        serializer: CommentSerializer = CommentSerializer(
            paginated_comments, many=True, context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    @extend_schema(
        summary="Create movie comment",
        description="Creates a new comment for a movie (optionally as a reply to another comment)",
        tags=['Comments'],
        request=CommentSerializer,
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Movie ID',
                required=True
            ),
        ],
        responses={
            201: CommentSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Example request',
                value={
                    'text': 'Great movie!',
                    'parent': None
                },
                request_only=True
            ),
        ]
    )
    def post(
            self, request: HttpRequest, 
            movie_id: int,
            *args, **kwargs
        ) -> Response:
        """
        Create a new comment (optionally as a reply).
        
        Params:
            - request: HttpRequest
            - movie_id: int
            - *args
            - **kwargs
        Return:
            - response: Response
        """
        try:
            movie: Movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Movie not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer: CommentSerializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, movie=movie)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )


class LikeView(APIView):
    """
    Generic Like/Unlike view.
    Works for both movies and comments.
    Only authenticated users can access.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Like/Unlike object",
        description="Likes or unlikes an object (movie or comment)",
        tags=['Likes'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'content_type': {
                        'type': 'string',
                        'enum': ['movie', 'comment'],
                        'description': 'Object type to like'
                    },
                    'object_id': {
                        'type': 'integer',
                        'description': 'Object ID'
                    }
                },
                'required': ['content_type', 'object_id']
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            201: OpenApiTypes.OBJECT,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Like a movie',
                value={
                    'content_type': 'movie',
                    'object_id': 1
                },
                request_only=True
            ),
            OpenApiExample(
                'Like a comment',
                value={
                    'content_type': 'comment',
                    'object_id': 5
                },
                request_only=True
            ),
        ]
    )
    def post(
            self, request: HttpRequest, 
            *args, **kwargs
        ) -> Response:
        """
        Like or unlike an object (movie or comment).

        Required JSON body:
        {
            "content_type": "movie" | "comment",
            "object_id": int
        }
        Params:
            - request: HttpRequest
            - *args
            - **kwargs
        Return:
            - response: Response
        """
        content_type_str: Optional[str] = request.data.get("content_type")
        object_id: Optional[int] = request.data.get("object_id")

        if not content_type_str or not object_id:
            return Response(
                {"detail": "content_type and object_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ct: ContentTypeModel = ContentType.objects.get(model=content_type_str)
        except ContentType.DoesNotExist:
            return Response({"detail": "Invalid content_type."}, status=status.HTTP_400_BAD_REQUEST)

        obj_model: Type[ModelBase] = ct.model_class()

        try:
            obj: ModelBase = obj_model.objects.get(id=object_id)
        except obj_model.DoesNotExist:
            return Response(
                {"detail": "Object not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        user: User = request.user
        
        # Debug logging
        print(f"\n=== LIKE DEBUG ===")
        print(f"User: {user.username}")
        print(f"Content Type: {content_type_str}")
        print(f"Object ID: {object_id}")
        
        # Check for active like
        existing_like: Optional[Like] = Like.objects.filter(
            user=user, 
            content_type=ct, 
            object_id=object_id
        ).first()
        
        print(f"Active like found: {existing_like is not None}")
        if existing_like:
            print(f"Active like ID: {existing_like.id}, deleted_at: {existing_like.deleted_at}")

        if existing_like:
            # Unlike: soft delete the like
            print("Soft deleting existing like...")
            existing_like.delete()
            
            # Check if it was soft deleted
            check_deleted = Like.all_objects.filter(id=existing_like.id).first()
            if check_deleted:
                print(f"After delete - deleted_at: {check_deleted.deleted_at}")
            
            likes_count = Like.objects.filter(
                content_type=ct,
                object_id=object_id
            ).count()
            print(f"Likes count after delete: {likes_count}")
            print("=== END DEBUG ===\n")
            
            return Response(
                {
                    "liked": False,
                    "likes_count": likes_count
                },
                status=status.HTTP_200_OK
            )

        # Check if there's a soft-deleted like that we can restore
        soft_deleted_like: Optional[Like] = Like.all_objects.filter(
            user=user,
            content_type=ct,
            object_id=object_id,
            deleted_at__isnull=False
        ).first()
        
        if soft_deleted_like:
            # Restore the soft-deleted like
            print(f"Restoring soft-deleted like ID: {soft_deleted_like.id}")
            soft_deleted_like.deleted_at = None
            soft_deleted_like.save(update_fields=['deleted_at'])
            new_like = soft_deleted_like
            print(f"Restored like ID: {new_like.id}")
        else:
            # Create a new like
            print("Creating new like...")
            new_like = Like.objects.create(
                user=user, 
                content_type=ct, 
                object_id=object_id
            )
            print(f"Created like ID: {new_like.id}")
        
        likes_count = Like.objects.filter(
            content_type=ct,
            object_id=object_id
        ).count()
        print(f"Likes count after create/restore: {likes_count}")
        print("=== END DEBUG ===\n")
        
        return Response(
            {
                "liked": True,
                "likes_count": likes_count
            },
            status=status.HTTP_201_CREATED
        )


class RatingView(APIView):
    """
    View to rate a movie or update the rating.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Rate a movie",
        description="Rates a movie (score from 1 to 5) or updates an existing rating",
        tags=['Ratings'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'score': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 5,
                        'description': 'Movie rating (1-5)'
                    }
                },
                'required': ['score']
            }
        },
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Movie ID',
                required=True
            ),
        ],
        responses={
            200: RatingSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Rate a movie',
                value={
                    'score': 5
                },
                request_only=True
            ),
        ]
    )
    def post(
            self, request: HttpRequest, 
            movie_id: int, 
            *args, **kwargs
        ) -> Response:
        """
        Rate a specific movie (score 1–5).
        Body: { "score": 4 }
        Params:
            - request: HttpRequest
            - movie_id: int
            - *args
            - **kwargs
        Return:
            - response: Response
        """
        try:
            movie: Movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Movie not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        score: Optional[int] = request.data.get("score")
        if score is None or not (1 <= int(score) <= 5):
            return Response(
                {'detail': 'Score must be between 1 and 5.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        rating: Rating
        rating, _ = Rating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'score': score},
        )
        serializer: RatingSerializer = RatingSerializer(rating)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
        )
    

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .models import Review, Favorite
from .serializers import (
    ReviewSerializer,
    RatingDetailSerializer,
    FavoriteSerializer
)


class ReviewViewSet(ViewSet):
    """
    ViewSet for handling Review-related endpoints.
    Supports full CRUD operations.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get list of all reviews",
        description="Returns a list of all reviews (optionally filtered by movie_id)",
        tags=['Reviews'],
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Movie ID for filtering',
                required=False
            ),
        ],
        responses={200: ReviewSerializer(many=True)}
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="list",
        url_name="review-list"
    )
    def list_reviews(
        self, 
        request: HttpRequest, 
        *args, **kwargs
    ) -> Response:
        """Get all reviews (optionally filter by movie_id)"""
        from .pagination import StandardResultsSetPagination
        
        movie_id = request.query_params.get('movie_id')
        
        if movie_id:
            reviews = Review.objects.filter(movie_id=movie_id)
        else:
            reviews = Review.objects.all()
            
        reviews = reviews.select_related('user', 'movie').order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create a new review",
        description="Creates a new review for a movie",
        tags=['Reviews'],
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="create",
        url_name="review-create"
    )
    def create_review(
        self, 
        request: HttpRequest, 
        *args, **kwargs
    ) -> Response:
        """Create a new review for a movie"""
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Get review details",
        description="Returns detailed information about a review by ID",
        tags=['Reviews'],
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Review ID',
                required=True
            ),
        ],
        responses={
            200: ReviewSerializer,
            404: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["GET"],
        detail=True,
        url_path="detail",
        url_name="review-detail"
    )
    def retrieve_review(
        self, 
        request: HttpRequest,
        pk: int = None,
        *args, **kwargs
    ) -> Response:
        """Get a specific review by ID"""
        try:
            review = Review.objects.select_related('user', 'movie').get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {'detail': 'Review not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a review",
        description="Updates an existing review (owner only)",
        tags=['Reviews'],
        request=ReviewSerializer,
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Review ID',
                required=True
            ),
        ],
        responses={
            200: ReviewSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["PUT", "PATCH"],
        detail=True,
        url_path="update",
        url_name="review-update"
    )
    def update_review(
        self, 
        request: HttpRequest,
        pk: int = None,
        *args, **kwargs
    ) -> Response:
        """Update an existing review (only by the owner)"""
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {'detail': 'Review not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not IsOwnerOrAdmin().has_object_permission(request, self, review):
            return Response(
                {'detail': 'You do not have permission to update this review.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = request.method == 'PATCH'
        serializer = ReviewSerializer(
            review, 
            data=request.data, 
            partial=partial
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Delete a review",
        description="Deletes a review (owner only)",
        tags=['Reviews'],
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Review ID',
                required=True
            ),
        ],
        responses={
            204: None,
            404: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["DELETE"],
        detail=True,
        url_path="delete",
        url_name="review-delete"
    )
    def delete_review(
        self, 
        request: HttpRequest,
        pk: int = None,
        *args, **kwargs
    ) -> Response:
        """Delete a review (only by the owner)"""
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {'detail': 'Review not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not IsOwnerOrAdmin().has_object_permission(request, self, review):
            return Response(
                {'detail': 'You do not have permission to delete this review.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RatingViewSet(ViewSet):
    """
    ViewSet for handling Rating-related endpoints.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get list of all ratings",
        description="Returns a list of all ratings (optionally filtered by movie_id)",
        tags=['Ratings'],
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Movie ID for filtering',
                required=False
            ),
        ],
        responses={200: RatingDetailSerializer(many=True)}
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="list",
        url_name="rating-list"
    )
    def list_ratings(
        self, 
        request: HttpRequest, 
        *args, **kwargs
    ) -> Response:
        """Get all ratings (optionally filter by movie_id)"""
        movie_id = request.query_params.get('movie_id')
        
        if movie_id:
            ratings = Rating.objects.filter(movie_id=movie_id)
        else:
            ratings = Rating.objects.all()
        
        serializer = RatingDetailSerializer(ratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Rate a movie (create or update)",
        description="Creates or updates a movie rating",
        tags=['Ratings'],
        request=RatingDetailSerializer,
        responses={
            200: RatingDetailSerializer,
            400: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="rate",
        url_name="rating-create"
    )
    def create_or_update_rating(
        self, 
        request: HttpRequest, 
        *args, **kwargs
    ) -> Response:
        """Rate a movie (creates or updates existing rating)"""
        serializer = RatingDetailSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Delete a rating",
        description="Deletes a movie rating (owner only)",
        tags=['Ratings'],
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Rating ID',
                required=True
            ),
        ],
        responses={
            204: None,
            404: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["DELETE"],
        detail=True,
        url_path="delete",
        url_name="rating-delete"
    )
    def delete_rating(
        self, 
        request: HttpRequest,
        pk: int = None,
        *args, **kwargs
    ) -> Response:
        """Delete a rating (only by the owner)"""
        try:
            rating = Rating.objects.get(id=pk)
        except Rating.DoesNotExist:
            return Response(
                {'detail': 'Rating not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not IsOwnerOrAdmin().has_object_permission(request, self, rating):
            return Response(
                {'detail': 'You do not have permission to delete this rating.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(ViewSet):
    """
    ViewSet for handling Favorite-related endpoints.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get list of favorite movies",
        description="Returns a list of favorite movies for the current user",
        tags=['Favorites'],
        responses={200: FavoriteSerializer(many=True)}
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="list",
        url_name="favorite-list"
    )
    def list_favorites(
        self, 
        request: HttpRequest, 
        *args, **kwargs
    ) -> Response:
        """Get all favorite movies for the current user"""
        from .pagination import StandardResultsSetPagination
        
        favorites = Favorite.objects.filter(user=request.user).select_related('movie').order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_favorites = paginator.paginate_queryset(favorites, request)
        
        serializer = FavoriteSerializer(paginated_favorites, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Add movie to favorites",
        description="Adds a movie to the current user's favorites list",
        tags=['Favorites'],
        request=FavoriteSerializer,
        responses={
            201: FavoriteSerializer,
            400: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="add",
        url_name="favorite-add"
    )
    def add_favorite(
        self, 
        request: HttpRequest, 
        *args, **kwargs
    ) -> Response:
        """Add a movie to favorites"""
        serializer = FavoriteSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if already favorited
            movie_id = serializer.validated_data.get('movie_id')
            if Favorite.objects.filter(
                user=request.user, 
                movie_id=movie_id
            ).exists():
                return Response(
                    {'detail': 'Movie already in favorites.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(user=request.user)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Remove movie from favorites",
        description="Removes a movie from the current user's favorites list",
        tags=['Favorites'],
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Favorite record ID',
                required=True
            ),
        ],
        responses={
            204: None,
            404: ErrorResponseSerializer,
        }
    )
    @action(
        methods=["DELETE"],
        detail=True,
        url_path="remove",
        url_name="favorite-remove"
    )
    def remove_favorite(
        self, 
        request: HttpRequest,
        pk: int = None,
        *args, **kwargs
    ) -> Response:
        """Remove a movie from favorites"""
        try:
            favorite = Favorite.objects.get(id=pk)
        except Favorite.DoesNotExist:
            return Response(
                {'detail': 'Favorite not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not IsOwnerOrAdmin().has_object_permission(request, self, favorite):
            return Response(
                {'detail': 'You do not have permission to remove this favorite.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class MovieSearchPagination(PageNumberPagination):
    """Custom pagination for movie search results"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class MovieSearchView(APIView):
    """
    Advanced movie search view with filtering and pagination.
    
    Supports filtering by:
        - query: Search by title and description (case-insensitive)
        - genre: Filter by genre (exact match)
        - year_from: Minimum release year
        - year_to: Maximum release year
        - ordering: Sort order (default: -created_at)
        - page: Page number for pagination
        - page_size: Number of results per page (default: 10, max: 50)
    """
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from .pagination import StandardResultsSetPagination
        self.pagination_class = StandardResultsSetPagination
    
    @extend_schema(
        summary="Search movies",
        description="""
        Search movies with various filters.
        
        Supported parameters:
        - query: Search by title and description (case-insensitive)
        - genre: Filter by genre (exact match)
        - year_from: Minimum release year
        - year_to: Maximum release year
        - ordering: Sort order for results
        - page: Page number for pagination
        - page_size: Number of results per page (default: 10, max: 50)
        """,
        tags=['Movies'],
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=False
            ),
            OpenApiParameter(
                name='genre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Movie genre',
                required=False
            ),
            OpenApiParameter(
                name='year_from',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Minimum release year',
                required=False
            ),
            OpenApiParameter(
                name='year_to',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum release year',
                required=False
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Sort order',
                required=False,
                enum=['title', '-title', 'year', '-year', 'average_rating', '-average_rating', 'created_at', '-created_at']
            ),
        ],
        responses={
            200: MovieSerializer(many=True),
            400: ErrorResponseSerializer,
        }
    )
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Search movies based on query parameters.
        
        Returns:
            - Paginated list of movies matching search criteria
        """
        search_serializer = MovieSearchSerializer(data=request.query_params)
        if not search_serializer.is_valid():
            return Response(
                search_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = search_serializer.validated_data
        query = validated_data.get('query', '').strip()
        genre = validated_data.get('genre', '').strip()
        year_from = validated_data.get('year_from')
        year_to = validated_data.get('year_to')
        ordering = validated_data.get('ordering', '-created_at')
        movies = Movie.objects.annotate(
            avg_rating=Avg('ratings__score')
        )

        if query:
            movies = movies.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        
        if genre:
            movies = movies.filter(genre__iexact=genre)
        
        if year_from:
            movies = movies.filter(year__gte=year_from)
        
        if year_to:
            movies = movies.filter(year__lte=year_to)
        if ordering in ['average_rating', '-average_rating']:
            ordering = ordering.replace('average_rating', 'avg_rating')
        
        movies = movies.order_by(ordering)[:100]  
        
        paginator = self.pagination_class()
        paginated_movies = paginator.paginate_queryset(movies, request)
        
        serializer = MovieSerializer(
            paginated_movies, many=True, context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)
