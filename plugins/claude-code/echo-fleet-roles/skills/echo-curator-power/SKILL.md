---
name: echo-curator-power
description: Consolidate ECHO knowledge, memory, provenance, and retrieval quality without losing source truth. Use for Claude auto or Codex cauto curator sessions, knowledge ingestion, deduplication, taxonomy, or memory lifecycle work.
---

# ECHO Curator Power

Transform scattered evidence into current, retrievable, provenance-rich knowledge while preserving originals and uncertainty.

## Required composition

Load `$echo-ragops`, `$memory-orchestration`, `$contextual-memory-bridge`, and `$consolidate-memory`.

## Curation loop

1. Define the corpus, audience, retrieval task, retention boundary, and protected-data exclusions.
2. Inventory sources and existing records. Preserve canonical artifacts; never treat derived summaries as replacements for source evidence.
3. Normalize metadata, provenance, dates, entities, access labels, hashes, and stable identifiers.
4. De-duplicate by identity and meaning while retaining version history, conflicts, supersession, and source lineage.
5. Chunk and index for the real retrieval task; protect tables, code, citations, and semantic boundaries from destructive splitting.
6. Run representative retrieval evaluations for precision, recall, freshness, provenance, and restricted-data exclusion.
7. Publish the manifest, ingest durable knowledge, record superseded items, checkpoint SOL, and continue with the next bounded corpus.

## Capability contract

Use base knowledge and memory scopes plus `echo.knowledge.*`, `echo.library.*`, `echo.memory-spine.*`, `echo.memoryconsolidationnode.*`, `echo.fs.*`, and `echo.caps.*` through the scoped broker. Inspect current schemas and retention policy before writes.

## Proof gate

Counts alone are insufficient. Completion requires source-to-record traceability, duplicate and conflict handling, retrieval evaluation, restricted-data checks, and a recoverable manifest.
