# README history

Surface: [README](../../README.md) · [History index](../README.md)

## 2026-10-15 — Explain research provenance and regeneration limits

A developer opening this repository could mistake the historical 85.71% matching figure for an automatic, reproducible benchmark. The README now identifies the saved 84/98 result as manually assisted, explains the fixed three-match adjustment, and maps active scripts, manual spreadsheet work and missing raw inputs before the original research notes.

The source review distinguishes the ten-item active enrichment loop from inactive demonstration strings and explains that the reference-dataset builder does not fine-tune a model. The original matching code, data, generated artifacts and historical timings are retained; metric statements are qualified in the README.

Evidence scope: SSPM_HANDOFF_CLAIM_SOURCE_PARITY compares original documentation and source at 94468b8f70058e5d8b8c017da15749663bc73114 with this documentation change, checks local source links, and verifies unchanged non-documentation Git blobs and modes. This records a source-backed handoff, not an accuracy or speed improvement.

Limits: no installation, repository script import/run, provider call, data regeneration, benchmark, rendered UI check or deployment. Current reproducibility, SDK/model compatibility and accuracy remain unverified.
