Lecture 10 submission files for the Nomad + Ollama assignment.

Included evidence:

- `lecture10-ollama-nomad-ui-running.png`
  Cleaner Nomad UI screenshot showing the `ollama` job running and healthy.
- `lecture10-api-tags.png`
  Screenshot of the terminal output from the Ollama `api/tags` endpoint showing `qwen3.5:35b-a3b`.
- `lecture10-open-webui-qwen35-home.png`
  Open WebUI screenshot showing `qwen3.5:35b-a3b` selected in the UI.
- `api-tags-output.json`
  Saved JSON output from the same API call.
- `SHORT_NOTE.md`
  The short note linking Lecture 10 to Lecture 9.
- `JOBSPEC_CHANGES.md`
  Summary of the Mac-specific jobspec changes and the larger model/resource changes.
- `PR_BODY.md`
  Suggested PR title and body.

Relevant changed jobspecs in this repo:

- `/Users/guishuyu/PycharmProjects/datapipeline/airflow_home/dags/data-pipelines-cu-main/lecture10/assignment/ollama.nomad.hcl`
- `/Users/guishuyu/PycharmProjects/datapipeline/airflow_home/dags/data-pipelines-cu-main/lecture10/assignment/open-webui.nomad.hcl`
