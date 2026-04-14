# Lecture 10 — Ollama on Nomad (simplified from HashiCorp AI workloads tutorial)
# - ollama-task: Docker ollama/ollama + Nomad service ollama-backend
# - pull-model: poststart task curls /api/pull (qwen3.5:35b-a3b by default for this machine)

job "ollama" {
  type = "service"

  group "ollama" {
    count = 1

    network {
      port "ollama" {
        to     = 11434
        static = 11434
      }
    }

    task "ollama-task" {
      driver = "docker"

      service {
        name     = "ollama-backend"
        port     = "ollama"
        provider = "nomad"
      }

      config {
        image = "ollama/ollama:latest"
        ports = ["ollama"]
        mount {
          type     = "volume"
          source   = "ollama-models"
          target   = "/root/.ollama"
          readonly = false
        }
      }

      # Tuned for a 64 GiB laptop running qwen3.5:35b-a3b via Ollama.
      resources {
        cpu    = 8000
        memory = 40960
      }
    }

    task "pull-model" {
      driver = "raw_exec"

      lifecycle {
        hook    = "poststart"
        sidecar = false
      }

      resources {
        cpu    = 500
        memory = 1024
      }

      template {
        data = <<EOH
{{ range nomadService "ollama-backend" }}
OLLAMA_BASE_URL=http://[{{ .Address }}]:{{ .Port }}
{{ end }}
EOH
        destination = "secrets/env.env"
        env         = true
      }

      config {
        command = "/bin/sh"
        args = [
          "-c",
          <<-SCRIPT
            set -e
            echo "Waiting for Ollama at $OLLAMA_BASE_URL ..."
            i=0
            while [ "$i" -lt 60 ]; do
              if curl -sf "$OLLAMA_BASE_URL/api/tags" >/dev/null 2>&1; then
                break
              fi
              sleep 2
              i=$((i + 1))
            done
            echo "Pulling model qwen3.5:35b-a3b ..."
            curl -sS -X POST "$OLLAMA_BASE_URL/api/pull" -d '{"name":"qwen3.5:35b-a3b"}'
            echo "Done."
          SCRIPT
        ]
      }
    }
  }
}
