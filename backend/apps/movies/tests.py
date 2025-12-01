import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.movies.models import Movie, Review, Rating, Favorite


@pytest.fixture
def api_client():
    """Fixture for creating API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture for creating test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def another_user(db):
    """Fixture for creating second user."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


@pytest.fixture
def movie(db):
    """Fixture for creating test movie."""
    return Movie.objects.create(
        title='Test Movie',
        description='Test Description',
        year=2024,
        genre='Action',
        duration=120
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture for creating authenticated client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestReviewViewSet:
    """Group of tests for ReviewViewSet."""

    def test_list_reviews_success(self, authenticated_client, movie, user):
        """TEST 1: Check listing all reviews."""
        Review.objects.create(
            user=user,
            movie=movie,
            title='Great Movie',
            text='I loved it!',
            rating=5
        )
        
        response = authenticated_client.get('/api/movies/reviews/list/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'Great Movie'

    def test_list_reviews_filter_by_movie(self, authenticated_client, movie, user):
        """TEST 2: Check filtering reviews by movie."""
        another_movie = Movie.objects.create(
            title='Another Movie',
            description='Another Description',
            year=2023,
            genre='Drama',
            duration=100
        )
        
        Review.objects.create(user=user, movie=movie, title='Review 1', text='Text 1', rating=5)
        Review.objects.create(user=user, movie=another_movie, title='Review 2', text='Text 2', rating=4)
        
        response = authenticated_client.get(f'/api/movies/reviews/list/?movie_id={movie.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'Review 1'

    def test_create_review_success(self, authenticated_client, movie):
        """TEST 3: Check creating new review."""
        data = {
            'movie_id': movie.id,
            'title': 'Amazing!',
                   'text': 'Best movie ever!',
            'rating': 5
        }
        
        response = authenticated_client.post('/api/movies/reviews/create/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Amazing!'
        assert Review.objects.count() == 1

    def test_create_review_invalid_movie(self, authenticated_client):
        """TEST 4: Check creating review for non-existing movie."""
        data = {
            'movie_id': 99999,
            'title': 'Test',
            'text': 'Test text',
            'rating': 5
        }
        
        response = authenticated_client.post('/api/movies/reviews/create/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_review_duplicate(self, authenticated_client, movie, user):
        """TEST 5: Check preventing duplicate review."""
        Review.objects.create(
            user=user,
            movie=movie,
            title='First Review',
            text='First text',
            rating=5
        )
        
        data = {
            'movie_id': movie.id,
            'title': 'Second Review',
            'text': 'Second text',
            'rating': 4
        }
        
        response = authenticated_client.post('/api/movies/reviews/create/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_review_success(self, authenticated_client, movie, user):
        """TEST 6: Check retrieving review by ID."""
        review = Review.objects.create(
            user=user,
            movie=movie,
            title='Test Review',
            text='Test text',
            rating=5
        )
        
        response = authenticated_client.get(f'/api/movies/reviews/{review.id}/detail/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Review'

    def test_retrieve_review_not_found(self, authenticated_client):
        """TEST 7: Check retrieving non-existing review."""
        response = authenticated_client.get('/api/movies/reviews/99999/detail/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_review_success(self, authenticated_client, movie, user):
        review = Review.objects.create(
            user=user,
            movie=movie,
            title='Old Title',
            text='Old text',
            rating=3
        )
    
        data = {
            'title': 'New Title',
            'text': 'New text',
            'rating': 5
        }
    
        response = authenticated_client.put(f'/api/movies/reviews/{review.id}/update/', data)
    
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'New Title'
    
        review.refresh_from_db()
        assert review.title == 'New Title'

    def test_update_review_partial(self, authenticated_client, movie, user):
        """TEST 9: Check partial update of review (PATCH)."""
        review = Review.objects.create(
            user=user,
            movie=movie,
            title='Original Title',
            text='Original text',
            rating=3
        )
        
        data = {'rating': 5}
        
        response = authenticated_client.patch(f'/api/movies/reviews/{review.id}/update/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rating'] == 5
        assert response.data['title'] == 'Original Title'

    def test_update_review_permission_denied(self, authenticated_client, another_user, movie, user):
        """TEST 10: Check editing another user's review is forbidden."""
        review = Review.objects.create(
            user=another_user,
            movie=movie,
            title='Another User Review',
            text='Text',
            rating=4
        )
        
        data = {'title': 'Hacked Title'}
        
        response = authenticated_client.put(f'/api/movies/reviews/{review.id}/update/', data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_review_success(self, authenticated_client, movie, user):
        review = Review.objects.create(
            user=user,
            movie=movie,
            title='To Delete',
            text='Text',
            rating=3
        )
    
        review_id = review.id
    
        response = authenticated_client.delete(f'/api/movies/reviews/{review_id}/delete/')
    
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Review.objects.get(id=review_id).deleted_at is not None

    def test_delete_review_permission_denied(self, authenticated_client, another_user, movie):
        """TEST 12: Check preventing deletion of another user's review."""
        review = Review.objects.create(
            user=another_user,
            movie=movie,
            title='Another User Review',
            text='Text',
            rating=4
        )
        
        response = authenticated_client.delete(f'/api/movies/reviews/{review.id}/delete/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Review.objects.count() == 1


@pytest.mark.django_db
class TestRatingViewSet:
    """Group of tests for RatingViewSet."""

    def test_list_ratings_success(self, authenticated_client, movie, user):
        """TEST 13: Check listing ratings."""
        Rating.objects.create(user=user, movie=movie, score=5)
        
        response = authenticated_client.get('/api/movies/ratings/list/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_rating_success(self, authenticated_client, movie):
        """TEST 14: Check creating rating."""
        data = {'movie_id': movie.id, 'score': 5}
        
        response = authenticated_client.post('/api/movies/ratings/rate/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['score'] == 5
        assert Rating.objects.count() == 1

    def test_update_rating_success(self, authenticated_client, movie, user):
        """TEST 15: Check updating existing rating."""
        Rating.objects.create(user=user, movie=movie, score=3)
        
        data = {'movie_id': movie.id, 'score': 5}
        
        response = authenticated_client.post('/api/movies/ratings/rate/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['score'] == 5
        assert Rating.objects.count() == 1

    def test_create_rating_invalid_score(self, authenticated_client, movie):
        """TEST 16: Check validation for rating (1–5 only)."""
        data = {'movie_id': movie.id, 'score': 10}
        
        response = authenticated_client.post('/api/movies/ratings/rate/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_rating_success(self, authenticated_client, movie, user):
        """TEST 17: Check rating deletion."""
        rating = Rating.objects.create(user=user, movie=movie, score=5)
        
        response = authenticated_client.delete(f'/api/movies/ratings/{rating.id}/delete/')
        
        assert Rating.objects.get(id=rating.id).deleted_at is not None
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestFavoriteViewSet:
    """Group of tests for FavoriteViewSet."""

    def test_list_favorites_success(self, authenticated_client, movie, user):
        """TEST 18: Check listing favorite movies."""
        Favorite.objects.create(user=user, movie=movie)
        
        response = authenticated_client.get('/api/movies/favorites/list/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_add_favorite_success(self, authenticated_client, movie):
        """TEST 19: Check adding to favorites."""
        data = {'movie_id': movie.id}
        
        response = authenticated_client.post('/api/movies/favorites/add/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Favorite.objects.count() == 1

    def test_add_favorite_duplicate(self, authenticated_client, movie, user):
        """TEST 20: Check preventing duplicate favorites."""
        Favorite.objects.create(user=user, movie=movie)
        
        data = {'movie_id': movie.id}
        
        response = authenticated_client.post('/api/movies/favorites/add/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Favorite.objects.count() == 1

    def test_remove_favorite_success(self, authenticated_client, movie, user):
        """TEST 21: Check removing from favorites."""
        favorite = Favorite.objects.create(user=user, movie=movie)
        
        response = authenticated_client.delete(f'/api/movies/favorites/{favorite.id}/remove/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Favorite.objects.get(id=favorite.id).deleted_at is not None
