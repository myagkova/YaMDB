import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    class UserRole(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField(
        unique=True,
        verbose_name='Почта')
    confirmation_code = models.CharField(
        max_length=36,
        null=True,
        unique=True,
        verbose_name='Код подтверждения'
    )
    role = models.CharField(
        max_length=36,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        default='user',
        verbose_name='Биография')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[MaxValueValidator(datetime.datetime.now().year)]
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        to='Genre', blank=True,
        related_name='title_genre',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        to='Category', on_delete=models.SET_NULL, blank=True, null=True,
        related_name='title_category',
        verbose_name='Категория'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название категории(русский)'
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название категории(английский)'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название жанра(русский)'
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название жанра(английский)'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Review(models.Model):
    title = models.ForeignKey(
        to='Title',
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Ревью',
    )
    author = models.ForeignKey(
        to='User',
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв "{self.author}" к произведению "{self.title.name}"'


class Comment(models.Model):
    review = models.ForeignKey(
        to='Review',
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Комментарий к отзыву',
    )
    author = models.ForeignKey(
        to='User',
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'Комментарий пользователя {self.author.username}, '
                f'к отзыву "{self.review.author}" '
                f'на произведение "{self.review.title.name}"')
