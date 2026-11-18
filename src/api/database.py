"""Camada de persistência SQLAlchemy 2.0 + SQLite para a API Pet & Gatô."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable, Generator
from datetime import date, datetime, timezone
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.models import (
    AgendamentoModel,
    AnimalModel,
    AtendimentoModel,
    Base,
    InternacaoModel,
    PlantaoModel,
    ProntuarioModel,
    RecepcaoModel,
    TutorModel,
    UsuarioModel,
    VacinacaoModel,
    VeterinarioModel,
)
from src.api.schemas import (
    Agendamento,
    Animal,
    Atendimento,
    Internacao,
    NivelGravidade,
    PerfilUsuario,
    Plantao,
    Prontuario,
    Recepcao,
    SexoAnimal,
    StatusAgendamento,
    StatusInternacao,
    StatusPlantao,
    Tutor,
    UsuarioCreate,
    UsuarioResponse,
    Vacinacao,
    Veterinario,
)

TModel = TypeVar("TModel", bound=Base)
TSchema = TypeVar("TSchema", bound=BaseModel)

SQLALCHEMY_DATABASE_URL = "sqlite:///./petegato.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
    """Habilita a verificação de chaves estrangeiras em todas as conexões SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseDomainError(Exception):
    """Exceção base para erros de integridade, consulta e autenticação."""

    def __init__(self, mensagem: str, detalhes: str) -> None:
        self.mensagem = mensagem
        self.detalhes = detalhes
        super().__init__(detalhes)


class ResourceNotFoundError(DatabaseDomainError):
    """Erro lançado quando o recurso solicitado não existe (404)."""


class DuplicateKeyError(DatabaseDomainError):
    """Erro lançado ao tentar inserir uma chave primária ou única já existente (422)."""


class ForeignKeyViolationError(DatabaseDomainError):
    """Erro lançado quando uma chave estrangeira referencia registro inexistente (422)."""


class PathBodyMismatchError(DatabaseDomainError):
    """Erro lançado quando o identificador no corpo diverge do path no PUT (422)."""


def hash_password(senha: str) -> str:
    """Gera hash PBKDF2-HMAC-SHA256 com salt aleatório para armazenar senhas sem texto puro."""
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${derived.hex()}"


def verify_password(senha: str, senha_hash: str) -> bool:
    """Verifica uma senha em texto puro contra o hash PBKDF2 armazenado."""
    try:
        salt, expected_hex = senha_hash.split("$", 1)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return hmac.compare_digest(derived.hex(), expected_hex)


def seed_db(session: Session) -> None:
    """Popula registros iniciais de exemplo de forma idempotente."""
    if session.scalar(select(UsuarioModel.id_usuario).limit(1)) is not None:
        return

    session.add_all(
        [
            UsuarioModel(
                id_usuario=1,
                nome_usuario="Dra. Juliana Santos",
                email_usuario="juliana.santos@petegato.com",
                senha_hash=hash_password("Vet@2026Pass"),
                perfil=PerfilUsuario.VETERINARIO.value,
            ),
            UsuarioModel(
                id_usuario=2,
                nome_usuario="Marcos Oliveira",
                email_usuario="marcos.oliveira@petegato.com",
                senha_hash=hash_password("Rec@2026Pass"),
                perfil=PerfilUsuario.RECEPCAO.value,
            ),
        ]
    )
    session.flush()

    session.add_all(
        [
            VeterinarioModel(
                crmv=12345,
                cnpj="12.345.678/0001-90",
                especialidade="Felinos e Clínica Médica",
                id_usuario=1,
            ),
            RecepcaoModel(
                matricula=1010,
                cpf_recepcao="123.456.789-00",
                id_usuario=2,
            ),
            TutorModel(
                id_tutor=1,
                nome_tutor="Carlos Eduardo Lima",
                cpf_tutor="987.654.321-11",
                email_tutor="carlos.edu@gmail.com",
                telefone="(11) 98765-4321",
                observacoes="Prefere contato por mensagem de texto.",
            ),
        ]
    )
    session.flush()

    session.add(
        AnimalModel(
            id_animal=501,
            id_tutor=1,
            nome_animal="Mingau",
            tipo_animal="Gato",
            raca="Siamês",
            sexo=SexoAnimal.MACHO.value,
            data_nascimento=date(2021, 6, 15),
        )
    )
    session.flush()

    session.add(
        ProntuarioModel(
            id_prontuario=1001,
            crmv=12345,
            id_animal=501,
            data_abertura=datetime(2026, 10, 5, 14, 30, 0, tzinfo=timezone.utc),
            peso_atual=4.35,
            queixa="Falta de apetite e letargia há 2 dias.",
            anamnese="Animal alimentado com ração seca; troca recente de marca.",
            diagnostico="Gastrite leve por mudança de ração",
            receita="Omeprazol 10mg SID por 7 dias",
            vacina="Nenhuma administrada na consulta",
        )
    )
    session.flush()

    session.add_all(
        [
            AgendamentoModel(
                id_agendamento=100,
                hora_agendamento=datetime(2026, 10, 5, 14, 30, 0, tzinfo=timezone.utc),
                id_animal=501,
                crmv=12345,
                matricula=1010,
                status_agendamento=StatusAgendamento.AGENDADO.value,
            ),
            AtendimentoModel(
                id_atendimento=8001,
                id_prontuario=1001,
                hora_atendimento=datetime(2026, 10, 5, 14, 35, 10, tzinfo=timezone.utc),
            ),
            VacinacaoModel(
                id_vacinacao=1,
                data_aplicacao=datetime(2026, 10, 5, 15, 0, 0, tzinfo=timezone.utc),
                crmv=12345,
                id_prontuario=1001,
                nome_vacina="V4 Felina",
                lote_vacina="LOTE-99882B",
                data_proxima_dose=date(2027, 10, 5),
            ),
            InternacaoModel(
                id_internacao=4001,
                id_animal=501,
                crmv=12345,
                data_internacao=datetime(2026, 10, 5, 16, 0, 0, tzinfo=timezone.utc),
                data_alta=None,
                nivel_gravidade=NivelGravidade.MEDIO.value,
                status_internacao=StatusInternacao.INTERNADO.value,
                evolucao_internacao="Paciente em observação com hidratação intravenosa.",
            ),
            PlantaoModel(
                id_plantao=3001,
                id_animal=501,
                id_tutor=1,
                crmv=12345,
                chegada_plantao=datetime(2026, 10, 5, 22, 15, 0, tzinfo=timezone.utc),
                status_plantao=StatusPlantao.EM_ANALISE.value,
                evolucao_plantao="Triagem inicial realizada no plantão noturno.",
            ),
        ]
    )
    session.commit()


def init_db(bind_engine: Engine = engine, session_factory: sessionmaker = SessionLocal) -> None:
    """Cria o schema no banco SQLite e executa o seed inicial."""
    Base.metadata.create_all(bind=bind_engine)
    with session_factory() as session:
        seed_db(session)


def get_db() -> Generator[Session, None, None]:
    """Dependência FastAPI que fornece e encerra a sessão SQLAlchemy por requisição."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _require_fk(
    session: Session,
    model_cls: type[TModel],
    key: int,
    fk_name: str,
    target_name: str,
) -> None:
    if session.get(model_cls, key) is None:
        raise ForeignKeyViolationError(
            mensagem="Erro de integridade referencial",
            detalhes=f"O campo '{fk_name}' referencia '{target_name}' com ID {key}, que não existe.",
        )


def _list_records(
    session: Session,
    model_cls: type[TModel],
    pk_col,
    schema_cls: type[TSchema],
    page: int,
    limit: int,
) -> list[TSchema]:
    offset = (page - 1) * limit
    rows = session.scalars(select(model_cls).order_by(pk_col).offset(offset).limit(limit)).all()
    return [schema_cls.model_validate(row) for row in rows]


def _get_record(
    session: Session,
    model_cls: type[TModel],
    item_id: int,
    schema_cls: type[TSchema],
    resource_name: str,
) -> TSchema:
    row = session.get(model_cls, item_id)
    if row is None:
        raise ResourceNotFoundError(
            mensagem="Recurso não encontrado",
            detalhes=f"{resource_name} com identificador {item_id} não foi encontrado.",
        )
    return schema_cls.model_validate(row)


def _create_record(
    session: Session,
    model_cls: type[TModel],
    payload: TSchema,
    pk_attr: str,
    schema_cls: type[TSchema],
    resource_name: str,
    fk_validator: Callable[[Session, TSchema], None] | None = None,
) -> TSchema:
    pk_val = getattr(payload, pk_attr)
    if session.get(model_cls, pk_val) is not None:
        raise DuplicateKeyError(
            mensagem="Erro de validação semântica",
            detalhes=f"Já existe {resource_name} cadastrado com '{pk_attr}' igual a {pk_val}.",
        )
    if fk_validator is not None:
        fk_validator(session, payload)
    row = model_cls(**payload.model_dump(mode="python"))
    # Converte enums para seus valores literais ao gravar no SQLite
    for field_name, value in payload.model_dump(mode="python").items():
        if hasattr(value, "value"):
            setattr(row, field_name, value.value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return schema_cls.model_validate(row)


def _update_record(
    session: Session,
    model_cls: type[TModel],
    path_id: int,
    payload: TSchema,
    pk_attr: str,
    schema_cls: type[TSchema],
    resource_name: str,
    fk_validator: Callable[[Session, TSchema], None] | None = None,
) -> TSchema:
    row = session.get(model_cls, path_id)
    if row is None:
        raise ResourceNotFoundError(
            mensagem="Recurso não encontrado",
            detalhes=f"{resource_name} com identificador {path_id} não foi encontrado.",
        )
    body_id = getattr(payload, pk_attr)
    if body_id != path_id:
        raise PathBodyMismatchError(
            mensagem="Erro de validação semântica",
            detalhes=(
                f"O identificador '{pk_attr}' no corpo ({body_id}) "
                f"diverge do identificador na URL ({path_id})."
            ),
        )
    if fk_validator is not None:
        fk_validator(session, payload)
    for field_name, value in payload.model_dump(mode="python").items():
        setattr(row, field_name, value.value if hasattr(value, "value") else value)
    session.commit()
    session.refresh(row)
    return schema_cls.model_validate(row)


def _delete_record(
    session: Session,
    model_cls: type[TModel],
    item_id: int,
    resource_name: str,
) -> None:
    row = session.get(model_cls, item_id)
    if row is None:
        raise ResourceNotFoundError(
            mensagem="Recurso não encontrado",
            detalhes=f"{resource_name} com identificador {item_id} não foi encontrado.",
        )
    session.delete(row)
    session.commit()


# --- Validadores de Chave Estrangeira ---


def _validate_usuario_fk(session: Session, item: Veterinario | Recepcao) -> None:
    _require_fk(session, UsuarioModel, item.id_usuario, "id_usuario", "usuarios")


def _validate_animal_fk(session: Session, item: Animal) -> None:
    _require_fk(session, TutorModel, item.id_tutor, "id_tutor", "tutores")


def _validate_prontuario_fk(session: Session, item: Prontuario) -> None:
    _require_fk(session, VeterinarioModel, item.crmv, "crmv", "veterinarios")
    _require_fk(session, AnimalModel, item.id_animal, "id_animal", "animais")


def _validate_agendamento_fk(session: Session, item: Agendamento) -> None:
    _require_fk(session, AnimalModel, item.id_animal, "id_animal", "animais")
    _require_fk(session, VeterinarioModel, item.crmv, "crmv", "veterinarios")
    _require_fk(session, RecepcaoModel, item.matricula, "matricula", "recepcao")


def _validate_atendimento_fk(session: Session, item: Atendimento) -> None:
    _require_fk(session, ProntuarioModel, item.id_prontuario, "id_prontuario", "prontuarios")


def _validate_vacinacao_fk(session: Session, item: Vacinacao) -> None:
    _require_fk(session, VeterinarioModel, item.crmv, "crmv", "veterinarios")
    _require_fk(session, ProntuarioModel, item.id_prontuario, "id_prontuario", "prontuarios")


def _validate_internacao_fk(session: Session, item: Internacao) -> None:
    _require_fk(session, AnimalModel, item.id_animal, "id_animal", "animais")
    _require_fk(session, VeterinarioModel, item.crmv, "crmv", "veterinarios")


def _validate_plantao_fk(session: Session, item: Plantao) -> None:
    _require_fk(session, VeterinarioModel, item.crmv, "crmv", "veterinarios")
    if item.id_animal is not None:
        _require_fk(session, AnimalModel, item.id_animal, "id_animal", "animais")
    if item.id_tutor is not None:
        _require_fk(session, TutorModel, item.id_tutor, "id_tutor", "tutores")


# --- Usuários ---


def list_usuarios(session: Session, page: int, limit: int) -> list[UsuarioResponse]:
    return _list_records(
        session, UsuarioModel, UsuarioModel.id_usuario, UsuarioResponse, page, limit
    )


def get_usuario(session: Session, id_usuario: int) -> UsuarioResponse:
    return _get_record(session, UsuarioModel, id_usuario, UsuarioResponse, "Usuário")


def get_usuario_by_email(session: Session, email_usuario: str) -> UsuarioModel | None:
    return session.scalar(
        select(UsuarioModel).where(UsuarioModel.email_usuario == email_usuario)
    )


def create_usuario(session: Session, payload: UsuarioCreate) -> UsuarioResponse:
    if session.get(UsuarioModel, payload.id_usuario) is not None:
        raise DuplicateKeyError(
            mensagem="Erro de validação semântica",
            detalhes=f"Já existe Usuário cadastrado com 'id_usuario' igual a {payload.id_usuario}.",
        )
    if get_usuario_by_email(session, payload.email_usuario) is not None:
        raise DuplicateKeyError(
            mensagem="Erro de validação semântica",
            detalhes=f"Já existe Usuário cadastrado com 'email_usuario' igual a '{payload.email_usuario}'.",
        )
    row = UsuarioModel(
        id_usuario=payload.id_usuario,
        nome_usuario=payload.nome_usuario,
        email_usuario=payload.email_usuario,
        senha_hash=hash_password(payload.senha),
        perfil=payload.perfil.value,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return UsuarioResponse.model_validate(row)


def update_usuario(session: Session, id_usuario: int, payload: UsuarioCreate) -> UsuarioResponse:
    row = session.get(UsuarioModel, id_usuario)
    if row is None:
        raise ResourceNotFoundError(
            mensagem="Recurso não encontrado",
            detalhes=f"Usuário com identificador {id_usuario} não foi encontrado.",
        )
    if payload.id_usuario != id_usuario:
        raise PathBodyMismatchError(
            mensagem="Erro de validação semântica",
            detalhes=(
                f"O identificador 'id_usuario' no corpo ({payload.id_usuario}) "
                f"diverge do identificador na URL ({id_usuario})."
            ),
        )
    existing_email = get_usuario_by_email(session, payload.email_usuario)
    if existing_email is not None and existing_email.id_usuario != id_usuario:
        raise DuplicateKeyError(
            mensagem="Erro de validação semântica",
            detalhes=f"Já existe Usuário cadastrado com 'email_usuario' igual a '{payload.email_usuario}'.",
        )
    row.nome_usuario = payload.nome_usuario
    row.email_usuario = payload.email_usuario
    row.senha_hash = hash_password(payload.senha)
    row.perfil = payload.perfil.value
    session.commit()
    session.refresh(row)
    return UsuarioResponse.model_validate(row)


def delete_usuario(session: Session, id_usuario: int) -> None:
    _delete_record(session, UsuarioModel, id_usuario, "Usuário")


# --- Veterinários ---


def list_veterinarios(session: Session, page: int, limit: int) -> list[Veterinario]:
    return _list_records(
        session, VeterinarioModel, VeterinarioModel.crmv, Veterinario, page, limit
    )


def get_veterinario(session: Session, crmv: int) -> Veterinario:
    return _get_record(session, VeterinarioModel, crmv, Veterinario, "Veterinário")


def create_veterinario(session: Session, payload: Veterinario) -> Veterinario:
    return _create_record(
        session, VeterinarioModel, payload, "crmv", Veterinario, "Veterinário", _validate_usuario_fk
    )


def update_veterinario(session: Session, crmv: int, payload: Veterinario) -> Veterinario:
    return _update_record(
        session,
        VeterinarioModel,
        crmv,
        payload,
        "crmv",
        Veterinario,
        "Veterinário",
        _validate_usuario_fk,
    )


def delete_veterinario(session: Session, crmv: int) -> None:
    _delete_record(session, VeterinarioModel, crmv, "Veterinário")


# --- Recepção ---


def list_recepcao(session: Session, page: int, limit: int) -> list[Recepcao]:
    return _list_records(
        session, RecepcaoModel, RecepcaoModel.matricula, Recepcao, page, limit
    )


def get_recepcao(session: Session, matricula: int) -> Recepcao:
    return _get_record(session, RecepcaoModel, matricula, Recepcao, "Recepção")


def create_recepcao(session: Session, payload: Recepcao) -> Recepcao:
    return _create_record(
        session, RecepcaoModel, payload, "matricula", Recepcao, "Recepção", _validate_usuario_fk
    )


def update_recepcao(session: Session, matricula: int, payload: Recepcao) -> Recepcao:
    return _update_record(
        session, RecepcaoModel, matricula, payload, "matricula", Recepcao, "Recepção", _validate_usuario_fk
    )


def delete_recepcao(session: Session, matricula: int) -> None:
    _delete_record(session, RecepcaoModel, matricula, "Recepção")


# --- Tutores ---


def list_tutores(session: Session, page: int, limit: int) -> list[Tutor]:
    return _list_records(session, TutorModel, TutorModel.id_tutor, Tutor, page, limit)


def get_tutor(session: Session, id_tutor: int) -> Tutor:
    return _get_record(session, TutorModel, id_tutor, Tutor, "Tutor")


def create_tutor(session: Session, payload: Tutor) -> Tutor:
    return _create_record(session, TutorModel, payload, "id_tutor", Tutor, "Tutor")


def update_tutor(session: Session, id_tutor: int, payload: Tutor) -> Tutor:
    return _update_record(session, TutorModel, id_tutor, payload, "id_tutor", Tutor, "Tutor")


def delete_tutor(session: Session, id_tutor: int) -> None:
    _delete_record(session, TutorModel, id_tutor, "Tutor")


# --- Animais ---


def list_animais(session: Session, page: int, limit: int) -> list[Animal]:
    return _list_records(session, AnimalModel, AnimalModel.id_animal, Animal, page, limit)


def get_animal(session: Session, id_animal: int) -> Animal:
    return _get_record(session, AnimalModel, id_animal, Animal, "Animal")


def create_animal(session: Session, payload: Animal) -> Animal:
    return _create_record(
        session, AnimalModel, payload, "id_animal", Animal, "Animal", _validate_animal_fk
    )


def update_animal(session: Session, id_animal: int, payload: Animal) -> Animal:
    return _update_record(
        session, AnimalModel, id_animal, payload, "id_animal", Animal, "Animal", _validate_animal_fk
    )


def delete_animal(session: Session, id_animal: int) -> None:
    _delete_record(session, AnimalModel, id_animal, "Animal")


# --- Prontuários ---


def list_prontuarios(session: Session, page: int, limit: int) -> list[Prontuario]:
    return _list_records(
        session, ProntuarioModel, ProntuarioModel.id_prontuario, Prontuario, page, limit
    )


def get_prontuario(session: Session, id_prontuario: int) -> Prontuario:
    return _get_record(session, ProntuarioModel, id_prontuario, Prontuario, "Prontuário")


def create_prontuario(session: Session, payload: Prontuario) -> Prontuario:
    return _create_record(
        session,
        ProntuarioModel,
        payload,
        "id_prontuario",
        Prontuario,
        "Prontuário",
        _validate_prontuario_fk,
    )


def update_prontuario(session: Session, id_prontuario: int, payload: Prontuario) -> Prontuario:
    return _update_record(
        session,
        ProntuarioModel,
        id_prontuario,
        payload,
        "id_prontuario",
        Prontuario,
        "Prontuário",
        _validate_prontuario_fk,
    )


def delete_prontuario(session: Session, id_prontuario: int) -> None:
    _delete_record(session, ProntuarioModel, id_prontuario, "Prontuário")


# --- Agendamentos ---


def list_agendamentos(session: Session, page: int, limit: int) -> list[Agendamento]:
    return _list_records(
        session, AgendamentoModel, AgendamentoModel.id_agendamento, Agendamento, page, limit
    )


def get_agendamento(session: Session, id_agendamento: int) -> Agendamento:
    return _get_record(
        session, AgendamentoModel, id_agendamento, Agendamento, "Agendamento"
    )


def create_agendamento(session: Session, payload: Agendamento) -> Agendamento:
    return _create_record(
        session,
        AgendamentoModel,
        payload,
        "id_agendamento",
        Agendamento,
        "Agendamento",
        _validate_agendamento_fk,
    )


def update_agendamento(
    session: Session, id_agendamento: int, payload: Agendamento
) -> Agendamento:
    return _update_record(
        session,
        AgendamentoModel,
        id_agendamento,
        payload,
        "id_agendamento",
        Agendamento,
        "Agendamento",
        _validate_agendamento_fk,
    )


def delete_agendamento(session: Session, id_agendamento: int) -> None:
    _delete_record(session, AgendamentoModel, id_agendamento, "Agendamento")


# --- Atendimentos ---


def list_atendimentos(session: Session, page: int, limit: int) -> list[Atendimento]:
    return _list_records(
        session, AtendimentoModel, AtendimentoModel.id_atendimento, Atendimento, page, limit
    )


def get_atendimento(session: Session, id_atendimento: int) -> Atendimento:
    return _get_record(
        session, AtendimentoModel, id_atendimento, Atendimento, "Atendimento"
    )


def create_atendimento(session: Session, payload: Atendimento) -> Atendimento:
    return _create_record(
        session,
        AtendimentoModel,
        payload,
        "id_atendimento",
        Atendimento,
        "Atendimento",
        _validate_atendimento_fk,
    )


def update_atendimento(
    session: Session, id_atendimento: int, payload: Atendimento
) -> Atendimento:
    return _update_record(
        session,
        AtendimentoModel,
        id_atendimento,
        payload,
        "id_atendimento",
        Atendimento,
        "Atendimento",
        _validate_atendimento_fk,
    )


def delete_atendimento(session: Session, id_atendimento: int) -> None:
    _delete_record(session, AtendimentoModel, id_atendimento, "Atendimento")


# --- Vacinações ---


def list_vacinacoes(session: Session, page: int, limit: int) -> list[Vacinacao]:
    return _list_records(
        session, VacinacaoModel, VacinacaoModel.id_vacinacao, Vacinacao, page, limit
    )


def get_vacinacao(session: Session, id_vacinacao: int) -> Vacinacao:
    return _get_record(session, VacinacaoModel, id_vacinacao, Vacinacao, "Vacinação")


def create_vacinacao(session: Session, payload: Vacinacao) -> Vacinacao:
    return _create_record(
        session,
        VacinacaoModel,
        payload,
        "id_vacinacao",
        Vacinacao,
        "Vacinação",
        _validate_vacinacao_fk,
    )


def update_vacinacao(session: Session, id_vacinacao: int, payload: Vacinacao) -> Vacinacao:
    return _update_record(
        session,
        VacinacaoModel,
        id_vacinacao,
        payload,
        "id_vacinacao",
        Vacinacao,
        "Vacinação",
        _validate_vacinacao_fk,
    )


def delete_vacinacao(session: Session, id_vacinacao: int) -> None:
    _delete_record(session, VacinacaoModel, id_vacinacao, "Vacinação")


# --- Internações ---


def list_internacoes(session: Session, page: int, limit: int) -> list[Internacao]:
    return _list_records(
        session, InternacaoModel, InternacaoModel.id_internacao, Internacao, page, limit
    )


def get_internacao(session: Session, id_internacao: int) -> Internacao:
    return _get_record(session, InternacaoModel, id_internacao, Internacao, "Internação")


def create_internacao(session: Session, payload: Internacao) -> Internacao:
    return _create_record(
        session,
        InternacaoModel,
        payload,
        "id_internacao",
        Internacao,
        "Internação",
        _validate_internacao_fk,
    )


def update_internacao(session: Session, id_internacao: int, payload: Internacao) -> Internacao:
    return _update_record(
        session,
        InternacaoModel,
        id_internacao,
        payload,
        "id_internacao",
        Internacao,
        "Internação",
        _validate_internacao_fk,
    )


def delete_internacao(session: Session, id_internacao: int) -> None:
    _delete_record(session, InternacaoModel, id_internacao, "Internação")


# --- Plantões ---


def list_plantoes(session: Session, page: int, limit: int) -> list[Plantao]:
    return _list_records(
        session, PlantaoModel, PlantaoModel.id_plantao, Plantao, page, limit
    )


def get_plantao(session: Session, id_plantao: int) -> Plantao:
    return _get_record(session, PlantaoModel, id_plantao, Plantao, "Plantão")


def create_plantao(session: Session, payload: Plantao) -> Plantao:
    return _create_record(
        session, PlantaoModel, payload, "id_plantao", Plantao, "Plantão", _validate_plantao_fk
    )


def update_plantao(session: Session, id_plantao: int, payload: Plantao) -> Plantao:
    return _update_record(
        session,
        PlantaoModel,
        id_plantao,
        payload,
        "id_plantao",
        Plantao,
        "Plantão",
        _validate_plantao_fk,
    )


def delete_plantao(session: Session, id_plantao: int) -> None:
    _delete_record(session, PlantaoModel, id_plantao, "Plantão")
