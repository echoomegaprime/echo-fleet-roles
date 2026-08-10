"""Build a deterministic connector manifest; sign only when a key is supplied."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from security import signature


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="registry/manifest.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    payload = {
        "version": "1.0.0",
        "connectors": json.loads((root / "registry/connectors/core.json").read_text(encoding="utf-8")),
        "providers": json.loads((root / "registry/providers.json").read_text(encoding="utf-8")),
        "protocols": json.loads((root / "registry/protocols.json").read_text(encoding="utf-8")),
        "roles": json.loads((root / "registry/roles.json").read_text(encoding="utf-8")),
        "catalog": json.loads((root / "registry/catalog.json").read_text(encoding="utf-8")),
    }
    secret = os.environ.get("ECHO_CONNECTOR_MANIFEST_HMAC")
    if secret:
        payload["signature"] = signature(payload, secret)
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "signed": bool(secret), "secret_value_emitted": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
