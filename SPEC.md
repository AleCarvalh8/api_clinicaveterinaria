# SPEC.md — Especificação de Negócio e Contrato (Módulo predefinido)

## 1. Visão Geral e Fonte da Verdade do Contrato
Este projeto implementa a API definida em **Módulo predefinido.openapi.json**, uma API RESTful para o sistema de gestão da clínica veterinária **Pet & Gatô**, baseada no modelo relacional DDL (Oracle SQL Developer). Cobre usuários, funcionários (veterinários e recepção), tutores, animais, agendamentos, prontuários, atendimentos, vacinações, internações e plantões.
O contrato formal de interface (rotas, parâmetros, respostas e JSON Schemas) está definido em `@[Módulo predefinido.openapi.json](Módulo predefinido.openapi.json)` (OpenAPI 3.0.1, versão `1.0.0`). Em caso de divergência entre este documento e o contrato, o contrato prevalece.

---

## 2. Prioridade Arquitetural: Extração de Tipos (Schema-First)
O sistema DEVE extrair e consolidar todas as tipagens estáticas (modelos Pydantic v2 em `src/api/schemas.py`) diretamente de `components/schemas` do Módulo predefinido.openapi.json **antes** de implementar qualquer lógica de banco de dados ou rotas HTTP. Os nomes de campos são `snake_case` e devem ser preservados exatamente como no contrato.

1. **Enums de Domínio:**
   - `StatusAgendamento`: `"Agendado"`, `"Em espera"`, `"Em atendimento"`, `"Concluido"`, `"Cancelado"`
   - `NivelGravidade`: `"Baixa"`, `"Medio"`, `"Alta"`, `"Critica"`
   - `StatusInternacao`: `"Internado"`, `"Alta"`, `"Obito"`
   - `StatusPlantao`: `"Em analise"`, `"Internado"`, `"Alta"`, `"Obito"`
   - `perfil` (de `UsuarioCreate`/`UsuarioResponse`): `"Recepcao"`, `"Veterinario"`
   - `sexo` (de `Animal`): `"F"`, `"M"`
2. **Usuários:**
   - `UsuarioCreate` (entrada): `id_usuario` (int), `nome_usuario` (até 120), `email_usuario` (até 50, padrão `^[A-Za-z0-9._%+-]+@petegato\.com$`), `senha` (8 a 50 caracteres, padrão `^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,50}$`, **writeOnly**), `perfil` (até 11, enum). Todos obrigatórios.
   - `UsuarioResponse` (saída): `id_usuario`, `nome_usuario`, `email_usuario`, `perfil`. A `senha` NUNCA pode aparecer em respostas.
3. **Funcionários:**
   - `Veterinario`: `crmv` (int, PK), `cnpj` (até 18, padrão `^[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}$`), `especialidade` (até 50), `id_usuario` (int, FK). Todos obrigatórios.
   - `Recepcao`: `matricula` (int, PK), `cpf_recepcao` (até 14, padrão `^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$`), `id_usuario` (int, FK). Todos obrigatórios.
4. **Tutores e Animais:**
   - `Tutor`: `id_tutor` (int), `nome_tutor` (até 120), `cpf_tutor` (até 14, padrão de CPF acima) obrigatórios; `email_tutor` (até 50, padrão `^[A-Za-z0-9._%+-]+@[a-z]+\.[a-z.]{2,}$`, nulável), `telefone` (até 15, nulável), `observacoes` (até 300, nulável).
   - `Animal`: `id_animal` (int), `id_tutor` (int, FK), `tipo_animal` (até 15), `raca` (até 35) obrigatórios; `nome_animal` (até 30, nulável), `sexo` (enum `F`/`M`, nulável), `data_nascimento` (`date`, nulável).
5. **Clínico:**
   - `Prontuario`: obrigatórios `id_prontuario`, `crmv`, `id_animal`, `peso_atual` (double, mínimo `0.01`), `queixa` (até 300), `diagnostico` (até 200); opcionais `data_abertura` (`date-time`, padrão timestamp atual), `anamnese` (nulável), `receita` (até 200, nulável), `vacina` (até 200, nulável).
   - `Atendimento`: obrigatórios `id_atendimento`, `id_prontuario`; opcional `hora_atendimento` (`date-time`).
   - `Vacinacao`: obrigatórios `id_vacinacao`, `data_aplicacao` (`date-time`), `crmv`, `id_prontuario`, `nome_vacina` (até 30), `lote_vacina` (até 30); opcional `data_proxima_dose` (`date`, nulável).
6. **Agenda e Internação:**
   - `Agendamento`: obrigatórios `id_agendamento`, `hora_agendamento` (`date-time`), `id_animal`, `crmv`, `matricula`; opcional `status_agendamento` (`StatusAgendamento`, padrão `"Agendado"`).
   - `Internacao`: obrigatórios `id_internacao`, `id_animal`, `crmv`; opcionais `data_internacao` (`date-time`, padrão timestamp atual), `data_alta` (nulável), `nivel_gravidade` (`NivelGravidade`, nulável), `status_internacao` (`StatusInternacao`, padrão `"Internado"`), `evolucao_internacao` (nulável).
   - `Plantao`: obrigatórios `id_plantao`, `crmv`; opcionais `id_animal` (nulável), `id_tutor` (nulável), `chegada_plantao` (`date-time`, padrão timestamp atual), `status_plantao` (`StatusPlantao`, padrão `"Em analise"`), `evolucao_plantao` (nulável).
7. **Modelos de Erro:**
   - `ErrorResponse`: `mensagem` (str) e `detalhes` (str), ambos obrigatórios. É o schema referenciado pelas respostas reutilizáveis `400BadRequest`, `404NotFound` e `422UnprocessableEntity`.
   - Os schemas `Error` (Problem Details) e `Meta` existem em `components/schemas`, mas **não são referenciados por nenhuma rota**; não devem ser usados nas respostas enquanto o contrato não os adotar.

---

## 3. Regras de Negócio e Comportamento dos Endpoints

### 3.1. Padrão CRUD das Coleções
Todas as 11 coleções seguem o mesmo padrão, mudando apenas o recurso, o schema e o parâmetro de path:

| Coleção | Base | Parâmetro de path | Schema |
|---|---|---|---|
| Usuários | `/api/v1/usuarios` | `id_usuario` | `UsuarioCreate` (entrada) / `UsuarioResponse` (saída) |
| Veterinários | `/api/v1/veterinarios` | `crmv` | `Veterinario` |
| Recepção | `/api/v1/recepcao` | `matricula` | `Recepcao` |
| Tutores | `/api/v1/tutores` | `id_tutor` | `Tutor` |
| Animais | `/api/v1/animais` | `id_animal` | `Animal` |
| Prontuários | `/api/v1/prontuarios` | `id_prontuario` | `Prontuario` |
| Agendamentos | `/api/v1/agendamentos` | `id_agendamento` | `Agendamento` |
| Atendimentos | `/api/v1/atendimentos` | `id_atendimento` | `Atendimento` |
| Vacinações | `/api/v1/vacinacoes` | `id_vacinacao` | `Vacinacao` |
| Internações | `/api/v1/internacoes` | `id_internacao` | `Internacao` |
| Plantões | `/api/v1/plantoes` | `id_plantao` | `Plantao` |

Operações (sem `PATCH` no contrato):
- **`GET {base}`**: lista paginada. Query: `page` (int, default `1`, min `1`), `limit` (int, default `10`, min `1`, max `100`). Retorna `200 OK` com um **array JSON** do schema (sem envelope `data`/`meta`). Parâmetros fora dos limites/tipos → `400 Bad Request` (`ErrorResponse`).
- **`POST {base}`**: cria o recurso e retorna `201 Created` com o objeto criado. Corpo inválido (campo obrigatório ausente, violação de `maxLength`/`pattern`/`enum`/`minimum`) → `422` (`ErrorResponse`).
- **`GET {base}/{id}`**: `200 OK` com o objeto ou `404 Not Found` (`ErrorResponse`). O parâmetro de path é `integer`.
- **`PUT {base}/{id}`**: atualização integral (substitui todos os campos); `200 OK` com o objeto atualizado, `404` se inexistente, `422` em erro de validação.
- **`DELETE {base}/{id}`**: `204 No Content` (sem corpo) ou `404 Not Found`.

Observações:
- As chaves primárias (`id_*`, `crmv`, `matricula`) são informadas pelo cliente no corpo do `POST`, conforme o contrato. Chave duplicada ou chave estrangeira inexistente (ex.: `id_tutor` em `Animal`, `id_usuario` em `Veterinario`) é erro semântico e retorna `422`, pois o contrato não documenta `409`.
- Em `PUT`, o identificador do corpo deve coincidir com o do path; divergência retorna `422`.
- `POST /api/v1/usuarios`: o perfil (`perfil`) e o e-mail corporativo `@petegato.com` são validados; a resposta usa `UsuarioResponse` (sem `senha`).

### 3.2. Resiliência e Comportamentos Transversais
- **ID inexistente:** qualquer `GET`, `PUT` ou `DELETE` sobre um identificador que não exista retorna `404 Not Found` com `ErrorResponse`.
- **Middleware de JSON Malformado:** requisições `POST` ou `PUT` com `Content-Type: application/json` e corpo JSON inválido retornam `400 Bad Request` com `ErrorResponse`.
- **Seed Inicial:** o banco deve inicializar com registros de exemplo coerentes entre si, usando os exemplos do contrato: usuário `1` (Veterinario, `juliana.santos@petegato.com`) e `2` (Recepcao), veterinário `crmv=12345`, recepção `matricula=1010`, tutor `1`, animal `501` (Mingau, Gato, Siamês), prontuário `1001`, agendamento `100`, atendimento `8001`, vacinação `1`, internação `4001` e plantão `3001`.

---

## 4. Evolução: Persistência ORM (SQLAlchemy 2.0 + SQLite)
- A persistência passa a utilizar **SQLite** (`petegato.db`) via **SQLAlchemy 2.0** (`DeclarativeBase`, `Mapped[...]`, `mapped_column(...)`, `ForeignKey` e `relationship`) em `src/api/models.py` e `src/api/database.py`.
- A dependência de sessão `get_db()` deve fornecer e encerrar corretamente a sessão por requisição, mantendo o seed inicial idempotente com senhas armazenadas exclusivamente com hash seguro.
- Todos os 11 recursos existentes devem preservar exatamente os mesmos contratos de entrada/saída, paginação e integridade referencial definidos nas Seções 2 e 3.

---

## 5. Evolução: Autenticação JWT e Controle de Acesso (RBAC)
- **Schemas de Autenticação:**
  - `LoginRequest`: `email_usuario` (str), `senha` (str).
  - `TokenResponse`: `access_token` (str), `token_type` (str, padrão `"bearer"`).
- **Endpoints de Autenticação (`/api/v1/auth`):**
  - `POST /api/v1/auth/login`: valida `email_usuario` e `senha` contra o hash armazenado; retorna `200 OK` com `TokenResponse` (JWT HS256) ou `401 Unauthorized` (`ErrorResponse`) em credenciais inválidas.
  - `GET /api/v1/auth/me`: retorna `200 OK` com `UsuarioResponse` do usuário autenticado ou `401 Unauthorized` (`ErrorResponse`).
- **Política de Proteção das Rotas:**
  - Consultas `GET` das 11 coleções permanecem públicas.
  - `POST /api/v1/usuarios` permanece aberto para permitir o cadastro inicial de usuários.
  - Demais rotas de mutação (`POST`, `PUT`, `DELETE`) exigem header `Authorization: Bearer <token>` válido via `get_current_user`.
  - `require_perfil(*perfis)` permite restringir acesso por perfil (`Veterinario` / `Recepcao`), retornando `403 Forbidden` no schema `ErrorResponse` quando o perfil não for autorizado.
- **Erros `401` e `403`:** devem obrigatoriamente retornar o schema `ErrorResponse` (`mensagem` e `detalhes`).
