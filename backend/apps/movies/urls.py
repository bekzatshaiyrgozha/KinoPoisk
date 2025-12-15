#Django modules 
from django.urls import path 

#Project modules 
from .views import(
    MovieViewSet,
    LikeViewSet,
    ReviewViewSet,
    RatingViewSet,
    FavoriteViewSet,
)

app_name="movies"

urlpatterns=[
    #Movie endpoints
     path(route="", view=MovieViewSet.as_view({"get": "list_movies"}), name="movie-list"),
    path(route="search/", view=MovieViewSet.as_view({"get": "search_movies"}), name="movie-search"),
    path(route="<int:pk>/", view=MovieViewSet.as_view({"get": "retrieve_movie"}), name="movie-detail"),
    path(route="<int:pk>/video/", view=MovieViewSet.as_view({"put": "upload_video", "post": "upload_video"}), name="movie-video"),
    path(route="<int:pk>/comments/", view=MovieViewSet.as_view({"get": "get_comments", "post": "create_comment"}), name="movie-comments"),
    path(route="<int:pk>/rate/", view=MovieViewSet.as_view({"post": "rate_movie"}), name="movie-rate"),
    
    # Like endpoints
    path(route="like/", view=LikeViewSet.as_view({"post": "toggle_like"}), name="like-toggle"),
    
    # Review endpoints
    path(route="reviews/", view=ReviewViewSet.as_view({"get": "list", "post": "create"}), name="review-list"),
    path(route="reviews/<int:pk>/", view=ReviewViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}), name="review-detail"),
    
    # Rating endpoints
    path(route="ratings/", view=RatingViewSet.as_view({"get": "list", "post": "create"}), name="rating-list"),
    path(route="ratings/<int:pk>/", view=RatingViewSet.as_view({"delete": "destroy"}), name="rating-delete"),
    
    # Favorite endpoints
    path(route="favorites/", view=FavoriteViewSet.as_view({"get": "list", "post": "create"}), name="favorite-list"),
    path(route="favorites/<int:pk>/", view=FavoriteViewSet.as_view({"delete": "destroy"}), name="favorite-delete"),
]