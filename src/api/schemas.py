"""Contratos Pydantic v2 da API Pet & Gatô extraídos de Módulo predefinido.openapi.json."""

from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


def _utc_now() -> datetime:
    """Retorna o timestamp UTC atual para campos com valor padrão de data/hora."""
    return datetime.now(timezone.utc)


class StatusAgendamento(str, Enum):
    """Estados possíveis para o fluxo de agendamento de consultas."""

    AGENDADO = "Agendado"
    EM_ESPERA = "Em espera"
    EM_ATENDIMENTO = "Em atendimento"
    CONCLUIDO = "Concluido"
    CANCELADO = "Cancelado"


class NivelGravidade(str, Enum):
    """Classificação de risco ou gravidade clínica do paciente."""

    BAIXA = "Baixa"
    MEDIO = "Medio"
    ALTA = "Alta"
    CRITICA = "Critica"


class StatusInternacao(str, Enum):
    """Estado atual da internação hospitalar do animal."""

    INTERNADO = "Internado"
    ALTA = "Alta"
    OBITO = "Obito"


class StatusPlantao(str, Enum):
    """Status dos atendimentos realizados durante plantões ou emergências."""

    EM_ANALISE = "Em analise"
    INTERNADO = "Internado"
    ALTA = "Alta"
    OBITO = "Obito"


class PerfilUsuario(str, Enum):
    """Papel ou perfil de acesso do usuário no sistema."""

    RECEPCAO = "Recepcao"
    VETERINARIO = "Veterinario"


class SexoAnimal(str, Enum):
    """Sexo biológico do animal."""

    FEMEA = "F"
    MACHO = "M"


class ErrorResponse(BaseModel):
    """Schema padronizado para retorno de erros na API da clínica veterinária."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    mensagem: str = Field(..., description="Resumo descritivo do erro ocorrido.")
    detalhes: str = Field(..., description="Explicação detalhada sobre a causa raiz do erro.")


class LoginRequest(BaseModel):
    """Credenciais de entrada para autenticação JWT."""

    model_config = ConfigDict(from_attributes=True)

    email_usuario: str = Field(..., description="E-mail corporativo do usuário.")
    senha: str = Field(..., description="Senha do usuário.")


class TokenResponse(BaseModel):
    """Resposta de autenticação contendo o token JWT Bearer."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="Token de acesso JWT HS256.")
    token_type: str = Field(default="bearer", description="Tipo do token de autenticação.")


class UsuarioCreate(BaseModel):
    """DTO para criação ou atualização integral de um usuário do sistema."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_usuario: int = Field(..., description="Identificador único numérico do usuário.")
    nome_usuario: str = Field(..., max_length=120, description="Nome completo do usuário.")
    email_usuario: str = Field(
        ...,
        max_length=50,
        pattern=r"^[A-Za-z0-9._%+-]+@petegato\.com$",
        description="E-mail corporativo válido com o domínio @petegato.com.",
    )
    senha: str = Field(
        ...,
        min_length=8,
        max_length=50,
        pattern=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,50}$",
        description=(
            "Senha segura contendo ao menos uma letra maiúscula, uma minúscula, "
            "um número e um caractere especial."
        ),
        json_schema_extra={"writeOnly": True},
    )
    perfil: PerfilUsuario = Field(..., description="Papel ou perfil de acesso do usuário no sistema.")


class UsuarioResponse(BaseModel):
    """Representação pública de dados de um usuário cadastrado."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_usuario: int = Field(..., description="Identificador único numérico do usuário.")
    nome_usuario: str = Field(..., description="Nome completo do usuário.")
    email_usuario: str = Field(..., description="E-mail corporativo do usuário.")
    perfil: PerfilUsuario = Field(..., description="Perfil de acesso do usuário.")


class Veterinario(BaseModel):
    """Modelo de dados para representação de um médico veterinário."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    crmv: int = Field(
        ...,
        description="Número de registro no Conselho Regional de Medicina Veterinária (Chave Primária).",
    )
    cnpj: str = Field(
        ...,
        max_length=18,
        pattern=r"^[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}$",
        description="CNPJ formatado do consultório ou profissional.",
    )
    especialidade: str = Field(..., max_length=50, description="Área de especialização médica veterinária.")
    id_usuario: int = Field(
        ...,
        description="Chave estrangeira vinculada ao ID do usuário na tabela de usuários.",
    )


class Recepcao(BaseModel):
    """Modelo de dados para funcionários do setor de recepção."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    matricula: int = Field(..., description="Matrícula funcional interna (Chave Primária).")
    cpf_recepcao: str = Field(
        ...,
        max_length=14,
        pattern=r"^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$",
        description="CPF formatado do atendente de recepção.",
    )
    id_usuario: int = Field(
        ...,
        description="Chave estrangeira vinculada ao ID do usuário correspondente.",
    )


class Tutor(BaseModel):
    """Modelo de dados para tutores ou responsáveis legais pelos animais."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_tutor: int = Field(..., description="Identificador único numérico do tutor.")
    nome_tutor: str = Field(..., max_length=120, description="Nome completo do tutor.")
    cpf_tutor: str = Field(
        ...,
        max_length=14,
        pattern=r"^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$",
        description="CPF formatado do tutor.",
    )
    email_tutor: str | None = Field(
        default=None,
        max_length=50,
        pattern=r"^[A-Za-z0-9._%+-]+@[a-z]+\.[a-z.]{2,}$",
        description="E-mail de contato do tutor.",
    )
    telefone: str | None = Field(
        default=None,
        max_length=15,
        description="Número de telefone ou celular para contato.",
    )
    observacoes: str | None = Field(
        default=None,
        max_length=300,
        description="Observações gerais sobre o comportamento ou preferências do tutor.",
    )


class Animal(BaseModel):
    """Modelo de dados para os pacientes (animais) atendidos na clínica."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_animal: int = Field(..., description="Identificador único do animal/paciente.")
    id_tutor: int = Field(..., description="Chave estrangeira apontando para o tutor responsável.")
    nome_animal: str | None = Field(
        default=None,
        max_length=30,
        description="Nome de registro ou de chamada do animal.",
    )
    tipo_animal: str = Field(..., max_length=15, description="Espécie do animal (ex: Gato, Cachorro, Ave).")
    raca: str = Field(..., max_length=35, description="Raça predominante do animal.")
    sexo: SexoAnimal | None = Field(
        default=None,
        description="Sexo biológico do animal (F para Fêmea, M para Macho).",
    )
    data_nascimento: date | None = Field(
        default=None,
        description="Data de nascimento estimada ou exata do animal (Formato YYYY-MM-DD).",
    )


class Prontuario(BaseModel):
    """Modelo de dados contendo o histórico clínico de atendimento do animal."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_prontuario: int = Field(..., description="Identificador único do prontuário médico.")
    crmv: int = Field(..., description="CRMV do veterinário responsável pela abertura do prontuário.")
    id_animal: int = Field(..., description="Identificador do animal paciente.")
    data_abertura: datetime = Field(
        default_factory=_utc_now,
        description="Data e hora de criação do prontuário (padrão carimbo de tempo atual).",
    )
    peso_atual: float = Field(
        ...,
        ge=0.01,
        description="Peso atual do animal em quilogramas (precisão de duas casas decimais, maior que zero).",
    )
    queixa: str = Field(
        ...,
        max_length=300,
        description="Relato principal do tutor sobre o estado de saúde do animal.",
    )
    anamnese: str | None = Field(
        default=None,
        description="Histórico médico detalhado e avaliação clínica prévia.",
    )
    diagnostico: str = Field(
        ...,
        max_length=200,
        description="Conclusão médica ou diagnóstico provisório.",
    )
    receita: str | None = Field(
        default=None,
        max_length=200,
        description="Prescrição de medicamentos e orientações terapêuticas.",
    )
    vacina: str | None = Field(
        default=None,
        max_length=200,
        description="Informações sobre vacinas aplicadas durante o atendimento.",
    )


class Agendamento(BaseModel):
    """Registro de marcação de consulta ou atendimento para um animal."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_agendamento: int = Field(..., description="Identificador único do agendamento.")
    hora_agendamento: datetime = Field(..., description="Data e horário planejados para a consulta.")
    id_animal: int = Field(..., description="Chave estrangeira do animal agendado.")
    crmv: int = Field(..., description="CRMV do veterinário escalado.")
    matricula: int = Field(..., description="Matrícula do recepcionista que efetuou a marcação.")
    status_agendamento: StatusAgendamento = Field(
        default=StatusAgendamento.AGENDADO,
        description="Status atual do agendamento.",
    )


class Atendimento(BaseModel):
    """Registro de execução efetiva de um atendimento clínico vinculado a um prontuário."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_atendimento: int = Field(..., description="Identificador único do atendimento.")
    id_prontuario: int = Field(..., description="Chave estrangeira apontando para o prontuário correspondente.")
    hora_atendimento: datetime | None = Field(
        default=None,
        description="Horário exato de início ou registro do atendimento.",
    )


class Vacinacao(BaseModel):
    """Registro de aplicação de vacinas em pacientes."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_vacinacao: int = Field(..., description="Identificador único do registro de vacinação.")
    data_aplicacao: datetime = Field(..., description="Data e hora em que a vacina foi administrada.")
    crmv: int = Field(..., description="CRMV do veterinário responsável pela aplicação.")
    id_prontuario: int = Field(..., description="Prontuário associado à aplicação.")
    nome_vacina: str = Field(..., max_length=30, description="Nome comercial ou tipo da vacina.")
    lote_vacina: str = Field(..., max_length=30, description="Número de lote do imunizante.")
    data_proxima_dose: date | None = Field(
        default=None,
        description="Data recomendada para o reforço ou próxima dose.",
    )


class Internacao(BaseModel):
    """Registro de internação clínica ou cirúrgica do animal."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_internacao: int = Field(..., description="Identificador único da internação.")
    id_animal: int = Field(..., description="ID do animal internado.")
    crmv: int = Field(..., description="CRMV do veterinário supervisor da internação.")
    data_internacao: datetime = Field(
        default_factory=_utc_now,
        description="Data e hora de entrada na ala de internação.",
    )
    data_alta: datetime | None = Field(
        default=None,
        description="Data e hora da alta hospitalar ou óbito.",
    )
    nivel_gravidade: NivelGravidade | None = Field(
        default=None,
        description="Grau de criticidade do estado de saúde do paciente.",
    )
    status_internacao: StatusInternacao = Field(
        default=StatusInternacao.INTERNADO,
        description="Status atual da internação.",
    )
    evolucao_internacao: str | None = Field(
        default=None,
        description="Notas contínuas de evolução clínica e procedimentos realizados.",
    )


class Plantao(BaseModel):
    """Registro de atendimento de urgência ou emergência (plantão)."""

    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")

    id_plantao: int = Field(..., description="Identificador único do plantão/atendimento de urgência.")
    id_animal: int | None = Field(
        default=None,
        description="ID do animal (pode ser nulo caso o paciente ainda não esteja cadastrado na chegada).",
    )
    id_tutor: int | None = Field(
        default=None,
        description="ID do tutor (pode ser nulo em casos de resgate sem tutor imediato).",
    )
    crmv: int = Field(..., description="CRMV do médico veterinário plantonista.")
    chegada_plantao: datetime = Field(
        default_factory=_utc_now,
        description="Data e hora de entrada do paciente no plantão de urgência.",
    )
    status_plantao: StatusPlantao = Field(
        default=StatusPlantao.EM_ANALISE,
        description="Estado clínico atual no plantão.",
    )
    evolucao_plantao: str | None = Field(
        default=None,
        description="Observações e relatos de urgência realizados pelo plantonista.",
    )
