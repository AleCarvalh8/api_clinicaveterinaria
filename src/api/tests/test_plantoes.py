"""Testes de contrato para a coleção /api/v1/plantoes."""

from fastapi.testclient import TestClient


def test_crud_plantao_e_campos_nulaveis(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    list_resp = client.get("/api/v1/plantoes")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_plantao"] == 3001

    payload = {
        "id_plantao": 3002,
        "id_animal": None,
        "id_tutor": None,
        "crmv": 12345,
        "evolucao_plantao": "Resgate de emergência sem tutor identificado.",
    }
    create_resp = client.post("/api/v1/plantoes", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["status_plantao"] == "Em analise"
    assert created["id_animal"] is None
    assert created["id_tutor"] is None

    get_resp = client.get("/api/v1/plantoes/3002")
    assert get_resp.status_code == 200

    updated = {
        "id_plantao": 3002,
        "id_animal": 501,
        "id_tutor": 1,
        "crmv": 12345,
        "status_plantao": "Obito",
        "evolucao_plantao": "Atualização de prontuário de urgência.",
    }
    put_resp = client.put("/api/v1/plantoes/3002", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["status_plantao"] == "Obito"

    del_resp = client.delete("/api/v1/plantoes/3002", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/plantoes/3002").status_code == 404


def test_plantao_fk_e_enum_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/plantoes",
            json={"id_plantao": 3003, "crmv": 12345, "id_animal": 9999},
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/plantoes",
            json={"id_plantao": 3004, "crmv": 12345, "status_plantao": "Em análise"},
            headers=auth_headers,
        ).status_code
        == 422
    )
