"""Testes de contrato para a coleção /api/v1/atendimentos."""

from fastapi.testclient import TestClient


def test_crud_atendimento(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/atendimentos")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_atendimento"] == 8001

    payload = {
        "id_atendimento": 8002,
        "id_prontuario": 1001,
        "hora_atendimento": "2026-10-06T11:00:00Z",
    }
    create_resp = client.post("/api/v1/atendimentos", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["id_atendimento"] == 8002

    get_resp = client.get("/api/v1/atendimentos/8002")
    assert get_resp.status_code == 200
    assert get_resp.json()["id_prontuario"] == 1001

    updated = {
        "id_atendimento": 8002,
        "id_prontuario": 1001,
        "hora_atendimento": "2026-10-06T11:15:00Z",
    }
    put_resp = client.put("/api/v1/atendimentos/8002", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200

    del_resp = client.delete("/api/v1/atendimentos/8002", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/atendimentos/8002").status_code == 404


def test_atendimento_fk_invalida(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/atendimentos",
            json={"id_atendimento": 8003, "id_prontuario": 9999},
            headers=auth_headers,
        ).status_code
        == 422
    )
