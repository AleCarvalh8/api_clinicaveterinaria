"""Módulo de autenticação JWT HS256 e controle de acesso baseado em perfil (RBAC)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import ForbiddenError, UnauthorizedError
from src.api.models import UsuarioModel
from src.api.schemas import PerfilUsuario, UsuarioResponse

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "petegato-clinica-vet-jwt-secret-key-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

_bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str | int,
    perfil: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Gera um token JWT HS256 assinado contendo o identificador e perfil do usuário."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(subject),
        "perfil": perfil,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decodifica e valida a assinatura e expiração de um token JWT HS256."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="O token de autenticação expirou.",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="Token de autenticação inválido.",
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    """Valida o header Authorization Bearer e retorna o usuário autenticado."""
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="Token de autenticação Bearer não informado.",
        )

    payload = decode_access_token(credentials.credentials)
    sub = payload.get("sub")
    if sub is None:
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="Token de autenticação sem identificador de usuário.",
        )

    try:
        user_id = int(sub)
    except ValueError as exc:
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="Identificador de usuário inválido no token.",
        ) from exc

    user = db.get(UsuarioModel, user_id)
    if user is None:
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="Usuário associado ao token não foi encontrado.",
        )
    return UsuarioResponse.model_validate(user)


def require_perfil(*perfis: PerfilUsuario | str) -> Callable[[UsuarioResponse], UsuarioResponse]:
    """Cria uma dependência FastAPI que restringe o acesso aos perfis informados."""
    allowed = {p.value if isinstance(p, PerfilUsuario) else str(p) for p in perfis}

    def _check_perfil(current_user: UsuarioResponse = Depends(get_current_user)) -> UsuarioResponse:
        if current_user.perfil.value not in allowed:
            raise ForbiddenError(
                mensagem="Acesso negado",
                detalhes=(
                    f"O perfil '{current_user.perfil.value}' não possui permissão "
                    "para executar esta operação."
                ),
            )
        return current_user

    return _check_perfil
