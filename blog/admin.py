from django.contrib import admin

from blog.models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    exclude = ('count_of_view',)
    list_display = ('title', 'text', 'image',)
    list_filter = ('title',)
    search_fields = ('title', 'text',)
