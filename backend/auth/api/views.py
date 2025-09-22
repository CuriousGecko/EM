from access.api.models import Session
from auth.api.serializers import LoginSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.api.serializers import UserSerializer
from users.models import User


class LoginView(APIView):
    """Обработка логина пользователя."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Неверный email или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'Неверный email или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        session = Session.create_for_user(user)

        response = Response({
            'message': 'Вы вошли!',
            'user': UserSerializer(user).data
        })

        response.set_cookie(
            key='sessionid',
            value=session.session_id,
            expires=session.expire_at,
            httponly=True,
        )

        return response


class LogoutView(APIView):
    """Обработка выхода пользователя."""

    def post(self, request):
        session_id = request.COOKIES.get('sessionid')

        if not session_id:
            return Response(
                {'detail': 'Нет активной сессии.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = Session.objects.get(session_id=session_id, is_valid=True)
            session.is_valid = False
            session.save()
        except Session.DoesNotExist:
            return Response(
                {'detail': 'Сессия недействительна.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response(
            {'message': 'Сессия успешно закрыта.'},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('sessionid')

        return response
