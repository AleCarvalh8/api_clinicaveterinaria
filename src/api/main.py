"""Aplicação principal FastAPI da clínica veterinária Pet & Gatô."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.api.database import init_db
from src.api.exceptions import build_error_response, register_exception_handlers
from src.api.routers import (
    agendamentos,
    animais,
    atendimentos,
    auth,
    internacoes,
    plantoes,
    prontuarios,
    recepcao,
    tutores,
    usuarios,
    vacinacoes,
    veterinarios,
)

OPENAPI_TAGS = [
    {"name": "Autenticação"},
    {"name": "Usuários"},
    {"name": "Veterinários"},
    {"name": "Recepção"},
    {"name": "Tutores"},
    {"name": "Animais"},
    {"name": "Prontuários"},
    {"name": "Agendamentos"},
    {"name": "Atendimentos"},
    {"name": "Vacinações"},
    {"name": "Internações"},
    {"name": "Plantões"},
]


class MalformedJSONMiddleware:
    """Middleware ASGI que intercepta JSON malformado em POST/PUT retornando 400 ErrorResponse."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") not in ("POST", "PUT"):
            await self.app(scope, receive, send)
            return

        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        content_type = headers.get(b"content-type", b"").decode("latin-1").lower()
        if "application/json" not in content_type:
            await self.app(scope, receive, send)
            return

        body_chunks: list[bytes] = []
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.request":
                body_chunks.append(message.get("body", b""))
                more_body = message.get("more_body", False)
            elif message["type"] == "http.disconnect":
                return

        raw_body = b"".join(body_chunks)
        if raw_body.strip():
            try:
                json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                response = build_error_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    mensagem="Requisição inválida",
                    detalhes="O corpo da requisição contém JSON malformado.",
                )
                await response(scope, receive, send)
                return

        sent = False

        async def replay_receive() -> Message:
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": raw_body, "more_body": False}
            return await receive()

        await self.app(scope, replay_receive, send)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicializa o banco SQLite e o seed inicial na inicialização da aplicação."""
    init_db()
    yield


def create_app() -> FastAPI:
    """Cria e configura a instância FastAPI com CORS, middlewares, handlers e routers."""
    application = FastAPI(
        title="Módulo predefinido",
        description=(
            "API REST para o sistema de gestão da clínica veterinária Pet & Gatô, "
            "baseada no modelo relacional DDL (Oracle SQL Developer). Inclui gestão de "
            "usuários, funcionários (veterinários e recepção), tutores, animais, "
            "agendamentos, prontuários, atendimentos, vacinações, internações e plantões."
        ),
        version="1.0.0",
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(MalformedJSONMiddleware)

    register_exception_handlers(application)

    for router_module in (
        auth,
        usuarios,
        veterinarios,
        recepcao,
        tutores,
        animais,
        prontuarios,
        agendamentos,
        atendimentos,
        vacinacoes,
        internacoes,
        plantoes,
    ):
        application.include_router(router_module.router)

    return application


app = create_app()
