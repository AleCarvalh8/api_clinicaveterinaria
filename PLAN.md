# PLAN.md — Plano de Implementação da API Pet & Gatô

Este documento define o roteiro técnico sequencial e granular para a implementação da API REST da clínica veterinária **Pet & Gatô**, em total conformidade com `@[SPEC.md](SPEC.md)`, `@[STYLEGUIDE.md](STYLEGUIDE.md)` e `@[Módulo predefinido.openapi.json](Módulo predefinido.openapi.json)`.

---

## Fase 1: Estrutura de diretórios e `src/api/requirements.txt`

- [x] Criar o pacote raiz `src/api/` e o arquivo `src/api/__init__.py`.
- [x] Criar o subpacote `src/api/routers/` e o arquivo `src/api/routers/__init__.py`.
- [x] Criar o subpacote `src/api/tests/` e o arquivo `src/api/tests/__init__.py`.
- [x] Criar `src/api/requirements.txt` com as dependências estritas do projeto (`fastapi`, `uvicorn[standard]`, `pydantic>=2.0`, `pytest`, `httpx`).

---

## Fase 2: Extração de schemas Pydantic v2 (`src/api/schemas.py`)

- [x] Configurar base Pydantic v2 (`BaseModel`, `ConfigDict`, `Field`, `@field_validator`, `datetime`, `date`, `Enum`) preservando estritamente os nomes `snake_case` do contrato (sem aliases `camelCase`).
- [x] Implementar os Enums de domínio com valores literais exatos do contrato (incluindo espaços e ausência de acentos):
  - [x] `StatusAgendamento`: `"Agendado"`, `"Em espera"`, `"Em atendimento"`, `"Concluido"`, `"Cancelado"`.
  - [x] `NivelGravidade`: `"Baixa"`, `"Medio"`, `"Alta"`, `"Critica"`.
  - [x] `StatusInternacao`: `"Internado"`, `"Alta"`, `"Obito"`.
  - [x] `StatusPlantao`: `"Em analise"`, `"Internado"`, `"Alta"`, `"Obito"`.
  - [x] Enums auxiliares de campos: `PerfilUsuario` (`"Recepcao"`, `"Veterinario"`) e `SexoAnimal` (`"F"`, `"M"`).
- [x] Implementar o schema de erro `ErrorResponse` (`mensagem: str`, `detalhes: str`, ambos obrigatórios), garantindo que `Error` (Problem Details) e `Meta` não sejam usados nas respostas.
- [x] Implementar os schemas de Usuários:
  - [x] `UsuarioCreate`: `id_usuario` (`int`), `nome_usuario` (`max_length=120`), `email_usuario` (`max_length=50`, `pattern=r"^[A-Za-z0-9._%+-]+@petegato\.com$"`), `senha` (`min_length=8`, `max_length=50`, `pattern=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,50}$"`, `writeOnly`), `perfil` (`PerfilUsuario`).
  - [x] `UsuarioResponse`: `id_usuario`, `nome_usuario`, `email_usuario`, `perfil` (sem o campo `senha`).
- [x] Implementar os schemas de Funcionários:
  - [x] `Veterinario`: `crmv` (`int`), `cnpj` (`max_length=18`, `pattern=r"^[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}$"`), `especialidade` (`max_length=50`), `id_usuario` (`int`).
  - [x] `Recepcao`: `matricula` (`int`), `cpf_recepcao` (`max_length=14`, `pattern=r"^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$"`), `id_usuario` (`int`).
- [x] Implementar os schemas de Tutores e Animais:
  - [x] `Tutor`: `id_tutor` (`int`), `nome_tutor` (`max_length=120`), `cpf_tutor` (`max_length=14`, padrão CPF), `email_tutor` (opcional/nulável, `max_length=50`, `pattern=r"^[A-Za-z0-9._%+-]+@[a-z]+\.[a-z.]{2,}$"`), `telefone` (opcional/nulável, `max_length=15`), `observacoes` (opcional/nulável, `max_length=300`).
  - [x] `Animal`: `id_animal` (`int`), `id_tutor` (`int`), `nome_animal` (opcional/nulável, `max_length=30`), `tipo_animal` (`max_length=15`), `raca` (`max_length=35`), `sexo` (opcional/nulável, `SexoAnimal`), `data_nascimento` (opcional/nulável, `date`).
- [x] Implementar os schemas Clínicos:
  - [x] `Prontuario`: `id_prontuario` (`int`), `crmv` (`int`), `id_animal` (`int`), `data_abertura` (opcional, `datetime` com default timestamp atual), `peso_atual` (`float`, `ge=0.01`), `queixa` (`max_length=300`), `anamnese` (opcional/nulável), `diagnostico` (`max_length=200`), `receita` (opcional/nulável, `max_length=200`), `vacina` (opcional/nulável, `max_length=200`).
  - [x] `Atendimento`: `id_atendimento` (`int`), `id_prontuario` (`int`), `hora_atendimento` (opcional, `datetime`).
  - [x] `Vacinacao`: `id_vacinacao` (`int`), `data_aplicacao` (`datetime`), `crmv` (`int`), `id_prontuario` (`int`), `nome_vacina` (`max_length=30`), `lote_vacina` (`max_length=30`), `data_proxima_dose` (opcional/nulável, `date`).
- [x] Implementar os schemas de Agenda, Internação e Plantão:
  - [x] `Agendamento`: `id_agendamento` (`int`), `hora_agendamento` (`datetime`), `id_animal` (`int`), `crmv` (`int`), `matricula` (`int`), `status_agendamento` (`StatusAgendamento`, default `"Agendado"`).
  - [x] `Internacao`: `id_internacao` (`int`), `id_animal` (`int`), `crmv` (`int`), `data_internacao` (opcional, `datetime` com default timestamp atual), `data_alta` (opcional/nulável, `datetime`), `nivel_gravidade` (opcional/nulável, `NivelGravidade`), `status_internacao` (`StatusInternacao`, default `"Internado"`), `evolucao_internacao` (opcional/nulável).
  - [x] `Plantao`: `id_plantao` (`int`), `id_animal` (opcional/nulável, `int`), `id_tutor` (opcional/nulável, `int`), `crmv` (`int`), `chegada_plantao` (opcional, `datetime` com default timestamp atual), `status_plantao` (`StatusPlantao`, default `"Em analise"`), `evolucao_plantao` (opcional/nulável).

---

## Fase 3: Camada de persistência isolada (`src/api/database.py`)

- [x] Estruturar repositório In-Memory Thread-Safe protegido por `threading.RLock` para as 11 coleções.
- [x] Implementar hash seguro de senha (ex.: `hashlib.pbkdf2_hmac` ou equivalente da stdlib) no armazenamento de usuários para garantir que `senha` nunca seja armazenada em texto puro nem exposta em respostas.
- [x] Implementar método `reset_db()` para restaurar o estado inicial entre execuções de testes.
- [x] Implementar o seed inicial coerente com os exemplos do contrato:
  - [x] Usuários `1` (`Veterinario`, `juliana.santos@petegato.com`) e `2` (`Recepcao`).
  - [x] Veterinário `crmv=12345` (`id_usuario=1`).
  - [x] Recepção `matricula=1010` (`id_usuario=2`).
  - [x] Tutor `1` (`Carlos Eduardo Lima`).
  - [x] Animal `501` (`Mingau`, `Gato`, `Siamês`, `id_tutor=1`).
  - [x] Prontuário `1001` (`crmv=12345`, `id_animal=501`).
  - [x] Agendamento `100` (`id_animal=501`, `crmv=12345`, `matricula=1010`).
  - [x] Atendimento `8001` (`id_prontuario=1001`).
  - [x] Vacinação `1` (`crmv=12345`, `id_prontuario=1001`).
  - [x] Internação `4001` (`id_animal=501`, `crmv=12345`).
  - [x] Plantão `3001` (`id_animal=501`, `id_tutor=1`, `crmv=12345`).
- [x] Implementar operações CRUD genéricas/tipadas com paginação (`page`, `limit`), validação de chave primária duplicada (422), verificação de existência por ID (404) e consistência entre ID do path e do corpo no `PUT` (422).
- [x] Implementar validação de integridade referencial (chave estrangeira inexistente → 422):
  - [x] `Veterinario.id_usuario` → `usuarios`
  - [x] `Recepcao.id_usuario` → `usuarios`
  - [x] `Animal.id_tutor` → `tutores`
  - [x] `Prontuario.crmv` → `veterinarios`, `Prontuario.id_animal` → `animais`
  - [x] `Agendamento.id_animal` → `animais`, `Agendamento.crmv` → `veterinarios`, `Agendamento.matricula` → `recepcao`
  - [x] `Atendimento.id_prontuario` → `prontuarios`
  - [x] `Vacinacao.crmv` → `veterinarios`, `Vacinacao.id_prontuario` → `prontuarios`
  - [x] `Internacao.id_animal` → `animais`, `Internacao.crmv` → `veterinarios`
  - [x] `Plantao.crmv` → `veterinarios`, `Plantao.id_animal` (quando não nulo) → `animais`, `Plantao.id_tutor` (quando não nulo) → `tutores`

---

## Fase 4: Exceções de domínio e handlers globais (`src/api/exceptions.py`)

- [x] Definir exceções de domínio tipadas:
  - [x] `BadRequestError` (status `400`).
  - [x] `ResourceNotFoundError` (status `404`).
  - [x] `SemanticValidationError` / `DuplicateKeyError` / `ForeignKeyViolationError` / `PathBodyMismatchError` (status `422`).
- [x] Implementar função utilitária para construir `JSONResponse` sempre no formato `ErrorResponse` (`{"mensagem": ..., "detalhes": ...}`), proibindo o formato padrão `{"detail": ...}` do FastAPI.
- [x] Registrar handler global para `RequestValidationError`:
  - [x] Mapear erros em parâmetros de `query` (`page`, `limit`) e `path` (identificador não inteiro) para `400 Bad Request`.
  - [x] Mapear erros no corpo (`body`: campo obrigatório ausente, `maxLength`, `minLength`, `pattern`, `enum`, `minimum`) para `422 Unprocessable Entity`.
- [x] Registrar handlers globais para `HTTPException` / `StarletteHTTPException` e exceções de domínio, convertendo todos para `ErrorResponse`.

---

## Fase 5: Routers das 11 coleções e `src/api/main.py`

- [x] Implementar os 11 routers em `src/api/routers/` seguindo o padrão CRUD do contrato (sem `PATCH`, `GET` coleção retornando array JSON paginado por `page`/`limit`, `POST` retornando `201`, `PUT` retornando `200`, `DELETE` retornando `204` sem corpo, e `responses=` declarando `404` e `422` com `ErrorResponse`):
  - [x] `src/api/routers/usuarios.py` (`/api/v1/usuarios`, path `{id_usuario}`, entrada `UsuarioCreate`, saída `UsuarioResponse`).
  - [x] `src/api/routers/veterinarios.py` (`/api/v1/veterinarios`, path `{crmv}`, schema `Veterinario`).
  - [x] `src/api/routers/recepcao.py` (`/api/v1/recepcao`, path `{matricula}`, schema `Recepcao`).
  - [x] `src/api/routers/tutores.py` (`/api/v1/tutores`, path `{id_tutor}`, schema `Tutor`).
  - [x] `src/api/routers/animais.py` (`/api/v1/animais`, path `{id_animal}`, schema `Animal`).
  - [x] `src/api/routers/prontuarios.py` (`/api/v1/prontuarios`, path `{id_prontuario}`, schema `Prontuario`).
  - [x] `src/api/routers/agendamentos.py` (`/api/v1/agendamentos`, path `{id_agendamento}`, schema `Agendamento`).
  - [x] `src/api/routers/atendimentos.py` (`/api/v1/atendimentos`, path `{id_atendimento}`, schema `Atendimento`).
  - [x] `src/api/routers/vacinacoes.py` (`/api/v1/vacinacoes`, path `{id_vacinacao}`, schema `Vacinacao`).
  - [x] `src/api/routers/internacoes.py` (`/api/v1/internacoes`, path `{id_internacao}`, schema `Internacao`).
  - [x] `src/api/routers/plantoes.py` (`/api/v1/plantoes`, path `{id_plantao}`, schema `Plantao`).
- [x] Implementar `src/api/main.py`:
  - [x] Instanciar `FastAPI` com título, descrição e versão `1.0.0` conforme `Módulo predefinido.openapi.json`.
  - [x] Configurar `CORSMiddleware`.
  - [x] Implementar middleware para interceptar requisições `POST` e `PUT` com `Content-Type: application/json` e corpo JSON malformado, retornando `400 Bad Request` no schema `ErrorResponse`.
  - [x] Registrar os handlers de `src/api/exceptions.py` e incluir todos os 11 routers.

---

## Fase 6: Suíte completa de testes `pytest` (`src/api/tests/`)

- [x] Implementar `src/api/tests/conftest.py` com fixture `client` (`TestClient`) e reset automático do banco em memória antes/depois de cada teste.
- [x] Implementar testes de contrato para cada uma das 11 coleções (cobrindo `GET` lista + paginação `page`/`limit`, `POST` `201`, `GET /{id}` `200`/`404`, `PUT /{id}` `200`/`404`/`422`, `DELETE /{id}` `204`/`404`, regras de FK, campos nuláveis, defaults, padrões regex e enums):
  - [x] `src/api/tests/test_usuarios.py` (incluindo validação de e-mail `@petegato.com`, força de senha e ausência de `senha` nas respostas).
  - [x] `src/api/tests/test_veterinarios.py`.
  - [x] `src/api/tests/test_recepcao.py`.
  - [x] `src/api/tests/test_tutores.py`.
  - [x] `src/api/tests/test_animais.py`.
  - [x] `src/api/tests/test_prontuarios.py`.
  - [x] `src/api/tests/test_agendamentos.py`.
  - [x] `src/api/tests/test_atendimentos.py`.
  - [x] `src/api/tests/test_vacinacoes.py`.
  - [x] `src/api/tests/test_internacoes.py`.
  - [x] `src/api/tests/test_plantoes.py`.
- [x] Implementar `src/api/tests/test_errors.py` validando conformidade estrita com `ErrorResponse` (`mensagem` e `detalhes`, sem chave `detail`) para:
  - [x] `400 Bad Request`: JSON malformado em `POST`/`PUT`, `page < 1`, `limit < 1` ou `limit > 100`, `page`/`limit` não inteiros, identificador de path não inteiro.
  - [x] `404 Not Found`: identificador inexistente em `GET`, `PUT` e `DELETE`.
  - [x] `422 Unprocessable Entity`: campo obrigatório ausente, violação de `maxLength`/`minLength`/`pattern`/`enum`/`minimum`, chave primária duplicada, chave estrangeira inexistente e divergência entre ID do path e do corpo no `PUT`.
- [x] Executar `pytest` no terminal e comprovar 100% de aprovação de todos os testes antes de concluir a fase.

---

## Fase 7: ORM SQLAlchemy 2.0 + SQLite (`src/api/models.py` e `src/api/database.py`)

- [x] Atualizar `src/api/requirements.txt` adicionando `sqlalchemy>=2.0.0` e biblioteca JWT (`pyjwt>=2.8.0`).
- [x] Criar `src/api/models.py` usando `DeclarativeBase`, `Mapped[...]` e `mapped_column(...)` com `ForeignKey` e `relationship` para todas as 11 tabelas:
  - [x] `UsuarioModel` (`usuarios`): `id_usuario` (PK), `nome_usuario`, `email_usuario`, `senha_hash`, `perfil`.
  - [x] `VeterinarioModel` (`veterinarios`): `crmv` (PK), `cnpj`, `especialidade`, `id_usuario` (FK → `usuarios.id_usuario`).
  - [x] `RecepcaoModel` (`recepcao`): `matricula` (PK), `cpf_recepcao`, `id_usuario` (FK → `usuarios.id_usuario`).
  - [x] `TutorModel` (`tutores`): `id_tutor` (PK), `nome_tutor`, `cpf_tutor`, `email_tutor`, `telefone`, `observacoes`.
  - [x] `AnimalModel` (`animais`): `id_animal` (PK), `id_tutor` (FK → `tutores.id_tutor`), `nome_animal`, `tipo_animal`, `raca`, `sexo`, `data_nascimento`.
  - [x] `ProntuarioModel` (`prontuarios`): `id_prontuario` (PK), `crmv` (FK → `veterinarios.crmv`), `id_animal` (FK → `animais.id_animal`), `data_abertura`, `peso_atual`, `queixa`, `anamnese`, `diagnostico`, `receita`, `vacina`.
  - [x] `AgendamentoModel` (`agendamentos`): `id_agendamento` (PK), `hora_agendamento`, `id_animal` (FK → `animais.id_animal`), `crmv` (FK → `veterinarios.crmv`), `matricula` (FK → `recepcao.matricula`), `status_agendamento`.
  - [x] `AtendimentoModel` (`atendimentos`): `id_atendimento` (PK), `id_prontuario` (FK → `prontuarios.id_prontuario`), `hora_atendimento`.
  - [x] `VacinacaoModel` (`vacinacoes`): `id_vacinacao` (PK), `data_aplicacao`, `crmv` (FK → `veterinarios.crmv`), `id_prontuario` (FK → `prontuarios.id_prontuario`), `nome_vacina`, `lote_vacina`, `data_proxima_dose`.
  - [x] `InternacaoModel` (`internacoes`): `id_internacao` (PK), `id_animal` (FK → `animais.id_animal`), `crmv` (FK → `veterinarios.crmv`), `data_internacao`, `data_alta`, `nivel_gravidade`, `status_internacao`, `evolucao_internacao`.
  - [x] `PlantaoModel` (`plantoes`): `id_plantao` (PK), `id_animal` (FK opcional → `animais.id_animal`), `id_tutor` (FK opcional → `tutores.id_tutor`), `crmv` (FK → `veterinarios.crmv`), `chegada_plantao`, `status_plantao`, `evolucao_plantao`.
- [x] Atualizar `src/api/database.py`:
  - [x] Configurar engine SQLite (`sqlite:///./petegato.db` com `check_same_thread=False`), `PRAGMA foreign_keys=ON`, `sessionmaker` (`SessionLocal`) e `init_db()` (`Base.metadata.create_all`).
  - [x] Implementar a dependência `get_db()` (gerador de `Session` com fechamento garantido).
  - [x] Migrar as operações CRUD e validações de integridade referencial / PK duplicada / `PUT` mismatch para operar sobre `Session` SQLAlchemy 2.0, preservando exatamente os mesmos contratos e exceções de domínio (`404` / `422`).
  - [x] Adaptar `seed_db(db_session)` / `reset_db()` para popular os registros iniciais do contrato (usuários `1` e `2` com senhas com hash, `crmv=12345`, `matricula=1010`, tutor `1`, animal `501`, prontuário `1001`, agendamento `100`, atendimento `8001`, vacinação `1`, internação `4001` e plantão `3001`).

---

## Fase 8: Autenticação JWT + RBAC (`src/api/security.py`, `src/api/routers/auth.py` e proteção de rotas)

- [x] Adicionar schemas `LoginRequest` (`email_usuario`, `senha`) e `TokenResponse` (`access_token`, `token_type`) em `src/api/schemas.py`.
- [x] Criar `src/api/security.py`:
  - [x] Implementar verificação de senha (`verify_password`) compatível com o hash PBKDF2 armazenado em `UsuarioModel.senha_hash`.
  - [x] Implementar criação e decodificação de token JWT HS256 (`create_access_token`, `decode_access_token`).
  - [x] Implementar dependência `get_current_user` (usando `HTTPBearer(auto_error=False)`): valida o token e busca o usuário no banco, lançando exceção `401 Unauthorized` no formato `ErrorResponse` se ausente, inválido ou expirado.
  - [x] Implementar fábrica de dependência `require_perfil(*perfis)`: valida se `current_user.perfil` está autorizado, lançando exceção `403 Forbidden` no formato `ErrorResponse` caso contrário.
- [x] Atualizar `src/api/exceptions.py`:
  - [x] Definir exceções `UnauthorizedError` (`401`) e `ForbiddenError` (`403`) e registrar seus handlers globais retornando `ErrorResponse` (`mensagem` e `detalhes`).
  - [x] Garantir mapeamento de `401` e `403` também no handler de `HTTPException`/`StarletteHTTPException`.
- [x] Criar `src/api/routers/auth.py` (`/api/v1/auth`):
  - [x] `POST /api/v1/auth/login`: autentica `email_usuario` e `senha`, retornando `200 OK` com `TokenResponse` ou `401 Unauthorized` (`ErrorResponse`).
  - [x] `GET /api/v1/auth/me`: retorna `200 OK` com `UsuarioResponse` do usuário autenticado ou `401 Unauthorized` (`ErrorResponse`).
- [x] Proteger as rotas de mutação (`POST`, `PUT`, `DELETE`) nos 11 routers existentes exigindo `Depends(get_current_user)` (mantendo `POST /api/v1/usuarios` aberto para cadastro inicial e todos os `GET` das 11 coleções públicos), declarando `401` em `responses=`.
- [x] Registrar `auth.router` e inicialização do banco (`init_db()` + seed) em `src/api/main.py`.

---

## Fase 9: Atualização da Suíte de Testes + Documentação e CI

- [x] Atualizar `src/api/tests/conftest.py`:
  - [x] Configurar engine/sessão SQLite isolada por teste (ex.: arquivo temporário `tmp_path` ou `sqlite://` compartilhado em memória) sobrescrevendo `get_db` via `app.dependency_overrides`.
  - [x] Criar fixtures `auth_headers` / `veterinario_headers` / `recepcao_headers` obtendo tokens JWT válidos para os testes.
- [x] Criar `src/api/tests/test_auth.py`:
  - [x] Testar `POST /api/v1/auth/login` com sucesso (`200 OK`, `access_token` e `token_type == "bearer"`).
  - [x] Testar `POST /api/v1/auth/login` com e-mail ou senha inválidos (`401 Unauthorized`, formato `ErrorResponse`).
  - [x] Testar `GET /api/v1/auth/me` autenticado (`200 OK` com `UsuarioResponse`, sem `senha`) e sem token (`401` em `ErrorResponse`).
  - [x] Testar rota protegida de mutação sem token (`401`) e validação de `require_perfil` retornando `403` no formato `ErrorResponse`.
- [x] Adaptar os arquivos de teste das 11 coleções (`test_usuarios.py` a `test_plantoes.py` e `test_errors.py`) para enviar o header `Authorization: Bearer <token>` nas requisições `POST`, `PUT` e `DELETE` (mantendo `POST /api/v1/usuarios` aberto).
- [x] Criar `README.md` na raiz do projeto documentando arquitetura, instalação, execução da API, fluxo de autenticação JWT e execução dos testes.
- [x] Criar `.github/workflows/ci.yml` executando instalação de dependências e `pytest` automaticamente.
- [x] Executar `python -m pytest -v src/api/tests` no terminal e comprovar 100% de aprovação de todos os testes antes de concluir a fase.
