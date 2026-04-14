PR title:

`Lecture 10: Nomad + Ollama - Shuyu Gui`

Suggested PR body:

```md
## Summary

Completed the Lecture 10 Nomad + Ollama assignment.

## Evidence

- Added submission screenshots in `lecture10/assignment_submission/`
- Verified the Ollama model pull with `api/tags`
- Verified Open WebUI can connect to the Ollama backend
- Included an Open WebUI screenshot with `qwen3.5:35b-a3b` selected

## Short note

Lecture 10 builds on Lecture 9 by using Nomad service orchestration for an AI workload. Ollama is deployed as a long-running backend service, and Open WebUI is connected to it as another service managed through Nomad.

## Jobspec changes

- Changed the model from `tinyllama` to `qwen3.5:35b-a3b`
- Increased CPU and memory for the larger model
- Switched the poststart task from `exec` to `raw_exec` on this macOS client
- Added persistent Docker volumes for Ollama models and Open WebUI data
```
