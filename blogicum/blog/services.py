from django.utils import timezone

from .models import Post


def filter_posts_by_publication(queryset=Post.objects):
    return queryset.select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )
