# Diagnostic matrix

| Symptom | First evidence | Safe next probe |
|---|---|---|
| Connector not found | registry and role binding | gateway `list`, then `retrieve` |
| SDK 4xx/422 | capability schema and serialized options | plan-mode invocation with minimal fields |
| SDK timeout | gateway health, broker duration, service health | bounded read-only health call |
| Chat ignores tools | provider capability, MCP/A2A tool visibility | explicit retrieve request in agent/tool mode |
| CLI hangs | process tree, stdin/stdout contract | JSONL health request with timeout |
| Service 5xx | staging logs and request id | real HTTP smoke with empty/malformed inputs |
| Shader artifact | compiler output and fixed-camera capture | fallback shader plus target-GPU frame capture |
| Performance regression | baseline GPU/CPU/memory telemetry | compare one feature at a time against budget |
