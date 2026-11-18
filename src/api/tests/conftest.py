"""Fixtures compartilhadas com banco SQLite isolado por teste e autenticação JWT."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.database import get_db, init_db
from src.api.main import app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    """Fornece um TestClient conectado a um banco SQLite isolado por teste."""
    db_path = tmp_path / "test_petegato.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def _enable_fk(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    init_db(bind_engine=test_engine, session_factory=TestingSessionLocal)

    def _override_get_db() -> Generator[Session, None, None]:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    """Realiza login com o usuário veterinário do seed e retorna o header Bearer."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email_usuario": "juliana.santos@petegato.com",
            "senha": "Vet@2026Pass",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def recepcao_headers(client: TestClient) -> dict[str, str]:
    """Realiza login com o usuário de recepção do seed e retorna o header Bearer."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email_usuario": "marcos.oliveira@petegato.com",
            "senha": "Rec@2026Pass",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
