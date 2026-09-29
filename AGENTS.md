# Development instructions for sketch2026

## Project intent

Build a standalone browser-based building sketch application for assessor offices, with SmartCAMA as the proposed first CAMA integration. Read `docs/product-plan.md`, `docs/roadmap.md`, and `docs/architecture.md` before implementing a milestone. The repository begins as a planning repository; documentation is not evidence of implemented features.

## Working rules

- Follow the current user request and implement a bounded milestone. Keep README status and relevant docs accurate.
- Preserve existing work and avoid unrelated rewrites. Use focused branches/PRs for implementation work once development starts.
- Record significant architecture choices in `docs/decisions/` with the reason, alternatives, and compatibility implications.
- Keep the product brand, company ownership, hosting provider, and price unassigned until decided by the owner.
- Do not add production deployment or live CAMA writes as an incidental part of building a prototype.

## Geometry requirements

- Keep geometry and calculations independent of rendering and UI state.
- Use explicit real-world units and a documented numeric precision policy. Screen pixels and formatted dimension labels must never be the calculation source.
- Preserve original measurement input and provenance. Rounding is a declared presentation/reporting rule.
- Reject open, self-crossing, or otherwise invalid outlines for official area calculation. Show closure discrepancies; never silently stretch dimensions.
- Preserve adjacent/shared boundaries or expose conflicts when editing dimensions.
- Keep gross area, deductions, net area, classifications, and assessment factors separate.
- Prevent overlapping deductions or overlapping counted regions from silently double-counting space.
- Use the same versioned calculation rules for screen, save/reopen, reports, and CAMA output.

## Verification

- Maintain meaningful tests for known areas/perimeters, irregular polygons, unit parsing, invalid shapes, hole/overlap behavior, and undo/redo.
- Verify that save/reopen and supported import/export round trips preserve geometry and classifications.
- Test organization isolation, revision immutability, stale-update rejection, and idempotent CAMA delivery when those capabilities are introduced.
- Test offline/reconnect behavior on actual target devices before claiming field readiness.
- State exactly what was verified and what is still incomplete. Do not treat a visual demo as validated conversion or production readiness.

## Data and integration

- Use synthetic sample records in this public repository. Keep credentials, customer source files, and private office data outside version control.
- Authenticate CAMA launch context and derive tenant access server-side; never trust a client-provided organization ID alone.
- Preserve original conversion files in authorized storage and report unsupported content. Do not promise APEX file compatibility without representative tested samples.
- Keep adapters separate from the canonical geometry model. Use a test receiver and confirmed field/code mappings before live writes.
- Preserve both versions on conflicting edits and make recovery possible.
- AI suggestions require geometry validation and explicit user confirmation; inferred measurements must stay visibly identified.

## Handoff

Each implementation PR should state the user workflow changed, acceptance criteria met, checks performed, known limitations, and any schema or integration compatibility impact. Keep proposed targets separate from measured results.
