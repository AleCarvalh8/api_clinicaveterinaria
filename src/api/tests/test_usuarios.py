"""Testes de contrato para a coleção /api/v1/usuarios."""

from fastapi.testclient import TestClient


def test_listar_usuarios_seed_sem_senha(client: TestClient) -> None:
    response = client.get("/api/v1/usuarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id_usuario"] == 1
    assert data[0]["email_usuario"] == "juliana.santos@petegato.com"
    for item in data:
        assert "senha" not in item


def test_paginacao_usuarios(client: TestClient) -> None:
    response = client.get("/api/v1/usuarios?page=2&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_usuario"] == 2


def test_criar_obter_atualizar_e_remover_usuario(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    payload = {
        "id_usuario": 3,
        "nome_usuario": "Dr. Rafael Costa",
        "email_usuario": "rafael.costa@petegato.com",
        "senha": "Vet@2026Strong!",
        "perfil": "Veterinario",
    }
    create_resp = client.post("/api/v1/usuarios", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id_usuario"] == 3
    assert "senha" not in created

    get_resp = client.get("/api/v1/usuarios/3")
    assert get_resp.status_code == 200
    assert get_resp.json()["nome_usuario"] == "Dr. Rafael Costa"
    assert "senha" not in get_resp.json()

    updated_payload = {
        "id_usuario": 3,
        "nome_usuario": "Rafael Costa Atualizado",
        "email_usuario": "rafael.atualizado@petegato.com",
        "senha": "New@2026Pass!",
        "perfil": "Recepcao",
    }
    put_resp = client.put("/api/v1/usuarios/3", json=updated_payload, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["perfil"] == "Recepcao"
    assert "senha" not in put_resp.json()

    del_resp = client.delete("/api/v1/usuarios/3", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    not_found_resp = client.get("/api/v1/usuarios/3")
    assert not_found_resp.status_code == 404


def test_usuario_email_e_senha_invalidos_retornam_422(client: TestClient) -> None:
    bad_email = {
        "id_usuario": 10,
        "nome_usuario": "Teste",
        "email_usuario": "teste@gmail.com",
        "senha": "Vet@2026Strong!",
        "perfil": "Recepcao",
    }
    resp_email = client.post("/api/v1/usuarios", json=bad_email)
    assert resp_email.status_code == 422

    bad_password = {
        "id_usuario": 11,
        "nome_usuario": "Teste",
        "email_usuario": "teste@petegato.com",
        "senha": "fraca",
        "perfil": "Recepcao",
    }
    resp_pass = client.post("/api/v1/usuarios", json=bad_password)
    assert resp_pass.status_code == 422
