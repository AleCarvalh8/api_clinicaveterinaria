# Pet & Gatô API 🐾

## Nome e Propósito da API
A **Pet & Gatô API** é uma solução backend robusta desenvolvida exclusivamente para a gestão completa do fluxo operacional e clínico de uma clínica veterinária.

**Contexto e Problema Resolvido:** 
O dia a dia de uma clínica veterinária exige agilidade e precisão no cruzamento de dados entre a recepção e os consultórios. Esta API resolve a necessidade de centralizar o atendimento, conectando o cadastro de tutores e pacientes (animais) diretamente aos prontuários médicos, agendamentos e controle de urgências (plantões e internações). Desenvolvida como projeto acadêmico para a disciplina de Programação Web (Fatec 2026.2), a aplicação adota o paradigma *Design-First* com tipagem estrita via Pydantic v2 e persistência em memória.

**Público-Alvo:**
- Equipe de clínicas (Recepcionistas, Médicos Veterinários e Gestores/Administradores).
- Desenvolvedores frontend e mobile que consumirão os recursos RESTful para construir as interfaces da clínica.

**Principais Funcionalidades:**
- Gestão unificada de usuários e funcionários (Recepção e Veterinários com registro CRMV).
- Cadastro de tutores e prontuários de animais.
- Controle de agendamentos e esteira de atendimentos.
- Histórico clínico detalhado: registro de prontuários, aplicações de vacinas e acompanhamento de internações.
- Módulo de triagem para plantões de urgência e emergência.

---

## Arquitetura de Recursos

O sistema foi modelado seguindo uma arquitetura relacional RESTful, focado no domínio clínico. As principais entidades e seus relacionamentos incluem:

- **Usuários, Veterinários e Recepção:** Entidades base de controle de acesso (Roles). Cada funcionário logado (seja Veterinário ou Recepcionista) está vinculado a um Usuário do sistema.
- **Tutores e Animais:** Relação de `1:N`. Um tutor humano pode ter vários animais registrados sob sua responsabilidade.
- **Agendamentos e Atendimentos:** Entidades transacionais essenciais. Um agendamento une o Animal, o Recepcionista (que marca) e o Veterinário designado em uma linha do tempo, evoluindo posteriormente para um Atendimento.
- **Prontuários, Vacinações e Internações:** Compõem o cerne do histórico médico. O Prontuário centraliza as queixas e diagnósticos, servindo como base estrutural para registrar Vacinas aplicadas ou encaminhamentos de Internação.
- **Plantões:** Entidade isolada e ágil para gerenciamento de entradas de urgência, permitindo o registro rápido de animais (mesmo sem tutor inicialmente identificado) sob a responsabilidade do veterinário plantonista.

*(Nota técnica: O projeto implementa tratamento de erros padronizado, utilizando o schema customizado `ErrorResponse` em todas as rotas da aplicação em casos de recursos não encontrados (404) ou requisições inválidas (400)).*

---

## Equipe Envolvida

1. **Alexandre de Paula Carvalho** — RA: 2840482423027
2. **Ana Beatriz Baldivia Portas** — RA: 2840482423002
3. **Lídia da Rocha Arruda** — RA: 2840482423022

---

## Metodologia e Arquitetura SDD (Spec-Driven Development)

O desenvolvimento segue o fluxo **Spec-Driven Development (SDD)**, mantendo o contrato OpenAPI como fonte única da verdade e evoluindo para persistência **SQLAlchemy 2.0 + SQLite (`petegato.db`)** e **Autenticação JWT HS256 / RBAC**:

- **`Módulo predefinido.openapi.json`**: Contrato formal OpenAPI 3.0.1 contendo as 11 coleções, schemas, enums, validações (`pattern`, `maxLength`, `minimum`) e respostas padronizadas (`ErrorResponse`).
- **`SPEC.md`**: Especificação de negócio, regras de integridade referencial, seed inicial, persistência ORM e política de autenticação JWT.
- **`STYLEGUIDE.md`**: Constituição técnica definindo stack (Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, pytest), convenções `snake_case`, árvore de diretórios e tratamento de erros.
- **`AGENTS.md`**: Governança de personas (`[Tech Lead]`, `[Backend Coder]`, `[QA Engineer]`) e regras anti-vibe-coding.
- **`PLAN.md`**: Checklist sequencial e granular das 9 fases de implementação, evolução e verificação.

---

## Instalação, Execução e Testes

### 1. Instalar dependências

```bash
pip install -r src/api/requirements.txt
```

### 2. Executar a API

```bash
uvicorn src.api.main:app --reload
```

Acesse a documentação interativa em `http://127.0.0.1:8000/docs`.

- Consultas (`GET`) e cadastro inicial (`POST /api/v1/usuarios`) são públicos.
- Operações de escrita/exclusão (`POST`, `PUT`, `DELETE`) exigem token JWT obtido em `POST /api/v1/auth/login` (ex.: `juliana.santos@petegato.com` / `Vet@2026Pass`).

### 3. Executar a suíte de testes

```bash
python -m pytest -v src/api/tests
```
