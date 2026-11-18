"""Router da coleção /api/v1/tutores."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, Tutor, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/tutores", tags=["Tutores"])


@router.get("", response_model=list[Tutor], status_code=status.HTTP_200_OK)
def listar_tutores(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Tutor]:
    """Retorna uma lista paginada de tutores."""
    return database.list_tutores(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Tutor,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_tutor(
    payload: Tutor,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Tutor:
    """Cadastra um novo tutor no sistema."""
    return database.create_tutor(db, payload)


@router.get(
    "/{id_tutor}",
    response_model=Tutor,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_tutor(id_tutor: int, db: Session = Depends(get_db)) -> Tutor:
    """Retorna os detalhes de um tutor específico por ID."""
    return database.get_tutor(db, id_tutor)


@router.put(
    "/{id_tutor}",
    response_model=Tutor,
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
def atualizar_tutor(
    id_tutor: int,
    payload: Tutor,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Tutor:
    """Atualiza integralmente os dados de um tutor existente."""
    return database.update_tutor(db, id_tutor, payload)


@router.delete(
    "/{id_tutor}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_tutor(
    id_tutor: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de tutor do sistema."""
    database.delete_tutor(db, id_tutor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
