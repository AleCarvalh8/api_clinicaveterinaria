"""Exceções de domínio e handlers globais padronizados no schema ErrorResponse."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.database import (
    DatabaseDomainError,
    DuplicateKeyError,
    ForeignKeyViolationError,
    PathBodyMismatchError,
    ResourceNotFoundError,
)
from src.api.schemas import ErrorResponse


class BadRequestError(DatabaseDomainError):
    """Erro lançado para requisições inválidas ou parâmetros malformados (400)."""


class UnauthorizedError(DatabaseDomainError):
    """Erro lançado quando a autenticação falha ou o token JWT está ausente/inválido (401)."""


class ForbiddenError(DatabaseDomainError):
    """Erro lançado quando o usuário autenticado não tem perfil autorizado (403)."""


class SemanticValidationError(DatabaseDomainError):
    """Erro lançado para violações semânticas genéricas no payload (422)."""


def build_error_response(status_code: int, mensagem: str, detalhes: str) -> JSONResponse:
    """Constrói uma resposta JSON estritamente no schema ErrorResponse."""
    payload = ErrorResponse(mensagem=mensagem, detalhes=detalhes)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def _format_validation_details(errors: list[dict]) -> str:
    """Formata a lista de erros do Pydantic/FastAPI em uma descrição legível."""
    parts: list[str] = []
    for err in errors:
        loc = err.get("loc", ())
        field_path = ".".join(str(segment) for segment in loc if segment != "body")
        msg = err.get("msg", "Valor inválido")
        if field_path:
            parts.append(f"Campo '{field_path}': {msg}.")
        else:
            parts.append(f"{msg}.")
    return " ".join(parts) if parts else "Dados de entrada inválidos."


async def _request_validation_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Mapeia erros de query/path/json_invalid para 400 e erros de body para 422."""
    errors = exc.errors()
    is_json_invalid = any(err.get("type") == "json_invalid" for err in errors)
    is_query_or_path = any(
        (err.get("loc") or (None,))[0] in ("query", "path") for err in errors
    )

    if is_json_invalid:
        return build_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            mensagem="Requisição inválida",
            detalhes="O corpo da requisição não contém um JSON válido.",
        )

    if is_query_or_path:
        return build_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            mensagem="Requisição inválida",
            detalhes=_format_validation_details(errors),
        )

    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        mensagem="Erro de validação",
        detalhes=_format_validation_details(errors),
    )


async def _http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Converte qualquer HTTPException padrão para o schema ErrorResponse."""
    default_messages = {
        status.HTTP_400_BAD_REQUEST: "Requisição inválida",
        status.HTTP_401_UNAUTHORIZED: "Não autenticado",
        status.HTTP_403_FORBIDDEN: "Acesso negado",
        status.HTTP_404_NOT_FOUND: "Recurso não encontrado",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "Erro de validação",
    }
    mensagem = default_messages.get(exc.status_code, "Erro na requisição")
    detalhes = str(exc.detail) if exc.detail else mensagem
    return build_error_response(
        status_code=exc.status_code,
        mensagem=mensagem,
        detalhes=detalhes,
    )


async def _bad_request_handler(_request: Request, exc: BadRequestError) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        mensagem=exc.mensagem,
        detalhes=exc.detalhes,
    )


async def _unauthorized_handler(_request: Request, exc: UnauthorizedError) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        mensagem=exc.mensagem,
        detalhes=exc.detalhes,
    )


async def _forbidden_handler(_request: Request, exc: ForbiddenError) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        mensagem=exc.mensagem,
        detalhes=exc.detalhes,
    )


async def _not_found_handler(_request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        mensagem=exc.mensagem,
        detalhes=exc.detalhes,
    )


async def _semantic_validation_handler(
    _request: Request, exc: DatabaseDomainError
) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        mensagem=exc.mensagem,
        detalhes=exc.detalhes,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os exception handlers globais na instância FastAPI."""
    app.add_exception_handler(RequestValidationError, _request_validation_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(BadRequestError, _bad_request_handler)
    app.add_exception_handler(UnauthorizedError, _unauthorized_handler)
    app.add_exception_handler(ForbiddenError, _forbidden_handler)
    app.add_exception_handler(ResourceNotFoundError, _not_found_handler)
    app.add_exception_handler(SemanticValidationError, _semantic_validation_handler)
    app.add_exception_handler(DuplicateKeyError, _semantic_validation_handler)
    app.add_exception_handler(ForeignKeyViolationError, _semantic_validation_handler)
    app.add_exception_handler(PathBodyMismatchError, _semantic_validation_handler)
