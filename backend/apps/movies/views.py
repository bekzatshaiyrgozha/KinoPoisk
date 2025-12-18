# Python modules
from typing import Any, Optional

# Django modules
from django.db.models import QuerySet, Avg, Count, Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

# Third-party modules
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Project modules
from .models import Movie, Comment, Like, Rating, Review, Favorite
from .serializers import (
    MovieSerializer,
    CommentSerializer,
    RatingSerializer,
    MovieSearchSerializer,
    MovieVideoUploadSerializer,
    ReviewSerializer,
    RatingDetailSerializer,
    FavoriteSerializer,
)
from .pagination import StandardResultsSetPagination
from apps.abstracts.serializers import (
    ErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)
from apps.accounts.permissions import IsOwnerOrAdmin

# Typing imports
from django.contrib.contenttypes.models import ContentType as ContentTypeModel
from django.db.models.base import ModelBase

User: type = get_user_model()


class MovieViewSet(ViewSet):
    """
    Docstring for MovieViewSet
    """

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Get list of all movies",
        description="Returns a list of all movies with average rating and likes count",
        tags=["Movies"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="List of all movies",
                response=MovieSerializer(many=True),
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("GET",),
        detail=False,
        url_path="list",
        url_name="movie-list",
    )
    def list_movies(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to list movies.
        """
        movies: QuerySet[Movie] = Movie.objects.annotate(
            average_rating=Avg("ratings__score"),
            likes_count=Count("likes", distinct=True),
        ).all()

        paginator = StandardResultsSetPagination()
        paginated_movies = paginator.paginate_queryset(movies, request)

        serializer: MovieSerializer = MovieSerializer(
            paginated_movies, many=True, context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Get movie details",
        description="Returns detailed information about a specific movie by ID",
        tags=["Movies"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Movie details",
                response=MovieSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Movie not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("GET",),
        detail=True,
        url_path="detail",
        url_name="movie-detail",
        permission_classes=(IsAuthenticated,),
    )
    def retrieve_movie(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle GET requests to retrieve a specific movie by ID.
        """

        try:
            movie: Movie = Movie.objects.annotate(
                average_rating=Avg("ratings__score"),
                likes_count=Count("likes", distinct=True),
            ).get(id=pk)
        except Movie.DoesNotExist:
            return DRFResponse(
                data={"detail": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        serializer: MovieSerializer = MovieSerializer(
            movie, context={"request": request}
        )
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="Search movies",
        description="searching the movie with different filters",
        tags=["Movies"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Search results", response=MovieSearchSerializer(many=True)
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("GET",),
        detail=False,
        url_path="search",
        url_name="movie-search",
    )
    def search_movies(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to search movies.
        """
        search_serializer: MovieSearchSerializer = MovieSearchSerializer(
            data=request.query_params
        )

        if not search_serializer.is_valid():
            return DRFResponse(
                data=search_serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )
        validated_data = search_serializer.validated_data
        query = validated_data.get("query", "").strip()
        genre = validated_data.get("genre", "").strip()
        year_from = validated_data.get("year_from")
        year_to = validated_data.get("year_to")
        ordering = validated_data.get("ordering", "-created_at")

        movies = Movie.objects.annotate(avg_rating=Avg("ratings__score"))

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

        if ordering in ["average_rating", "-average_rating"]:
            ordering = ordering.replace("average_rating", "avg_rating")

        movies = movies.order_by(ordering)[:100]

        paginator = StandardResultsSetPagination()

        paginated_movies = paginator.paginate_queryset(movies, request)

        seralizer = MovieSerializer(
            paginated_movies,
            many=True,
            context={"request": request},
        )
        return paginator.get_paginated_response(seralizer.data)

    @extend_schema(
        summary="Upload/replace movie video",
        description="Uploads or replace the video file of the given movie",
        tags=["Movies"],
        request=MovieVideoUploadSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Video uploaded sucessfully",
                response=MovieSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ValidationErrorResponseSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Movie not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("PUT", "POST"),
        detail=True,
        url_path="video",
        url_name="upload-video",
        permission_classes=(IsAdminUser,),
        parser_classes=(MultiPartParser, FormParser),
    )
    def upload_video(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handling the PUT/POST requests to upload movie video
        """
        try:
            movie: Movie = Movie.objects.get(id=pk)
        except Movie.DoesNotExist:
            return DRFResponse(
                data={"detail": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = MovieVideoUploadSerializer(movie, data=request.data, partial=True)
        if not serializer.is_valid():
            return DRFResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save()

        return DRFResponse(
            data=MovieSerializer(movie, context={"request": request}).data,
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="Get movie comments",
        description="Returns a list of all comments for a movie includes replies",
        tags=["Comments"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="List of all comments",
                response=CommentSerializer(many=True),
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("GET",),
        detail=True,
        url_path="comments",
        url_name="movie-comments",
        permission_classes=(IsAuthenticated,),
    )
    def get_comments(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handles get requests to retrieve movie comments for a specific movie
        """

        comments: QuerySet[Comment] = (
            Comment.objects.filter(movie_id=pk, parent=None)
            .select_related("user", "movie")
            .prefetch_related("replies__user")
            .annotate(likes_count=Count("likes", distinct=True))
        )

        paginator = StandardResultsSetPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)

        serializer: CommentSerializer = CommentSerializer(
            paginated_comments, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create  movie comment",
        description="Creates a new comment for a movie ",
        tags=["Comments"],
        request=CommentSerializer,
        responses={
            HTTP_201_CREATED: OpenApiResponse(
                description="Comment created",
                response=CommentSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request", response=ValidationErrorResponseSerializer
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Movie not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("POST",),
        detail=True,
        url_path="comments",
        url_name="create-comment",
        permission_classes=(IsAuthenticated,),
    )
    def create_comment(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handling POST requests to create a new comment for a specific movie
        """
        try:
            movie: Movie = Movie.objects.get(id=pk)
        except Movie.DoesNotExist:
            return DRFResponse(
                data={"detail": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )
        serializer: CommentSerializer = CommentSerializer(data=request.data)

        if not serializer.is_valid():
            return DRFResponse(
                data=serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=request.user, movie=movie)
        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Rate a movie",
        description="Rates a movie (score from 1 to 5) or updates an existing rating",
        tags=["Ratings"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Rating sucessful",
                response=RatingSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ValidationErrorResponseSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Movie not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("POST",),
        detail=True,
        url_path="rate",
        url_name="rate-movie",
        permission_classes=(IsAuthenticated,),
    )
    def rate_movie(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handling POST requests to rate a specific movie
        """
        try:
            movie: Movie = Movie.objects.get(id=pk)
        except Movie.DoesNotExist:
            return DRFResponse(
                data={"detail": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        score: Optional[int] = request.data.get("score")

        if score is None or not (1 <= int(score) <= 5):
            return DRFResponse(
                data={"detail": "Score must be between 1 and 5"},
                status=HTTP_400_BAD_REQUEST,
            )
        rating, _ = Rating.objects.update_or_create(
            user=request.user, movie=movie, defaults={"score": score}
        )
        serializer: RatingSerializer = RatingSerializer(rating)

        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )


class LikeViewSet(ViewSet):
    """
    ViewSet for handling Like-related endpoints.
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Like/Unlike object",
        description="Likes or unlikes an object (movie or comment)",
        tags=["Likes"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Unliked successfully",
            ),
            HTTP_201_CREATED: OpenApiResponse(
                description="Liked successfully",
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Object not found",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="toggle",
        url_name="toggle-like",
    )
    def toggle_like(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle POST requests to like or unlike an object.
        """
        content_type_str: Optional[str] = request.data.get("content_type")
        object_id: Optional[int] = request.data.get("object_id")

        if not content_type_str or not object_id:
            return DRFResponse(
                data={"detail": "content_type and object_id are required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            ct: ContentTypeModel = ContentType.objects.get(model=content_type_str)
        except ContentType.DoesNotExist:
            return DRFResponse(
                data={"detail": "Invalid content_type."}, status=HTTP_400_BAD_REQUEST
            )

        obj_model: type[ModelBase] = ct.model_class()

        try:
            obj_model.objects.get(id=object_id)
        except obj_model.DoesNotExist:
            return DRFResponse(
                data={"detail": "Object not found."}, status=HTTP_404_NOT_FOUND
            )

        user: User = request.user

        existing_like: Optional[Like] = Like.objects.filter(
            user=user, content_type=ct, object_id=object_id
        ).first()

        if existing_like:
            existing_like.delete()
            likes_count = Like.objects.filter(
                content_type=ct, object_id=object_id
            ).count()

            return DRFResponse(
                data={"liked": False, "likes_count": likes_count}, status=HTTP_200_OK
            )

        soft_deleted_like: Optional[Like] = Like.all_objects.filter(
            user=user, content_type=ct, object_id=object_id, deleted_at__isnull=False
        ).first()

        if soft_deleted_like:
            soft_deleted_like.deleted_at = None
            soft_deleted_like.save(update_fields=["deleted_at"])
        else:
            Like.objects.create(user=user, content_type=ct, object_id=object_id)

        likes_count = Like.objects.filter(content_type=ct, object_id=object_id).count()

        return DRFResponse(
            data={"liked": True, "likes_count": likes_count}, status=HTTP_201_CREATED
        )


class ReviewViewSet(ViewSet):
    """
    ViewSet for handling Review-related endpoints.
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Get list of all reviews",
        description="Returns a list of all reviews (optionally filtered by movie_id)",
        tags=["Reviews"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="List of reviews",
                response=ReviewSerializer(many=True),
            ),
        },
    )
    def list(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to list reviews.
        """
        movie_id = request.query_params.get("movie_id")

        if movie_id:
            reviews = Review.objects.filter(movie_id=movie_id)
        else:
            reviews = Review.objects.all()

        reviews = reviews.select_related("user", "movie").order_by("-created_at")

        paginator = StandardResultsSetPagination()
        paginated_reviews = paginator.paginate_queryset(reviews, request)

        serializer = ReviewSerializer(paginated_reviews, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create a new review",
        description="Creates a new review for a movie",
        tags=["Reviews"],
        request=ReviewSerializer,
        responses={
            HTTP_201_CREATED: OpenApiResponse(
                description="Review created",
                response=ReviewSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def create(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle POST requests to create a new review.
        """
        serializer = ReviewSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return DRFResponse(data=serializer.data, status=HTTP_201_CREATED)

    @extend_schema(
        summary="Get review details",
        description="Returns detailed information about a review by ID",
        tags=["Reviews"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Review details",
                response=ReviewSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Review not found",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def retrieve(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle GET requests to retrieve a specific review.
        """
        try:
            review = Review.objects.select_related("user", "movie").get(id=pk)
        except Review.DoesNotExist:
            return DRFResponse(
                data={"detail": "Review not found."}, status=HTTP_404_NOT_FOUND
            )

        serializer = ReviewSerializer(review)

        return DRFResponse(data=serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Update a review",
        description="Updates an existing review (owner only)",
        tags=["Reviews"],
        request=ReviewSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Review updated",
                response=ReviewSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Review not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def partial_update(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle PATCH requests to partially update a review.
        """
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return DRFResponse(
                data={"detail": "Review not found."}, status=HTTP_404_NOT_FOUND
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, review):
            return DRFResponse(
                data={"detail": "You do not have permission to update this review."},
                status=HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(review, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(data=serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Delete a review",
        description="Deletes a review (owner only)",
        tags=["Reviews"],
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Review deleted",
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Review not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def destroy(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle DELETE requests to delete a review.
        """
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return DRFResponse(
                data={"detail": "Review not found."}, status=HTTP_404_NOT_FOUND
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, review):
            return DRFResponse(
                data={"detail": "You do not have permission to delete this review."},
                status=HTTP_403_FORBIDDEN,
            )

        review.delete()

        return DRFResponse(status=HTTP_204_NO_CONTENT)


class RatingViewSet(ViewSet):
    """
    ViewSet for handling Rating-related endpoints.
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Get list of all ratings",
        description="Returns a list of all ratings (optionally filtered by movie_id)",
        tags=["Ratings"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="List of ratings",
                response=RatingDetailSerializer(many=True),
            ),
        },
    )
    def list(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to list ratings.
        """
        movie_id = request.query_params.get("movie_id")

        if movie_id:
            ratings = Rating.objects.filter(movie_id=movie_id)
        else:
            ratings = Rating.objects.all()

        serializer = RatingDetailSerializer(ratings, many=True)

        return DRFResponse(data=serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Rate a movie (create or update)",
        description="Creates or updates a movie rating",
        tags=["Ratings"],
        request=RatingDetailSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Rating successful",
                response=RatingDetailSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def create(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle POST requests to create or update a rating.
        """
        serializer = RatingDetailSerializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(data=serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Delete a rating",
        description="Deletes a movie rating (owner only)",
        tags=["Ratings"],
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Rating deleted",
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Rating not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def destroy(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle DELETE requests to delete a rating.
        """
        try:
            rating = Rating.objects.get(id=pk)
        except Rating.DoesNotExist:
            return DRFResponse(
                data={"detail": "Rating not found."}, status=HTTP_404_NOT_FOUND
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, rating):
            return DRFResponse(
                data={"detail": "You do not have permission to delete this rating."},
                status=HTTP_403_FORBIDDEN,
            )

        rating.delete()

        return DRFResponse(status=HTTP_204_NO_CONTENT)


class FavoriteViewSet(ViewSet):
    """
    ViewSet for handling Favorite-related endpoints.
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Get list of favorite movies",
        description="Returns a list of favorite movies for the current user",
        tags=["Favorites"],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="List of favorites",
                response=FavoriteSerializer(many=True),
            ),
        },
    )
    def list(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to list favorite movies.
        """
        favorites = (
            Favorite.objects.filter(user=request.user)
            .select_related("movie")
            .order_by("-created_at")
        )

        paginator = StandardResultsSetPagination()
        paginated_favorites = paginator.paginate_queryset(favorites, request)

        serializer = FavoriteSerializer(paginated_favorites, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Add movie to favorites",
        description="Adds a movie to the current user's favorites list",
        tags=["Favorites"],
        request=FavoriteSerializer,
        responses={
            HTTP_201_CREATED: OpenApiResponse(
                description="Favorite added",
                response=FavoriteSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def create(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle POST requests to add a movie to favorites.
        """
        serializer = FavoriteSerializer(data=request.data)

        if not serializer.is_valid():
            return DRFResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        movie_id = serializer.validated_data.get("movie_id")
        if Favorite.objects.filter(user=request.user, movie_id=movie_id).exists():
            return DRFResponse(
                data={"detail": "Movie already in favorites."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user)

        return DRFResponse(data=serializer.data, status=HTTP_201_CREATED)

    @extend_schema(
        summary="Remove movie from favorites",
        description="Removes a movie from the current user's favorites list",
        tags=["Favorites"],
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Favorite removed",
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Favorite not found",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Permission denied",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def destroy(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle DELETE requests to remove a movie from favorites.
        """
        try:
            favorite = Favorite.objects.get(id=pk)
        except Favorite.DoesNotExist:
            return DRFResponse(
                data={"detail": "Favorite not found."}, status=HTTP_404_NOT_FOUND
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, favorite):
            return DRFResponse(
                data={"detail": "You do not have permission to remove this favorite."},
                status=HTTP_403_FORBIDDEN,
            )

        favorite.delete()

        return DRFResponse(status=HTTP_204_NO_CONTENT)
