# System architecture

## Design rule

AURUM consists of two physically separated loops connected only by a qualified, cell-free
intermediate. The production loop contains donor-derived cells. The recovery loop contains the
gold-bearing process feed. No untreated process feed returns to the cell loop.

## Functional decomposition

| Module | Input | Output | Release criterion |
|---|---|---|---|
| M1 donor intake | Consented urine specimen and metadata | Coded specimen | Consent, chain of custody, acceptance screen |
| M2 cell bank | Coded specimen | Characterized urine-derived cell lot | Identity, viability, sterility, traceability |
| M3 production | Qualified cell lot and controlled medium | Conditioned medium | Batch record complete |
| M4 cell exclusion | Conditioned medium | Cell-free candidate secretome | No detectable viable production cells by qualified assay |
| M5 product qualification | Cell-free candidate | Released capture phase | Identity, activity, endotoxin/bioburden as applicable |
| M6 feed qualification | Independent industrial source | Characterized Au-bearing feed | Au speciation, matrix, hazards, chain of custody |
| M7 affinity capture | Released capture phase plus feed | Loaded phase plus depleted feed | Closed Au mass balance |
| M8 reduction/mineralization | Loaded phase | Particle-bearing stream | Au oxidation-state confirmation |
| M9 separation | Particle-bearing stream | Concentrate plus liquid residual | Recovery and residual assay |
| M10 external refining | Concentrate | Assayed product | Independent purity and mass report |

## Information architecture

Every batch receives immutable identifiers for donor material, cell lot, secretome lot, feed lot,
capture run, analytical sequence, and recovered product. A result is not promotable unless all
identifiers link and all blanks, controls, calibrations, and mass balances pass.

Minimum data record:

```text
run_id
scenario_schema_version
evidence_status
donor_material_code
cell_lot_id
secretome_lot_id
feed_lot_id
instrument_sequence_id
feed_volume_l
feed_gold_concentration_mg_l
gold_speciation_method
capture_phase_volume_l
measured_binding_capacity_mg_l
captured_gold_mg
refined_gold_mg
all_stage_residuals_mg
mass_balance_closure_fraction
control_results
deviation_ids
reviewer_signoff
```

Personal identifiers must remain in a separate access-controlled system and never enter process
analytics or this repository.

## Control strategy

### Production-loop controls

- cell identity and lot traceability;
- culture health and contamination status;
- secreted-product identity and concentration;
- absence of viable production cells in released product;
- lot-to-lot capture activity against a nonhazardous reference matrix.

### Recovery-loop controls

- feed gold concentration and chemical form;
- pH, redox potential, temperature, residence time, and competing ions;
- capture breakthrough and loading capacity;
- reduction state and particle-size distribution;
- residual gold in every liquid and solid output;
- cleaning verification and cross-batch carryover.

### Interlocks

1. M7 cannot receive material until both secretome and feed lots are released.
2. Any cell-exclusion failure quarantines the secretome lot.
3. Any analytical blank above its limit invalidates the sequence.
4. Mass-balance closure outside the predetermined interval blocks a recovery claim.
5. Unresolved hazardous-waste characterization blocks discharge or reuse.

## Failure modes

| Failure | Detection | Safe state |
|---|---|---|
| Secretome has no Au affinity | Matched-medium control and isotherm | Stop; do not proceed to scale claims |
| Apparent Au signal is contamination | Field/process blanks and lot tracing | Invalidate sequence and investigate source |
| Competing metals dominate | Multi-element mass balance | Reformulate or terminate candidate |
| Au remains ionic after “reduction” | Oxidation-state assay | Report adsorption only |
| Capacity collapses on reuse | Cycle-resolved capacity | Single-use classification or terminate |
| Viable cells enter recovery loop | Qualified cell-exclusion test | Quarantine and decontaminate |
| Gold is unaccounted for | Stage residual assay | Hold all outputs and reconcile |
| Model reports favorable economics from assumptions | Evidence-status check | Label as hypothesis; prohibit commercial claim |

## Scale-up principle

Scale is earned through dimensionless performance and closed mass balance, not by increasing
vessel size first. Required scale descriptors include capacity per unit secretome, selectivity
factor, conversion yield, capacity retention, volumetric productivity, energy per gram recovered,
and waste per gram recovered.

