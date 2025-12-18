from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.movies.models import Movie, Comment, Like, Rating, Review, Favorite
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class MovieTests(APITestCase):
    """Test suite for Movie endpoints"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )

        # Create test movies
        self.movie1 = Movie.objects.create(
            title="Test Movie 1",
            description="Test description 1",
            year=2020,
            genre="Action",
            duration=120,
        )
        self.movie2 = Movie.objects.create(
            title="Test Movie 2",
            description="Test description 2",
            year=2021,
            genre="Drama",
            duration=90,
        )

    # MovieListView Tests
    def test_list_movies_success(self):
        """Test getting list of movies"""
        response = self.client.get("/api/movies/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_movies_pagination(self):
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

        response = self.client.get("/api/movies/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)  # Default page size
        self.assertIn("next", response.data)

    def test_list_movies_empty(self):
        """Test getting empty list"""
        Movie.objects.all().delete()
        response = self.client.get("/api/movies/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    # MovieDetailView Tests
    def test_get_movie_success(self):
        """Test getting single movie"""
        # Login first
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/api/movies/{self.movie1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("title", response.data["data"])
        self.assertEqual(response.data["data"]["title"], "Test Movie 1")
        self.assertIn("average_rating", response.data["data"])
        self.assertIn("likes_count", response.data["data"])

    def test_get_movie_not_found(self):
        """Test getting non-existent movie"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/movies/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_movie_unauthenticated(self):
        """Test getting movie without authentication"""
        response = self.client.get(f"/api/movies/{self.movie1.id}/")

        # Movie detail view doesn't require authentication for GET
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_movie_with_ratings(self):
        """Test movie includes user rating"""
        self.client.force_authenticate(user=self.user)

        # Create rating
        Rating.objects.create(user=self.user, movie=self.movie1, score=5)

        response = self.client.get(f"/api/movies/{self.movie1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("user_rating", response.data["data"])
        if response.data["data"]["user_rating"] is not None:
            self.assertEqual(response.data["data"]["user_rating"], 5)


class CommentTests(APITestCase):
    """Test suite for Comment endpoints"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            year=2020,
            genre="Action",
            duration=120,
        )

    def test_create_comment_success(self):
        """Test creating a comment"""
        self.client.force_authenticate(user=self.user)

        data = {"text": "Great movie!", "movie": self.movie.id}

        response = self.client.post(f"/api/movies/{self.movie.id}/comments/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_empty_text(self):
        """Test creating comment with empty text"""
        self.client.force_authenticate(user=self.user)

        data = {"text": "", "movie": self.movie.id}

        response = self.client.post(f"/api/movies/{self.movie.id}/comments/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comment_unauthenticated(self):
        """Test creating comment without authentication"""
        data = {"text": "Great movie!", "movie": self.movie.id}

        response = self.client.post(f"/api/movies/{self.movie.id}/comments/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_nonexistent_movie(self):
        """Test creating comment for non-existent movie"""
        self.client.force_authenticate(user=self.user)

        data = {"text": "Great movie!", "movie": 9999}

        response = self.client.post("/api/movies/9999/comments/", data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments_success(self):
        """Test getting comments list"""
        self.client.force_authenticate(user=self.user)

        # Create comments
        Comment.objects.create(user=self.user, movie=self.movie, text="Comment 1")
        Comment.objects.create(user=self.user, movie=self.movie, text="Comment 2")

        response = self.client.get(f"/api/movies/{self.movie.id}/comments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_reply_success(self):
        """Test creating a reply to comment"""
        self.client.force_authenticate(user=self.user)

        # Create parent comment
        parent = Comment.objects.create(user=self.user, movie=self.movie, text="Parent")

        data = {"text": "Reply", "movie": self.movie.id, "parent": parent.id}

        response = self.client.post(f"/api/movies/{self.movie.id}/comments/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(parent=parent).count(), 1)


class LikeTests(APITestCase):
    """Test suite for Like endpoints"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            year=2020,
            genre="Action",
            duration=120,
        )

    def test_like_movie_success(self):
        """Test liking a movie"""
        self.client.force_authenticate(user=self.user)

        data = {"content_type": "movie", "object_id": self.movie.id}

        response = self.client.post("/api/movies/like/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["liked"])

    def test_unlike_movie_success(self):
        """Test unliking a movie"""
        self.client.force_authenticate(user=self.user)

        # Create like first
        ct = ContentType.objects.get_for_model(Movie)
        Like.objects.create(user=self.user, content_type=ct, object_id=self.movie.id)

        data = {"content_type": "movie", "object_id": self.movie.id}

        response = self.client.post("/api/movies/like/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["liked"])

    def test_like_unauthenticated(self):
        """Test liking without authentication"""
        data = {"content_type": "movie", "object_id": self.movie.id}

        response = self.client.post("/api/movies/like/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_invalid_content_type(self):
        """Test liking with invalid content type"""
        self.client.force_authenticate(user=self.user)

        data = {"content_type": "invalid", "object_id": self.movie.id}

        response = self.client.post("/api/movies/like/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_nonexistent_object(self):
        """Test liking non-existent object"""
        self.client.force_authenticate(user=self.user)

        data = {"content_type": "movie", "object_id": 9999}

        response = self.client.post("/api/movies/like/", data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RatingTests(APITestCase):
    """Test suite for Rating endpoints"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            year=2020,
            genre="Action",
            duration=120,
        )

    def test_rate_movie_success(self):
        """Test rating a movie"""
        self.client.force_authenticate(user=self.user)

        data = {"score": 5}

        response = self.client.post(f"/api/movies/{self.movie.id}/rate/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)

    def test_update_rating_success(self):
        """Test updating existing rating"""
        self.client.force_authenticate(user=self.user)

        # Create rating first
        Rating.objects.create(user=self.user, movie=self.movie, score=3)

        data = {"score": 5}

        response = self.client.post(f"/api/movies/{self.movie.id}/rate/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)  # Still only 1
        self.assertEqual(Rating.objects.first().score, 5)  # Updated

    def test_rate_movie_invalid_score_low(self):
        """Test rating with score below 1"""
        self.client.force_authenticate(user=self.user)

        data = {"score": 0}

        response = self.client.post(f"/api/movies/{self.movie.id}/rate/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_movie_invalid_score_high(self):
        """Test rating with score above 5"""
        self.client.force_authenticate(user=self.user)

        data = {"score": 6}

        response = self.client.post(f"/api/movies/{self.movie.id}/rate/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_movie_unauthenticated(self):
        """Test rating without authentication"""
        data = {"score": 5}

        response = self.client.post(f"/api/movies/{self.movie.id}/rate/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchTests(APITestCase):
    """Test suite for Movie Search endpoint"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()

        # Create test movies
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

    def test_search_by_title(self):
        """Test searching by title"""
        response = self.client.get("/api/movies/search/?query=Action")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Action Movie")

    def test_search_by_genre(self):
        """Test searching by genre"""
        response = self.client.get("/api/movies/search/?genre=Drama")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_year_range(self):
        """Test searching by year range"""
        response = self.client.get("/api/movies/search/?year_from=2021")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_no_results(self):
        """Test search with no results"""
        response = self.client.get("/api/movies/search/?query=NonExistent")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_ordering(self):
        """Test search with ordering"""
        response = self.client.get("/api/movies/search/?ordering=-year")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["year"], 2021)


class ReviewTests(APITestCase):
    """Test suite for Review endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            year=2020,
            genre="Action",
            duration=120,
        )

    def test_list_reviews_success(self):
        """Test getting list of reviews"""
        self.client.force_authenticate(user=self.user)
        Review.objects.create(
            user=self.user, movie=self.movie, title="Review 1", text="Text 1", rating=5
        )

        response = self.client.get("/api/movies/reviews/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_review_success(self):
        """Test creating a review"""
        self.client.force_authenticate(user=self.user)

        data = {
            "movie_id": self.movie.id,
            "title": "Great Movie",
            "text": "Loved it!",
            "rating": 5,
        }

        response = self.client.post("/api/movies/reviews/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_invalid_data(self):
        """Test creating review with missing fields"""
        self.client.force_authenticate(user=self.user)

        data = {"movie_id": self.movie.id}

        response = self.client.post("/api/movies/reviews/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_duplicate(self):
        """Test creating duplicate review"""
        self.client.force_authenticate(user=self.user)

        # Create first review
        Review.objects.create(
            user=self.user, movie=self.movie, title="First", text="Text", rating=5
        )

        data = {
            "movie_id": self.movie.id,
            "title": "Second",
            "text": "Text",
            "rating": 4,
        }

        response = self.client.post("/api/movies/reviews/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_unauthenticated(self):
        """Test creating review without authentication"""
        data = {
            "movie_id": self.movie.id,
            "title": "Great Movie",
            "text": "Loved it!",
            "rating": 5,
        }

        response = self.client.post("/api/movies/reviews/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_not_owner(self):
        """Test updating review by non-owner"""
        review = Review.objects.create(
            user=self.user, movie=self.movie, title="Review 1", text="Text 1", rating=5
        )

        other_user = User.objects.create_user(
            email="other@example.com", password="Pass"
        )
        self.client.force_authenticate(user=other_user)

        data = {"title": "Updated"}

        response = self.client.patch(f"/api/movies/reviews/{review.id}/", data)

        # 403 Forbidden is correct - user is authenticated but not owner
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_success(self):
        """Test deleting review"""
        review = Review.objects.create(
            user=self.user, movie=self.movie, title="Review 1", text="Text 1", rating=5
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f"/api/movies/reviews/{review.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)


class FavoriteTests(APITestCase):
    """Test suite for Favorite endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            year=2020,
            genre="Action",
            duration=120,
        )

    def test_list_favorites_success(self):
        """Test getting favorites list"""
        self.client.force_authenticate(user=self.user)
        Favorite.objects.create(user=self.user, movie=self.movie)

        response = self.client.get("/api/movies/favorites/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_favorites_unauthenticated(self):
        """Test getting favorites without authentication"""
        response = self.client.get("/api/movies/favorites/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_favorite_success(self):
        """Test adding movie to favorites"""
        self.client.force_authenticate(user=self.user)

        data = {"movie_id": self.movie.id}

        response = self.client.post("/api/movies/favorites/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_add_favorite_invalid_movie(self):
        """Test adding non-existent movie to favorites"""
        self.client.force_authenticate(user=self.user)

        data = {"movie_id": 9999}

        response = self.client.post("/api/movies/favorites/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_favorite_duplicate(self):
        """Test adding duplicate favorite"""
        self.client.force_authenticate(user=self.user)

        # Add first time
        Favorite.objects.create(user=self.user, movie=self.movie)

        data = {"movie_id": self.movie.id}

        response = self.client.post("/api/movies/favorites/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_favorite_success(self):
        """Test removing movie from favorites"""
        self.client.force_authenticate(user=self.user)
        favorite = Favorite.objects.create(user=self.user, movie=self.movie)

        response = self.client.delete(f"/api/movies/favorites/{favorite.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_remove_favorite_not_found(self):
        """Test removing non-favorite movie"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete("/api/movies/favorites/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
