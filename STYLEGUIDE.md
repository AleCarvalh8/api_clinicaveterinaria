# STYLEGUIDE.md — Constituição Técnica (Módulo predefinido)

## 1. Stack Tecnológica e Versões Obrigatórias
- **Linguagem:** Python 3.12+ com anotações de tipo (`typing`, `datetime`, `date`, `Enum`).
- **Framework Web:** FastAPI.
- **Validação e Serialização:** Pydantic v2 (`BaseModel`, `ConfigDict`, `Field`, `@field_validator`).
- **Persistência:** Camada de dados isolada em `database.py` com **SQLAlchemy 2.0** (`DeclarativeBase`, `Mapped[...]`, `mapped_column(...)`) e **SQLite** (`petegato.db`), com modelos ORM em `models.py` e sessão via `get_db()`.
- **Autenticação & Autorização:** JWT HS256 em `security.py` (`get_current_user` e `require_perfil`) e rotas em `routers/auth.py`.
- **Suíte de Testes:** `pytest` + `fastapi.testclient.TestClient`.

---

## 2. Arquitetura de Diretórios e Separação de Camadas
Todo o código da API deve respeitar rigorosamente a estrutura abaixo:

```text
.github/
└── workflows/
    └── ci.yml           # Pipeline CI executando pytest
README.md                # Documentação de uso, arquitetura e endpoints
src/api/
├── __init__.py
├── main.py          # Instância FastAPI, CORS, middleware de JSON malformado e registro de rotas
├── schemas.py       # Exclusivamente contratos Pydantic v2 espelhando os components/schemas do Módulo predefinido.openapi.json + Auth (LoginRequest/TokenResponse)
├── models.py        # Modelos ORM SQLAlchemy 2.0 (DeclarativeBase, Mapped[...], relationship)
├── database.py      # Engine SQLite (petegato.db), SessionLocal, get_db(), seed inicial e operações ORM
├── security.py      # Geração/validação JWT HS256, get_current_user (401) e require_perfil (403)
├── exceptions.py    # Exceções de domínio e handlers globais que produzem o schema ErrorResponse (400, 401, 403, 404, 422)
├── requirements.txt # Dependências estritas do projeto
├── routers/
│   ├── __init__.py
│   ├── auth.py          # /api/v1/auth (/login, /me)
│   ├── usuarios.py      # /api/v1/usuarios
│   ├── veterinarios.py  # /api/v1/veterinarios
│   ├── recepcao.py      # /api/v1/recepcao
│   ├── tutores.py       # /api/v1/tutores
│   ├── animais.py       # /api/v1/animais
│   ├── prontuarios.py   # /api/v1/prontuarios
│   ├── agendamentos.py  # /api/v1/agendamentos
│   ├── atendimentos.py  # /api/v1/atendimentos
│   ├── vacinacoes.py    # /api/v1/vacinacoes
│   ├── internacoes.py   # /api/v1/internacoes
│   └── plantoes.py      # /api/v1/plantoes
└── tests/
    ├── __init__.py
    ├── conftest.py            # Fixtures (banco SQLite isolado por teste, client e token JWT)
    ├── test_auth.py           # Testes de login (200/401), /auth/me e proteção JWT/RBAC (401/403)
    ├── test_usuarios.py       # Testes de contrato (um arquivo por coleção, mesmo padrão)
    ├── test_veterinarios.py
    ├── test_recepcao.py
    ├── test_tutores.py
    ├── test_animais.py
    ├── test_prontuarios.py
    ├── test_agendamentos.py
    ├── test_atendimentos.py
    ├── test_vacinacoes.py
    ├── test_internacoes.py
    ├── test_plantoes.py
    └── test_errors.py         # Testes de conformidade do ErrorResponse (400, 401, 403, 404, 422)
```

---

## 3. Regras Inegociáveis de Implementação

### 3.1. Tratamento de Erros (`ErrorResponse`)
- É **PROIBIDO** retornar erros no formato padrão do FastAPI (`{"detail": "..."}`).
- Qualquer erro HTTP (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`) DEVE retornar um JSON compatível com o schema `ErrorResponse` do contrato:
  - `mensagem`: resumo descritivo curto do erro (ex.: `"Não autenticado"`, `"Acesso negado"`, `"Recurso não encontrado"`, `"Erro de validação"`, `"Requisição inválida"`).
  - `detalhes`: explicação detalhada da causa específica (ex.: `"O campo 'nome_tutor' é obrigatório e não foi informado."`).
- Mapeamento de status:
  - `400`: JSON malformado e parâmetros de query/path com tipo ou limite inválido (`page`, `limit`, identificador não inteiro).
  - `401`: token JWT ausente, inválido, expirado ou credenciais de login incorretas.
  - `403`: usuário autenticado sem permissão (`perfil`) exigida por `require_perfil`.
  - `404`: identificador inexistente em `GET`, `PUT` e `DELETE`.
  - `422`: corpo que viola o schema (campo obrigatório ausente, `maxLength`, `pattern`, `enum`, `minimum`), chave duplicada ou chave estrangeira inexistente.
- Todos os handlers globais (`RequestValidationError`, `HTTPException`, exceções de domínio) devem ser registrados em `exceptions.py`.
- Os schemas `Error` (Problem Details) e `Meta` do contrato não são usados em nenhuma rota e não devem ser implementados nas respostas.

### 3.2. Convenções de Nomenclatura JSON vs. Python
- Os payloads JSON de entrada e saída DEVEM preservar exatamente os nomes `snake_case` definidos no contrato, sem aliases `camelCase`:
  - Identificadores: `id_usuario`, `id_tutor`, `id_animal`, `id_prontuario`, `id_agendamento`, `id_atendimento`, `id_vacinacao`, `id_internacao`, `id_plantao`, `crmv`, `matricula`.
  - Demais campos: `nome_usuario`, `email_usuario`, `cpf_recepcao`, `cpf_tutor`, `peso_atual`, `hora_agendamento`, `data_abertura`, `data_proxima_dose`, `status_agendamento`, `nivel_gravidade`, `status_internacao`, `status_plantao`, entre outros.
- Valores de enum devem ser preservados exatamente como no contrato, incluindo espaços e ausência de acentos (`"Em espera"`, `"Em analise"`, `"Concluido"`, `"Obito"`, `"Medio"`, `"Critica"`).
- A `senha` (`writeOnly`) existe apenas em `UsuarioCreate` e jamais deve ser serializada em respostas nem armazenada em texto puro.

### 3.3. Semântica de Verbos e Status HTTP
- `GET` de coleção: `200 OK` com **array JSON** paginado por `page`/`limit`, sem envelope.
- `POST`: deve retornar `201 Created` com o recurso criado.
- `PUT`: atualização integral; retorna `200 OK` com o recurso atualizado. O contrato não define `PATCH`.
- `DELETE`: deve retornar `204 No Content` sem corpo na resposta (`Response(status_code=status.HTTP_204_NO_CONTENT)`).
- As rotas devem declarar `responses=` com os códigos documentados no contrato (`404`, `422`) para refletir o OpenAPI de origem.
