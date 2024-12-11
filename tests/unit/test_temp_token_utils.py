import pytest
from unittest.mock import patch
from freezegun import freeze_time
from datetime import datetime, timedelta
import jwt

from django.conf import settings

from src.utils.jwt import create_temp_token, verify_temp_token


@pytest.fixture
def temp_settings():
	old_secret = getattr(settings, 'TEMP_TOKEN_SECRET', None)
	old_algo = getattr(settings, 'TEMP_TOKEN_ALGO', None)
	old_exp = getattr(settings, 'TEMP_TOKEN_EXP_MINUTES', None)

	settings.TEMP_TOKEN_SECRET = 'test_secret'
	settings.TEMP_TOKEN_ALGO = 'HS256'
	settings.TEMP_TOKEN_EXP_MINUTES = 5

	yield

	# Возвращаем старые значения после тестов
	if old_secret is not None:
		settings.TEMP_TOKEN_SECRET = old_secret
	if old_algo is not None:
		settings.TEMP_TOKEN_ALGO = old_algo
	if old_exp is not None:
		settings.TEMP_TOKEN_EXP_MINUTES = old_exp


@pytest.mark.usefixtures("temp_settings")
class TestTempTokenUtils:

	def test_create_temp_token(self):
		user_id = 123
		token = create_temp_token(user_id)
		assert isinstance(token, str)

		decoded = jwt.decode(token, settings.TEMP_TOKEN_SECRET, algorithms=[settings.TEMP_TOKEN_ALGO])
		assert decoded['user_id'] == user_id
		assert decoded['type'] == 'otp'
		# Проверим, что exp присутствует
		assert 'exp' in decoded

	@freeze_time("2024-01-01 12:00:00")
	def test_verify_temp_token_success(self):
		user_id = 456
		token = create_temp_token(user_id)
		decoded_user_id = verify_temp_token(token)
		assert decoded_user_id == user_id

	@freeze_time("2024-01-01 12:00:00")
	def test_verify_temp_token_expired(self):
		user_id = 789
		token = create_temp_token(user_id)
		future_time = datetime.now() + timedelta(minutes=10)
		with freeze_time(future_time):
			assert verify_temp_token(token) is None

	def test_verify_temp_token_wrong_type(self):
		user_id = 111
		exp = datetime.now() + timedelta(minutes=settings.TEMP_TOKEN_EXP_MINUTES)
		wrong_payload = {
			"user_id": user_id,
			"exp": exp,
			"type": "wrong"
		}
		token = jwt.encode(wrong_payload, settings.TEMP_TOKEN_SECRET, algorithm=settings.TEMP_TOKEN_ALGO)
		assert verify_temp_token(token) is None

	def test_verify_temp_token_invalid_token(self):
		invalid_token = "this.is.not.valid"
		assert verify_temp_token(invalid_token) is None

	def test_verify_temp_token_modified_token(self):
		user_id = 222
		token = create_temp_token(user_id)

		modified_token = token.rsplit('.', 1)[0]
		assert verify_temp_token(modified_token) is None
