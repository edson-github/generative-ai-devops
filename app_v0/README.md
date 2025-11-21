# App v0 - FastAPI + Streamlit (CRUD de Items)

Projeto mínimo para aulas: backend FastAPI com CRUD completo de `Item` persistido em Postgres via SQLAlchemy 2.0 e frontend Streamlit consumindo a API via HTTP.

## Pré-requisitos
- Python 3.11
- Postgres em execução e acessível.
- Criar um arquivo `.env` baseado em `.env.example` na raiz `app_v0/`.

```
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/appdb
API_HOST=127.0.0.1
API_PORT=8000
```

## Instalação

Windows PowerShell:
```
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```
(CMD tradicional: ` .\.venv\Scripts\activate.bat`)

Linux/macOS:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## Subir banco no docker
docker run --name devops-postgres -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=appdb -p 5432:5432 -d postgres:16

## Ativação via Podman

### Opção 1: Apenas o banco de dados com Podman
```bash
podman run --name devops-postgres -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=appdb -p 5432:5432 -d postgres:16
```

### Opção 2: Aplicação completa com Podman (Pod)

#### 1. Criar um Pod
```bash
podman pod create --name devops-app-pod -p 5432:5432 -p 8000:8000 -p 8501:8501
```

#### 2. Subir o banco no Pod
```bash
podman run -d --pod devops-app-pod --name devops-postgres \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=app \
  -e POSTGRES_DB=appdb \
  postgres:16
```

#### 3. Criar imagem da aplicação (se necessário)
Crie um `Dockerfile` na raiz do projeto:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/appdb
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

EXPOSE 8000 8501
```

Construir a imagem:
```bash
podman build -t devops-app:v0 .
```

#### 4. Executar backend no Pod
```bash
podman run -d --pod devops-app-pod --name devops-backend \
  -e DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/appdb \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  devops-app:v0 \
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

#### 5. Executar frontend no Pod
```bash
podman run -d --pod devops-app-pod --name devops-frontend \
  devops-app:v0 \
  streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

### Comandos úteis Podman
```bash
# Listar pods
podman pod ps

# Listar containers no pod
podman ps --pod

# Ver logs
podman logs devops-postgres
podman logs devops-backend
podman logs devops-frontend

# Parar o pod
podman pod stop devops-app-pod

# Iniciar o pod
podman pod start devops-app-pod

# Remover o pod (para todos os containers)
podman pod rm -f devops-app-pod
```

## Executar Backend
```
uvicorn app_v0.backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Executar Frontend
```
streamlit run app_v0/frontend/app.py
```

## Entidade Item
Campos:
- id: UUID
- title: str (obrigatório, não vazio)
- description: str | None
- status: enum (pending, in_progress, done) default pending
- created_at, updated_at: datetimes UTC

## Endpoints
- GET /items?limit=50&offset=0&status=
- GET /items/{id}
- POST /items (201)
- PUT /items/{id}
- DELETE /items/{id} (204)

Paginação: `limit <= 200`.

## Observação
Tabelas são criadas automaticamente no startup apenas para fins didáticos. Em produção usar Alembic.

## Notas
- Sem Docker, sem Alembic neste exemplo.
- Frontend nunca acessa o banco diretamente.
