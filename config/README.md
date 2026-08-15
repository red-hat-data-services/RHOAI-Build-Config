# Catalog Validation Config

## Overview

`new-config.yaml` is the configuration file for the RHOAI catalog validator.
It tells the validator which operator bundles should be present (or absent) in
each OCP version's catalog, using version range expressions.

`config.yaml` is the legacy format using single-value `onboarded-since` /
`discontinued-from` fields. It is **deprecated** — use `new-config.yaml` for
all new entries. See
[PR #49](https://github.com/red-hat-data-services/RHOAI-Konflux-Automation/pull/49)
for the validator changes that support the range-based format.

## Fields

Each OCP version gets an entry under `config.supported-ocp-versions`:

```yaml
config:
  supported-ocp-versions:
    - version: v4.XX
      onboarded-range: '>=2.25.0 <2.26.0 || >=3.5.0'
      discontinued-range: '>=3.0.0'
      skip-bundles:
        - rhods-operator.X.Y.Z
```

| Field | Required | Description |
| ----- | -------- | ----------- |
| `version` | Yes | OCP version, e.g. `v4.22`. |
| `onboarded-range` | No | Range of RHOAI versions expected in the catalog. Defaults to all versions if omitted. |
| `discontinued-range` | No | Range of RHOAI versions no longer expected (offboarded). Defaults to none if omitted. |
| `skip-bundles` | No | Explicit list of bundles to exclude from validation for true one-off exceptions (see below). |

## Range Syntax

Range expressions are inspired by
[OLM's skipRange](https://olm.operatorframework.io/docs/concepts/olm-architecture/operator-catalog/creating-an-update-graph/#skiprange)
(which uses [blang/semver](https://github.com/blang/semver#ranges) under the
hood). We support a deliberate subset of that grammar — enough for onboarding
and discontinuation rules, without wildcards or full blang prerelease semantics.

Ranges use bare semver versions (e.g. `3.5.0`, `3.6.0-ea.2`) — not
`rhods-operator.` prefixed names.

- **Comparators:** `>=`, `>`, `<=`, `<`, `=`, `!=`
- **AND:** space-separated conditions — all must be true
- **OR:** `||` between clauses — any clause can match

### Examples

**Simple lower bound** — expect all versions from 3.6.0-ea.1 onward
(including later EAs and GA releases):

```text
>=3.6.0-ea.1
```

**Bounded range** — expect only the 2.25.x line (2.25.0 up to but not
including 2.26.0):

```text
>=2.25.0 <2.26.0
```

**Gap range** — expect the 2.25.x EUS line and everything from 3.5.0 GA
onward, but nothing in between:

```text
>=2.25.0 <2.26.0 || >=3.5.0
```

Intermediate releases that shipped before this OCP went GA fall in the gap
and are excluded automatically:

- GA versions like `3.2.1`, `3.4.1` — not `>=2.25.0 <2.26.0`, not `>=3.5.0`
- EA versions like `3.4.0-ea.1`, `3.4.0-ea.2`, `3.5.0-ea.1`, `3.5.0-ea.2` —
  also fall in the gap because EA releases sort **below** their corresponding
  GA release (`3.5.0-ea.2 < 3.5.0 GA`), so they do not satisfy `>=3.5.0`

### EA version ordering

EA releases sort below their corresponding GA release:

```text
3.5.0-ea.1 < 3.5.0-ea.2 < 3.5.0 (GA) < 3.6.0-ea.1
```

This means `>=3.5.0` includes the GA release and everything after it
(including later EA series like `3.6.0-ea.1`), but excludes all
`3.5.0-ea.*` pre-releases.

Invalid range strings are caught at config load time before validation runs.

### When to use `skip-bundles`

Use `skip-bundles` only for GA versions that fall inside the `onboarded-range`
but are expected to be absent from that OCP version's catalog.

For example, `rhods-operator.2.25.9` falls inside `>=2.25.0 <2.26.0` for
v4.22, but was deliberately excluded from OCP 4.22 because of an Istio 1.28
incompatibility that broke llm-d TP
([RHOAIENG-78143](https://redhat.atlassian.net/browse/RHOAIENG-78143)).
PM decided to not support OCP 4.22 for the 2.25 stream until the llm-d fix
lands in 2.25.11. Until then, newer 2.25.z releases (2.25.10, etc.) should
also be added to `skip-bundles` as they ship:

```yaml
- version: v4.22
  onboarded-range: '>=2.25.0 <2.26.0 || >=3.5.0'
  skip-bundles:
    - rhods-operator.2.25.9
    - rhods-operator.2.25.10   # add as each z-stream ships without the fix
```

Once 2.25.11 ships with the fix, it will be included in the v4.22 catalog
and does not need to be skipped.

> **Note:** EA bundles never need to be listed in `skip-bundles`. Older EA
> versions are always pruned in favour of newer EA releases, and the
> validator accounts for this — e.g. once `3.6.0-ea.2` is published,
> `3.6.0-ea.1`, `3.5.0-ea.2` and earlier EAs are expected to be absent.
