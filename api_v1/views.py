from uuid import uuid4

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorAdminModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          EmailCodeTokenObtainPairSerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializer, UserSerializer)


class EmailCodeTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailCodeTokenObtainPairSerializer
    permission_classes = []


@api_view(['POST'])
@permission_classes([])
def send_confirmation_code(request):
    email = request.data.get('email', '')
    if not email:
        return Response(
            data={'error': 'Не передан email'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(email=email).update(confirmation_code=uuid4()):
        user = User.objects.get(email=email)
    else:
        user = User.objects.create_user(
            username=uuid4(),
            email=email,
            confirmation_code=uuid4()
        )
    success = send_mail(
        'Yamdb registration',
        f'Your confirmation code: {user.confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        (email,)
    )
    if success:
        return Response(
            data={'message': 'Код выслан на email'},
            status=status.HTTP_200_OK
        )
    return Response(
        data={'error': 'Не удалось отправить код на email'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    permission_classes = [IsAdmin]

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        else:
            serializer = self.get_serializer(request.user)

        return Response(serializer.data)

    class Meta:
        ordering = ['role']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        rating = Title.objects.all().annotate(
            rating=Avg('reviews__score')).order_by('rating')
        return rating

    class Meta:
        ordering = ['reviews__pub_date']


class DeleteViewSet(mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    pass


class CategoryViewSet(DeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'

    class Meta:
        ordering = ['name']


class GenreViewSet(DeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'

    class Meta:
        ordering = ['name']


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id', ))
        return title.reviews.all().order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        )

    class Meta:
        ordering = ['-pub_date']


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id', )
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review, pk=self.kwargs.get('review_id'))
        )

    class Meta:
        ordering = ['-pub_date']
