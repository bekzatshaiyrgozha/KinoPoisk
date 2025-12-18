# Django modules
from django.db.models import Avg, Count, Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

# Django Third-party modules
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
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
from drf_spectacular.utils import extend_schema

# Project modules
from apps.movies.models import Movie, Comment, Like, Rating, Review, Favorite
from apps.movies.serializers import (
    MovieSerializer,
    CommentSerializer,
    RatingSerializer,
    MovieSearchSerializer,
    MovieVideoUploadSerializer,
    ReviewSerializer,
    RatingDetailSerializer,
    FavoriteSerializer,
)
from apps.movies.serializers_requests import (
    MovieSearchRequestSerializer,
    CommentRequestSerializer,
    RatingRequestSerializer,
    LikeToggleRequestSerializer,
    ReviewRequestSerializer,
    RatingDetailRequestSerializer,
    FavoriteRequestSerializer,
    VideoUploadRequestSerializer,
)
from apps.movies.serializers_responses import (
    MovieSuccessResponseSerializer,
    MovieListSuccessResponseSerializer,
    CommentSuccessResponseSerializer,
    CommentListSuccessResponseSerializer,
    RatingSuccessResponseSerializer,
    ReviewSuccessResponseSerializer,
    ReviewListSuccessResponseSerializer,
    RatingDetailSuccessResponseSerializer,
    RatingDetailListSuccessResponseSerializer,
    FavoriteSuccessResponseSerializer,
    FavoriteListSuccessResponseSerializer,
)
from apps.movies.pagination import StandardResultsSetPagination
from apps.abstracts.serializers import (
    ErrorResponseSerializer,
    UnauthorizedResponseSerializer,
    NotFoundResponseSerializer,
    ForbiddenResponseSerializer,
    MethodNotAllowedResponseSerializer,
)
from apps.accounts.permissions import IsOwnerOrAdmin

User = get_user_model()


class MovieViewSet(ViewSet):
    """ViewSet for managing movies."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            HTTP_200_OK: MovieListSuccessResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(methods=["GET"], detail=False, url_path="list")
    def list_movies(self, request):
        movies = Movie.objects.annotate(
            average_rating=Avg("ratings__score"),
            likes_count=Count("likes", distinct=True),
        ).all()

        paginator = StandardResultsSetPagination()
        paginated_movies = paginator.paginate_queryset(movies, request)
        serializer = MovieSerializer(
            paginated_movies, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        responses={
            HTTP_200_OK: MovieSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(
        methods=["GET"],
        detail=True,
        url_path="detail",
        permission_classes=[IsAuthenticated],
    )
    def retrieve_movie(self, request, pk=None):
        try:
            movie = Movie.objects.annotate(
                average_rating=Avg("ratings__score"),
                likes_count=Count("likes", distinct=True),
            ).get(id=pk)
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "message": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = MovieSerializer(movie, context={"request": request})
        return Response(
            {"success": True, "data": serializer.data},
            status=HTTP_200_OK,
        )

    @extend_schema(
        request=MovieSearchRequestSerializer,
        responses={
            HTTP_200_OK: MovieListSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="search",
        permission_classes=[IsAuthenticated],
    )
    def search_movies(self, request):
        serializer = MovieSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
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
        serializer = MovieSerializer(
            paginated_movies, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=VideoUploadRequestSerializer,
        responses={
            HTTP_201_CREATED: MovieSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_403_FORBIDDEN: ForbiddenResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(
        methods=["PUT", "POST"],
        detail=True,
        url_path="video",
        permission_classes=[IsAdminUser],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_video(self, request, pk=None):
        try:
            movie = Movie.objects.get(id=pk)
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "message": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = MovieVideoUploadSerializer(movie, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Video uploaded successfully",
                "data": MovieSerializer(movie, context={"request": request}).data,
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        responses={
            HTTP_200_OK: CommentListSuccessResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(
        methods=["GET"],
        detail=True,
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def get_comments(self, request, pk=None):
        comments = (
            Comment.objects.filter(movie_id=pk, parent=None)
            .select_related("user", "movie")
            .prefetch_related("replies__user")
            .annotate(likes_count=Count("likes", distinct=True))
        )

        paginator = StandardResultsSetPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(
            paginated_comments, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=CommentRequestSerializer,
        responses={
            HTTP_201_CREATED: CommentSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def create_comment(self, request, pk=None):
        try:
            movie = Movie.objects.get(id=pk)
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "message": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user, movie=movie)
        return Response(
            {
                "success": True,
                "message": "Comment created successfully",
                "data": serializer.data,
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        request=RatingRequestSerializer,
        responses={
            HTTP_201_CREATED: RatingSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="rate",
        permission_classes=[IsAuthenticated],
    )
    def rate_movie(self, request, pk=None):
        try:
            movie = Movie.objects.get(id=pk)
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "message": "Movie not found"},
                status=HTTP_404_NOT_FOUND,
            )

        score = request.data.get("score")
        if score is None or not (1 <= int(score) <= 5):
            return Response(
                {"success": False, "message": "Score must be between 1 and 5"},
                status=HTTP_400_BAD_REQUEST,
            )

        rating, _ = Rating.objects.update_or_create(
            user=request.user, movie=movie, defaults={"score": score}
        )
        serializer = RatingSerializer(rating)
        return Response(
            {
                "success": True,
                "message": "Rating saved successfully",
                "data": serializer.data,
            },
            status=HTTP_200_OK,
        )


class LikeViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LikeToggleRequestSerializer,
        responses={
            HTTP_200_OK: ErrorResponseSerializer,
            HTTP_201_CREATED: ErrorResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    @action(methods=["POST"], detail=False, url_path="toggle")
    def toggle_like(self, request):
        content_type_str = request.data.get("content_type")
        object_id = request.data.get("object_id")

        if not content_type_str or not object_id:
            return Response(
                {
                    "success": False,
                    "message": "content_type and object_id are required",
                },
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            ct = ContentType.objects.get(model=content_type_str)
        except ContentType.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid content_type"},
                status=HTTP_400_BAD_REQUEST,
            )

        obj_model = ct.model_class()
        try:
            obj_model.objects.get(id=object_id)
        except obj_model.DoesNotExist:
            return Response(
                {"success": False, "message": "Object not found"},
                status=HTTP_404_NOT_FOUND,
            )

        existing_like = Like.objects.filter(
            user=request.user, content_type=ct, object_id=object_id
        ).first()

        if existing_like:
            existing_like.delete()
            likes_count = Like.objects.filter(
                content_type=ct, object_id=object_id
            ).count()
            return Response(
                {"success": True, "liked": False, "likes_count": likes_count},
                status=HTTP_200_OK,
            )

        soft_deleted_like = Like.all_objects.filter(
            user=request.user,
            content_type=ct,
            object_id=object_id,
            deleted_at__isnull=False,
        ).first()

        if soft_deleted_like:
            soft_deleted_like.deleted_at = None
            soft_deleted_like.save(update_fields=["deleted_at"])
        else:
            Like.objects.create(user=request.user, content_type=ct, object_id=object_id)

        likes_count = Like.objects.filter(content_type=ct, object_id=object_id).count()
        return Response(
            {"success": True, "liked": True, "likes_count": likes_count},
            status=HTTP_201_CREATED,
        )


class ReviewViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            HTTP_200_OK: ReviewListSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def list(self, request):
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
        request=ReviewRequestSerializer,
        responses={
            HTTP_201_CREATED: ReviewSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def create(self, request):
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Review created successfully",
                "data": serializer.data,
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        responses={
            HTTP_200_OK: ReviewSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def retrieve(self, request, pk=None):
        try:
            review = Review.objects.select_related("user", "movie").get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {"success": False, "message": "Review not found"},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = ReviewSerializer(review)
        return Response(
            {"success": True, "data": serializer.data},
            status=HTTP_200_OK,
        )

    @extend_schema(
        request=ReviewRequestSerializer,
        responses={
            HTTP_200_OK: ReviewSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_403_FORBIDDEN: ForbiddenResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def partial_update(self, request, pk=None):
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {"success": False, "message": "Review not found"},
                status=HTTP_404_NOT_FOUND,
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, review):
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to update this review",
                },
                status=HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Review updated successfully",
                "data": serializer.data,
            },
            status=HTTP_200_OK,
        )

    @extend_schema(
        responses={
            HTTP_200_OK: ReviewSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_403_FORBIDDEN: ForbiddenResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def destroy(self, request, pk=None):
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {"success": False, "message": "Review not found"},
                status=HTTP_404_NOT_FOUND,
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, review):
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to delete this review",
                },
                status=HTTP_403_FORBIDDEN,
            )

        review.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RatingViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            HTTP_200_OK: RatingDetailListSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def list(self, request):
        movie_id = request.query_params.get("movie_id")
        if movie_id:
            ratings = Rating.objects.filter(movie_id=movie_id)
        else:
            ratings = Rating.objects.all()

        serializer = RatingDetailSerializer(ratings, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=HTTP_200_OK,
        )

    @extend_schema(
        request=RatingDetailRequestSerializer,
        responses={
            HTTP_200_OK: RatingDetailSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def create(self, request):
        serializer = RatingDetailSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Rating saved successfully",
                "data": serializer.data,
            },
            status=HTTP_200_OK,
        )

    @extend_schema(
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_403_FORBIDDEN: ForbiddenResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def destroy(self, request, pk=None):
        try:
            rating = Rating.objects.get(id=pk)
        except Rating.DoesNotExist:
            return Response(
                {"success": False, "message": "Rating not found"},
                status=HTTP_404_NOT_FOUND,
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, rating):
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to delete this rating",
                },
                status=HTTP_403_FORBIDDEN,
            )

        rating.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class FavoriteViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            HTTP_200_OK: FavoriteListSuccessResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def list(self, request):
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
        request=FavoriteRequestSerializer,
        responses={
            HTTP_201_CREATED: FavoriteSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def create(self, request):
        serializer = FavoriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=HTTP_400_BAD_REQUEST,
            )

        movie_id = serializer.validated_data.get("movie_id")
        if Favorite.objects.filter(user=request.user, movie_id=movie_id).exists():
            return Response(
                {"success": False, "message": "Movie already in favorites"},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Movie added to favorites",
                "data": serializer.data,
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_401_UNAUTHORIZED: UnauthorizedResponseSerializer,
            HTTP_403_FORBIDDEN: ForbiddenResponseSerializer,
            HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowedResponseSerializer,
        },
    )
    def destroy(self, request, pk=None):
        try:
            favorite = Favorite.objects.get(id=pk)
        except Favorite.DoesNotExist:
            return Response(
                {"success": False, "message": "Favorite not found"},
                status=HTTP_404_NOT_FOUND,
            )

        if not IsOwnerOrAdmin().has_object_permission(request, self, favorite):
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to remove this favorite",
                },
                status=HTTP_403_FORBIDDEN,
            )

        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)
