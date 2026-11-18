"""Testes de contrato para a coleção /api/v1/tutores."""

from fastapi.testclient import TestClient


def test_crud_tutor(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/tutores")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_tutor"] == 1

    payload = {
        "id_tutor": 2,
        "nome_tutor": "Mariana Alves",
        "cpf_tutor": "456.789.123-22",
        "email_tutor": "mariana.alves@gmail.com",
        "telefone": "(11) 91234-5678",
        "observacoes": None,
    }
    create_resp = client.post("/api/v1/tutores", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["nome_tutor"] == "Mariana Alves"

    get_resp = client.get("/api/v1/tutores/2")
    assert get_resp.status_code == 200
    assert get_resp.json()["cpf_tutor"] == "456.789.123-22"

    updated = {**payload, "telefone": "(11) 99999-0000"}
    put_resp = client.put("/api/v1/tutores/2", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["telefone"] == "(11) 99999-0000"

    del_resp = client.delete("/api/v1/tutores/2", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/tutores/2").status_code == 404


def test_tutor_cpf_e_email_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/tutores",
            json={"id_tutor": 10, "nome_tutor": "João", "cpf_tutor": "12345678900"},
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/tutores",
            json={
                "id_tutor": 11,
                "nome_tutor": "João",
                "cpf_tutor": "123.456.789-00",
                "email_tutor": "email-invalido",
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
