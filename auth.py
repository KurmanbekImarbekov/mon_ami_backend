from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError


SECRET_KEY = "mon-ami-super-secret-key-change-later"

ALGORITHM = "HS256"


security = HTTPBearer()


def create_access_token(user_id, username, role):

    expire = datetime.now(timezone.utc) + timedelta(days=4)

    data = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Недействительный токен"
        )

    return payload


def require_role(required_role):

    def role_checker(
        current_user = Depends(get_current_user)
    ):

        if current_user["role"] != required_role:

            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав"
            )

        return current_user

    return role_checker