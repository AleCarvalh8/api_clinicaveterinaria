"""Testes de contrato para a coleção /api/v1/recepcao."""

from fastapi.testclient import TestClient


def test_crud_recepcao(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/recepcao")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["matricula"] == 1010

    payload = {
        "matricula": 2020,
        "cpf_recepcao": "321.654.987-00",
        "id_usuario": 2,
    }
    create_resp = client.post("/api/v1/recepcao", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["matricula"] == 2020

    get_resp = client.get("/api/v1/recepcao/2020")
    assert get_resp.status_code == 200
    assert get_resp.json()["cpf_recepcao"] == "321.654.987-00"

    updated = {**payload, "cpf_recepcao": "111.222.333-44"}
    put_resp = client.put("/api/v1/recepcao/2020", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["cpf_recepcao"] == "111.222.333-44"

    del_resp = client.delete("/api/v1/recepcao/2020", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/recepcao/2020").status_code == 404


def test_recepcao_fk_e_cpf_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/recepcao",
            json={"matricula": 3030, "cpf_recepcao": "111.222.333-44", "id_usuario": 999},
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/recepcao",
            json={"matricula": 3031, "cpf_recepcao": "11122233344", "id_usuario": 2},
            headers=auth_headers,
        ).status_code
        == 422
    )
