from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    MovieListView,
    MovieDetailView,
    MovieVideoUploadView,
    CommentView,
    LikeView,
    RatingView,
    ReviewViewSet,
    RatingViewSet,
    FavoriteViewSet,
    MovieSearchView,
)

app_name = "movies"

router = DefaultRouter()

urlpatterns = [
    path("", MovieListView.as_view(), name="movie-list"),
    path("search/", MovieSearchView.as_view(), name="movie-search"),
    path("<int:movie_id>/", MovieDetailView.as_view(), name="movie-detail"),
    path("<int:movie_id>/video/", MovieVideoUploadView.as_view(), name="movie-video"),
    path("<int:movie_id>/comments/", CommentView.as_view(), name="movie-comments"),
    path("<int:movie_id>/rate/", RatingView.as_view(), name="movie-rate"),
    path("like/", LikeView.as_view(), name="like-object"),
    path(
        "reviews/list/",
        ReviewViewSet.as_view({"get": "list_reviews"}),
        name="review-list",
    ),
    path(
        "reviews/create/",
        ReviewViewSet.as_view({"post": "create_review"}),
        name="review-create",
    ),
    path(
        "reviews/<int:pk>/detail/",
        ReviewViewSet.as_view({"get": "retrieve_review"}),
        name="review-detail",
    ),
    path(
        "reviews/<int:pk>/update/",
        ReviewViewSet.as_view({"put": "update_review", "patch": "update_review"}),
        name="review-update",
    ),
    path(
        "reviews/<int:pk>/delete/",
        ReviewViewSet.as_view({"delete": "delete_review"}),
        name="review-delete",
    ),
    path(
        "ratings/list/",
        RatingViewSet.as_view({"get": "list_ratings"}),
        name="rating-list",
    ),
    path(
        "ratings/rate/",
        RatingViewSet.as_view({"post": "create_or_update_rating"}),
        name="rating-create",
    ),
    path(
        "ratings/<int:pk>/delete/",
        RatingViewSet.as_view({"delete": "delete_rating"}),
        name="rating-delete",
    ),
    path(
        "favorites/list/",
        FavoriteViewSet.as_view({"get": "list_favorites"}),
        name="favorite-list",
    ),
    path(
        "favorites/add/",
        FavoriteViewSet.as_view({"post": "add_favorite"}),
        name="favorite-add",
    ),
    path(
        "favorites/<int:pk>/remove/",
        FavoriteViewSet.as_view({"delete": "remove_favorite"}),
        name="favorite-remove",
    ),
]
