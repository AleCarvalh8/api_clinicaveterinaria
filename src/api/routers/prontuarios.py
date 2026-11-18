"""Router da coleção /api/v1/prontuarios."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api import database
from src.api.database import get_db
from src.api.schemas import ErrorResponse, Prontuario, UsuarioResponse
from src.api.security import get_current_user

router = APIRouter(prefix="/api/v1/prontuarios", tags=["Prontuários"])


@router.get("", response_model=list[Prontuario], status_code=status.HTTP_200_OK)
def listar_prontuarios(
    page: int = Query(default=1, ge=1, description="Número da página atual (1-indexed)"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Quantidade máxima de itens por página"
    ),
    db: Session = Depends(get_db),
) -> list[Prontuario]:
    """Retorna uma lista paginada de prontuários."""
    return database.list_prontuarios(db, page=page, limit=limit)


@router.post(
    "",
    response_model=Prontuario,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        422: {
            "model": ErrorResponse,
            "description": "Erro de validação semântica nos campos informados.",
        },
    },
)
def criar_prontuario(
    payload: Prontuario,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Prontuario:
    """Cadastra um novo prontuário no sistema."""
    return database.create_prontuario(db, payload)


@router.get(
    "/{id_prontuario}",
    response_model=Prontuario,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recurso não encontrado."}},
)
def obter_prontuario(id_prontuario: int, db: Session = Depends(get_db)) -> Prontuario:
    """Retorna os detalhes de um prontuário específico por ID."""
    return database.get_prontuario(db, id_prontuario)


@router.put(
    "/{id_prontuario}",
    response_model=Prontuario,
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
def atualizar_prontuario(
    id_prontuario: int,
    payload: Prontuario,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Prontuario:
    """Atualiza integralmente os dados de um prontuário existente."""
    return database.update_prontuario(db, id_prontuario, payload)


@router.delete(
    "/{id_prontuario}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado."},
        404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    },
)
def remover_prontuario(
    id_prontuario: int,
    db: Session = Depends(get_db),
    _current_user: UsuarioResponse = Depends(get_current_user),
) -> Response:
    """Remove o registro de prontuário do sistema."""
    database.delete_prontuario(db, id_prontuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
