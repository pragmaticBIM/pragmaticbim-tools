# Agent instructions

Standing instructions for every coding agent working on this repo. Read `CONTRIBUTING.md` first.

## What this repo is

A neutral registry of software tools that help carry out the use cases of the pragmaticBIM Reference: one YAML file per tool in `tools/`, validated against the LinkML schema in `schema/`.

## How to check your work

```
linkml-validate -s schema/tool.yaml -C Tool tools/*.yaml
```

Run it until it passes. CI (`validate` workflow) also runs `scripts/check_codes.py` (ids, use case codes, own entries, dates) and checks that `tool.schema.json` is up to date; keep your change consistent with those checks.

## Rules

- One issue = one change. Do not touch anything the issue does not ask for.
- Never weaken or delete a check to make it pass.
- Use case codes come from the Reference. Do not invent codes.
- Do not add, change or remove `own: true` entries unless the issue says so.
- If the issue is unclear, needs an editorial decision, or needs a protected path, write the reason to `.agent-tmp/blocked.md` and stop. Do not guess.

## Do not touch

The pipeline never opens a PR for changes in these paths. Keep this list in step with `protected_paths` in `.github/workflows/agent-worker.yml`.

- `.github/`, any `.env` or `.env.*` file (always protected)
- `LICENSE`, `MAINTAINERS`
