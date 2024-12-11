from rest_framework import generics
from .serializers import UserLoginSerializer, UserRegisterSerializer
from ...utils.common import delete_otp_from_redis, generate_otp, reset_otp_attempts, store_otp_in_redis
from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import OTPConfirmSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ...utils.jwt import create_temp_token


class UserRegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserRegisterSerializer
	permission_classes = [AllowAny]
	authentication_classes = []


class UserLoginView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserLoginSerializer
	permission_classes = [AllowAny]
	authentication_classes = []
	throttle_scope = 'login'

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = serializer.validated_data["user"]

		# Generate temporary token
		tmp_token = create_temp_token(user.id)
		# Generate OTP
		code = generate_otp()

		# Store OTP in Redis
		store_otp_in_redis(user.id, code)

		# TODO: In real scenario: send code via email/SMS
		logger.debug(f"User {user.email} login: OTP code is {code}, temporary token is {tmp_token}")

		# temp_token = create_temp_token(user.id)
		return Response(
			{
				"message": "OTP sent successfully",
			}, status=status.HTTP_201_CREATED
		)


class OTPConfirmView(APIView):
	permission_classes = [AllowAny]
	authentication_classes = []
	throttle_scope = 'confirm_otp'

	@extend_schema(
		request=OTPConfirmSerializer,
		parameters=[
			OpenApiParameter(
				name="X-Temp-Token",
				description="Temporary token",
				required=True,
				location=OpenApiParameter.HEADER,
				type=str
			)
		]

	)
	def post(self, request):
		serializer = OTPConfirmSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)

		user_id = serializer.validated_data["user_id"]
		user = User.objects.get(id=user_id)

		# OTP is valid; reset attempts and remove OTP
		reset_otp_attempts(user_id)
		delete_otp_from_redis(user_id)

		# Create JWT with custom claims (email, full name)
		refresh = RefreshToken.for_user(user)
		# Add custom claims
		refresh['email'] = user.email
		full_name = f"{user.last_name} {user.first_name}"
		if user.patronymic:
			full_name += f" {user.patronymic}"
		refresh['full_name'] = full_name

		return Response(
			{
				"access": str(refresh.access_token),
				"refresh": str(refresh)
			}, status=status.HTTP_200_OK
		)
