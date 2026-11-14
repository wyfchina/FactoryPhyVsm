# I1 Input Snapshot Manifest: VSM_V0.9

## Identity

- Snapshot ID: `VSM_I1_InputSnapshot_20261114_v1`
- Created: `2026-11-14`
- Frozen copies: `data/snapshots/VSM_I1_InputSnapshot_20261114_v1/`
- Decision owner and business reviewer: `Wu`
- Bound candidate model: `VSM_V0.9_ProductGroupAuditCandidate`
- Model file: `models/VSM_MichiganSteel_V0.9_ProductGroupAuditCandidate.spfx`
- Model SHA-256: `49197D44DA482F97B6B06E4A47D97931875AF6C4DA639C684D6FF8794B5363A8`
- Source PDF SHA-256: `75523E199982D165C480EF7F0407CFF4DBF6F26C441B14EEBF98559CCFF3C005`

The model binding identifies the V0.9 product-group audit candidate. The candidate has passed current-session deterministic regression, but its independent close/reopen regression and stochastic consumption of this snapshot remain open under Issues 06 and 08.

## Input files and hashes

| File | Purpose | SHA-256 |
|---|---|---|
| `data/processes.csv` | Process time, setup, availability, distribution, stream and failure parameters | `25555C859F4E6FA535DD275337EC8895AEEA626828F471C80D2AB45070DB121C` |
| `data/wip-initial.csv` | Initial WIP by position and product, including raw-material days | `5FEA6E6AF4E7839EA9B611E534CAF3370B84E1CD0C7E25A45E457448777CCF76` |
| `data/demand-calendar.csv` | Demand mix, workdays, shifts, effective hours, takt and transfer batch | `9460AC2B940927FF0AAB8CBB5ADC63D388DFF2A2BCB372D747798B48EB3031C5` |
| `assumptions-register.csv` | Source facts, project assumptions, implementation choices and verification ownership | `8FD1BBDB718308DDD673A4965E5DDD11B94EAF1D457726FBC827B767C0795D28` |

## Frozen conversion and implementation rules

- All source quantities remain in workpiece units.
- A standard computational entity represents 20 workpieces; a tail entity preserves its actual quantity. This abstraction is not a physical tray.
- Single-piece process time uses an exponential distribution with the source process time as its mean. A `q`-piece computational entity receives the sum of `q` independent single-piece samples.
- The master random seed is `20261114`; process-time streams are `PROC_P01` through `PROC_P05` and failure streams are `FAIL_P01` and `FAIL_P03`.
- Stamping uses `MTTF=5.6667 h`, `MTTR=1 h`; S. Weld #2 uses `MTTF=4 h`, `MTTR=1 h`. Failure and repair time accrue in effective operating hours. These produce target steady-state availabilities of 85% and 80% under the two-state exponential convention.
- I1 deterministic structural/conservation regression uses 306.6667 h, no warm-up, one run, and random sampling disabled. This is not the B0/B1 stochastic KPI contract.
- Raw-material `5 days` remains a VSM inventory metric; no raw-material entities are created.

## Quality checks

| Check | Expected result | Result |
|---|---:|---:|
| Monthly demand | 18,400 pieces | Pass |
| Daily demand | 920 pieces/day | Pass |
| Process value time | 188 seconds | Pass |
| Initial process WIP | 12,990 pieces | Pass |
| Initial finished goods | 4,140 pieces | Pass |
| Initial counted WIP | 17,130 pieces | Pass |
| W03-R source quantity | 850 pieces | Pass |
| L/R mix | 12,000 / 6,400 pieces | Pass |
| `processes.csv` unresolved distribution fields | 0 `TBD` values | Pass |
| Reliability parameter arithmetic | 85% / 80% target under selected convention | Pass |

## Acceptance boundary

This manifest closes the Issue 03 input-snapshot responsibility: source fields, units, transformations, implementation values, model identity, file hashes and quality checks are reproducible. It does not claim that the V0.9 model has consumed the stochastic fields, that observed availability has been measured, or that B0/B1 has passed. Those remain Issue 06–09 responsibilities.
