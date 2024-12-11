import jwt
import redis
from datetime import datetime, timedelta
from django.conf import settings

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def create_temp_token(user_id: int) -> str:
	exp = datetime.now() + timedelta(minutes=settings.TEMP_TOKEN_EXP_MINUTES)
	payload = {
		"user_id": user_id,
		"exp": exp,
		"type": "otp"
	}
	return jwt.encode(payload, settings.TEMP_TOKEN_SECRET, algorithm=settings.TEMP_TOKEN_ALGO)


def verify_temp_token(token: str) -> str | None:
	try:
		payload = jwt.decode(token, settings.TEMP_TOKEN_SECRET, algorithms=[settings.TEMP_TOKEN_ALGO])
		if payload.get("type") != "otp":
			return None
		return payload["user_id"]
	except jwt.ExpiredSignatureError:
		return None
	except jwt.InvalidTokenError:
		return None
