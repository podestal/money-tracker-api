from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from . import models


class FilteredUserViewSet(UserViewSet):

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["username"]
