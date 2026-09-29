# Assessor Sketch Product and Build Plan

September 29 2026

Project repository  scamaagent-sudo/sketch2026

Build a standalone browser application for assessor offices, with SmartCAMA as the first integration. Start with dependable building geometry, fast keyboard entry, and clear area classifications. Make migration and approved data exchange part of the product from the beginning.

The initial market should be residential assessment and routine outbuildings, followed by more complex commercial properties. The product must let an office create, revise, review, and retain a building sketch without depending on a particular CAMA vendor.

### Competitive starting point

APEX already markets browser sketching, offline operation, portal synchronization, and integrations with CAMA providers. Its desktop product supports modern and legacy drawing modes. Browser availability alone will not establish a compelling reason to switch. [1]

APEX also documents decimal-foot and feet-and-inches entry, area calculations, and subtractive areas. Its broader GeoViewPort offering includes review workflows, imagery, and CAMA integration. These are established competitive capabilities. [2, 3]

| Proposed advantage | How to prove it |
| --- | --- |
| Faster routine editing | Time the same new sketch and addition in both products, with practicing sketch technicians. |
| Clear assessment data | Explain every reported area, classification, exclusion, and change before approval. |
| Low-friction conversion | Import a representative customer sample and account for every unsupported object. |
| Easy CAMA adoption | Launch from a parcel, return approved geometry and classified areas, and confirm receipt. |

These are product hypotheses to validate with pilot users; they are not claims that APEX lacks the corresponding capabilities.

### Commercial approach

Offer an annual office subscription with a clear editor allowance, read-only review access, and separately scoped conversion and integration services. Start with two or three design-partner offices. Set prices after confirming their current sketching costs, conversion effort, procurement requirements, and willingness to switch.

## Product workflow and release scope

The main screen should open directly to the sketch. Place building and floor selection on the left, a large drawing surface in the center, and classified area totals on the right. Keep a keyboard command field visible. Tablet mode should use larger controls and a measurement keypad.

### Daily workflow

1. Open a parcel from the standalone parcel list or an authorized CAMA launch. Select the building, floor, assessment year, and working revision.

1. Draw with distance and direction commands, a mouse, or touch. A command such as R 40 adds a 40-foot segment to the right; the final syntax should be tested with experienced APEX users.

1. Close the outline and classify areas using the office’s codes. Attach a garage, porch, or addition and identify deductions such as an open-to-below area.

1. Review dimensions, area calculations, and changes against the prior approved sketch. Resolve open outlines, overlaps, and missing classifications.

1. Save a draft, submit it for review, or approve it according to the office’s permissions. Export the approved revision to CAMA and retain the delivery receipt.

| Capability | First prototype | Assessor pilot |
| --- | --- | --- |
| Drawing | Exact line and polygon entry; snapping; selection; pan and zoom | Shared-wall behavior; edit dimensions; split and combine regions; tested touch controls |
| Area model | Living area, garage, porch, and deductions; live square footage | Office-defined codes; multiple buildings and floors; explicit inclusion and rounding rules |
| Editing | Undo and redo; move vertices and shapes; copy and delete | Revision comparison; recoverable drafts; controlled edits to shared boundaries |
| Records and output | Save and reopen a sample sketch; JSON and SVG export | Tenant access; review history; PDF and image reports; approved CAMA delivery |
| Field use | Tablet-sized interface for evaluation | Offline job download, local recovery, conflict review, and verified synchronization |
| Legacy conversion | Inspect sample files and establish a conversion path | Supported-format import with exception reporting and area reconciliation |

Treat circles, arcs, complex commercial segmentation, laser measurement devices, and aerial tracing as explicit scope decisions after examining pilot files. Add any geometry essential to those offices before their pilot; do not silently approximate it.

## Geometry and calculation requirements

The geometry engine is the central product asset. Keep it independent of the screen so drawing, reports, imports, and CAMA exports calculate the same result. Store entered measurements and geometry; derive the image and totals from that record.

### Rules for trustworthy sketches

- Use real-world coordinates, explicit units, and a documented precision policy. Never calculate square footage from screen pixels or repeatedly rounded labels. Preserve decimal and fractional input, including the original measurement text.

- Changing a wall length must follow an explicit editing rule: hold the selected endpoint fixed, move the other endpoint, and show affected walls. Connected regions must remain consistent or require the user to resolve the conflict.

- Keep geometric area separate from assessment treatment. Store gross area, deductions, net area, and the office’s reporting category. Any assessment factor belongs in a separate field and must not change the underlying geometry.

- Define whether an area is adjacent, nested, or subtractive. Deduct only the part inside its parent and combine overlapping deductions before subtracting, so the same space is never deducted twice.

- Reject self-crossing polygons and zero-length walls. Show the distance and direction needed to close an outline. Never silently stretch a measured building to force closure.

- Version the calculation and classification rules. Approvals preserve their geometry, rules, totals, author, and date; subsequent changes create a new revision.

### Reference calculations for the first build

| Test case | Expected result |
| --- | --- |
| Rectangle measuring 40 by 30 feet | 1,200 square feet; 140 feet of perimeter |
| 40 by 30 rectangle with a 10 by 10 corner removed | 1,100 square feet; outline remains valid |
| 1,200-square-foot parent with an interior 8 by 10 deduction | 1,120 square feet of net parent area |
| Two 100-square-foot deductions overlapping by 25 square feet | 175 square feet deducted from their shared parent |
| 12 feet 6 inches by 10 feet | 125 square feet; unchanged after switching display units |
| Add a separate 20 by 20 garage to a 1,200-square-foot living area | Living area stays 1,200; garage is 400; combined area is explicitly labeled |
| Translate or rotate a closed outline | Area remains unchanged within the documented engine tolerance |

Require automatic tests for these cases, irregular polygons, invalid shapes, import round trips, and undo/redo. Compare a larger benchmark set against independently verified calculations. Pilot reviewers must resolve every unexplained area discrepancy.

## Architecture and CAMA integration

Recommended architecture: a React and TypeScript web client, an independent geometry package, a TypeScript API service, PostgreSQL for records and revisions, and object storage for source files, photos, and report outputs. Start with an SVG drawing surface; benchmark large sketches before considering a different renderer. These are proposed choices, with final hosting and package versions selected during implementation.

| Component | Responsibility |
| --- | --- |
| Browser editor | Drawing, selection, dimensions, command entry, undo/redo, local draft recovery, and review display. |
| Shared geometry package | Validation, intersections, area operations, measurement parsing, tolerances, and deterministic calculations. |
| Application API | Tenant permissions, revisions, server-side recalculation, approval, exports, and integration jobs. |
| PostgreSQL and file storage | Parcel/building identity, immutable approved versions, audit history, originals, and generated outputs. |
| CAMA adapters | Map office codes and identifiers to each CAMA system; deliver approved revisions and record acknowledgments. |

### Core records

Model Organization, User, Parcel, Building, Floor, SketchRevision, Area, Boundary, Annotation, RuleSet, SourceFile, and ExportJob. Every business record carries an organization identifier. An area carries its floor, type, parent relationship, geometry, measurement provenance, and calculation result. Store local sketch coordinates separately from any future map georeferencing.

### Integration contract

A CAMA launch supplies verified organization, parcel, building, year, and user context through a short-lived authorized exchange. The adapter returns a versioned payload containing sketch identity, classified gross and net areas, units, geometry, preview/report references, and approval metadata. Support standalone login and parcel import through the same application.

Return only approved revisions for official record updates. Include an idempotency key so retries do not duplicate changes, and a base-version check so an old sketch cannot overwrite newer CAMA data. Record Pending, Delivered, or Failed status with a retry path. SmartCAMA field mappings and update behavior must be confirmed with its engineering team in a sandbox.

### Access and data ownership

Use established organization sign-in with technician, reviewer, and administrator roles. Enforce tenant access in the API and database; PostgreSQL row security can add record-level enforcement. Use an application role that cannot bypass those policies. Test isolation, including exports and file downloads. [6]

Each office must be able to export its geometry, classifications, history, and reports. Keep database backups and rehearse restoring them. Tenant-scoped file links, signed integration messages, and secure handling of credentials are required before using live assessment records.

## Migration field work and AI

### Make conversion an early workstream

Existing sketches represent years of office work. Obtain representative native files, exported data, and printed reports from a willing pilot office before selecting an import strategy. First classify the files by product/version, geometry, area codes, and available metadata. A PDF preview and an editable source sketch require different conversion paths.

1. Inventory a recommended 50 to 100 sketches, including additions, deductions, multiple floors, unusual angles, arcs, and commercial examples.

1. Evaluate documented interchange formats, available integration agreements, and customer-authorized exports. Establish which source versions can be converted reliably.

1. Preserve original files. Produce a conversion report listing source and destination identifiers, mapped codes, unsupported objects, and differences in gross and net area.

1. Require review of exceptions. Mark a converted record as usable only after its supported geometry and reported values reconcile under an agreed tolerance.

1. Run a small parallel pilot before bulk conversion. Keep a rollback path to the original records and support incremental imports during transition.

Offer reference-image attachment and calibrated manual tracing when editable geometry is unavailable. Label measured, imported, traced, and inferred geometry distinctly. Do not describe a tracing workflow as lossless APEX conversion.

### Offline field work

Package the editor as a progressive web app. Use service-worker caching for the application and IndexedDB for downloaded jobs, drafts, and a pending synchronization queue. These browser capabilities support offline operation, but storage limits and eviction behavior require device testing. [4, 5]

Before leaving the office, the user downloads assigned parcels and verifies that they are available offline. Show Saved on this device and Synced to server as separate states. Protect drafts during updates, handle expired sign-in after reconnection, and make recovery/export possible when synchronization fails.

Use revision checks when two people change the same sketch. Preserve both drafts and ask the reviewer to resolve competing geometry edits. Avoid automatic last-write-wins behavior. Validate a full field session on the actual iPads, Windows tablets, or Android devices the pilot offices use.

### AI after the drawing engine

The first useful AI feature is assisted entry: translate a command such as “add a 20 by 20 garage on the east side” into a proposed edit with a visible preview. Later, extract labeled measurements from scans and suggest geometry. The geometry engine validates every proposal; the user confirms placement and uncertain measurements before saving.

AI should also flag open outlines, missing dimensions, and inconsistent classifications. Keep sources and confidence visible for extracted values. Never infer a reliable scale from an uncalibrated image or automatically approve AI-generated assessment data.

## Roadmap and pilot acceptance

Use completion criteria to control releases. The effort ranges below are planning estimates for two experienced engineers, part-time product/design support, and an assessor subject-matter expert with regular testing time. They are not commitments; source-format access, integration access, and geometry complexity can change them.

| Phase | Indicative effort | Completion criterion |
| --- | --- | --- |
| 1  Validate workflows | 1–2 weeks | Observe sketch technicians, inventory source files, agree on office codes, and record baseline task times. |
| 2  Prove the engine | 3–5 weeks | Working browser editor passes reference calculations, exact-entry edits, undo/redo, and save/reopen checks. |
| 3  Build the office product | 4–6 weeks | Tenant access, parcel records, review, reports, and immutable approved revisions work end to end. |
| 4  Integrate and migrate | 4–8 weeks | SmartCAMA sandbox exchange succeeds; selected source formats reconcile; offline recovery and conflicts are tested. |
| 5  Run a controlled pilot | 4–6 weeks | Design partners complete real work, reconcile outputs, and confirm that speed and reliability justify switching. |

A narrow working prototype could be ready in roughly 4 to 7 weeks. Allow roughly 4 to 7 months for the sequence through a controlled pilot. Research and integration preparation can overlap; broader commercial geometry and additional CAMA adapters should have their own estimates after the pilot.

### Recommended pilot targets

- Accuracy: every accepted benchmark sketch reconciles to the office-approved expected result and reporting precision; every discrepancy has a documented resolution.

- Speed: target at least a 25 percent reduction in median time for selected routine edit tasks after training, measured against the same staff using their current workflow. This is a proposed target, not a current performance claim.

- Data safety: no lost acknowledged saves in reconnect, reload, conflict, or recovery scenarios. Approved revisions remain reproducible.

- Conversion: every imported record is accounted for as converted, review required, or unsupported. A failed object cannot disappear silently.

- Integration: repeated delivery does not duplicate updates; stale revisions and wrong-tenant requests are rejected; the receiving CAMA record matches the approved payload.

### Expand after the pilot

Prioritize remaining needs by observed frequency: commercial sketches and curves, sketch-to-imagery review, measurement-device support, additional CAMA adapters, bulk quality review, and assisted extraction. Broader APEX replacement should follow demonstrated coverage of the target offices’ real sketch inventory.

## Initial engineering backlog and decisions

Start the first development sprint with a small repository and explicit acceptance criteria. Keep geometry, application behavior, and CAMA mappings separate so a second integration does not require rewriting the editor.

| Order | Work item | Acceptance |
| --- | --- | --- |
| 1 | Versioned sketch schema | Document units, identities, area relationships, and compatibility rules; sample records validate. |
| 2 | Geometry and measurement engine | Reference calculations pass, invalid outlines are rejected, and original measurement input is preserved. |
| 3 | Keyboard drawing and command history | Create a measured outline, undo/redo every operation, and reproduce the same saved geometry. |
| 4 | Region classification and deductions | Adjacent and nested areas reconcile without double counting; classified totals explain their components. |
| 5 | Dimension editing and selection | Show the proposed result of a wall edit and any affected geometry before committing it. |
| 6 | Save reopen and report output | Saved geometry, reopened geometry, displayed totals, and exported JSON/SVG agree. |
| 7 | Early conversion feasibility | Analyze sample files, choose one supported path, and produce an explicit exception inventory. |
| 8 | CAMA contract and test receiver | Launch a sample parcel and return an approved, versioned result with a recorded acknowledgment. |

### Inputs that most improve the first build

- A screen recording of an experienced assessor sketch technician completing a new building, an addition, and a correction in the current tool.

- Representative editable APEX files plus their printed reports and the office’s area-code list. An initial handful can start the feasibility work; expand to the migration sample before committing to coverage.

- The actual devices and browsers used in the field, including connectivity constraints and current measurement equipment.

- A SmartCAMA integration contact, sample parcel/building identifiers, and a test environment for the proposed handoff.

### Decisions already established

The first customers are assessor offices. The application is a standalone product with CAMA integration, and the next deliverable is a product and build plan. Brand name, ownership entity, hosting provider, final subscription pricing, and pilot participants remain separate business decisions.

### Recommended first demonstration

Open a parcel, enter a measured outline using the keyboard, attach a garage and porch, change one wall dimension, and show the revised classified totals. Save and reopen it, compare the revision, then show the approved payload in a CAMA test receiver. Add legacy conversion to the demonstration once sample files establish a supported path.

## Sources and validation basis

Public product descriptions and technical documentation were reviewed on September 29 2026. Competitive features below are vendor-documented. Proposed differentiation, architecture, effort estimates, acceptance targets, and rollout decisions are recommendations that require implementation and pilot validation.

### 1  APEX Sketch product overview

Supports the competitive baseline for desktop and browser offerings, offline operation, cloud synchronization, and CAMA integration.

[View reference](https://apexappraisalsolutions.com/apexsketch/)

### 2  APEX Portal and ApexSketch vX

Documents cross-device use, offline synchronization, measurement entry styles, and subtractive-area functionality.

[View reference](https://www.apexwin.com/promos/apexsketchvx/index.html)

### 3  APEX GeoViewPort Desktop Review

Documents assigned review workflows, imagery, property-data editing, CAMA integration, and synchronization.

[View reference](https://apexappraisalsolutions.com/desktop-review/)

### 4  MDN IndexedDB API

Technical basis for structured browser storage, transactions, and browser-dependent storage/eviction considerations.

[View reference](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)

### 5  MDN Service Worker API

Technical basis for cached application resources and offline-capable web behavior.

[View reference](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

### 6  PostgreSQL Row Security Policies

Technical basis for row-level access policies and the need to account for privileged roles that bypass them.

[View reference](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

### Validation work before a replacement commitment

Benchmark experienced users on their own tasks; inspect the formats and objects present in their legacy data; agree on assessment calculation rules; validate the receiving CAMA fields; and complete recovery and field-device trials. Conversion coverage and operating reliability determine when an office can adopt the product for live work.
