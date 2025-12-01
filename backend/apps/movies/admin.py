# Django modules
from django.contrib import admin
from django.utils.html import format_html

# Project modules
from .models import Movie, Comment, Rating, Like, Review, Favorite



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'movie', 'title', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['title', 'text', 'user__username', 'movie__title']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'movie', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'movie__title']

class CommentInline(admin.TabularInline):
    """Inline comments in Movie admin."""
    model = Comment
    extra = 1
    fields = ('user', 'text', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


class RatingInline(admin.TabularInline):
    """Inline ratings in Movie admin."""
    model = Rating
    extra = 0
    fields = ('user', 'score', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin interface for Movie model."""

    list_display = (
        'id',
        'title',
        'year',
        'genre',
        'duration',
        'average_rating_display',
        'likes_count_display',
    )
    list_display_links = ('id', 'title')
    list_filter = ('genre', 'year')
    search_fields = ('title', 'description', 'genre')
    readonly_fields = ('average_rating_display', 'likes_count_display')
    list_per_page = 25
    inlines = [RatingInline, CommentInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('Main Info', {
            'fields': ('title', 'description', 'poster')
        }),
        ('Details', {
            'fields': ('year', 'genre', 'duration')
        }),
        ('Stats', {
            'fields': ('average_rating_display', 'likes_count_display')
        }),
    )

    @admin.display(description='Average Rating')
    def average_rating_display(self, obj):
        return f'{obj.average_rating:.1f} / 5' if obj.average_rating else 'No ratings'

    @admin.display(description='Likes Count')
    def likes_count_display(self, obj):
        return obj.likes_count


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""

    list_display = (
        'id',
        'movie',
        'user',
        'short_text',
        'parent',
        'likes_count_display',
        'created_at',
    )
    list_display_links = ('id', 'movie')
    list_filter = ('movie', 'user', 'created_at')
    search_fields = ('movie__title', 'user__username', 'text')
    list_editable = ('parent',)
    readonly_fields = ('likes_count_display',)
    list_per_page = 25
    ordering = ('-created_at',)

    @admin.display(description='Text')
    def short_text(self, obj):
        """Show short preview of comment text."""
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text

    @admin.display(description='Likes Count')
    def likes_count_display(self, obj):
        return obj.likes_count


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin interface for Rating model."""

    list_display = (
        'id',
        'movie',
        'user',
        'score',
        'created_at',
    )
    list_display_links = ('id', 'movie')
    list_filter = ('score', 'movie', 'user')
    search_fields = ('movie__title', 'user__username')
    list_editable = ('score',)
    list_per_page = 25
    ordering = ('-created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for Like model."""

    list_display = (
        'id',
        'user',
        'content_type',
        'object_id',
        'target_object_display',
        'created_at',
    )
    list_display_links = ('id', 'user')
    list_filter = ('content_type', 'user', 'created_at')
    search_fields = ('user__username',)
    list_per_page = 25
    ordering = ('-created_at',)

    @admin.display(description='Target Object')
    def target_object_display(self, obj):
        """Human-readable linked object."""
        return format_html('<b>{}</b>', str(obj.content_object))
