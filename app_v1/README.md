# App v1 - FastAPI + Streamlit (CRUD de Items)

Aplicação didática com backend FastAPI (SQLAlchemy 2.0 + Postgres) e frontend Streamlit consumindo a API por HTTP.

Portas padrão:
- Backend: 8000
- Frontend: 8501
- Postgres: 5432
- Prometheus: 9090
- PostgreSQL Exporter: 9187
- Grafana: 3000
- OpenSearch: 9200
- OpenSearch Dashboards: 5601

## Rodando com Podman Compose

Arquivos de containerização:
- `backend/Dockerfile`: imagem do backend (FastAPI + Uvicorn)
- `frontend/Dockerfile`: imagem do frontend (Streamlit)
- `docker-compose.yml`: orquestra backend, frontend e Postgres (compatível com Podman)
- `.dockerignore`: ignora artefatos locais ao buildar

Compose cria um volume nomeado `pgdata` para o banco e usa bind mounts (`./:/app`) para hot-reload em desenvolvimento (backend e frontend).

### Pré-requisitos

1. **Podman** e **podman-compose** instalados:
   ```bash
   # macOS (via Homebrew)
   brew install podman
   pip3 install podman-compose
   
   # Linux
   sudo apt install podman  # Debian/Ubuntu
   pip3 install podman-compose
   ```

2. Arquivo `.env` na raiz `app_v1/` (opcional, valores padrão já estão no docker-compose.yml).

### Passo a passo

1. **(Opcional)** Crie o arquivo `.env` na pasta `app_v1`:
```env
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=appdb
DATABASE_URL=postgresql+psycopg://app:app@db:5432/appdb
API_HOST=backend
API_PORT=8000
```

2. Use o script auxiliar para gerenciar o ambiente:
```bash
# Iniciar todos os serviços
./podman-manage.sh up

# Verificar status
./podman-manage.sh status

# Ver logs
./podman-manage.sh logs

# Executar smoke tests
./podman-manage.sh test

# Parar serviços
./podman-manage.sh down
```

3. Ou use diretamente o podman-compose:
```bash
# Construir imagens
python3 -m podman_compose build

# Subir aplicação
python3 -m podman_compose up -d

# Verificar status
python3 -m podman_compose ps
podman ps
```

4. Acesse:
- Frontend: http://localhost:8501
- Backend Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090

5. Logs:
```bash
python3 -m podman_compose logs -f
# ou logs de um serviço específico:
python3 -m podman_compose logs -f backend
```

6. Parar:
```bash
python3 -m podman_compose down
```

### Script auxiliar `podman-manage.sh`

O script fornece comandos simplificados para gerenciar o ambiente:

| Comando | Descrição |
|---------|-----------|
| `up` | Inicia todos os serviços |
| `down` | Para todos os serviços |
| `restart` | Reinicia todos os serviços |
| `build` | Constrói as imagens |
| `rebuild` | Reconstrói tudo do zero e inicia |
| `logs [svc]` | Mostra logs (opcionalmente de um serviço específico) |
| `ps` ou `status` | Mostra status dos containers |
| `test` | Executa smoke tests |
| `clean` | Remove containers, volumes e limpa o sistema |
| `shell {svc}` | Abre shell em um container |

Exemplos:
```bash
./podman-manage.sh up                # Inicia todos os serviços
./podman-manage.sh logs backend      # Mostra logs do backend
./podman-manage.sh shell backend     # Abre shell no container do backend
./podman-manage.sh test              # Executa smoke tests
./podman-manage.sh clean             # Limpa tudo
```

## Variáveis de ambiente

- Backend lê `DATABASE_URL` (definida no docker-compose ou .env).
- Frontend usa `API_HOST` e `API_PORT` para encontrar o backend.

## Observações
- Criação de tabelas automática no startup do backend.
- Dockerfiles usam `python:3.11-slim` e usuário não-root para segurança.
- Hot-reload ativado via volumes.

## Entidade e Endpoints (resumo)
- Item: `id` (UUID), `title`, `description?`, `status` (`pending|in_progress|done`), `created_at`, `updated_at`.
- Endpoints: `GET /items`, `GET /items/{id}`, `POST /items` (201), `PUT /items/{id}`, `DELETE /items/{id}` (204).

## Entidade e Endpoints (resumo)
- Item: `id` (UUID), `title`, `description?`, `status` (`pending|in_progress|done`), `created_at`, `updated_at`.
- Endpoints: `GET /items`, `GET /items/{id}`, `POST /items` (201), `PUT /items/{id}`, `DELETE /items/{id}` (204).

## Monitoramento com Prometheus

A aplicação foi instrumentada para expor métricas no formato Prometheus.

### Métricas disponíveis
- `http_requests_total`: Total de requisições HTTP (labels: method, path, status_code)
- `http_request_duration_seconds`: Histograma da duração das requisições (labels: method, path)
- `http_requests_in_progress`: Gauge de requisições em andamento (labels: method, path)
- `http_exceptions_total`: Total de exceções não tratadas (labels: method, path, exception_type)

### Acesso
- Endpoint de métricas do backend: `http://localhost:8000/metrics`
- Prometheus UI: `http://localhost:9090`

## Monitoramento do Banco de Dados

A aplicação inclui o **PostgreSQL Exporter** para expor métricas detalhadas do banco de dados.

### Serviço PostgreSQL Exporter
- Imagem: `prometheuscommunity/postgres-exporter:latest`
- Porta: `9187`
- Endpoint: `http://localhost:9187/metrics`
- Conexão: Usa credenciais do banco (user: `app`, db: `appdb`)

### Métricas do PostgreSQL disponíveis
- `pg_up`: Status do banco (1 = up, 0 = down)
- `pg_stat_database_*`: Estatísticas por database
  - `pg_stat_database_xact_commit`: Transações commitadas
  - `pg_stat_database_xact_rollback`: Transações revertidas
  - `pg_stat_database_tup_inserted`: Tuplas inseridas
  - `pg_stat_database_tup_updated`: Tuplas atualizadas
  - `pg_stat_database_tup_deleted`: Tuplas deletadas
  - `pg_stat_database_tup_fetched`: Tuplas buscadas
- `pg_database_size_bytes`: Tamanho do banco em bytes
- `pg_stat_user_tables_*`: Estatísticas por tabela
- `pg_locks_*`: Informações sobre locks

### Queries úteis no Prometheus

**Status do banco:**
```promql
pg_up
```

**Tamanho do banco appdb:**
```promql
pg_database_size_bytes{datname="appdb"}
```

**Taxa de commits por segundo:**
```promql
rate(pg_stat_database_xact_commit{datname="appdb"}[1m])
```

**Taxa de inserções por segundo:**
```promql
rate(pg_stat_database_tup_inserted{datname="appdb"}[1m])
```

**Total de conexões ativas:**
```promql
pg_stat_database_numbackends{datname="appdb"}
```

### Validação
1. Acesse `http://localhost:9187/metrics` para ver métricas brutas
2. No Prometheus (`http://localhost:9090/targets`), verifique que `postgres-exporter` está UP
3. Execute queries no Prometheus Graph para visualizar métricas

### Boas práticas de segurança
- Em produção, crie um usuário dedicado com privilégios mínimos (ex.: `metrics`)
- Use variáveis de ambiente ou secrets para credenciais
- Não exponha a porta 9187 externamente em produção
- Configure ACLs/firewall para restringir acesso ao exporter

## Visualização com Grafana

A aplicação inclui **Grafana** para visualização avançada das métricas coletadas pelo Prometheus.

### Serviço Grafana
- Imagem: `grafana/grafana:latest`
- Porta: `3000`
- URL: `http://localhost:3000`
- Credenciais padrão: `admin` / `admin`

### Datasource Provisionado
O Grafana é configurado automaticamente com:
- **Datasource**: Prometheus (`http://prometheus:9090`)
- **Provisionamento automático**: Via arquivos em `grafana/provisioning/`

### Dashboards Disponíveis

#### 1. FastAPI Application Dashboard
Monitora métricas da aplicação backend:
- **Requisições HTTP**: Total, taxa, duração
- **Status codes**: Distribuição de respostas (200, 404, 500, etc)
- **Latência**: p50, p95, p99
- **Requisições em progresso**: Gauge de requisições concorrentes
- **Exceções**: Total de erros por tipo

**Queries principais:**
- `rate(http_requests_total[1m])` - Taxa de requisições
- `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` - Latência p95
- `http_requests_in_progress` - Requisições ativas

#### 2. PostgreSQL General Dashboard
Monitora métricas detalhadas do banco de dados:
- **Status**: pg_up, conexões ativas
- **Tamanho do banco**: Crescimento ao longo do tempo
- **Transações**: Commits, rollbacks, taxa de commits/s
- **Operações de tuplas**: Inserções, atualizações, deleções
- **Performance**: Cache hit ratio, blocos lidos
- **Locks**: Locks ativos por tipo

**Queries principais:**
- `pg_database_size_bytes{datname="appdb"}` - Tamanho do banco
- `rate(pg_stat_database_xact_commit[1m])` - Taxa de commits
- `rate(pg_stat_database_tup_inserted[1m])` - Taxa de inserções

#### 3. K6 Load Testing Dashboard
Visualiza resultados de testes de carga:
- **Virtual Users (VUs)**: Usuários simulados
- **Request Rate**: Requisições por segundo
- **Response Time**: Latências (min, max, avg, p95, p99)
- **HTTP Duration**: Breakdown das fases da requisição
- **Checks**: Validações passando/falhando
- **Data Transfer**: Bytes enviados/recebidos

### Acesso e Uso

1. **Login inicial:**
   - Acesse `http://localhost:3000`
   - Use: `admin` / `admin`
   - (Opcional) Altere a senha no primeiro acesso

2. **Navegar dashboards:**
   - Menu lateral → Dashboards
   - Dashboards provisionados aparecem automaticamente

3. **Criar dashboards customizados:**
   - Explore → Prometheus
   - Crie queries e salve painéis

### Provisionamento

A estrutura de provisionamento garante que datasources e dashboards sejam automaticamente configurados:

```
grafana/provisioning/
├── datasources/
│   └── datasource.yml          # Prometheus datasource
└── dashboards/
    ├── dashboards.yml          # Configuração de provisionamento
    └── json/
        ├── app_fastapi_dashboard.json
        ├── postgres_general_dashboard.json
        └── k6_stress_complete.json
```

### Persistência

Para persistir dashboards customizados entre reinícios, adicione um volume no `docker-compose.yml`:

```yaml
volumes:
  - grafana-data:/var/lib/grafana
```

### Boas práticas de segurança
- ⚠️ **Produção**: Altere as credenciais padrão!
- Use `GF_SECURITY_ADMIN_PASSWORD` via secret/variável de ambiente
- Configure autenticação externa (OAuth, LDAP)
- Habilite HTTPS com certificados válidos
- Restrinja acesso por rede/firewall

### Alertas (Opcional)

Grafana pode enviar alertas baseados em queries:
1. Edite um painel
2. Aba "Alert" → Criar regra
3. Configure condições e notificações
4. Integre com Slack, email, PagerDuty, etc.

## Testes de Carga com k6
Esta aplicação inclui dois scripts de teste de carga usando k6, integrados ao Docker Compose via profile `k6`.

### Objetivos
1. Validar disponibilidade e latência básica (`test_basico.js`).
2. Exercitar o ciclo CRUD completo (`test_crud.js`).
3. Exportar métricas para Prometheus (remote write) e visualizar no Grafana.

### Serviços necessários
`db`, `backend`, `prometheus` (Grafana opcional para visualização). Compose resolve dependências.

### Como executar

**Com Podman Compose:**
```bash
# Subir stack (se necessário)
python3 -m podman_compose -f docker-compose.yml up -d

# Teste básico (test_basico.js)
python3 -m podman_compose -f docker-compose.yml --profile k6 run --rm k6

# Teste CRUD (test_crud.js)
python3 -m podman_compose -f docker-compose.yml --profile k6 run --rm k6 run /scripts/test_crud.js

# Usando o script auxiliar
./podman-manage.sh up  # Subir stack
```

**Com Docker Compose:**
```bash
# Subir stack (se necessário)
docker compose up -d

# Teste básico
docker compose --profile k6 run --rm k6

# Teste CRUD
docker compose --profile k6 run --rm k6 run /scripts/test_crud.js
```

### Scripts
1. `k6/test_basico.js`
   - GET /items
   - Stages: 10s→5 VUs, 30s estável, 10s descendo
   - Thresholds: p95 < 500ms, erros < 1%
2. `k6/test_crud.js`
   - Fluxo: create → get → update → delete + list
   - Cenários:
     - smoke (ramping-vus 0→3→0)
     - crud_load (constant-vus: 5 VUs / 30s)
   - Thresholds: erros <2%, p95 <700ms
   - Trend custom: `custom_create_duration`

### Conceitos
| Conceito | Explicação |
|----------|-----------|
| VU | Usuário virtual concorrente |
| Stage | Período com alvo de VUs |
| Scenario | Padrão de carga isolado |
| Threshold | Regra de aprovação/falha |
| Iteration | Uma execução da função de teste |
| Trend | Métrica custom com distribuição |

### Variáveis de ambiente (serviço k6)
| Variável | Função | Default |
|----------|--------|---------|
| API_BASE | Base da API | http://backend:8000 |
| K6_OUT | Output/export | experimental-prometheus-rw |
| K6_PROMETHEUS_RW_SERVER_URL | Remote write endpoint | http://prometheus:9090/api/v1/write |
| K6_PROMETHEUS_RW_TREND_STATS | Estatísticas de Trend | p(95),p(99),avg,med,min,max |

Prometheus inicia com `--web.enable-remote-write-receiver` para expor `/api/v1/write`.

### Métricas k6 no Prometheus
| Métrica | Descrição |
|---------|-----------|
| http_reqs | Total de requisições |
| http_req_duration | Latência (s) |
| http_req_failed | Proporção de falhas |
| vus / vus_max | VUs atuais / máximo |
| iterations | Iterações completas |
| data_sent / data_received | Tráfego |
| checks | Resultados de check() |
| custom_create_duration | Tempo de criação (Trend) |

### Queries exemplo
| Objetivo | Query |
|----------|-------|
| RPS | rate(http_reqs[1m]) |
| Latência p95 | histogram_quantile(0.95, sum(rate(http_req_duration_bucket[5m])) by (le)) |
| Erro (%) | rate(http_req_failed[5m]) |
| VUs | avg(vus) |
| Iterações/s | rate(iterations[1m]) |

### Customizações rápidas
1. Aumentar carga:
```javascript
export const options = { stages: [
  { duration: '30s', target: 20 },
  { duration: '2m', target: 20 },
  { duration: '30s', target: 0 },
] }
```
2. Header de auth:
```javascript
const params = { headers: { Authorization: `Bearer ${__ENV.TOKEN}` } }
```
Execução: `TOKEN=seu_token docker compose --profile k6 run --rm k6`
3. Exportar resumo JSON:
```powershell
docker compose --profile k6 run --rm k6 run --summary-export=/scripts/saida.json /scripts/test_crud.js
```

### Exemplo novo script (`k6/stress_ramp.js`)
```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 30 },
    { duration: '3m', target: 30 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'],
    http_req_failed: ['rate<0.01']
  }
};

const API = __ENV.API_BASE || 'http://backend:8000';
export default function () {
  http.get(`${API}/items?limit=5`);
  sleep(0.5);
}
```
Execução:
```powershell
docker compose --profile k6 run --rm k6 run /scripts/stress_ramp.js
```

### Interpretação rápida
- checks_total / checks_failed: validações lógicas
- http_req_duration: comparar média vs p95
- http_req_failed: se > threshold => exit code ≠ 0
- iteration_duration: inclui sleeps + requisições

### Boas práticas
- Escale gradualmente.
- Use tags por operação.
- Thresholds = SLOs automatizados.
- Diferencie smoke, load, stress, spike.
- Correlacione com métricas de backend e DB.

---

## 6. Logs Estruturados com OpenSearch

### Arquitetura de Logging

A aplicação implementa logging estruturado em formato JSON com os seguintes componentes:

1. **JSON Formatter** (`backend/logging_conf.py`):
   - Serializa logs em formato JSON
   - Inclui timestamp, level, logger e message
   - Formato legível e fácil de parsear

2. **OpenSearch Handler** (`backend/logging_conf.py`):
   - Envia logs automaticamente para OpenSearch
   - Índice: `logs-app-v1`
   - Buffer de 50 logs ou flush a cada 1 segundo
   - Conexão: `http://opensearch:9200`

3. **Middleware de Correlação** (`backend/middleware.py`):
   - Gera `request_id` único por requisição (UUID4)
   - Injeta `request_id` em todos os logs da requisição
   - Log de acesso com metadados completos:
     * method, path, status_code
     * duration_ms (tempo de processamento)
     * client_ip, user_agent
     * request_id para correlação

### Estrutura dos Logs

**Log de Acesso (HTTP):**
```json
{
  "message": "HTTP access",
  "request_id": "7df1ad5d-8765-4c90-ae91-06d246792fa4",
  "method": "GET",
  "path": "/items/",
  "status_code": 200,
  "duration_ms": 4,
  "client_ip": "10.89.0.8",
  "user_agent": "Prometheus/3.7.3",
  "timestamp": "2025-11-23T18:27:07.385724+00:00",
  "level": "INFO",
  "logger": "uvicorn.access"
}
```

**Log da Aplicação:**
```json
{
  "message": "Item created successfully",
  "item_id": 123,
  "timestamp": "2025-11-23T18:27:07.385724+00:00",
  "level": "INFO",
  "logger": "app.repository"
}
```

### Consultando Logs

#### Via API do OpenSearch

1. **Verificar índices:**
```bash
curl "http://localhost:9200/_cat/indices?v"
```

2. **Buscar logs recentes:**
```bash
curl "http://localhost:9200/logs-app-v1/_search?size=10&sort=timestamp:desc&pretty"
```

3. **Buscar por request_id (correlação):**
```bash
curl "http://localhost:9200/logs-app-v1/_search?q=request_id:7df1ad5d-8765-4c90-ae91-06d246792fa4&pretty"
```

4. **Buscar logs de erro:**
```bash
curl "http://localhost:9200/logs-app-v1/_search?q=level:ERROR&pretty"
```

5. **Buscar logs de endpoint específico:**
```bash
curl "http://localhost:9200/logs-app-v1/_search?q=path:/items/&pretty"
```

#### Via OpenSearch Dashboards

Acesse: http://localhost:5601

**Configurar Index Pattern:**
1. Acesse "Stack Management" > "Index Patterns"
2. Criar pattern: `logs-app-v1`
3. Selecionar time field: `timestamp`

**Visualizar Logs:**
1. Acesse "Discover"
2. Selecione o index pattern `logs-app-v1`
3. Filtre por campos: `level`, `request_id`, `path`, etc.

**Queries úteis:**
- Logs de erro: `level: ERROR`
- Por método HTTP: `method: POST`
- Por status code: `status_code: 500`
- Tempo > 100ms: `duration_ms: >100`

### Benefícios da Correlação

Com o `request_id`, você pode:
1. **Rastrear requisições completas** através de múltiplos logs
2. **Debugar problemas** seguindo o fluxo de uma requisição específica
3. **Medir performance** fim-a-fim de uma transação
4. **Correlacionar** logs entre diferentes serviços

**Exemplo de correlação:**
```bash
# 1. Pegar request_id de um log de erro
curl "http://localhost:9200/logs-app-v1/_search?q=level:ERROR&size=1" | grep request_id

# 2. Buscar todos os logs daquela requisição
curl "http://localhost:9200/logs-app-v1/_search?q=request_id:abc-123&sort=timestamp:asc&pretty"
```

### Monitoramento de Logs

**Métricas importantes:**
- Taxa de erros: `count(level:ERROR) / count(*)`
- Latência p95: `percentile(duration_ms, 95)`
- Endpoints mais lentos: `avg(duration_ms) group by path`
- Erros por endpoint: `count(status_code:5*) group by path`

### Configuração Avançada

**Ajustar nível de log:**
```python
# backend/logging_conf.py
logging.basicConfig(level=logging.DEBUG)  # Mais verboso
```

**Filtrar logs sensíveis:**
```python
# backend/middleware.py
# Não logar tokens/senhas
if 'Authorization' in request.headers:
    del request.headers['Authorization']
```

**Ajustar buffer do OpenSearch:**
```python
# backend/logging_conf.py
opensearch_handler = OpenSearchHandler(
    hosts=[{'host': 'opensearch', 'port': 9200}],
    buffer_size=100,  # Aumentar buffer
    flush_frequency_in_sec=5,  # Flush menos frequente
)
```

### Troubleshooting

**Logs não aparecem no OpenSearch:**
1. Verificar conectividade: `curl http://localhost:9200`
2. Verificar backend logs: `podman logs app_v1_backend_1`
3. Verificar índice: `curl "http://localhost:9200/_cat/indices?v"`

**OpenSearch Dashboards não carrega:**
1. Verificar status: `curl http://localhost:5601/api/status`
2. Aguardar inicialização completa (~30s)
3. Verificar logs: `podman logs app_v1_opensearch-dashboards_1`

**Performance degradada:**
1. Reduzir verbosidade dos logs (level=INFO ou WARNING)
2. Aumentar buffer do OpenSearchHandler
3. Desabilitar logs de acesso para healthchecks:
```python
if request.url.path not in ["/health", "/metrics"]:
    logger.info("HTTP access", extra={...})
```