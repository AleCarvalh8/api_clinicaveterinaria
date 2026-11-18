"""Router da coleção /api/v1/atendimentos."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import Atendimento, ErrorResponse, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/atendimentos", tags=["Atendimentos"])


@router.get("", response_model=list[Atendimento], status_code=status.HTTP_200_OK)
def listar_atendimentos(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Atendimento]:
    """Retorna uma lista paginada de atendimentos."""
    return database.list_atendimentos(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Atendimento,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_atendimento(
    payload: Atendimento,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Atendimento:
    """Cadastra um novo atendimento no sistema."""
    return database.create_atendimento(db, payload)


@router.get(
    "/{id_atendimento}",
    response_model=Atendimento,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_atendimento(id_atendimento: int, db: Session = Depends(get_db)) -> Atendimento:
    """Retorna os detalhes de um atendimento específico por ID."""
    return database.get_atendimento(db, id_atendimento)


@router.put(
    "/{id_atendimento}",
    response_model=Atendimento,
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
def atualizar_atendimento(
    id_atendimento: int,
    payload: Atendimento,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Atendimento:
    """Atualiza integralmente os dados de um atendimento existente."""
    return database.update_atendimento(db, id_atendimento, payload)


@router.delete(
    "/{id_atendimento}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de atendimento do sistema."""
    database.delete_atendimento(db, id_atendimento)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
