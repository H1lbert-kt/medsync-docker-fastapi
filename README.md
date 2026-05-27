# MedSync API

O MedSync é uma API de gerenciamento de clínicas médicas desenvolvida com o framework FastAPI e o banco de dados PostgreSQL. Este é um projeto inicial criado com o objetivo principal de estudar e aplicar conceitos de conteinerização de aplicações, isolamento de ambientes e orquestração de serviços com Docker e Docker Compose.

# Tecnologias Utilizadas

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Docker
* Docker Compose

# Pré requisitos

Para executar este projeto, é necessário ter instalado em sua máquina:

* Docker
* Docker Compose

# Instruções de Execução

1. Clone este repositório para a sua máquina local:
   git clone https://github.com/H1lbert-kt/medsync-docker-fastapi.git

2. Acesse a pasta do projeto:
   cd medsync-docker-fastapi

3. Configure as variáveis de ambiente necessárias para o banco de dados criando um arquivo chamado .env na raiz do projeto com a estrutura contida no arquivo .env.example.

4. Execute o comando do Docker Compose para construir as imagens e iniciar os serviços:
   docker compose up --build

5. Após a inicialização completa dos contêineres, a documentação interativa da API estará disponível no seguinte endereço:
   http://localhost:8000/docs
