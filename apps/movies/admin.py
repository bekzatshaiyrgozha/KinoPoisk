from django.contrib import admin
from .models import Film, Comment



class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('user', 'created_at')
    fields = ('user', 'text', 'created_at')



@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    list_filter = ('id',)
    ordering = ('title',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('film', 'user', 'created_at')
    search_fields = ('film__title', 'user__username', 'text')
    list_filter = ('created_at', 'film')
    ordering = ('-created_at',)

    readonly_fields = ('user', 'film', 'created_at')