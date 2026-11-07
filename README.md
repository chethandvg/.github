# Shared CI and settings for Frequencies of Life

This repository holds what every [Frequencies of Life](https://chethandvg.github.io/frequencies-of-life/) repository reuses: one copy of each CI workflow, the site address, and the registry of repositories. Code is written once here and called everywhere else, so a fix in one place reaches every repo.

## Reusable workflows

Call a workflow from another repo with `uses: chethandvg/.github/.github/workflows/<file>@v1`.

| Workflow | What it does |
|---|---|
| [`rust-ci.yml`](.github/workflows/rust-ci.yml) | `cargo fmt`, `clippy -D warnings` and tests on Linux and Windows |
| [`py-bindings-ci.yml`](.github/workflows/py-bindings-ci.yml) | Builds the PyO3 bindings with maturin and runs their golden-vector tests |
| [`wasm-ci.yml`](.github/workflows/wasm-ci.yml) | Builds the WebAssembly bindings and runs their golden-vector tests in Node |
| [`python-ci.yml`](.github/workflows/python-ci.yml) | Ruff lint and pytest across Python versions, for pure-Python packages |
| [`lean-check.yml`](.github/workflows/lean-check.yml) | Builds the Lean 4 proofs with the Mathlib cache, rejects `sorry` and non-standard axioms, and checks that every proved claim names a real theorem |
| [`claims-verify.yml`](.github/workflows/claims-verify.yml) | Validates `claims.yaml`, resolves every DOI and PMID (failing on retractions), checks cross-repo claim dependencies, and keeps the README claims table current |
| [`license-check.yml`](.github/workflows/license-check.yml) | Dependency licence policy: permissive licences only, no GPL or AGPL |
| [`site-url-check.yml`](.github/workflows/site-url-check.yml) | Fails if a file links to the site under an old address |
| [`release.yml`](.github/workflows/release.yml) | Checks that every version field matches the tag, publishes the GitHub release (Zenodo archives it and mints a DOI) and asks Software Heritage to archive the source |
| [`pages-deploy.yml`](.github/workflows/pages-deploy.yml) | Builds a static site with Node and deploys it to GitHub Pages |

Versions: `@v1` always points to the latest compatible release. Breaking changes get a new major tag.

## Settings and data

| File | Purpose |
|---|---|
| [`site.json`](site.json) | The single source of the site address (`site_url`). Builds and checks read it; changing it is the only edit a domain switch needs. |
| [`registry.json`](registry.json) | Every repository in the project, with its layer, licence, claim prefix and dependencies. The hub site and the claims checks read it. |
| [`scripts/switch-domain.py`](scripts/switch-domain.py) | Rewrites old site links across all local repos when the site moves to a custom domain |

## Licence

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
