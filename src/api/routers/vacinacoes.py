"""Router da coleção /api/v1/vacinacoes."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, UsuarioResponse, Vacinacao
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/vacinacoes", tags=["Vacinações"])


@router.get("", response_model=list[Vacinacao], status_code=status.HTTP_200_OK)
def listar_vacinacoes(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Vacinacao]:
    """Retorna uma lista paginada de vacinações."""
    return database.list_vacinacoes(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Vacinacao,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_vacinacao(
    payload: Vacinacao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Vacinacao:
    """Cadastra uma nova vacinação no sistema."""
    return database.create_vacinacao(db, payload)


@router.get(
    "/{id_vacinacao}",
    response_model=Vacinacao,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_vacinacao(id_vacinacao: int, db: Session = Depends(get_db)) -> Vacinacao:
    """Retorna os detalhes de uma vacinação específica por ID."""
    return database.get_vacinacao(db, id_vacinacao)


@router.put(
    "/{id_vacinacao}",
    response_model=Vacinacao,
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
def atualizar_vacinacao(
    id_vacinacao: int,
    payload: Vacinacao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Vacinacao:
    """Atualiza integralmente os dados de uma vacinação existente."""
    return database.update_vacinacao(db, id_vacinacao, payload)


@router.delete(
    "/{id_vacinacao}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_vacinacao(
    id_vacinacao: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de vacinação do sistema."""
    database.delete_vacinacao(db, id_vacinacao)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
