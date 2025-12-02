import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework.test import APIClient
from rest_framework import status
from apps.movies.models import Movie, Review, Rating, Favorite
from django.test import TestCase

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

@pytest.mark.django_db
class TestMovieSearch:
    """Test cases for movie search functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_movies(self, user):
        """Set up test data"""
        # Create test movies with different attributes
        self.movie1 = Movie.objects.create(
            title='The Matrix',
            description='A computer hacker learns about the true nature of reality',
            year=1999,
            genre='Sci-Fi',
            duration=136
        )
        
        self.movie2 = Movie.objects.create(
            title='The Matrix Reloaded',
            description='Neo and his allies race against time',
            year=2003,
            genre='Sci-Fi',
            duration=138
        )
        
        self.movie3 = Movie.objects.create(
            title='Inception',
            description='A thief who steals corporate secrets through dream-sharing',
            year=2010,
            genre='Sci-Fi',
            duration=148
        )
        
        self.movie4 = Movie.objects.create(
            title='The Godfather',
            description='The aging patriarch of an organized crime dynasty',
            year=1972,
            genre='Crime',
            duration=175
        )
        
        self.movie5 = Movie.objects.create(
            title='Pulp Fiction',
            description='The lives of two mob hitmen, a boxer, and others',
            year=1994,
            genre='Crime',
            duration=154
        )
        
        # Create some ratings for testing ordering
        Rating.objects.create(user=user, movie=self.movie1, score=5)
        Rating.objects.create(user=user, movie=self.movie3, score=4)
        Rating.objects.create(user=user, movie=self.movie4, score=5)
    
    def test_search_by_title(self, api_client):
        """Test searching movies by title"""
        response = api_client.get('/api/movies/search/?query=matrix')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        titles = [movie['title'] for movie in response.data['results']]
        assert 'The Matrix' in titles
        assert 'The Matrix Reloaded' in titles
    
    def test_search_by_description(self, api_client):
        """Test searching movies by description"""
        response = api_client.get('/api/movies/search/?query=dream')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Inception'
    
    def test_filter_by_genre(self, api_client):
        """Test filtering movies by genre"""
        response = api_client.get('/api/movies/search/?genre=Crime')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        titles = [movie['title'] for movie in response.data['results']]
        assert 'The Godfather' in titles
        assert 'Pulp Fiction' in titles
    
    def test_filter_by_year_range(self, api_client):
        """Test filtering movies by year range"""
        response = api_client.get('/api/movies/search/?year_from=2000&year_to=2010')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        titles = [movie['title'] for movie in response.data['results']]
        assert 'The Matrix Reloaded' in titles
        assert 'Inception' in titles
    
    def test_combined_search(self, api_client):
        """Test combined search with multiple parameters"""
        response = api_client.get(
            '/api/movies/search/?query=matrix&genre=Sci-Fi&year_from=1990&year_to=2000'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'The Matrix'
    
    def test_empty_results(self, api_client):
        """Test search with no matching results"""
        response = api_client.get('/api/movies/search/?query=nonexistent')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_pagination(self, api_client):
        """Test pagination of search results"""
        # Create more movies to test pagination
        for i in range(15):
            Movie.objects.create(
                title=f'Test Movie {i}',
                description=f'Description {i}',
                year=2020,
                genre='Action',
                duration=120
            )
        
        # First page
        response = api_client.get('/api/movies/search/?genre=Action&page=1&page_size=10')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10
        assert response.data['next'] is not None
        
        # Second page
        response = api_client.get('/api/movies/search/?genre=Action&page=2&page_size=10')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert response.data['next'] is None
    
    def test_ordering_by_title(self, api_client):
        """Test ordering results by title"""
        response = api_client.get('/api/movies/search/?genre=Sci-Fi&ordering=title')
        
        assert response.status_code == status.HTTP_200_OK
        titles = [movie['title'] for movie in response.data['results']]
        assert titles == sorted(titles)
    
    def test_ordering_by_year_desc(self, api_client):
        """Test ordering results by year (descending)"""
        response = api_client.get('/api/movies/search/?genre=Sci-Fi&ordering=-year')
        
        assert response.status_code == status.HTTP_200_OK
        years = [movie['year'] for movie in response.data['results']]
        assert years == sorted(years, reverse=True)
    
    def test_invalid_year_range(self, api_client):
        """Test validation error when year_from > year_to"""
        response = api_client.get('/api/movies/search/?year_from=2010&year_to=2000')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'year_from' in response.data
    
    def test_case_insensitive_search(self, api_client):
        """Test that search is case-insensitive"""
        response1 = api_client.get('/api/movies/search/?query=MATRIX')
        response2 = api_client.get('/api/movies/search/?query=matrix')
        response3 = api_client.get('/api/movies/search/?query=MaTrIx')
        
        assert response1.data['count'] == response2.data['count']
        assert response2.data['count'] == response3.data['count']