"""Testes de contrato para a coleção /api/v1/animais."""

from fastapi.testclient import TestClient


def test_crud_animal(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/animais")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["nome_animal"] == "Mingau"

    payload = {
        "id_animal": 502,
        "id_tutor": 1,
        "nome_animal": "Thor",
        "tipo_animal": "Cachorro",
        "raca": "Golden Retriever",
        "sexo": "M",
        "data_nascimento": "2022-03-10",
    }
    create_resp = client.post("/api/v1/animais", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["id_animal"] == 502

    get_resp = client.get("/api/v1/animais/502")
    assert get_resp.status_code == 200
    assert get_resp.json()["raca"] == "Golden Retriever"

    updated = {**payload, "nome_animal": "Thorzinho", "sexo": "F"}
    put_resp = client.put("/api/v1/animais/502", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["nome_animal"] == "Thorzinho"

    del_resp = client.delete("/api/v1/animais/502", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/animais/502").status_code == 404


def test_animal_fk_e_sexo_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/animais",
            json={"id_animal": 503, "id_tutor": 999, "tipo_animal": "Gato", "raca": "Persa"},
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/animais",
            json={
                "id_animal": 504,
                "id_tutor": 1,
                "tipo_animal": "Gato",
                "raca": "Persa",
                "sexo": "X",
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
