import os

from fastapi import Header, HTTPException


def require_app_token(x_app_token: str | None = Header(default=None, alias="X-App-Token")) -> None:
    expected = os.getenv("APP_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="APP_TOKEN no esta configurado.")
    if x_app_token != expected:
        raise HTTPException(status_code=401, detail="Token privado invalido.")
