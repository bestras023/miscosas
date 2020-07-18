from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import *


class ListUsers(APIView):

    def get(self, request):
        usernames = [profile.user.username for profile in Profile.objects.all()]
        return Response(usernames)


class RegisterUser(CreateAPIView):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()


class LoginUser(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            return Response(new_data['username'], status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
