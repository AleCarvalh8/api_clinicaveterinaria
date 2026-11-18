"""Router da coleção /api/v1/usuarios."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, UsuarioCreate, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuários"])


@router.get("", response_model=list[UsuarioResponse], status_code=status.HTTP_200_OK)
def listar_usuarios(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[UsuarioResponse]:
    """Retorna uma lista paginada de usuários."""
    return database.list_usuarios(db, page=page, limit=limit)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        }
    },
)
def criar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)) -> UsuarioResponse:
    """Cadastra um novo usuário no sistema (rota pública para cadastro inicial)."""
    return database.create_usuario(db, payload)


@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_usuario(id_usuario: int, db: Session = Depends(get_db)) -> UsuarioResponse:
    """Retorna os detalhes de um usuário específico por ID."""
    return database.get_usuario(db, id_usuario)


@router.put(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def atualizar_usuario(
    id_usuario: int,
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> UsuarioResponse:
    """Atualiza integralmente os dados de um usuário existente."""
    return database.update_usuario(db, id_usuario, payload)


@router.delete(
    "/{id_usuario}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de usuário do sistema."""
    database.delete_usuario(db, id_usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
