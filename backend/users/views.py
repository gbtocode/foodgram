from api.paginators import CustomPagination
from api.serializers import SubscriberSerializer, SubscriptionSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.serializers import UsersSerializer

from .models import Subscriber, User


class UserViewSet(UserViewSet):
    """Переопределенный вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    @action(['GET'], permission_classes=(IsAuthenticated,), detail=False)
    def me(self, request):
        serializer = UsersSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(['GET'], detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscriber__in=request.user.subscriber.all()
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={
                    'request': request
                }
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset,
            context={
                'request': request
            },
            many=True
        )
        return Response(serializer.data)

    @action(['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,),
            detail=True
            )
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            author_to_sub = get_object_or_404(User, pk=id)
            serializer = SubscriberSerializer(
                data={'author': author_to_sub.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            user = request.user
            author_to_unsub = get_object_or_404(User, pk=id)
            try:
                subscription = Subscriber.objects.get(
                    author=user,
                    subscriber=author_to_unsub
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscriber.DoesNotExist:
                return Response(
                    {'errors': 'Подписка не найдена.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
