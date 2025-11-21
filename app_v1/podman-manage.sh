#!/bin/bash
# Script para gerenciar o ambiente app_v1 com Podman Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    up)
        echo "🚀 Iniciando serviços com Podman Compose..."
        python3 -m podman_compose up -d
        echo "✅ Serviços iniciados!"
        echo ""
        echo "Aguardando serviços ficarem prontos..."
        sleep 10
        python3 -m podman_compose ps
        ;;
    
    down)
        echo "🛑 Parando serviços..."
        python3 -m podman_compose down
        echo "✅ Serviços parados!"
        ;;
    
    restart)
        echo "🔄 Reiniciando serviços..."
        python3 -m podman_compose restart
        echo "✅ Serviços reiniciados!"
        ;;
    
    build)
        echo "🔨 Construindo imagens..."
        python3 -m podman_compose build
        echo "✅ Imagens construídas!"
        ;;
    
    rebuild)
        echo "🔨 Reconstruindo e reiniciando serviços..."
        python3 -m podman_compose down
        python3 -m podman_compose build --no-cache
        python3 -m podman_compose up -d
        echo "✅ Serviços reconstruídos e iniciados!"
        ;;
    
    logs)
        if [ -z "$2" ]; then
            python3 -m podman_compose logs -f
        else
            python3 -m podman_compose logs -f "$2"
        fi
        ;;
    
    ps|status)
        echo "📊 Status dos containers:"
        python3 -m podman_compose ps
        echo ""
        podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ;;
    
    test)
        echo "🧪 Executando smoke tests..."
        cd tests
        python3 smoke_test.py
        ;;
    
    clean)
        echo "🧹 Limpando containers, volumes e imagens..."
        python3 -m podman_compose down -v
        podman system prune -f
        echo "✅ Ambiente limpo!"
        ;;
    
    shell)
        if [ -z "$2" ]; then
            echo "❌ Especifique o serviço: backend, frontend, db, ou prometheus"
            exit 1
        fi
        python3 -m podman_compose exec "$2" /bin/bash
        ;;
    
    *)
        echo "🐳 Gerenciador do ambiente app_v1 com Podman"
        echo ""
        echo "Uso: $0 {comando} [opções]"
        echo ""
        echo "Comandos disponíveis:"
        echo "  up          - Inicia todos os serviços"
        echo "  down        - Para todos os serviços"
        echo "  restart     - Reinicia todos os serviços"
        echo "  build       - Constrói as imagens"
        echo "  rebuild     - Reconstrói tudo do zero e inicia"
        echo "  logs [svc]  - Mostra logs (opcionalmente de um serviço específico)"
        echo "  ps|status   - Mostra status dos containers"
        echo "  test        - Executa smoke tests"
        echo "  clean       - Remove containers, volumes e limpa o sistema"
        echo "  shell {svc} - Abre shell em um container (backend, frontend, db, prometheus)"
        echo ""
        echo "Exemplos:"
        echo "  $0 up                    # Inicia todos os serviços"
        echo "  $0 logs backend          # Mostra logs do backend"
        echo "  $0 shell backend         # Abre shell no container do backend"
        echo "  $0 test                  # Executa smoke tests"
        exit 1
        ;;
esac
