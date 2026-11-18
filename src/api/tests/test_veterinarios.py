"""Testes de contrato para a coleção /api/v1/veterinarios."""

from fastapi.testclient import TestClient


def test_crud_veterinario(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/veterinarios")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["crmv"] == 12345

    payload = {
        "crmv": 54321,
        "cnpj": "98.765.432/0001-10",
        "especialidade": "Ortopedia Veterinária",
        "id_usuario": 1,
    }
    create_resp = client.post("/api/v1/veterinarios", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["crmv"] == 54321

    get_resp = client.get("/api/v1/veterinarios/54321")
    assert get_resp.status_code == 200
    assert get_resp.json()["especialidade"] == "Ortopedia Veterinária"

    updated = {**payload, "especialidade": "Cirurgia Geral"}
    put_resp = client.put("/api/v1/veterinarios/54321", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["especialidade"] == "Cirurgia Geral"

    del_resp = client.delete("/api/v1/veterinarios/54321", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/veterinarios/54321").status_code == 404


def test_veterinario_fk_e_cnpj_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    fk_invalida = {
        "crmv": 99999,
        "cnpj": "12.345.678/0001-90",
        "especialidade": "Dermatologia",
        "id_usuario": 999,
    }
    assert (
        client.post("/api/v1/veterinarios", json=fk_invalida, headers=auth_headers).status_code
        == 422
    )

    cnpj_invalido = {
        "crmv": 99998,
        "cnpj": "12345678000190",
        "especialidade": "Dermatologia",
        "id_usuario": 1,
    }
    assert (
        client.post("/api/v1/veterinarios", json=cnpj_invalido, headers=auth_headers).status_code
        == 422
    )
