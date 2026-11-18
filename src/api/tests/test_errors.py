"""Testes transversais de conformidade do schema ErrorResponse (400, 401, 404, 422)."""

from fastapi.testclient import TestClient


def _assert_error_response(response, expected_status: int) -> dict:
    assert response.status_code == expected_status
    body = response.json()
    assert set(body.keys()) == {"mensagem", "detalhes"}
    assert "detail" not in body
    assert isinstance(body["mensagem"], str) and body["mensagem"]
    assert isinstance(body["detalhes"], str) and body["detalhes"]
    return body


def test_400_json_malformado_post_e_put(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp_post = client.post(
        "/api/v1/tutores",
        content="{json_invalido:",
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    _assert_error_response(resp_post, 400)

    resp_put = client.put(
        "/api/v1/tutores/1",
        content='{"id_tutor": 1,',
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    _assert_error_response(resp_put, 400)


def test_400_query_e_path_invalidos(client: TestClient) -> None:
    _assert_error_response(client.get("/api/v1/usuarios?page=0"), 400)
    _assert_error_response(client.get("/api/v1/usuarios?limit=101"), 400)
    _assert_error_response(client.get("/api/v1/usuarios?limit=abc"), 400)
    _assert_error_response(client.get("/api/v1/tutores/nao_inteiro"), 400)


def test_401_token_ausente_ou_invalido(client: TestClient) -> None:
    _assert_error_response(
        client.post(
            "/api/v1/tutores",
            json={"id_tutor": 99, "nome_tutor": "Sem Auth", "cpf_tutor": "111.222.333-44"},
        ),
        401,
    )
    _assert_error_response(
        client.get("/api/v1/auth/me", headers={"Authorization": "Bearer token-invalido"}),
        401,
    )


def test_404_recurso_inexistente_em_get_put_delete(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _assert_error_response(client.get("/api/v1/tutores/999999"), 404)
    _assert_error_response(
        client.put(
            "/api/v1/tutores/999999",
            json={
                "id_tutor": 999999,
                "nome_tutor": "Inexistente",
                "cpf_tutor": "111.222.333-44",
            },
            headers=auth_headers,
        ),
        404,
    )
    _assert_error_response(
        client.delete("/api/v1/tutores/999999", headers=auth_headers), 404
    )


def test_422_validacao_schema_pk_duplicada_fk_e_divergencia_put(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # Campo obrigatório ausente
    _assert_error_response(
        client.post("/api/v1/tutores", json={"id_tutor": 50}, headers=auth_headers), 422
    )

    # Chave primária duplicada (tutor 1 já existe no seed)
    _assert_error_response(
        client.post(
            "/api/v1/tutores",
            json={
                "id_tutor": 1,
                "nome_tutor": "Duplicado",
                "cpf_tutor": "111.222.333-44",
            },
            headers=auth_headers,
        ),
        422,
    )

    # Chave estrangeira inexistente
    _assert_error_response(
        client.post(
            "/api/v1/animais",
            json={
                "id_animal": 999,
                "id_tutor": 99999,
                "tipo_animal": "Gato",
                "raca": "SRD",
            },
            headers=auth_headers,
        ),
        422,
    )

    # Divergência entre ID do path e ID do corpo no PUT
    _assert_error_response(
        client.put(
            "/api/v1/tutores/1",
            json={
                "id_tutor": 2,
                "nome_tutor": "Divergente",
                "cpf_tutor": "111.222.333-44",
            },
            headers=auth_headers,
        ),
        422,
    )
