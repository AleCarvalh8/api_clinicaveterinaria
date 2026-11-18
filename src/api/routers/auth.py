"""Router de autenticação JWT (/api/v1/auth)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.database import get_db, get_usuario_by_email, verify_password
from src.api.exceptions import UnauthorizedError
from src.api.schemas import ErrorResponse, LoginRequest, TokenResponse, UsuarioResponse
from src.api.security import create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Credenciais inválidas.",
        }
    },
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Autentica um usuário por e-mail e senha e retorna um token JWT Bearer."""
    user = get_usuario_by_email(db, payload.email_usuario)
    if user is None or not verify_password(payload.senha, user.senha_hash):
        raise UnauthorizedError(
            mensagem="Não autenticado",
            detalhes="E-mail ou senha inválidos.",
        )
    token = create_access_token(subject=user.id_usuario, perfil=user.perfil)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
        }
    },
)
def me(current_user: UsuarioResponse = Depends(get_current_user)) -> UsuarioResponse:
    """Retorna os dados públicos do usuário autenticado pelo token JWT."""
    return current_user
