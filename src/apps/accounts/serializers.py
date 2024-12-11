from rest_framework import serializers
from .models import User
from loguru import logger

from ...utils.common import get_otp_from_redis, increment_otp_attempts
from ...utils.jwt import verify_temp_token


class UserRegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	password_confirmation = serializers.CharField(write_only=True)

	class Meta:
		model = User
		fields = [
			'id',
			'email',
			'password',
			"password_confirmation",
			'first_name',
			'last_name',
			'patronymic',
			'phone_number',
			'gender',
			'birth_date',
		]

	def validate(self, attrs):
		password = attrs.get('password')
		password_confirmation = attrs.get('password_confirmation')

		if password != password_confirmation:
			logger.warning("User registration failed: passwords do not match.")
			raise serializers.ValidationError({"password_confirmation": "Passwords do not match."})
		return attrs

	def create(self, validated_data):
		validated_data.pop('password_confirmation', None)
		password = validated_data.pop('password')
		user = User.objects.create_user(**validated_data, password=password)
		logger.info(f"User registered successfully: {user.email}")
		return user


class UserLoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField(write_only=True)

	def validate(self, attrs):
		from django.contrib.auth import authenticate
		email = attrs.get("email")
		password = attrs.get("password")

		user = authenticate(username=email, password=password)

		if user is None:
			logger.info(f"Login attempt: email={email}, success=False")
			logger.warning(f"User login failed: invalid credentials for {email}")
			raise serializers.ValidationError("Invalid credentials")

		attrs["user"] = user

		logger.info(f"Login attempt: email={email}, success=True")
		return attrs


class OTPConfirmSerializer(serializers.Serializer):
	code = serializers.CharField()

	def validate(self, attrs):
		request = self.context.get('request')
		# Expect the temp token in headers (e.g., X-Temp-Token)
		temp_token = request.headers.get('X-Temp-Token')
		if not temp_token:
			raise serializers.ValidationError("Temporary token not provided in headers.")

		user_id = verify_temp_token(temp_token)
		if not user_id:
			raise serializers.ValidationError("Invalid or expired temporary token.")

		# Check OTP attempts
		attempts = increment_otp_attempts(user_id)
		if attempts > 5:
			raise serializers.ValidationError("Too many OTP attempts, please try again later.")

		stored_code: bytes = get_otp_from_redis(user_id)
		if not stored_code:
			raise serializers.ValidationError("OTP code expired or not found.")

		if stored_code.decode() != attrs['code']:
			raise serializers.ValidationError("Invalid OTP code.")

		attrs["user_id"] = user_id
		return attrs
