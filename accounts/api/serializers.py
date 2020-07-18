from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    Serializer,
    CharField
)
from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password',)
        extra_kwargs = {"password": {"write_only": True}}


class ProfileSerializer(ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Profile
        fields = ('user',)

    def validate(self, data):
        username = data['user']['username']
        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            raise ValidationError()
        return data

    def create(self, validated_data):
        user = validated_data['user']
        username = user['username']
        password = user['password']
        # create user
        user_obj = User(
            username=username
        )
        user_obj.set_password(password)
        user_obj.save()
        Profile.objects.create(user=user_obj)
        return validated_data


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField()

    def validate(self, data):
        username = data["username"]
        password = data["password"]
        user = User.objects.filter(username=username).distinct()
        if user.exists and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("Incorrect username.")
        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect password. Please try again.")
        return data
