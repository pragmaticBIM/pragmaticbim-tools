# pragmaticBIM tool registry

A neutral list of software tools that help carry out the use cases of the [pragmaticBIM Reference](https://github.com/pragmaticBIM/pragmaticBIM-reference). One YAML file per tool, each naming the use cases it serves by their code (for example `QAS-BENCHMARK`).

## Why a separate repository

The Reference describes what building owners order and what architects deliver with BIM. It stays free of product listings so that it remains a standard, not a catalogue. This registry sits next to it: the Reference defines the use cases, the registry lists tools that produce their required output.

Tools from abstract ag, which maintains pragmaticBIM, are listed here like any other tool and marked with `own: true`.

## Status of an entry

| Status | Meaning |
| --- | --- |
| `editorial` | Added by pragmaticBIM. The function was confirmed from the vendor's own documentation, linked in `source`. |
| `self-declared` | Submitted by the vendor. Not tested. |
| `verified` | Tested by pragmaticBIM against the checks of the use case. Records the date (`verified_on`) and product version (`verified_version`). |

**A listing is not an endorsement unless its status is `verified`.** `editorial` and `self-declared` entries say that a tool claims to cover a use case, not that pragmaticBIM vouches for the result.

Entries with `published: false` are kept for review and are not shown on the website.

## How the website uses it

A private generator reads this registry and the latest release of the Reference. On each use case page of [pragmaticbim.ch](https://pragmaticbim.ch) it lists the published tools whose `use_cases` contain that code, with the status shown next to each tool. Every push to `main` triggers a website build.

## Repository layout

| Path | Role |
| --- | --- |
| `schema/tool.yaml` | LinkML schema, source of truth for the file format |
| `schema/tool.schema.json` | JSON Schema generated from `tool.yaml`; do not edit by hand |
| `tools/{id}.yaml` | One file per tool; the file name equals `id` |
| `scripts/check_codes.py` | Checks the schema can't express: file names, use case codes, `own` entries, stale dates |
| `MAINTAINERS` | GitHub handles allowed to add or change `own: true` entries |

## Example

```yaml
id: oneclicklca
name: One Click LCA
vendor: One Click LCA Ltd
url: https://www.oneclicklca.com
category: lca
pricing: commercial
countries: [ch, de, at]
description:
  de: Ökobilanz und graue Energie mit KBOB-Daten, Minergie-akkreditiert.
use_cases:
  - code: DES-LCA
    note:
      de: Graue Energie nach Minergie mit KBOB-Daten.
own: false
status: editorial
source: https://help.oneclicklca.com/en/articles/663332
published: true
last_checked: "2026-10-17"
```

Write dates in quotes (`"2026-10-17"`). Unquoted, YAML reads them as dates and `linkml-validate` rejects them.

## Checks

```bash
pip install -r requirements.txt
linkml-validate -s schema/tool.yaml -C Tool tools/*.yaml
python scripts/check_codes.py
```

`check_codes.py` downloads the latest Reference release to look up use case codes. To check against a local checkout instead, set `REFERENCE_DIR=/path/to/pragmaticBIM-reference`.

After changing `schema/tool.yaml`, regenerate the JSON Schema:

```bash
gen-json-schema schema/tool.yaml > schema/tool.schema.json
```

## Contributing

Vendors and users can propose tools by pull request or with the issue form. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[PragmaticBIM Standard License](LICENSE). © abstract ag.
