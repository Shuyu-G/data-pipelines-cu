Jobspec changes used for this Mac-based submission:

1. `assignment/ollama.nomad.hcl`
   - Changed the pulled model from `tinyllama` to `qwen3.5:35b-a3b`.
   - Increased resources for the larger model:
     - `ollama-task`: `cpu = 8000`, `memory = 40960`
     - `pull-model`: `cpu = 500`, `memory = 1024`
   - Replaced `exec` with `raw_exec` for the `pull-model` task because `exec` is unsupported on this macOS Nomad client.
   - Wrapped the Nomad service IPv6 address in `[]` when generating `OLLAMA_BASE_URL`.
   - Added a Docker named volume mount:
     - `ollama-models:/root/.ollama`
     This keeps the downloaded model files after stopping the job.

2. `assignment/open-webui.nomad.hcl`
   - Replaced the original direct container approach with a `raw_exec` wrapper that starts Docker after discovering the running Ollama container IP.
   - Added a Docker named volume mount:
     - `open-webui-data:/app/backend/data`
     This preserves the Open WebUI account, chat history, and local app data.
