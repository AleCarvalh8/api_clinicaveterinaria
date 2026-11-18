"""Router da coleção /api/v1/animais."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import Animal, ErrorResponse, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/animais", tags=["Animais"])


@router.get("", response_model=list[Animal], status_code=status.HTTP_200_OK)
def listar_animais(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Animal]:
    """Retorna uma lista paginada de animais."""
    return database.list_animais(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Animal,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_animal(
    payload: Animal,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Animal:
    """Cadastra um novo animal no sistema."""
    return database.create_animal(db, payload)


@router.get(
    "/{id_animal}",
    response_model=Animal,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_animal(id_animal: int, db: Session = Depends(get_db)) -> Animal:
    """Retorna os detalhes de um animal específico por ID."""
    return database.get_animal(db, id_animal)


@router.put(
    "/{id_animal}",
    response_model=Animal,
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
def atualizar_animal(
    id_animal: int,
    payload: Animal,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Animal:
    """Atualiza integralmente os dados de um animal existente."""
    return database.update_animal(db, id_animal, payload)


@router.delete(
    "/{id_animal}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_animal(
    id_animal: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de animal do sistema."""
    database.delete_animal(db, id_animal)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
