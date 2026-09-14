# MedSync API

API REST para gerenciamento de clínicas médicas, permitindo cadastro de médicos, pacientes e agendamento de consultas, com autenticação JWT e controle de acesso por perfil.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Modelo de Dados](#modelo-de-dados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Instalação e Execução](#instalação-e-execução)
- [Docker](#docker)
- [Alembic (Migrations)](#alembic-migrations)
- [Endpoints da API](#endpoints-da-api)
- [Autenticação e Controle de Acesso](#autenticação-e-controle-de-acesso)
- [Testes](#testes)
- [Deploy](#deploy)

---

## Visão Geral

O MedSync API é um sistema de agendamento de consultas médicas construído com FastAPI e SQLAlchemy. Ele gerencia o ciclo completo de uma clínica:

- Cadastro de usuários com perfis distintos (Admin, Recepção, Médico, Paciente)
- Cadastro de médicos com CRM e vínculo ao perfil de usuário
- Cadastro de pacientes com telefone e vínculo ao perfil de usuário
- Agendamento de consultas com validações de data e horário
- Cancelamento de consultas com controle de permissão
- Consultas filtradas automaticamente por perfil (paciente vê só suas, médico vê só suas)

---

## Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| Autenticação JWT | Login com email/senha, retorno de token Bearer com expiração configurável |
| Cadastro de médicos | Admin pode cadastrar médicos com nome, CRM e dados de login |
| Cadastro de pacientes | Admin e Recepção podem cadastrar pacientes com nome, telefone e dados de login |
| Agendamento de consultas | Admin, Recepção e Paciente podem agendar consultas (paciente automaticamente vinculado ao seu perfil) |
| Listagem de consultas | Cada perfil vê apenas suas consultas: paciente vê as suas, médico vê as suas, admin/recepção vê todas |
| Cancelamento de consultas | Paciente só cancela as suas; admin e recepção podem cancelar qualquer uma |
| Validação de agendamento | Impede agendamento no passado e no mesmo horário para o mesmo médico |
| Controle de acesso | 4 perfis com permissões distintas: ADMIN, RECEPTIONIST, DOCTOR, PATIENT |
| Migrations com Alembic | Controle de versão do schema do banco de dados |

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.12+ | Linguagem principal |
| FastAPI | 0.136.1 | Framework web (async) |
| SQLAlchemy | 2.0.49 | ORM e acesso a banco |
| Pydantic | 2.13.4 | Validação e serialização de dados |
| Alembic | 1.20.0 | Migrations do banco de dados |
| PostgreSQL | 16 | Banco de dados principal |
| SQLite | — | Banco para desenvolvimento local e testes |
| PyJWT | 2.13.0 | Criação e validação de tokens JWT |
| Argon2 | 25.1.0 | Hash e verificação de senhas (mais seguro que bcrypt) |
| Docker | — | Containerização da aplicação |
| Docker Compose | — | Orquestração dos containers |
| Uvicorn | 0.48.0 | Servidor ASGI |
| pytest | 9.1.1 | Framework de testes |

---

## Modelo de Dados

### Diagrama de Relacionamento

```
UserModel (users)
├── id              PK
├── email           UNIQUE, NOT NULL
├── password_hash   NOT NULL
└── role            ENUM (ADMIN, RECEPTIONIST, DOCTOR, PATIENT)

DoctorModel (doctors)
├── id              PK
├── user_id         FK → users.id (CASCADE), UNIQUE, NOT NULL
├── name            NOT NULL
└── crm             UNIQUE, NULL

PatientModel (patients)
├── id              PK
├── user_id         FK → users.id (CASCADE), UNIQUE, NOT NULL
├── name            NOT NULL
└── phone           NOT NULL

AppointmentModel (appointments)
├── id              PK
├── doctor_id       FK → doctors.id (RESTRICT), NOT NULL
├── patient_id      FK → patients.id (RESTRICT), NOT NULL
├── date_consultation   NOT NULL
├── consultation_time   NOT NULL
├── status          ENUM (scheduled, confirmed, cancelled), DEFAULT 'scheduled'
├── created_at      DEFAULT UTC NOW
└── UNIQUE CONSTRAINT (doctor_id, date_consultation, consultation_time)
```

### Relacionamentos

- **User ↔ Doctor**: Um-para-um. Um usuário com role DOCTOR possui no máximo um perfil de médico. Ao deletar o usuário, o perfil do médico é deletado (CASCADE).
- **User ↔ Patient**: Um-para-um. Um usuário com role PATIENT possui no máximo um perfil de paciente. Ao deletar o usuário, o perfil do paciente é deletado (CASCADE).
- **Doctor ↔ Appointment**: Um-para-muitos. Um médico pode ter várias consultas. Não é possível deletar um médico que tenha consultas agendadas (RESTRICT).
- **Patient ↔ Appointment**: Um-para-muitos. Um paciente pode ter várias consultas. Não é possível deletar um paciente que tenha consultas agendadas (RESTRICT).

---

## Estrutura do Projeto

```
medsync/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Dependências FastAPI (autenticação, controle de acesso)
│   │   └── security.py          # Hash de senhas (Argon2) e criação de tokens JWT
│   ├── models/
│   │   ├── __init__.py
│   │   └── clinic.py            # Models SQLAlchemy (User, Doctor, Patient, Appointment)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Rota de autenticação (login)
│   │   └── clinic.py            # Rotas de CRUD (médicos, pacientes, consultas)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── clinic.py            # Schemas Pydantic (validação de entrada/saída)
│   ├── services/
│   │   ├── __init__.py
│   │   └── clinic_services.py   # Lógica de negócio (criação, autenticação)
│   ├── database.py              # Configuração do engine, session e Base
│   └── main.py                  # Entry point da aplicação FastAPI
├── alembic/
│   ├── versions/
│   │   └── 827eeaf94fc9_initial_tables.py  # Migration inicial
│   ├── env.py                   # Configuração do Alembic (conexão + metadata)
│   └── script.py.mako           # Template para novas migrations
├── tests/
│   ├── conftest.py              # Fixtures (cliente de teste, db em memória, tokens)
│   ├── test_auth.py             # Testes de autenticação
│   └── test_clinic.py           # Testes das rotas da clínica
├── .env                         # Variáveis de ambiente (não versionado)
├── .env.example                 # Exemplo das variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
├── alembic.ini                  # Configuração do Alembic
├── docker-compose.yml           # Orquestração dos containers
├── dockerfile                   # Build da imagem da API
├── medsync.db                   # Banco SQLite local (não versionado)
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

---

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória? | Padrão |
|----------|-----------|-------------|--------|
| `DATABASE_URL` | URL de conexão com o banco de dados | Sim (Docker configura automaticamente) | `sqlite:///./medsync.db` |
| `SECRET_KEY` | Chave secreta para assinar tokens JWT (mínimo 32 caracteres hex) | Sim | — |
| `ALGORITHM` | Algoritmo de codificação JWT | Não | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de vida do token em minutos | Não | `60` |
| `POSTGRES_USER` | Usuário do PostgreSQL (usado pelo Docker) | Sim (Docker) | — |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL (usado pelo Docker) | Sim (Docker) | — |
| `POSTGRES_DB` | Nome do banco de dados PostgreSQL (usado pelo Docker) | Sim (Docker) | — |

> **Importante**: Nunca versione o arquivo `.env`. Ele já está no `.gitignore`.

---

## Instalação e Execução

### Pré-requisitos

- Python 3.12+
- pip
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/H1lbert-kt/medsync-docker-fastapi.git
cd medsync-docker-fastapi
```

### 2. Crie e ative o virtualenv

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações. Para gerar uma `SECRET_KEY` segura:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Aplique as migrations do banco

```bash
alembic upgrade head
```

### 6. Inicie o servidor

```bash
uvicorn app.main:app --reload
```

### 7. Acesse a documentação

```
http://localhost:8000/docs
```

---

## Docker

### Subindo com Docker Compose

```bash
docker compose up --build
```

Isso irá:

1. Criar o container do PostgreSQL (`medsync_db`) na porta 5433
2. Aguardar o banco ficar saudável (healthcheck)
3. Criar o container da API (`medsync_api`) na porta 8000
4. Aplicar as migrations automaticamente via Alembic

### Estrutura dos Containers

| Container | Imagem | Porta | Descrição |
|-----------|--------|-------|-----------|
| `medsync_db` | `postgres:16-alpine` | 5433 → 5432 | Banco de dados PostgreSQL |
| `medsync_api` | Build do Dockerfile | 8000 → 8000 | API FastAPI |

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app/
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Parando os containers

```bash
docker compose down
```

### Parando e removendo dados

```bash
docker compose down -v
```

---

## Alembic (Migrations)

O projeto utiliza Alembic para controle de versão do schema do banco de dados. Isso permite alterar o banco sem perder dados.

### Fluxo de Trabalho

Quando você altera um model (ex: adiciona uma coluna), o processo é:

1. Altere o model em `app/models/clinic.py`
2. Gere a migration:
   ```bash
   alembic revision --autogenerate -m "descrição da mudança"
   ```
3. Revise o arquivo gerado em `alembic/versions/`
4. Aplique a migration:
   ```bash
   alembic upgrade head
   ```

### Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `alembic upgrade head` | Aplica todas as migrations pendentes |
| `alembic upgrade +1` | Aplica apenas a próxima migration |
| `alembic downgrade -1` | Desfaz a última migration aplicada |
| `alembic downgrade base` | Desfaz todas as migrations (zera o banco) |
| `alembic current` | Mostra qual migration está aplicada no banco |
| `alembic history` | Lista todas as migrations existentes |
| `alembic revision --autogenerate -m "msg"` | Gera uma nova migration automaticamente |

### Configuração

- **`alembic.ini`**: Configuração principal (path das migrations, logging)
- **`alembic/env.py`**: Configura a conexão com o banco e importa os models para autogenerate
- **`alembic/versions/`**: Pasta onde ficam os arquivos de migration

### Como Funciona por Baixo dos Panos

1. O Alembic mantém uma tabela `alembic_version` no banco com o hash da última migration aplicada
2. Ao rodar `alembic upgrade head`, ele compara a versão atual com o histórico e aplica apenas o que falta
3. Ao rodar `alembic downgrade`, ele executa a função `downgrade()` da migration para reverter as mudanças
4. O `autogenerate` compara os models SQLAlchemy com o estado atual do banco e gera automaticamente as operações necessárias (CREATE TABLE, ALTER TABLE, etc.)

---

## Endpoints da API

### Autenticação

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|-------------|
| `POST` | `/auth/login` | Login e retorno do token JWT | Nenhuma |

**Requisição POST /auth/login:**
```json
{
  "username": "admin@medsync.com",
  "password": "admin123"
}
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Médicos

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|-------------|
| `POST` | `/clinic/doctors` | Cadastrar médico | Admin |
| `GET` | `/clinic/doctors` | Listar todos os médicos | Admin, Recepção |

**Requisição POST /clinic/doctors:**
```json
{
  "user": {
    "email": "doctor@medsync.com",
    "password": "docpassword123",
    "role": "DOCTOR"
  },
  "name": "Gregory House",
  "crm": "123456-SP"
}
```

**Resposta (201):**
```json
{
  "id": 1,
  "name": "Gregory House",
  "crm": "123456-SP",
  "user": {
    "id": 2,
    "email": "doctor@medsync.com",
    "role": "DOCTOR"
  }
}
```

### Pacientes

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|-------------|
| `POST` | `/clinic/patients` | Cadastrar paciente | Admin, Recepção |
| `GET` | `/clinic/patients` | Listar todos os pacientes | Admin, Recepção |

**Requisição POST /clinic/patients:**
```json
{
  "user": {
    "email": "patient@medsync.com",
    "password": "patient123",
    "role": "PATIENT"
  },
  "name": "João Silva",
  "phone": "11999998888"
}
```

### Consultas

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|-------------|
| `POST` | `/clinic/appointments` | Agendar consulta | Admin, Recepção, Paciente |
| `GET` | `/clinic/appointments` | Listar consultas (filtrado por perfil) | Qualquer autenticado |
| `PATCH` | `/clinic/appointments/{id}/cancel` | Cancelar consulta | Dono da consulta, Admin, Recepção |

**Requisição POST /clinic/appointments:**
```json
{
  "doctor_id": 1,
  "patient_id": 1,
  "date_consultation": "2026-09-20",
  "consultation_time": "14:30:00"
}
```

**Resposta (201):**
```json
{
  "id": 1,
  "doctor_id": 1,
  "patient_id": 1,
  "date_consultation": "2026-09-20",
  "consultation_time": "14:30:00",
  "status": "scheduled",
  "created_at": "2026-09-14T15:30:00"
}
```

### Respostas de Erro

| Código | Descrição |
|--------|-----------|
| `400` | Dados inválidos ou email/CRM já cadastrado |
| `401` | Credenciais inválidas ou token expirado/ausente |
| `403` | Acesso negado para o perfil do usuário |
| `404` | Recurso não encontrado (médico, paciente, consulta) |
| `409` | Conflito (médico já tem consulta nesse horário) |
| `422` | Erro de validação nos dados de entrada |

---

## Autenticação e Controle de Acesso

### Fluxo de Autenticação

1. O usuário faz login em `POST /auth/login` com email e senha
2. O servidor valida as credenciais e retorna um token JWT
3. O token deve ser enviado no header de todas as requisições protegidas:
   ```
   Authorization: Bearer <token>
   ```

### Conteúdo do Token JWT

O token contém:
- `sub`: ID do usuário
- `role`: Role do usuário (ADMIN, RECEPTIONIST, DOCTOR, PATIENT)
- `exp`: Data de expiração

### Perfis e Permissões

| Permissão | Admin | Recepção | Médico | Paciente |
|-----------|-------|----------|--------|----------|
| Login | ✅ | ✅ | ✅ | ✅ |
| Cadastrar médico | ✅ | ❌ | ❌ | ❌ |
| Cadastrar paciente | ✅ | ✅ | ❌ | ❌ |
| Agendar consulta | ✅ | ✅ | ❌ | ✅ (si mesmo) |
| Listar médicos | ✅ | ✅ | ❌ | ❌ |
| Listar pacientes | ✅ | ✅ | ❌ | ❌ |
| Listar consultas | ✅ (todas) | ✅ (todas) | ✅ (as suas) | ✅ (as suas) |
| Cancelar consulta | ✅ | ✅ | ❌ | ✅ (as suas) |

### Segurança

- **Senhas**: Hasheadas com Argon2 (mais seguro que bcrypt/scrypt)
- **Tokens**: Assinados com HS256, expiração configurável
- **Banco**: Foreign keys com CASCADE/RESTRICT para integridade referencial
- **Validação**: Pydantic valida todos os dados de entrada
- **Profils**: Controle de acesso por role em cada endpoint

---

## Testes

### Rodando os Testes

```bash
# Com virtualenv ativo
PYTHONPATH=. pytest tests/ -v

# Com cobertura de código
PYTHONPATH=. pytest tests/ -v --cov=app --cov-report=term-missing
```

### Estrutura dos Testes

- **`tests/conftest.py`**: Configuração dos testes
  - Cria um banco SQLite em memória para cada teste
  - Fornece fixtures: `db_session`, `client`, `admin_user`, `admin_token`
  - Sobrescreve a dependência `get_db` do FastAPI para usar o banco de teste

- **`tests/test_auth.py`**: Testes de autenticação
  - Login com credenciais válidas
  - Login com credenciais inválidas

- **`tests/test_clinic.py`**: Testes das rotas da clínica
  - Cadastro de médico por admin (sucesso)
  - Cadastro de médico sem token (401)

### Testes Atuais

| Teste | Descrição | Status |
|-------|-----------|--------|
| `test_login_success` | Login com admin retorna token | ✅ Passou |
| `test_login_invalid_credentials` | Login com senha errada retorna 401 | ✅ Passou |
| `test_create_doctor_as_admin_success` | Admin cadastra médico com sucesso | ✅ Passou |
| `test_create_doctor_unauthorized_token` | Requisição sem token retorna 401 | ✅ Passou |

---

## Deploy

### Render

1. Crie um **Web Service** no [Render](https://render.com)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente no painel do Render
4. No campo **Start Command**, coloque:
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. O Render fornece a variável `$PORT` automaticamente

### Outros Provedores

Para qualquer provedor (Railway, Fly.io, AWS, etc.), o processo é similar:

1. Configure as variáveis de ambiente
2. Execute `alembic upgrade head` antes de iniciar o servidor
3. Inicie com `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Comandos Rápidos Referência

```bash
# Desenvolvimento
uvicorn app.main:app --reload                    # Iniciar com hot reload
PYTHONPATH=. pytest tests/ -v                     # Rodar testes

# Docker
docker compose up --build                         # Subir containers
docker compose down                               # Parar containers
docker compose down -v                            # Parar e remover dados

# Alembic
alembic upgrade head                              # Aplicar todas as migrations
alembic downgrade -1                              # Desfazer última migration
alembic revision --autogenerate -m "msg"          # Gerar nova migration
alembic current                                   # Verificar versão atual
alembic history                                   # Listar histórico
```
