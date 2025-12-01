# Third-party modules
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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
    MovieSearchSerializer
)

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
        
        movies: QuerySet[Movie] = Movie.objects.annotate(
            average_rating=Avg('ratings__score'),
            likes_count=Count('likes', distinct=True)
        )
        serializer: MovieSerializer = MovieSerializer(
            movies, many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class MovieDetailView(APIView):
    """
    View to retrieve a specific movie.
    Only authenticated users can access.
    """
    permission_classes = [IsAuthenticated]

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
                average_rating=Avg('ratings__score')
            ).get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Movie not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer: MovieSerializer = MovieSerializer(movie)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CommentView(APIView):
    """
    View for listing and creating comments under a specific movie.
    Only authenticated users can access.
    """
    permission_classes = [IsAuthenticated]

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
        comments: QuerySet[Comment] = Comment.objects.filter(
            movie_id=movie_id, parent=None
        )
        serializer: CommentSerializer = CommentSerializer(
            comments, many=True
        )
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
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
        existing_like: Optional[Like] = Like.objects.filter(
            user=user, 
            content_type=ct, 
            object_id=object_id
        ).first()

        if existing_like:
            existing_like.delete()
            return Response(
                {"detail": f"{content_type_str.capitalize()} unliked."},
                status=status.HTTP_200_OK
            )

        Like.objects.create(
            user=user, 
            content_type=ct, 
            object_id=object_id
        )
        return Response(
            {"detail": f"{content_type_str.capitalize()} liked."},
            status=status.HTTP_201_CREATED
        )


class RatingView(APIView):
    """
    View to rate a movie or update the rating.
    """
    permission_classes = [IsAuthenticated]

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
from drf_spectacular.utils import extend_schema, OpenApiResponse

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
        summary="List all reviews",
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
        movie_id = request.query_params.get('movie_id')
        
        if movie_id:
            reviews = Review.objects.filter(movie_id=movie_id)
        else:
            reviews = Review.objects.all()
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new review",
        request=ReviewSerializer,
        responses={201: ReviewSerializer}
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
        responses={200: ReviewSerializer}
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
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {'detail': 'Review not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a review",
        request=ReviewSerializer,
        responses={200: ReviewSerializer}
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
            review = Review.objects.get(id=pk, user=request.user)
        except Review.DoesNotExist:
            return Response(
                {'detail': 'Review not found or you do not have permission.'},
                status=status.HTTP_404_NOT_FOUND
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
        responses={204: None}
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
            review = Review.objects.get(id=pk, user=request.user)
        except Review.DoesNotExist:
            return Response(
                {'detail': 'Review not found or you do not have permission.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RatingViewSet(ViewSet):
    """
    ViewSet for handling Rating-related endpoints.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all ratings",
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
        summary="Create or update a rating",
        request=RatingDetailSerializer,
        responses={200: RatingDetailSerializer}
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
        responses={204: None}
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
            rating = Rating.objects.get(id=pk, user=request.user)
        except Rating.DoesNotExist:
            return Response(
                {'detail': 'Rating not found or you do not have permission.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(ViewSet):
    """
    ViewSet for handling Favorite-related endpoints.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List user's favorite movies",
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
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Add movie to favorites",
        request=FavoriteSerializer,
        responses={201: FavoriteSerializer}
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
        responses={204: None}
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
            favorite = Favorite.objects.get(id=pk, user=request.user)
        except Favorite.DoesNotExist:
            return Response(
                {'detail': 'Favorite not found.'},
                status=status.HTTP_404_NOT_FOUND
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
    View for searching movies with various filters.
    
    Query parameters:
        - query: Search in title and description (case-insensitive)
        - genre: Filter by exact genre match
        - year_from: Minimum release year
        - year_to: Maximum release year
        - ordering: Sort order (default: -created_at)
        - page: Page number for pagination
        - page_size: Number of results per page (default: 10, max: 50)
    """
    
    permission_classes = [AllowAny]
    pagination_class = MovieSearchPagination
    
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
        
        movies = movies.order_by(ordering)
        
        paginator = self.pagination_class()
        paginated_movies = paginator.paginate_queryset(movies, request)
        
        serializer = MovieSerializer(paginated_movies, many=True)
        
        return paginator.get_paginated_response(serializer.data)