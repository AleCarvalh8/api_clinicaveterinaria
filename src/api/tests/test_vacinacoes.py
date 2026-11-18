"""Testes de contrato para a coleção /api/v1/vacinacoes."""

from fastapi.testclient import TestClient


def test_crud_vacinacao(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/vacinacoes")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_vacinacao"] == 1

    payload = {
        "id_vacinacao": 2,
        "data_aplicacao": "2026-10-06T15:00:00Z",
        "crmv": 12345,
        "id_prontuario": 1001,
        "nome_vacina": "Antirrábica",
        "lote_vacina": "LOTE-2026A",
        "data_proxima_dose": "2027-10-06",
    }
    create_resp = client.post("/api/v1/vacinacoes", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["nome_vacina"] == "Antirrábica"

    get_resp = client.get("/api/v1/vacinacoes/2")
    assert get_resp.status_code == 200
    assert get_resp.json()["lote_vacina"] == "LOTE-2026A"

    updated = {**payload, "data_proxima_dose": None}
    put_resp = client.put("/api/v1/vacinacoes/2", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["data_proxima_dose"] is None

    del_resp = client.delete("/api/v1/vacinacoes/2", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/vacinacoes/2").status_code == 404


def test_vacinacao_fk_e_tamanho_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/vacinacoes",
            json={
                "id_vacinacao": 3,
                "data_aplicacao": "2026-10-06T15:00:00Z",
                "crmv": 99999,
                "id_prontuario": 1001,
                "nome_vacina": "V4",
                "lote_vacina": "L1",
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/vacinacoes",
            json={
                "id_vacinacao": 4,
                "data_aplicacao": "2026-10-06T15:00:00Z",
                "crmv": 12345,
                "id_prontuario": 1001,
                "nome_vacina": "X" * 31,
                "lote_vacina": "L1",
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
