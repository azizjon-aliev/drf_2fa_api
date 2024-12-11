import string
import random
import redis
from django.conf import settings


redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def generate_otp(length: int = 6) -> str:
	""" Generate random OTP code """
	return "".join(random.choices(string.digits, k=length))


def store_otp_in_redis(user_id: str, code: str, ttl=300) -> None:
	# Store code with 5 minutes expiration
	redis_client.set(f"otp:{user_id}", code, ex=ttl)


def get_otp_from_redis(user_id: str) -> bytes | None:
	return redis_client.get(f"otp:{user_id}")


def delete_otp_from_redis(user_id: str) -> None:
	redis_client.delete(f"otp:{user_id}")


def increment_otp_attempts(user_id: str) -> int:
	key = f"otp_attempts:{user_id}"
	attempts = redis_client.incr(key)
	# Set expiry on first increment
	if attempts == 1:
		redis_client.expire(key, 300)  # Attempts to expire after 5 minutes
	return attempts


def get_otp_attempts(user_id: str) -> int:
	val = redis_client.get(f"otp_attempts:{user_id}")
	return int(val) if val else 0


def reset_otp_attempts(user_id: str) -> None:
	redis_client.delete(f"otp_attempts:{user_id}")
