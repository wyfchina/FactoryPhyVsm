# VSM V0.5 Initial WIP Table Evidence

## Scope

This evidence records the live Simio change to `/Project/Model` for the table-driven initial-WIP mechanism. The user-saved source file was `VSM_V0.5_InitialWIPTable.spfx`; the live model was edited through Simio MCP. The MCP session has no save operation, so the live change must be persisted from Simio with `Ctrl+S` before this record is treated as a saved artifact.

## Implemented structure

- `VSM_InitialWIPTable`: 10 location-product records, 17,130 total units.
- `Source_InitialWIP_Table`: `Arrival Table`, `Arrival Time Property = VSM_InitialWIPTable.ArrivalTime`, `Entities Per Arrival = VSM_InitialWIPTable.EntitiesPerArrival`.
- `Transfer_InitialWIP`: routes through `VSM_InitialWIPDestinations` using `Candidate.Node.AssociatedObject == VSM_InitialWIPTable.CurrentResource`.
- `VSM_InitialWIPDestinations`: Weld1, Weld2, Assembly1, Assembly2 and FG Staging input nodes.
- `Before Exiting` copies `ProductType`, `ProductionBatch`, `ReleaseTimeHours` and `TrayID` from the bound table row to the entity states.
- The ten legacy per-location Sources were deleted from the live model after the table-driven mechanism was validated:
  `Source_Initial_W01_L/R`, `Source_Initial_W02_L/R`, `Source_Initial_W03_L/R`,
  `Source_Initial_W04_L/R` and `Source_Initial_W05_L/R`.
- Deleting those Sources also removed their ten generated output nodes and reduced the Connector collection from 22 to 12. The table-driven Source, transfer node, destination list and production-release Source remain.

## Validation evidence

### Mechanism sample

Five table records created 8 entities at time zero. The five target locations received 2, 1, 1, 2 and 2 entities respectively. FG Staging retained its 2 entities in its output buffer and released 0.

### Full initialization

With production release disabled and a 0.01-hour run:

- Total created: 17,130.
- Weld1 input entered: 7,000.
- Weld2 input entered: 1,700.
- Assembly1 input entered: 2,450.
- Assembly2 input entered: 1,840.
- FG Staging input entered: 4,140.
- FG Staging output-buffer exited: 0.
- Diagnostics: 0 errors.

### Deterministic regression

With production release restored to two arrivals and the existing 306.6666667-hour run length:

- Total created: 35,530 = 17,130 initial WIP + 18,400 released production.
- Total destroyed/shipped: 19,645.
- End-of-run population: 15,885.
- FG Staging output buffer: 4,140, with 0 exits.
- Diagnostics: 0 errors.
- Runtime warning: active entities exceed 20,000 at time 0. This is expected for a unit-level representation of the 17,130-unit snapshot and is not a logic error.

### Post-cleanup regression

After deleting the ten inactive legacy Sources, the same deterministic fast-forward was rerun:

- Total created: 35,530.
- Total destroyed/shipped: 19,645.
- End-of-run population: 15,885.
- `Source_InitialWIP_Table` created: 17,130.
- Diagnostics: 0 errors.
- The only runtime warning remained `Model_HighNumberOfAgentsInSystem`; deleting inactive Sources does not reduce the number of real unit-level WIP entities.

## Open persistence action

Press `Ctrl+S` in the Simio window for `VSM_V0.5_InitialWIPTable` after the desktop is unlocked. The post-cleanup live state has been validated through MCP, but it is not yet confirmed as persisted to disk. Reopen or reload the saved file and repeat the 0.01-hour full-initialization check before treating V0.5 as the persisted handoff version.
