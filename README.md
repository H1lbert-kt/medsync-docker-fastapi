# MedSync API

Uma API para gerenciamento de clínicas médicas, feita com FastAPI e PostgreSQL.

## O que ela faz?

- Cadastro de médicos, pacientes e consultas
- Sistema de autenticação com JWT (login e controle de acesso por perfil)
- Agendamento de consultas com validações (não agenda no passado, não agenda no mesmo horário)
- Cancelamento de consultas
- Perfis com permissões: Admin, Recepção, Médico e Paciente

## Tecnologias

- **Python** + **FastAPI**
- **SQLAlchemy** (ORM)
- **PostgreSQL** (banco de dados)
- **JWT** (autenticação)
- **Docker** + **Docker Compose** (containerização)
- **Pydantic** (validação de dados)

## Rodando local com Docker

1. Clone o repositório:
```bash
git clone https://github.com/H1lbert-kt/medsync-docker-fastapi.git
cd medsync-docker-fastapi
```

2. Crie o arquivo `.env` na raiz do projeto:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=medsync
SECRET_KEY=uma_chave_forte_de_64 caracteres_hex
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

3. Suba os containers:
```bash
docker compose up --build
```

4. Acesse a documentação interativa:
```
http://localhost:8000/docs
```

## Rodando local sem Docker

1. Crie e ative um virtualenv:
```bash
python -m venv venv
source venv/bin/activate
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie o arquivo `.env` (veja o exemplo acima)

4. Rode o servidor:
```bash
uvicorn app.main:app --reload
```

5. Acesse `http://localhost:8000/docs`

## Variáveis de ambiente

| Variável | Descrição | Obrigatória? |
|----------|-----------|-------------|
| `DATABASE_URL` | URL de conexão com o banco (ex: `postgresql://user:pass@host:5432/db`) | Sim (Docker já configura automaticamente) |
| `SECRET_KEY` | Chave secreta para assinar os tokens JWT | Sim |
| `ALGORITHM` | Algoritmo de codificação JWT (padrão: `HS256`) | Não |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de vida do token em minutos (padrão: 60) | Não |
| `POSTGRES_USER` | Usuário do PostgreSQL | Sim (Docker) |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | Sim (Docker) |
| `POSTGRES_DB` | Nome do banco de dados | Sim (Docker) |

## Deploy no Render

1. Crie um **Web Service** no [Render](https://render.com)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente no painel do Render (as mesmas do `.env`)
4. No campo **Start Command**, coloque:

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

> **Nota:** O Render fornece a variável `$PORT` automaticamente. Não precisa definir uma porta fixa.

5. Se estiver usando Docker no Render, o comando padrão do Dockerfile já funciona:
```
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Estrutura do projeto

```
medsync/
├── app/
│   ├── core/
│   │   ├── dependencies.py    # Autenticação e controle de acesso
│   │   └── security.py        # Hash de senhas e criação de tokens
│   ├── models/
│   │   └── clinic.py          # Models do banco (User, Doctor, Patient, Appointment)
│   ├── routers/
│   │   ├── auth.py            # Rota de login
│   │   └── clinic.py          # Rotas de CRUD
│   ├── schemas/
│   │   └── clinic.py          # Schemas Pydantic (validação)
│   ├── services/
│   │   └── clinic_services.py # Lógica de negócio
│   ├── database.py            # Configuração do banco
│   └── main.py                # Entry point da aplicação
├── tests/
│   ├── conftest.py            # Fixtures dos testes
│   ├── test_auth.py           # Testes de autenticação
│   └── test_clinic.py         # Testes das rotas da clínica
├── dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Endpoints principais

| Método | Rota | Descrição | Quem pode acessar |
|--------|------|-----------|-------------------|
| POST | `/auth/login` | Login e retorno do token JWT | Qualquer um |
| POST | `/clinic/doctors` | Cadastrar médico | Admin |
| POST | `/clinic/patients` | Cadastrar paciente | Admin, Recepção |
| POST | `/clinic/appointments` | Agendar consulta | Admin, Recepção, Paciente |
| GET | `/clinic/doctors` | Listar médicos | Qualquer um autenticado |
| GET | `/clinic/patients` | Listar pacientes | Admin, Recepção |
| GET | `/clinic/appointments` | Listar consultas | Qualquer um (filtra por perfil) |
| PATCH | `/clinic/appointments/{id}/cancel` | Cancelar consulta | Dono da consulta, Admin |

## Rodando os testes

```bash
python -m pytest tests/ -v
```
