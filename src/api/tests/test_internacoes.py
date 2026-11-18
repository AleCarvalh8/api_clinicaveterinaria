"""Testes de contrato para a coleção /api/v1/internacoes."""

from fastapi.testclient import TestClient


def test_crud_internacao(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/internacoes")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_internacao"] == 4001

    payload = {
        "id_internacao": 4002,
        "id_animal": 501,
        "crmv": 12345,
        "nivel_gravidade": "Critica",
        "evolucao_internacao": "Monitoramento intensivo.",
    }
    create_resp = client.post("/api/v1/internacoes", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["status_internacao"] == "Internado"
    assert created["nivel_gravidade"] == "Critica"

    get_resp = client.get("/api/v1/internacoes/4002")
    assert get_resp.status_code == 200

    updated = {
        **payload,
        "status_internacao": "Alta",
        "data_alta": "2026-10-07T09:00:00Z",
    }
    put_resp = client.put("/api/v1/internacoes/4002", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["status_internacao"] == "Alta"

    del_resp = client.delete("/api/v1/internacoes/4002", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/internacoes/4002").status_code == 404


def test_internacao_enum_e_fk_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/internacoes",
            json={
                "id_internacao": 4003,
                "id_animal": 501,
                "crmv": 12345,
                "nivel_gravidade": "Médio",  # acento inválido
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/internacoes",
            json={"id_internacao": 4004, "id_animal": 9999, "crmv": 12345},
            headers=auth_headers,
        ).status_code
        == 422
    )
