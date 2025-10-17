from django.urls import path
from .views import MovieListView, MovieDetailView, CommentView, LikeView, RatingView

app_name = 'movies'

urlpatterns = [
    path('', MovieListView.as_view(), name='movie-list'),
    path('<int:movie_id>/', MovieDetailView.as_view(), name='movie-detail'),
    path('<int:movie_id>/comments/', CommentView.as_view(), name='movie-comments'),
    path('<int:movie_id>/rate/', RatingView.as_view(), name='movie-rate'),
    path('like/', LikeView.as_view(), name='like-object'),
]
