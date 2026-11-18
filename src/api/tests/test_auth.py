"""Testes de autenticação JWT HS256, /auth/me e controle de acesso RBAC (401/403)."""

from fastapi import Depends
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.schemas import PerfilUsuario, UsuarioResponse
from src.api.security import require_perfil


def test_login_sucesso_e_auth_me(client: TestClient) -> None:
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email_usuario": "juliana.santos@petegato.com",
            "senha": "Vet@2026Pass",
        },
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert token_data["token_type"] == "bearer"
    assert isinstance(token_data["access_token"], str) and token_data["access_token"]

    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["id_usuario"] == 1
    assert me_data["email_usuario"] == "juliana.santos@petegato.com"
    assert me_data["perfil"] == "Veterinario"
    assert "senha" not in me_data


def test_login_credenciais_invalidas_retorna_401(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email_usuario": "juliana.santos@petegato.com",
            "senha": "SenhaErrada!99",
        },
    )
    assert resp.status_code == 401
    body = resp.json()
    assert set(body.keys()) == {"mensagem", "detalhes"}
    assert "detail" not in body


def test_auth_me_e_rota_protegida_sem_token_retornam_401(client: TestClient) -> None:
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401
    assert set(me_resp.json().keys()) == {"mensagem", "detalhes"}

    post_resp = client.post(
        "/api/v1/tutores",
        json={
            "id_tutor": 99,
            "nome_tutor": "Sem Token",
            "cpf_tutor": "111.222.333-44",
        },
    )
    assert post_resp.status_code == 401
    assert set(post_resp.json().keys()) == {"mensagem", "detalhes"}


def test_require_perfil_retorna_403_para_perfil_nao_autorizado(
    client: TestClient, recepcao_headers: dict[str, str]
) -> None:
    route_path = "/api/v1/_test-rbac-veterinario"

    @app.get(route_path)
    def _only_vet(
        current_user: UsuarioResponse = Depends(require_perfil(PerfilUsuario.VETERINARIO)),
    ) -> UsuarioResponse:
        return current_user

    try:
        resp = client.get(route_path, headers=recepcao_headers)
        assert resp.status_code == 403
        body = resp.json()
        assert set(body.keys()) == {"mensagem", "detalhes"}
        assert "detail" not in body
    finally:
        app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != route_path]
