from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.db.models import Count

from .constants import (
    CHAR_FIELD_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    STR_MAX_LENGTH,
    MIN_LENGTH_SHORT,
    MIN_LENGTH_TEXT
)

User = get_user_model()


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by('-pub_date')

    def with_comment_count(self):
        return self.annotate(comment_count=Count('comments'))

    def published_with_comments(self):
        return self.published().with_comment_count()


class CreatedAtAbstract(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
        ordering = ('created_at',)


class IsPublishedCreatedAtAbstract(CreatedAtAbstract):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Category(IsPublishedCreatedAtAbstract):
    title = models.CharField(
        max_length=CHAR_FIELD_MAX_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        max_length=SLUG_MAX_LENGTH,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL;'
        ' разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta(IsPublishedCreatedAtAbstract.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:STR_MAX_LENGTH]


class Location(IsPublishedCreatedAtAbstract):
    name = models.CharField(
        max_length=CHAR_FIELD_MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta(IsPublishedCreatedAtAbstract.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:STR_MAX_LENGTH]


class Post(IsPublishedCreatedAtAbstract):
    title = models.CharField(
        max_length=CHAR_FIELD_MAX_LENGTH,
        verbose_name='Заголовок',
        validators=[MinLengthValidator(MIN_LENGTH_SHORT)]
    )
    text = models.TextField(
        verbose_name='Текст',
        validators=[MinLengthValidator(MIN_LENGTH_TEXT)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True
    )

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:STR_MAX_LENGTH]


class Comment(CreatedAtAbstract):
    text = models.TextField(
        'Текст комментария',
        validators=[MinLengthValidator(MIN_LENGTH_SHORT)]
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta(CreatedAtAbstract.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий {self.author} к {self.post}'
