# Roadmap and initial backlog

Status: proposed plan, September 29 2026. No application code or deployment exists yet.

## Milestones

| Phase | Planning range | Exit condition |
| --- | --- | --- |
| Workflow discovery | 1–2 weeks | Observe actual sketching tasks, obtain sample source files, agree on codes, and record baseline times. |
| Geometry prototype | 3–5 weeks | Exact entry, valid closed shapes, classification, deductions, undo/redo, save/reopen, and reference calculations work. |
| Office application | 4–6 weeks | Organization access, records, reviews, reports, and approved revision history work. |
| Integration and migration | 4–8 weeks | SmartCAMA sandbox exchange, supported source conversion, offline recovery, and conflict handling are validated. |
| Controlled pilot | 4–6 weeks | Practicing users reconcile real sketches and confirm adoption criteria. |

These are initial estimates for two experienced engineers plus part-time product/design and assessor support. The sequence is approximately 4–7 weeks to a narrow prototype and 4–7 months through a controlled pilot. Integration access, source formats, and required geometry can change the estimate. Begin source-file and CAMA research during discovery rather than waiting for the integration milestone.

## Initial work items

1. **Versioned sketch schema.** Define organization, parcel, building, floor, revision, boundaries, areas, units, provenance, and rules. Validate sample documents and establish backward compatibility policy.
2. **Geometry engine.** Parse decimal and feet/inches measurements, validate outlines, calculate area/perimeter, and document numeric tolerances. Pass the reference calculations in the product plan.
3. **Keyboard drawing.** Build a working canvas and command field with exact directional entry, snapping, selection, pan/zoom, and undo/redo.
4. **Area relationships.** Support adjacent, nested, and subtractive areas. Union overlapping deductions before clipping/subtracting them from their parent; explain classified totals.
5. **Dimension editing.** Preview endpoint movement and affected walls; preserve shared boundaries or require explicit conflict resolution.
6. **Save and reopen.** Keep versioned geometry authoritative. Confirm save/reopen, displayed results, JSON export, and SVG output agree.
7. **Conversion feasibility.** Inspect authorized source examples and produce a supported-format proposal with an exception inventory. Preserve originals and do not claim untested format compatibility.
8. **CAMA contract and receiver.** Document a generic launch/export contract and build a synthetic receiver. Confirm identifiers and code mappings with SmartCAMA engineering before live integration.

Items 1–6 form the first editor prototype. Feasibility investigation for items 7–8 should run early; full conversion and integration follow validated access and sample data.

## Pilot criteria

- Reconcile every accepted benchmark sketch to independently verified results at the office's reporting precision.
- Target a 25% reduction in median time for selected routine edits after training, using the same staff and tasks for the baseline. This is a proposed target, not a measured claim.
- Lose no acknowledged saves in tested offline, reload, reconnect, conflict, and recovery scenarios.
- Account for every conversion as converted, review required, or unsupported.
- Reject wrong-organization access, stale revisions, and duplicate integration updates.

## Later scope

Prioritize complex commercial shapes, curves, imagery alignment, measurement devices, additional CAMA adapters, and AI assistance using pilot evidence. Any geometry necessary for an initial pilot office must be supported or explicitly excluded from that pilot.
