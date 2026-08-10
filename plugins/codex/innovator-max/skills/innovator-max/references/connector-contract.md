# Role connector contract

The runtime uses three small documents:

```json
{
  "role": "innovator",
  "intent": "find reusable implementation patterns",
  "constraints": {"read_only": true, "sensitivity": "internal"},
  "required_evidence": ["source", "freshness"]
}
```

Connector records provide `id`, `capability`, `description`, `verbs`, `input_schema`, `roles`, `sensitivity`, `health`, and `broker`. Retrieval ranks exact capability/role matches above keyword matches and rejects connectors that violate sensitivity or read-only constraints.

Invocation is always an explicit second step. The broker receives only the selected capability, verb, options, and a redacted request id. Secrets remain in the broker environment. Results are treated as untrusted evidence and must be verified before mutation or completion.

Add a connector by registering a JSON record and an acceptance probe. Do not create a bespoke role-specific HTTP client when the SDK broker can carry the call.
