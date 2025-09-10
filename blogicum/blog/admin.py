from django.contrib import admin

from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author', 'category', 'is_published')
    list_filter = ('category', 'is_published', 'pub_date')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'short_text')
    list_filter = ('created_at', 'post')
    search_fields = ('text', 'author__username', 'post__title')
    date_hierarchy = 'created_at'

    def short_text(self, obj: Comment) -> str:
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text
    short_text.short_description = 'Текст комментария'  # type: ignore
