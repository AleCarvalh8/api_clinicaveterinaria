"""Modelos ORM SQLAlchemy 2.0 para a API da clínica veterinária Pet & Gatô."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Classe base declarativa para os modelos ORM SQLAlchemy 2.0."""


class UsuarioModel(Base):
    """Tabela de usuários do sistema."""

    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_usuario: Mapped[str] = mapped_column(String(120), nullable=False)
    email_usuario: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(11), nullable=False)

    veterinarios: Mapped[list[VeterinarioModel]] = relationship(back_populates="usuario")
    recepcionistas: Mapped[list[RecepcaoModel]] = relationship(back_populates="usuario")


class VeterinarioModel(Base):
    """Tabela de médicos veterinários."""

    __tablename__ = "veterinarios"

    crmv: Mapped[int] = mapped_column(Integer, primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(18), nullable=False)
    especialidade: Mapped[str] = mapped_column(String(50), nullable=False)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"), nullable=False
    )

    usuario: Mapped[UsuarioModel] = relationship(back_populates="veterinarios")
    prontuarios: Mapped[list[ProntuarioModel]] = relationship(back_populates="veterinario")
    agendamentos: Mapped[list[AgendamentoModel]] = relationship(back_populates="veterinario")
    vacinacoes: Mapped[list[VacinacaoModel]] = relationship(back_populates="veterinario")
    internacoes: Mapped[list[InternacaoModel]] = relationship(back_populates="veterinario")
    plantoes: Mapped[list[PlantaoModel]] = relationship(back_populates="veterinario")


class RecepcaoModel(Base):
    """Tabela de funcionários da recepção."""

    __tablename__ = "recepcao"

    matricula: Mapped[int] = mapped_column(Integer, primary_key=True)
    cpf_recepcao: Mapped[str] = mapped_column(String(14), nullable=False)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"), nullable=False
    )

    usuario: Mapped[UsuarioModel] = relationship(back_populates="recepcionistas")
    agendamentos: Mapped[list[AgendamentoModel]] = relationship(back_populates="recepcionista")


class TutorModel(Base):
    """Tabela de tutores responsáveis pelos animais."""

    __tablename__ = "tutores"

    id_tutor: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_tutor: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf_tutor: Mapped[str] = mapped_column(String(14), nullable=False)
    email_tutor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(300), nullable=True)

    animais: Mapped[list[AnimalModel]] = relationship(back_populates="tutor")
    plantoes: Mapped[list[PlantaoModel]] = relationship(back_populates="tutor")


class AnimalModel(Base):
    """Tabela de animais/pacientes atendidos na clínica."""

    __tablename__ = "animais"

    id_animal: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_tutor: Mapped[int] = mapped_column(ForeignKey("tutores.id_tutor"), nullable=False)
    nome_animal: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tipo_animal: Mapped[str] = mapped_column(String(15), nullable=False)
    raca: Mapped[str] = mapped_column(String(35), nullable=False)
    sexo: Mapped[str | None] = mapped_column(String(1), nullable=True)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)

    tutor: Mapped[TutorModel] = relationship(back_populates="animais")
    prontuarios: Mapped[list[ProntuarioModel]] = relationship(back_populates="animal")
    agendamentos: Mapped[list[AgendamentoModel]] = relationship(back_populates="animal")
    internacoes: Mapped[list[InternacaoModel]] = relationship(back_populates="animal")
    plantoes: Mapped[list[PlantaoModel]] = relationship(back_populates="animal")


class ProntuarioModel(Base):
    """Tabela de prontuários clínicos."""

    __tablename__ = "prontuarios"

    id_prontuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    crmv: Mapped[int] = mapped_column(ForeignKey("veterinarios.crmv"), nullable=False)
    id_animal: Mapped[int] = mapped_column(ForeignKey("animais.id_animal"), nullable=False)
    data_abertura: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    peso_atual: Mapped[float] = mapped_column(Float, nullable=False)
    queixa: Mapped[str] = mapped_column(String(300), nullable=False)
    anamnese: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnostico: Mapped[str] = mapped_column(String(200), nullable=False)
    receita: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vacina: Mapped[str | None] = mapped_column(String(200), nullable=True)

    veterinario: Mapped[VeterinarioModel] = relationship(back_populates="prontuarios")
    animal: Mapped[AnimalModel] = relationship(back_populates="prontuarios")
    atendimentos: Mapped[list[AtendimentoModel]] = relationship(back_populates="prontuario")
    vacinacoes: Mapped[list[VacinacaoModel]] = relationship(back_populates="prontuario")


class AgendamentoModel(Base):
    """Tabela de agendamentos de consultas."""

    __tablename__ = "agendamentos"

    id_agendamento: Mapped[int] = mapped_column(Integer, primary_key=True)
    hora_agendamento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    id_animal: Mapped[int] = mapped_column(ForeignKey("animais.id_animal"), nullable=False)
    crmv: Mapped[int] = mapped_column(ForeignKey("veterinarios.crmv"), nullable=False)
    matricula: Mapped[int] = mapped_column(ForeignKey("recepcao.matricula"), nullable=False)
    status_agendamento: Mapped[str] = mapped_column(String(20), nullable=False)

    animal: Mapped[AnimalModel] = relationship(back_populates="agendamentos")
    veterinario: Mapped[VeterinarioModel] = relationship(back_populates="agendamentos")
    recepcionista: Mapped[RecepcaoModel] = relationship(back_populates="agendamentos")


class AtendimentoModel(Base):
    """Tabela de atendimentos clínicos."""

    __tablename__ = "atendimentos"

    id_atendimento: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_prontuario: Mapped[int] = mapped_column(
        ForeignKey("prontuarios.id_prontuario"), nullable=False
    )
    hora_atendimento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    prontuario: Mapped[ProntuarioModel] = relationship(back_populates="atendimentos")


class VacinacaoModel(Base):
    """Tabela de registros de vacinação."""

    __tablename__ = "vacinacoes"

    id_vacinacao: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_aplicacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    crmv: Mapped[int] = mapped_column(ForeignKey("veterinarios.crmv"), nullable=False)
    id_prontuario: Mapped[int] = mapped_column(
        ForeignKey("prontuarios.id_prontuario"), nullable=False
    )
    nome_vacina: Mapped[str] = mapped_column(String(30), nullable=False)
    lote_vacina: Mapped[str] = mapped_column(String(30), nullable=False)
    data_proxima_dose: Mapped[date | None] = mapped_column(Date, nullable=True)

    veterinario: Mapped[VeterinarioModel] = relationship(back_populates="vacinacoes")
    prontuario: Mapped[ProntuarioModel] = relationship(back_populates="vacinacoes")


class InternacaoModel(Base):
    """Tabela de internações hospitalares."""

    __tablename__ = "internacoes"

    id_internacao: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_animal: Mapped[int] = mapped_column(ForeignKey("animais.id_animal"), nullable=False)
    crmv: Mapped[int] = mapped_column(ForeignKey("veterinarios.crmv"), nullable=False)
    data_internacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_alta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    nivel_gravidade: Mapped[str | None] = mapped_column(String(15), nullable=True)
    status_internacao: Mapped[str] = mapped_column(String(15), nullable=False)
    evolucao_internacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    animal: Mapped[AnimalModel] = relationship(back_populates="internacoes")
    veterinario: Mapped[VeterinarioModel] = relationship(back_populates="internacoes")


class PlantaoModel(Base):
    """Tabela de atendimentos de urgência/plantão."""

    __tablename__ = "plantoes"

    id_plantao: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_animal: Mapped[int | None] = mapped_column(
        ForeignKey("animais.id_animal"), nullable=True
    )
    id_tutor: Mapped[int | None] = mapped_column(
        ForeignKey("tutores.id_tutor"), nullable=True
    )
    crmv: Mapped[int] = mapped_column(ForeignKey("veterinarios.crmv"), nullable=False)
    chegada_plantao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status_plantao: Mapped[str] = mapped_column(String(20), nullable=False)
    evolucao_plantao: Mapped[str | None] = mapped_column(Text, nullable=True)

    animal: Mapped[AnimalModel | None] = relationship(back_populates="plantoes")
    tutor: Mapped[TutorModel | None] = relationship(back_populates="plantoes")
    veterinario: Mapped[VeterinarioModel] = relationship(back_populates="plantoes")
