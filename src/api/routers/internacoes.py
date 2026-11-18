"""Router da coleção /api/v1/internacoes."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, Internacao, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/internacoes", tags=["Internações"])


@router.get("", response_model=list[Internacao], status_code=status.HTTP_200_OK)
def listar_internacoes(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Internacao]:
    """Retorna uma lista paginada de internações."""
    return database.list_internacoes(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Internacao,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_internacao(
    payload: Internacao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Internacao:
    """Cadastra uma nova internação no sistema."""
    return database.create_internacao(db, payload)


@router.get(
    "/{id_internacao}",
    response_model=Internacao,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_internacao(id_internacao: int, db: Session = Depends(get_db)) -> Internacao:
    """Retorna os detalhes de uma internação específica por ID."""
    return database.get_internacao(db, id_internacao)


@router.put(
    "/{id_internacao}",
    response_model=Internacao,
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
def atualizar_internacao(
    id_internacao: int,
    payload: Internacao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Internacao:
    """Atualiza integralmente os dados de uma internação existente."""
    return database.update_internacao(db, id_internacao, payload)


@router.delete(
    "/{id_internacao}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_internacao(
    id_internacao: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de internação do sistema."""
    database.delete_internacao(db, id_internacao)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
