"""Router da coleção /api/v1/recepcao."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, Recepcao, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/recepcao", tags=["Recepção"])


@router.get("", response_model=list[Recepcao], status_code=status.HTTP_200_OK)
def listar_recepcao(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Recepcao]:
    """Retorna uma lista paginada de funcionários de recepção."""
    return database.list_recepcao(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Recepcao,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_recepcao(
    payload: Recepcao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Recepcao:
    """Cadastra um novo atendente de recepção no sistema."""
    return database.create_recepcao(db, payload)


@router.get(
    "/{matricula}",
    response_model=Recepcao,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_recepcao(matricula: int, db: Session = Depends(get_db)) -> Recepcao:
    """Retorna os detalhes de um atendente de recepção por matrícula."""
    return database.get_recepcao(db, matricula)


@router.put(
    "/{matricula}",
    response_model=Recepcao,
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
def atualizar_recepcao(
    matricula: int,
    payload: Recepcao,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Recepcao:
    """Atualiza integralmente os dados de um atendente de recepção existente."""
    return database.update_recepcao(db, matricula, payload)


@router.delete(
    "/{matricula}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_recepcao(
    matricula: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de recepção do sistema."""
    database.delete_recepcao(db, matricula)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
