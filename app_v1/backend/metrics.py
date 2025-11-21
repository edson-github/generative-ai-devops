import time
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

# Métricas globais
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total de requisições HTTP",
    ["method", "path", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ["method", "path"]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Requisições HTTP em andamento",
    ["method", "path"]
)

HTTP_EXCEPTIONS_TOTAL = Counter(
    "http_exceptions_total",
    "Total de exceções não tratadas",
    ["method", "path", "exception_type"]
)

def setup_metrics(app: FastAPI) -> None:
    """
    Configura middleware de métricas e monta o endpoint /metrics.
    """
    
    # Monta o app do Prometheus em /metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        method = request.method
        # CUIDADO: path pode ter alta cardinalidade se houver IDs dinâmicos não tratados.
        # Em produção, idealmente usaríamos request.route.path se disponível ou normalização.
        path = request.url.path
        
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(process_time)
            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=response.status_code).inc()
            
            return response
        except Exception as e:
            # Em caso de exceção não tratada pelo app (500)
            process_time = time.perf_counter() - start_time
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(process_time)
            HTTP_EXCEPTIONS_TOTAL.labels(method=method, path=path, exception_type=type(e).__name__).inc()
            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=500).inc()
            raise e
        finally:
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()
