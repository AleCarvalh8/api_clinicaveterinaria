"""Router da coleção /api/v1/plantoes."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, Plantao, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/plantoes", tags=["Plantões"])


@router.get("", response_model=list[Plantao], status_code=status.HTTP_200_OK)
def listar_plantoes(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Plantao]:
    """Retorna uma lista paginada de plantões."""
    return database.list_plantoes(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Plantao,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_plantao(
    payload: Plantao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Plantao:
    """Cadastra um novo atendimento de plantão no sistema."""
    return database.create_plantao(db, payload)


@router.get(
    "/{id_plantao}",
    response_model=Plantao,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_plantao(id_plantao: int, db: Session = Depends(get_db)) -> Plantao:
    """Retorna os detalhes de um plantão específico por ID."""
    return database.get_plantao(db, id_plantao)


@router.put(
    "/{id_plantao}",
    response_model=Plantao,
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
def atualizar_plantao(
    id_plantao: int,
    payload: Plantao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Plantao:
    """Atualiza integralmente os dados de um plantão existente."""
    return database.update_plantao(db, id_plantao, payload)


@router.delete(
    "/{id_plantao}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_plantao(
    id_plantao: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de plantão do sistema."""
    database.delete_plantao(db, id_plantao)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
