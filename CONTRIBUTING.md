# Contributing to the pragmaticBIM tool registry

Anyone can propose a tool or correct an entry: vendors, users and consultants. Every change goes through a pull request and is reviewed by a maintainer.

## Propose or update a tool

1. Read the use case pages in the [pragmaticBIM Reference](https://github.com/pragmaticBIM/pragmaticBIM-reference) (`workflows/*.yaml`) and note the codes your tool serves.
2. Copy an existing file in `tools/` to `tools/{id}.yaml`. The `id` uses lowercase letters, digits and hyphens, equals the file name, and never changes once merged.
3. Fill in the fields as described in [`schema/tool.yaml`](schema/tool.yaml).
4. Run the checks (see [README.md](README.md#checks)).
5. Open a pull request. **One pull request per tool.**

Not using Git? Open an issue with the [tool listing form](.github/ISSUE_TEMPLATE/tool-listing.yml) and a maintainer will create the entry.

## Listing criteria

A tool is listed when it is:

- **available**: commercially or openly available to Swiss practices, not a prototype or a custom service;
- **maintained**: actively developed and supported;
- **fit for each listed use case**: it produces the required output (Lieferergebnis) of every use case it claims, as described on that use case's page. List only those use cases.

## Status

- Entries proposed by a vendor start as `status: self-declared`. They are listed without testing.
- `editorial` entries are added by pragmaticBIM after confirming the function from the vendor's documentation. They need a `source` page.
- `verified` is set only by pragmaticBIM after testing against the use case's checks. It needs `verified_on` and `verified_version`.

## Content rules

- `description` and `note` are neutral and factual, at most 140 characters, in German (`de`). French, Italian and English are welcome but optional.
- No marketing words: no "best", "leading", "revolutionary", "unique" or similar.
- `url` is the official product page: `https://`, no tracking or affiliate parameters.
- `source` is the vendor page that documents the function you describe.
- Write descriptions from the vendor's own documentation. If a function can't be confirmed there, leave it out.
- `own: true` is reserved for tools and actions by abstract ag. Their `url` points to the action page. If you are the vendor of the tool you propose, say so in the pull request.
- `pricing` reflects the vendor's website. If it is unclear, use `commercial`.
- Dates in quotes: `last_checked: "2026-10-17"`. Update `last_checked` whenever you confirm an entry; entries older than 12 months get a warning.

## Review

A maintainer checks the criteria and content rules, may shorten or neutralise wording, and merges. Entries can be unpublished (`published: false`) or removed if a tool is discontinued or no longer meets the criteria.

## License

By contributing you agree that your contribution is published under the [PragmaticBIM Standard License](LICENSE).
