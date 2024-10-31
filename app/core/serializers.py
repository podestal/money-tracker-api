from djoser.serializers import UserSerializer as BasedUserSerializer, UserCreateSerializer


class UserSerializer(BasedUserSerializer):
    class Meta(BasedUserSerializer.Meta):
        fields = ["id", "first_name", "last_name", "username", "email"]


class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ["id", "username", "password", "email", "first_name", "last_name"]
