Lecture 10 builds directly on Lecture 9.

In Lecture 9, Nomad was introduced as a workload orchestrator for services and batch jobs. In Lecture 10, I used the same Nomad service pattern to run Ollama as a long-running backend and then exposed the model through Open WebUI. This shows how Nomad can manage AI workloads the same way it manages other services: by scheduling the job, reserving resources, and connecting services together.
