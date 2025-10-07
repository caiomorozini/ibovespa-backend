# melhorpreco-backend

Microserviço FastAPI para ingestão, armazenamento e predição de preços de dispositivos (celulares).

## Visão geral

O `melhorpreco-backend` é um serviço escrito em Python/FastAPI que expõe endpoints para:

- Autenticação (OAuth2 password flow + JWT)
- CRUD/ingestão de registros (categorias, registros, preços)
- Treinamento e predição de modelos de preço

O projeto usa SQLAlchemy 2.x com AsyncSession e o banco PostgreSQL (via asyncpg). Os modelos estão em `app/models`.

## Estrutura principal

- `app/main.py` - inicializa a aplicação e registra routers
- `app/routes/` - endpoints da API (auth, data, categories, modelo)
- `app/models/` - modelos SQLAlchemy (auth/data)
- `app/schemas/` - Pydantic models (requests/responses)
- `app/database/` - criação de engine e sessão assíncrona
- `app/services/` - lógica de autenticação, hashing e JWT
- `app/dependencies/` - dependências do FastAPI (ex: get_current_user)

## Dependências

Gerenciador de pacotes: Poetry (arquivo `pyproject.toml`). Dependências principais:

- fastapi
- sqlalchemy >=2.x
- asyncpg
- python-jose
- pydantic-settings
- pandas, scikit-learn (para treinamento de modelos)

Consulte `pyproject.toml` para a lista completa.

## Variáveis de ambiente

Crie um arquivo `.env` com as variáveis necessárias (conforme `app/resources/config.py`):

- DATABASE_HOSTNAME / database_hostname
- DATABASE_PORT / database_port
- DATABASE_NAME / database_name
- DATABASE_USERNAME / database_username
- DATABASE_PASSWORD / database_password
- JWT_SECRET_KEY / jwt_secret_key
- FIRST_LOGIN / first_login
- FIRST_PASSWORD / first_password
- FIRST_EMAIL / first_email
- ENVIRONMENT / environment (ex: development)

Exemplo mínimo `.env`:

```
database_hostname=localhost
database_port=5432
database_name=melhorpreco_dev
database_username=admin
database_password=admin
jwt_secret_key=uma_chave_secreta
first_login=admin
first_password=admin
first_email=admin@example.com
environment=development
```

## Como rodar

1) Usando Poetry (recomendado durante desenvolvimento):

```bash
# instalar dependências
poetry install

# rodar localmente
poetry run uvicorn app.main:app --reload
```

2) Usando Docker (container de desenvolvimento com PostgreSQL):

```bash
# sobe apenas o banco de dados
docker compose up -d postgresql

# constrói e roda o container da aplicação
docker build -t melhorpreco-backend .
docker run --env-file .env --network host --name melhorpreco-backend -p 8000:8000 melhorpreco-backend
```

3) Usando `docker-compose` completo (pode adicionar serviço da aplicação ao compose):

```bash
docker compose up -d
```

## Endpoints principais

Nota: muitos endpoints requerem autenticação (Bearer token). Use `/api/v1/token` para obter token.

- POST `/api/v1/token` - login (form data: username, password). Retorna token JWT.

- GET `/users` - lista usuários (depende de implementação; usado para debug)

- Rotas de dados (`/api/v1/data` segundo montagem em `app.main`):
	- GET `/` - listar registros (requires auth)
	- POST `/` - criar novo registro (requires auth)

- Rotas de categorias (ex.: prefix `/api/v1/data` ou outra montagem conforme `app.main`):
	- GET `/` - listar categorias (requires auth)
	- POST `/` - criar categoria (requires auth)

- Rotas de modelo (`/api/v1/modelo` ou similar):
	- POST `/predict_hybrid` - prever preço híbrido (payload com características do dispositivo)
	- POST `/train` - treinar modelo com dados existentes (requires auth)

Verifique os arquivos em `app/routes` para caminhos e detalhes exatos.

## Endpoints detalhados (extraído do código)

Auth
- POST `/api/v1/token` - login
	- Request: form-data (username, password)
	- Response: {"access_token": "<jwt>", "token_type": "bearer"}

Categorias (`app/routes/categories.py`)
- GET `/` - listar categorias
	- Autenticação: Bearer token (dependency `get_current_active_user`)
	- Response: lista de categorias [{id, name, created_at, updated_at}]

- POST `/` - criar categoria
	- Autenticação: Bearer token
	- Request: {"name": "categoria"}
	- Response: categoria criada (Category)

Dados / Registros (`app/routes/data.py`)
- GET `/` - listar registros
	- Autenticação: Bearer token
	- Response: lista de registros (ORM `Registration`)

- POST `/` - criar registro
	- Request body: `Register` Pydantic model (veja `app/schemas/register.py`)
	- Comportamento: valida existência, cria categoria se necessário, insere registro

Modelo / ML (`app/routes/modelo.py`)
- POST `/predict_hybrid` - previsão
	- Request: payload com campos do modelo (veja `Celular` model em `modelo.py`)
	- Response: {"preco_previsto": float, "faixa_preco": str}

- POST `/train` - treina e salva `modelo_precos_regressor.pkl`
	- Autenticação: Bearer token
	- Retorno: {"message": "Modelo treinado com sucesso"}

Observação: os prefixes reais (ex.: `/api/v1/data`) dependem de como os routers são incluídos em `app/main.py`.

## Banco de dados e migrações

Atualmente o projeto cria schemas (auth, data, public) no startup via `app.database.db.startup` e executa `Base.metadata.create_all`.

Para produção recomenda-se migrar para Alembic para versionamento de esquema.

## Segurança

- Hashing de senha: `app/services/security.py` (passlib)
- Tokens JWT: `app/services/jwt.py` (python-jose)

## Observações e próximos passos

- Alguns módulos usam recursos de machine learning (treinamento, joblib). Garanta que os pacotes nativos estejam disponíveis.
- Recomendação: mover datasets e modelos para um diretório `models/` e usar caminhos configuráveis via `.env`.

## Contribuições

Abra um PR com mudanças e adicione testes quando alterar comportamento público da API.
