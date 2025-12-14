from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import LoginSerializer
from core.jwt import build_jwt_for_user


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        if user.status != User.STATUS_ACTIVE:
            return Response({'detail': 'User not active'}, status=status.HTTP_403_FORBIDDEN)

        token, expires_in = build_jwt_for_user(user)
        response_data = {
            'access_token': token,
            'expires_in': expires_in,
            'token_type': 'Bearer',
        }
        return Response(response_data, status=status.HTTP_200_OK)
