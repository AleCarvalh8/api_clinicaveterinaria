"""Testes de contrato para a coleção /api/v1/prontuarios."""

from fastapi.testclient import TestClient


def test_crud_prontuario(client: TestClient, auth_headers: dict[str, str]) -> None:
    list_resp = client.get("/api/v1/prontuarios")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id_prontuario"] == 1001

    payload = {
        "id_prontuario": 1002,
        "crmv": 12345,
        "id_animal": 501,
        "peso_atual": 4.5,
        "queixa": "Tosse persistente há 3 dias.",
        "anamnese": "Sem histórico prévio de alergias.",
        "diagnostico": "Traqueobronquite infecciosa",
        "receita": "Repouso e acompanhamento",
        "vacina": None,
    }
    create_resp = client.post("/api/v1/prontuarios", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id_prontuario"] == 1002
    assert "data_abertura" in created

    get_resp = client.get("/api/v1/prontuarios/1002")
    assert get_resp.status_code == 200
    assert get_resp.json()["peso_atual"] == 4.5

    updated = {**payload, "peso_atual": 4.65, "diagnostico": "Traqueobronquite em melhora"}
    put_resp = client.put("/api/v1/prontuarios/1002", json=updated, headers=auth_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["peso_atual"] == 4.65

    del_resp = client.delete("/api/v1/prontuarios/1002", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.content == b""

    assert client.get("/api/v1/prontuarios/1002").status_code == 404


def test_prontuario_peso_e_fk_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.post(
            "/api/v1/prontuarios",
            json={
                "id_prontuario": 1003,
                "crmv": 12345,
                "id_animal": 501,
                "peso_atual": 0.0,
                "queixa": "Queixa",
                "diagnostico": "Diagnóstico",
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/prontuarios",
            json={
                "id_prontuario": 1004,
                "crmv": 99999,
                "id_animal": 501,
                "peso_atual": 3.2,
                "queixa": "Queixa",
                "diagnostico": "Diagnóstico",
            },
            headers=auth_headers,
        ).status_code
        == 422
    )
