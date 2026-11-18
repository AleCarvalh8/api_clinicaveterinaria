"""Router da coleção /api/v1/agendamentos."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import Agendamento, ErrorResponse, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/agendamentos", tags=["Agendamentos"])


@router.get("", response_model=list[Agendamento], status_code=status.HTTP_200_OK)
def listar_agendamentos(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Agendamento]:
    """Retorna uma lista paginada de agendamentos."""
    return database.list_agendamentos(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Agendamento,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_agendamento(
    payload: Agendamento,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Agendamento:
    """Cadastra um novo agendamento no sistema."""
    return database.create_agendamento(db, payload)


@router.get(
    "/{id_agendamento}",
    response_model=Agendamento,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_agendamento(id_agendamento: int, db: Session = Depends(get_db)) -> Agendamento:
    """Retorna os detalhes de um agendamento específico por ID."""
    return database.get_agendamento(db, id_agendamento)


@router.put(
    "/{id_agendamento}",
    response_model=Agendamento,
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
def atualizar_agendamento(
    id_agendamento: int,
    payload: Agendamento,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Agendamento:
    """Atualiza integralmente os dados de um agendamento existente."""
    return database.update_agendamento(db, id_agendamento, payload)


@router.delete(
    "/{id_agendamento}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_agendamento(
    id_agendamento: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de agendamento do sistema."""
    database.delete_agendamento(db, id_agendamento)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
