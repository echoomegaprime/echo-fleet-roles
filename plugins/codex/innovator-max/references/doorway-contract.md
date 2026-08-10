# Doorway contract

The doorway is not another role prompt or knowledge library. It is the instruction-resolution layer shared by every role and transport. A client asks for a manifest, reads the applicable files locally or through its trusted filesystem connector, and then invokes the role-aware capability plane.

Keep the doorway T1-small: burn-in doctrine, hard limits, the retrieval bootstrap, and enrichment rules. Put deep material in T3/T4 pointers and fetch it on demand from the live system. A frozen summary is never evidence of current state.

The manifest contains only paths, sizes, hashes, and load-order metadata. This prevents accidental leakage of doctrine, secrets, or personal data into telemetry while still allowing reproducible instruction provenance.

Before trusting a result, verify the instrument that produced it: endpoint health, source freshness, schema, and real boundary behavior. A healthy status response alone is not proof that the underlying service works.
