# VSM V0.7 20-Piece Entity Evidence

## Scope and persistence

This record describes the Simio model at `/Project/Model` after converting the entity representation from one entity per workpiece to one entity per 20 workpieces. The 10-workpiece W03-R tail remains a separate entity. The user saved the model, closed and reopened it, and completed the native regression on 2026-11-14.

Persisted file: `VSM_V0.7_InitialWIPTable.spfx` in the `VSM_MichiganSteel` model folder. File size: 179,795 bytes. SHA-256: `D49089368991FA7F14B435D5BE6A5EAC1E74259A1F52ED2DA4ACC7A00F50EA7F`. The saved package contains the V0.7 model identity, the quantity state, the batch-count and unit-quantity WIP columns, the initialization and production-release processes, and weighted shipment logic.

After the user's close/reopen regression, the active MCP model identified itself as V0.7. MCP diagnostics returned 0 errors. The current run setup is deterministic, with randomness disabled, a 306.6666667-hour run length, and no warm-up. Run status reports 0 warnings and no last error.

The pre-change reference snapshot is `VSM_V0.6_InitialWIPTable.before-20piece-entities.spfx` in this output folder, SHA-256 `55A69A8EAD2BA9D775A470C34BBBE23D042C2161E2C842C99EEFA62492C6088C`.

## Representation

- `ModelEntity.VSM_QuantityState` records workpieces represented by each Simio entity.
- Standard entity quantity: 20 workpieces.
- Initial WIP: 17,130 workpieces represented by 857 entities across 11 table rows.
- W03-R: 840 workpieces in 42 standard entities plus one 10-workpiece tail entity; total remains 850.
- Production release: 460 entities per arrival, or 9,200 workpieces. The deterministic run generated 920 release entities, or 18,400 workpieces.
- Processing time at each modeled operation is the per-workpiece processing time multiplied by `VSM_QuantityState`, preserving the stated workload for each entity.
- Shipping is counted with a weighted workpiece statistic. Simio's native entity-created and entity-destroyed counts remain entity counts.

## Validation

Run setup: deterministic interactive fast-forward, random variation disabled, run length 306.6666667 hours, no warm-up.

- Model diagnostics: 0 errors.
- Runtime warnings: 0.
- Total entities created: 1,777 = 857 initial-WIP entities + 920 production-release entities.
- Total entities destroyed: 982. This is an entity count, not a shipped-workpiece count.
- Production release: 18,400 workpieces total; Left 12,000; Right 6,400.
- Weighted shipped output: 19,630 workpieces.
- End population: 795 entities, equivalent to 15,900 workpieces under the recorded quantity state.

The piece-count balance closes:

`17,130 initial WIP + 18,400 released = 19,630 shipped + 15,900 ending WIP = 35,530 workpieces`.

The entity-count balance also closes:

`1,777 created - 982 destroyed = 795 entities remaining`.

The difference between 982 destroyed entities and 19,630 shipped workpieces is expected: one of the destroyed entities represents the 10-workpiece W03-R tail, while the other 981 represent 20 workpieces each.

## Interpretation limits

This is a computational batch representation, not evidence that the original process physically moves or completes work in batches of 20. It preserves aggregate work content and piece totals, but hides within-batch completion order and timing. Entity-level queue counts, flow times, resource event timing, and fill rates therefore cannot be interpreted as piece-level results without a separate equivalence test. The 10-workpiece tail also has half the standard processing time under the current workload-scaling rule.

The user confirmed completion of the native close/reopen regression. The MCP statistics currently available for the reopened V0.7 model report the results above. Together, these checks cover initialization, release totals, weighted shipment count, aggregate work-content scaling, and total piece/entity conservation. They do not establish equivalence to the single-workpiece representation for detailed service-time distributions, queue dynamics, or author-reported VSM performance metrics.

## Persisted Version Status

V0.7 is saved as `VSM_V0.7_InitialWIPTable.spfx`, reopened, and regression-tested. V0.6 remains available as the one-workpiece-per-entity reference. V0.7 is the 20-workpiece computational-batch candidate; retain the interpretation limits above when comparing its queue, flow-time, and service results with the V0.6 reference.
