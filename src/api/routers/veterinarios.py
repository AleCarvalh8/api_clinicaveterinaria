"""Router da coleção /api/v1/veterinarios."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, UsuarioResponse, Veterinario
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/veterinarios", tags=["Veterinários"])


@router.get("", response_model=list[Veterinario], status_code=status.HTTP_200_OK)
def listar_veterinarios(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Veterinario]:
    """Retorna uma lista paginada de veterinários."""
    return database.list_veterinarios(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Veterinario,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_veterinario(
    payload: Veterinario,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Veterinario:
    """Cadastra um novo veterinário no sistema."""
    return database.create_veterinario(db, payload)


@router.get(
    "/{crmv}",
    response_model=Veterinario,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_veterinario(crmv: int, db: Session = Depends(get_db)) -> Veterinario:
    """Retorna os detalhes de um veterinário específico por CRMV."""
    return database.get_veterinario(db, crmv)


@router.put(
    "/{crmv}",
    response_model=Veterinario,
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
def atualizar_veterinario(
    crmv: int,
    payload: Veterinario,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Veterinario:
    """Atualiza integralmente os dados de um veterinário existente."""
    return database.update_veterinario(db, crmv, payload)


@router.delete(
    "/{crmv}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_veterinario(
    crmv: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de veterinário do sistema."""
    database.delete_veterinario(db, crmv)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
