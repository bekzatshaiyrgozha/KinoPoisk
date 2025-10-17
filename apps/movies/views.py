# Third-party modules
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django modules
from django.http import HttpRequest
from django.db.models import Avg
from django.contrib.contenttypes.models import ContentType


# Project modules
from .models import Movie, Comment, Like, Rating
from .serializers import (
    MovieSerializer, 
    CommentSerializer,
    RatingSerializer
)

# Typing imports
from typing import Optional, Type
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType as ContentTypeModel
from django.db.models.base import ModelBase


class MovieListView(APIView):
    """
    View to list all movies.
    Only authenticated users can access.
    """
    permission_classes = [IsAuthenticated]

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
            average_rating=Avg('ratings__score')
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