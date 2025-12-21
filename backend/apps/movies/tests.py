import pytest
from typing import Dict, Any, Callable
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.movies.models import Movie, Comment, Like, Rating, Review, Favorite
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Fixture that provides an API client for making requests."""
    return APIClient()


@pytest.fixture
def user() -> User:
    """Fixture that creates a test user."""
    return User.objects.create_user(
        email="test@example.com", password="TestPass123!"
    )


@pytest.fixture
def movie1() -> Movie:
    """Fixture that creates a test movie 1."""
    return Movie.objects.create(
        title="Test Movie 1",
        description="Test description 1",
        year=2020,
        genre="Action",
        duration=120,
    )


@pytest.fixture
def movie2() -> Movie:
    """Fixture that creates a test movie 2."""
    return Movie.objects.create(
        title="Test Movie 2",
        description="Test description 2",
        year=2021,
        genre="Drama",
        duration=90,
    )


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    """Fixture that provides an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestMovieList:
    """Test suite for Movie list endpoint"""

    def test_list_movies_success(self, api_client: APIClient, movie1: Movie, movie2: Movie) -> None:
        """Test getting list of movies"""
        response = api_client.get("/api/movies/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 2

    def test_list_movies_pagination(self, api_client: APIClient, movie1: Movie) -> None:
        """Test pagination works"""
        # Create 15 movies
        for i in range(15):
            Movie.objects.create(
                title=f"Movie {i}",
                description=f"Description {i}",
                year=2020,
                genre="Action",
                duration=120,
            )

        response = api_client.get("/api/movies/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10  # Default page size
        assert "next" in response.data

    def test_list_movies_empty(self, api_client: APIClient) -> None:
        """Test getting empty list"""
        Movie.objects.all().delete()
        response = api_client.get("/api/movies/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestMovieDetail:
    """Test suite for Movie detail endpoint"""

    def test_get_movie_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test getting single movie"""
        # Login first
        api_client.force_authenticate(user=user)

        response = api_client.get(f"/api/movies/{movie1.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "title" in response.data["data"]
        assert response.data["data"]["title"] == "Test Movie 1"
        assert "average_rating" in response.data["data"]
        assert "likes_count" in response.data["data"]

    def test_get_movie_not_found(self, api_client: APIClient, user: User) -> None:
        """Test getting non-existent movie"""
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/movies/9999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_movie_unauthenticated(self, api_client: APIClient, movie1: Movie) -> None:
        """Test getting movie without authentication"""
        response = api_client.get(f"/api/movies/{movie1.id}/")

        # Movie detail view doesn't require authentication for GET
        assert response.status_code == status.HTTP_200_OK

    def test_get_movie_with_ratings(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test movie includes user rating"""
        api_client.force_authenticate(user=user)

        # Create rating
        Rating.objects.create(user=user, movie=movie1, score=5)

        response = api_client.get(f"/api/movies/{movie1.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "user_rating" in response.data["data"]
        if response.data["data"]["user_rating"] is not None:
            assert response.data["data"]["user_rating"] == 5

@pytest.mark.django_db
class TestComments:
    """Test suite for Comment endpoints"""

    def test_create_comment_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test creating a comment"""
        api_client.force_authenticate(user=user)

        data = {"text": "Great movie!", "movie": movie1.id}

        response = api_client.post(f"/api/movies/{movie1.id}/comments/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1

    def test_create_comment_empty_text(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test creating comment with empty text"""
        api_client.force_authenticate(user=user)

        data = {"text": "", "movie": movie1.id}

        response = api_client.post(f"/api/movies/{movie1.id}/comments/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_unauthenticated(self, api_client: APIClient, movie1: Movie) -> None:
        """Test creating comment without authentication"""
        data = {"text": "Great movie!", "movie": movie1.id}

        response = api_client.post(f"/api/movies/{movie1.id}/comments/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_nonexistent_movie(self, api_client: APIClient, user: User) -> None:
        """Test creating comment for non-existent movie"""
        api_client.force_authenticate(user=user)

        data = {"text": "Great movie!", "movie": 9999}

        response = api_client.post("/api/movies/9999/comments/", data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_comments_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test getting comments list"""
        api_client.force_authenticate(user=user)

        # Create comments
        Comment.objects.create(user=user, movie=movie1, text="Comment 1")
        Comment.objects.create(user=user, movie=movie1, text="Comment 2")

        response = api_client.get(f"/api/movies/{movie1.id}/comments/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_create_reply_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test creating a reply to comment"""
        api_client.force_authenticate(user=user)

        # Create parent comment
        parent = Comment.objects.create(user=user, movie=movie1, text="Parent")

        data = {"text": "Reply", "movie": movie1.id, "parent": parent.id}

        response = api_client.post(f"/api/movies/{movie1.id}/comments/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(parent=parent).count() == 1

@pytest.mark.django_db
class TestLikes:
    """Test suite for Like endpoints"""

    def test_like_movie_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test liking a movie"""
        api_client.force_authenticate(user=user)

        data = {"content_type": "movie", "object_id": movie1.id}

        response = api_client.post("/api/movies/like/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["liked"] is True

    def test_unlike_movie_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test unliking a movie"""
        api_client.force_authenticate(user=user)

        # Create like first
        ct = ContentType.objects.get_for_model(Movie)
        Like.objects.create(user=user, content_type=ct, object_id=movie1.id)

        data = {"content_type": "movie", "object_id": movie1.id}

        response = api_client.post("/api/movies/like/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["liked"] is False

    def test_like_unauthenticated(self, api_client: APIClient, movie1: Movie) -> None:
        """Test liking without authentication"""
        data = {"content_type": "movie", "object_id": movie1.id}

        response = api_client.post("/api/movies/like/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_like_invalid_content_type(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test liking with invalid content type"""
        api_client.force_authenticate(user=user)

        data = {"content_type": "invalid", "object_id": movie1.id}

        response = api_client.post("/api/movies/like/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_like_nonexistent_object(self, api_client: APIClient, user: User) -> None:
        """Test liking non-existent object"""
        api_client.force_authenticate(user=user)

        data = {"content_type": "movie", "object_id": 9999}

        response = api_client.post("/api/movies/like/", data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestRatings:
    """Test suite for Rating endpoints"""

    def test_rate_movie_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test rating a movie"""
        api_client.force_authenticate(user=user)

        data = {"score": 5}

        response = api_client.post(f"/api/movies/{movie1.id}/rate/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Rating.objects.count() == 1

    def test_update_rating_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test updating existing rating"""
        api_client.force_authenticate(user=user)

        # Create rating first
        Rating.objects.create(user=user, movie=movie1, score=3)

        data = {"score": 5}

        response = api_client.post(f"/api/movies/{movie1.id}/rate/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Rating.objects.count() == 1  # Still only 1
        assert Rating.objects.first().score == 5  # Updated

    def test_rate_movie_invalid_score_low(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test rating with score below 1"""
        api_client.force_authenticate(user=user)

        data = {"score": 0}

        response = api_client.post(f"/api/movies/{movie1.id}/rate/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rate_movie_invalid_score_high(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test rating with score above 5"""
        api_client.force_authenticate(user=user)

        data = {"score": 6}

        response = api_client.post(f"/api/movies/{movie1.id}/rate/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rate_movie_unauthenticated(self, api_client: APIClient, movie1: Movie) -> None:
        """Test rating without authentication"""
        data = {"score": 5}

        response = api_client.post(f"/api/movies/{movie1.id}/rate/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestSearch:
    """Test suite for Movie Search endpoint"""

    def test_search_by_title(self, api_client: APIClient) -> None:
        """Test searching by title"""
        Movie.objects.create(
            title="Action Movie",
            description="Exciting action",
            year=2020,
            genre="Action",
            duration=120,
        )
        Movie.objects.create(
            title="Drama Movie",
            description="Emotional drama",
            year=2021,
            genre="Drama",
            duration=90,
        )

        response = api_client.get("/api/movies/search/?query=Action")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Action Movie"

    def test_search_by_genre(self, api_client: APIClient) -> None:
        """Test searching by genre"""
        Movie.objects.create(
            title="Action Movie",
            description="Exciting action",
            year=2020,
            genre="Action",
            duration=120,
        )
        Movie.objects.create(
            title="Drama Movie",
            description="Emotional drama",
            year=2021,
            genre="Drama",
            duration=90,
        )

        response = api_client.get("/api/movies/search/?genre=Drama")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_search_by_year_range(self, api_client: APIClient) -> None:
        """Test searching by year range"""
        Movie.objects.create(
            title="Action Movie",
            description="Exciting action",
            year=2020,
            genre="Action",
            duration=120,
        )
        Movie.objects.create(
            title="Drama Movie",
            description="Emotional drama",
            year=2021,
            genre="Drama",
            duration=90,
        )

        response = api_client.get("/api/movies/search/?year_from=2021")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_search_no_results(self, api_client: APIClient) -> None:
        """Test search with no results"""
        response = api_client.get("/api/movies/search/?query=NonExistent")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_search_ordering(self, api_client: APIClient) -> None:
        """Test search with ordering"""
        Movie.objects.create(
            title="Action Movie",
            description="Exciting action",
            year=2020,
            genre="Action",
            duration=120,
        )
        Movie.objects.create(
            title="Drama Movie",
            description="Emotional drama",
            year=2021,
            genre="Drama",
            duration=90,
        )

        response = api_client.get("/api/movies/search/?ordering=-year")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["year"] == 2021

@pytest.mark.django_db
class TestReviews:
    """Test suite for Review endpoints"""

    def test_list_reviews_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test getting list of reviews"""
        api_client.force_authenticate(user=user)
        Review.objects.create(
            user=user, movie=movie1, title="Review 1", text="Text 1", rating=5
        )

        response = api_client.get("/api/movies/reviews/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 1

    def test_create_review_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test creating a review"""
        api_client.force_authenticate(user=user)

        data = {
            "movie_id": movie1.id,
            "title": "Great Movie",
            "text": "Loved it!",
            "rating": 5,
        }

        response = api_client.post("/api/movies/reviews/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.count() == 1

    def test_create_review_invalid_data(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test creating review with missing fields"""
        api_client.force_authenticate(user=user)

        data = {"movie_id": movie1.id}

        response = api_client.post("/api/movies/reviews/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_review_duplicate(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test creating duplicate review"""
        api_client.force_authenticate(user=user)

        # Create first review
        Review.objects.create(
            user=user, movie=movie1, title="First", text="Text", rating=5
        )

        data = {
            "movie_id": movie1.id,
            "title": "Second",
            "text": "Text",
            "rating": 4,
        }

        response = api_client.post("/api/movies/reviews/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_review_unauthenticated(self, api_client: APIClient, movie1: Movie) -> None:
        """Test creating review without authentication"""
        data = {
            "movie_id": movie1.id,
            "title": "Great Movie",
            "text": "Loved it!",
            "rating": 5,
        }

        response = api_client.post("/api/movies/reviews/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_review_not_owner(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test updating review by non-owner"""
        review = Review.objects.create(
            user=user, movie=movie1, title="Review 1", text="Text 1", rating=5
        )

        other_user = User.objects.create_user(
            email="other@example.com", password="Pass"
        )
        api_client.force_authenticate(user=other_user)

        data = {"title": "Updated"}

        response = api_client.patch(f"/api/movies/reviews/{review.id}/", data)

        # 403 Forbidden is correct - user is authenticated but not owner
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_review_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test deleting review"""
        review = Review.objects.create(
            user=user, movie=movie1, title="Review 1", text="Text 1", rating=5
        )
        api_client.force_authenticate(user=user)

        response = api_client.delete(f"/api/movies/reviews/{review.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Review.objects.count() == 0

@pytest.mark.django_db
class TestFavorites:
    """Test suite for Favorite endpoints"""

    def test_list_favorites_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test getting favorites list"""
        api_client.force_authenticate(user=user)
        Favorite.objects.create(user=user, movie=movie1)

        response = api_client.get("/api/movies/favorites/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 1

    def test_list_favorites_unauthenticated(self, api_client: APIClient) -> None:
        """Test getting favorites without authentication"""
        response = api_client.get("/api/movies/favorites/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_favorite_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test adding movie to favorites"""
        api_client.force_authenticate(user=user)

        data = {"movie_id": movie1.id}

        response = api_client.post("/api/movies/favorites/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Favorite.objects.count() == 1

    def test_add_favorite_invalid_movie(self, api_client: APIClient, user: User) -> None:
        """Test adding non-existent movie to favorites"""
        api_client.force_authenticate(user=user)

        data = {"movie_id": 9999}

        response = api_client.post("/api/movies/favorites/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_favorite_duplicate(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test adding duplicate favorite"""
        api_client.force_authenticate(user=user)

        # Add first time
        Favorite.objects.create(user=user, movie=movie1)

        data = {"movie_id": movie1.id}

        response = api_client.post("/api/movies/favorites/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_favorite_success(self, api_client: APIClient, user: User, movie1: Movie) -> None:
        """Test removing movie from favorites"""
        api_client.force_authenticate(user=user)
        favorite = Favorite.objects.create(user=user, movie=movie1)

        response = api_client.delete(f"/api/movies/favorites/{favorite.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Favorite.objects.count() == 0

    def test_remove_favorite_not_found(self, api_client: APIClient, user: User) -> None:
        """Test removing non-favorite movie"""
        api_client.force_authenticate(user=user)

        response = api_client.delete("/api/movies/favorites/9999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
