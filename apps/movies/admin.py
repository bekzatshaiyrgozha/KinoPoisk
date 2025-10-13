from django.contrib import admin
from .models import Film, Comment

admin.site.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'description'
    )
    list_filter = (
        'title',
        'description'
    )
    search_fields = (
        'title', 
        'description'
    )
    list_per_page = 25
    list_editable = (
        'title', 
        'description'
    )
    list_display_links = (
        'title',
        'description'
    )
    list_max_show_all = 100

admin.site.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'film',
        'user', 
        'text', 
        'created_at'
    )
    list_filter = (
        'film', 
        'user', 
        'created_at'
    )
    search_fields = (
        'film',
        'user',
        'text'
    )
    list_per_page = 25
    list_editable = (
        'film', 
        'user', 
        'text'
    )
    list_display_links = (
        'film', 
        'user', 
        'text'
    )
    list_max_show_all = 100
