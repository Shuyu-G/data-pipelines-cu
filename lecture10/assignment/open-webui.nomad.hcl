# Lecture 10 — Open WebUI → Ollama (simplified; no S3 / nomadVar)
# Run AFTER job "ollama" is healthy. On this macOS setup, the task uses raw_exec to
# launch Docker so it can discover the Ollama container's bridge IP and reach it reliably.

job "open-webui" {
  type = "service"

  group "web" {
    count = 1

    network {
      port "ui" {
        to     = 8080
        static = 3000
      }
    }

    task "open-webui-task" {
      driver = "raw_exec"

      service {
        name     = "open-webui-svc"
        port     = "ui"
        provider = "nomad"

        check {
          type     = "http"
          path     = "/"
          interval = "20s"
          timeout  = "5s"
        }
      }

      config {
        command = "/bin/sh"
        args = [
          "-c",
          <<-SCRIPT
            set -e

            OLLAMA_CONTAINER=$(docker ps --format '{{.Names}}' | awk '/^ollama-task-/{print; exit}')
            if [ -z "$OLLAMA_CONTAINER" ]; then
              echo "Could not find a running ollama-task container"
              exit 1
            fi

            OLLAMA_IP=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$OLLAMA_CONTAINER")
            if [ -z "$OLLAMA_IP" ]; then
              echo "Could not determine Ollama container IP"
              exit 1
            fi

            WEBUI_CONTAINER="open-webui-${NOMAD_ALLOC_ID}"
            echo "Starting Open WebUI against Ollama at http://$OLLAMA_IP:11434"

            exec docker run --rm \
              --name "$WEBUI_CONTAINER" \
              -p 3000:8080 \
              -v open-webui-data:/app/backend/data \
              -e OLLAMA_BASE_URL="http://$OLLAMA_IP:11434" \
              -e WEBUI_SECRET_KEY="lecture10-dev-change-me" \
              -e ENABLE_SIGNUP="True" \
              ghcr.io/open-webui/open-webui:main
          SCRIPT
        ]
      }

      # Raw exec just supervises the foreground docker run process.
      resources {
        cpu    = 500
        memory = 1024
      }
    }
  }
}
