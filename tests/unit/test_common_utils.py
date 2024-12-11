import pytest
from unittest.mock import patch, MagicMock

from src.utils.common import (
	delete_otp_from_redis, generate_otp, get_otp_attempts, get_otp_from_redis, increment_otp_attempts,
	reset_otp_attempts, store_otp_in_redis,
)


@pytest.mark.django_db
class TestOTPUtils:
	def test_generate_otp(self):
		otp = generate_otp(length=6)
		assert len(otp) == 6
		assert otp.isdigit()

		# Проверим разный длины
		otp_4 = generate_otp(length=4)
		assert len(otp_4) == 4

	@patch("src.utils.common.redis_client")
	def test_store_otp_in_redis(self, mock_redis):
		store_otp_in_redis("user123", "123456", ttl=300)
		mock_redis.set.assert_called_once_with("otp:user123", "123456", ex=300)

	@patch("src.utils.common.redis_client")
	def test_get_otp_from_redis(self, mock_redis):
		mock_redis.get.return_value = b"654321"
		otp = get_otp_from_redis("user123")
		assert otp == b"654321"
		mock_redis.get.assert_called_once_with("otp:user123")

	@patch("src.utils.common.redis_client")
	def test_delete_otp_from_redis(self, mock_redis):
		delete_otp_from_redis("user123")
		mock_redis.delete.assert_called_once_with("otp:user123")

	@patch("src.utils.common.redis_client")
	def test_increment_otp_attempts(self, mock_redis):
		# Первый вызов incr вернёт 1
		mock_redis.incr.return_value = 1
		attempts = increment_otp_attempts("user123")
		assert attempts == 1
		mock_redis.incr.assert_called_once_with("otp_attempts:user123")
		mock_redis.expire.assert_called_once_with("otp_attempts:user123", 300)

		# Второй вызов incr вернёт 2
		mock_redis.reset_mock()
		mock_redis.incr.return_value = 2
		attempts = increment_otp_attempts("user123")
		assert attempts == 2
		mock_redis.incr.assert_called_once_with("otp_attempts:user123")
		# На второй раз expire уже не вызывается
		mock_redis.expire.assert_not_called()

	@patch("src.utils.common.redis_client")
	def test_get_otp_attempts(self, mock_redis):
		mock_redis.get.return_value = b"2"
		attempts = get_otp_attempts("user123")
		assert attempts == 2

		mock_redis.get.return_value = None
		attempts = get_otp_attempts("user456")
		assert attempts == 0

	@patch("src.utils.common.redis_client")
	def test_reset_otp_attempts(self, mock_redis):
		reset_otp_attempts("user123")
		mock_redis.delete.assert_called_once_with("otp_attempts:user123")
