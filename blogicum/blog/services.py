from django.core.paginator import Paginator
from .constants import POSTS_PER_PAGE


def paginate_posts(request, posts, per_page=POSTS_PER_PAGE):
    """Пагинация постов"""
    paginator = Paginator(posts, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
