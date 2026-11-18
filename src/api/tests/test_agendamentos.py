"""Testes de contrato para a coleção /api/v1/agendamentos."""

from fastapi.testclient import TestClient


def test_crud_agendamento(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/agendamentos")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_agendamento"] == 100

    payload = {
        "id_agendamento": 101,
        "hora_agendamento": "2026-10-06T10:00:00Z",
        "id_animal": 501,
        "crmv": 12345,
        "matricula": 1010,
    }
    create_resp = client.post("/api/v1/agendamentos", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["status_agendamento"] == "Agendado"

    get_resp = client.get("/api/v1/agendamentos/101")
    assert get_resp.status_code == 200

    updated = {**payload, "status_agendamento": "Em espera"}
    put_resp = client.put("/api/v1/agendamentos/101", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["status_agendamento"] == "Em espera"

    del_resp = client.delete("/api/v1/agendamentos/101", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/agendamentos/101").status_code == 404


def test_agendamento_enum_e_fk_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/agendamentos",
            json={
                "id_agendamento": 102,
                "hora_agendamento": "2026-10-06T10:00:00Z",
                "id_animal": 501,
                "crmv": 12345,
                "matricula": 1010,
                "status_agendamento": "Concluído",  # acento não existe no enum
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/agendamentos",
            json={
                "id_agendamento": 103,
                "hora_agendamento": "2026-10-06T10:00:00Z",
                "id_animal": 501,
                "crmv": 12345,
                "matricula": 9999,
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
