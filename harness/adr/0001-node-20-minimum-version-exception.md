# ADR-0001: Exception to supported-versions policy: Node.js 20 as minimum version

- **Status**: proposed
- **Date**: 2026-10-30
- **Owner**: @josemaria-toro
- **Expiry** (guardrail exceptions only): 2027-01-31

## Context

`guides/tech-stack.md` requires versions with active support (LTS when available). The frontend stack sheet (`stacks/frontend-react.md`) sets **Node.js 20 as the minimum supported version**.

Node.js 20 reached end-of-life on **2026-04-30** and no longer receives security patches (per third-party trackers such as endoflife.date; the official schedule at nodejs.org should be checked to confirm). Keeping it as the minimum therefore deviates from the supported-versions policy and from the security baseline (OWASP: vulnerable and outdated components).

Reason Node 20 is required: **<to be filled in by the owner: e.g. infrastructure/hosting constraint, dependency compatibility, migration timeline>**.

## Decision

Keep Node.js 20 as the **minimum** supported version, temporarily, until the expiry date above. Newer LTS versions (22, 24) remain allowed and CI also runs on them. Nothing may be implemented that is incompatible with Node 22/24, so the later migration is a version bump and not a rewrite.

This ADR is an exception to `tech-stack.md` ("Supported versions") and expires on **2027-01-31**. By that date the minimum is raised to a supported LTS, or this ADR is renewed with a new justification and expiry.

## Alternatives considered

| Alternative | Pros | Cons |
|---|---|---|
| Raise the minimum to Node 22 now | Supported, receives security patches; no exception needed | Requires the Node 20 blocker (see Context) to be removed first |
| Raise the minimum to Node 24 now | Longest remaining support | Same blocker; larger jump |
| Keep Node 20 with no expiry | No work | Unpatched runtime indefinitely; violates guardrail rules on exceptions |
| **Keep Node 20 temporarily with mitigations (chosen)** | Unblocks current constraints | Accepted security risk until expiry |

## Consequences

- Positive: current constraint is respected without blocking delivery.
- Negative / accepted risk: Node 20 has no security patches; runtime vulnerabilities will not be fixed upstream.
- Mitigations while the exception is active:
  - Run CI on a Node 20 and a Node 22/24 matrix to prove forward compatibility.
  - Keep the vulnerability gate (`guardrails.md`) active for dependencies and secrets; the Node runtime itself is not covered by the audit tools, so review Node security releases manually.
  - Do not expose Node 20 directly to untrusted networks without a hardened reverse proxy/WAF in front.
  - Use minimal container images and do not run as root.
  - Track the migration as an OpenSpec change/chore with an owner and a due date before the expiry.
- How it is verified or reverted: a CI check (or calendar reminder) fails/alerts after the expiry date; reverting means raising `engines.node` in `package.json`, `.nvmrc`, CI and Docker images to the new minimum and updating `stacks/frontend-react.md`.
