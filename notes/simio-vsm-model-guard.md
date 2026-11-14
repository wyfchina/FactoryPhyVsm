# Simio VSM model guard

- Date: 2026-11-10
- Active model: `/Project/Model`
- Simio version: `20.297.56736.0`
- Persistence: the Simio MCP has no save/copy operation. The active model is not yet confirmed saved as `.spfx`; this file is a configuration guard, not a model-package backup.
- Facility: `Source_ProductionRelease` → `Server_Stamping` → `Server_Weld1` → `Server_Weld2` → `Server_Assembly1` → `Server_Assembly2` → `Sink_Shipping`, joined by six Connectors.
- Data tables: `VSM_OperationTable` (6 rows), `VSM_ProductTable` (2), `VSM_InventoryTable` (6), `VSM_ScenarioTable` (2), `VSM_ReliabilityTable` (5).
- Facility parameter state after this pass: processing seconds = 1, 39, 46, 62, 40; setup minutes = 60, 10, 10, 0, 0; each process Server `Initial Capacity=1`.
- Reliability state after this pass: Stamping and S. Weld #2 use `Processing Time Based`; their expressions are `Random.Exponential(8)` hours for uptime, with repair means 1.411764705882353 and 2 hours. Weld #1 and both Assembly stations use `No Failures`.
- Source state after this pass: `Arrival Mode=Interarrival Time`, `Interarrival Time=60 Seconds`, `Entities Per Arrival=1`, `Maximum Arrivals=18400`, `Time Offset=0 Seconds`. This represents total takt input only; it does not yet represent product identity, EPE batches, or transfer batches.
- Diagnostics after this pass: 0 errors.
- Smoke test: one 24-hour fast-forward run completed on 2026-11-10 and was stopped; no runtime errors or warnings. `NumberCreated=1441`, `NumberDestroyed=1297`, and 144 entities remained in the line, so the count reconciles. `Server_Assembly1` scheduled utilization was 93.1432% for this short test; this is not a baseline result because upstream failures reduce its input and the prototype's product mix, work schedule, WIP, and setup execution are not yet represented.
- Explicit limitation: the current active model still lacks product-state assignment, initial WIP loading, work schedules, changeover execution, demand fulfillment, and experiment configuration.
- Worktree condition: `README.md` contains a user modification and is not part of this modeling change.
- Issue source: `notes/15.md`; format reference is the user-specified `AIT_issues\issues` directory.
