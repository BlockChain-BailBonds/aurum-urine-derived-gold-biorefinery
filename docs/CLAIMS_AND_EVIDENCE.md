# Claims and evidence ledger

This ledger prevents a plausible mechanism, a model output, and an experimental observation from
being presented as if they were equivalent.

## Evidence classes

- **E0 — physical law or authoritative reference:** stable boundary condition.
- **E1 — external biological precedent:** peer-reviewed result in another system.
- **E2 — AURUM analytical validation:** measurement system shown fit for purpose.
- **E3 — AURUM bench observation:** replicated integrated bench result.
- **E4 — AURUM pilot observation:** independently reviewed pilot result.
- **H — hypothesis:** proposed but not demonstrated.
- **X — excluded claim:** contradicted by the project boundary.

## Ledger

| ID | Claim | Class now | Required promotion evidence |
|---|---|---:|---|
| C-001 | Gold is element 79 | E0 | None |
| C-002 | Ordinary cell chemistry cannot transmute another element into gold | E0 | None |
| C-003 | Expandable human cells can be isolated from voided urine | E1 | Reproduce cell identity/expansion internally for E3 |
| C-004 | Certain microbial products interact with soluble gold and form particles | E1 | Not an AURUM performance claim |
| C-005 | A urine-derived human-cell secretome binds ionic gold above matrix controls | H | Preregistered, replicated, mass-balanced comparison |
| C-006 | The active fraction is molecularly identifiable | H | Fractionation/activity tracking plus orthogonal identity |
| C-007 | Captured ionic gold can be converted to Au(0) | H | Orthogonal oxidation-state and particle characterization |
| C-008 | The capture phase is selective in realistic mixed-ion feed | H | Multi-element selectivity study with full residual analysis |
| C-009 | The capture phase is reusable | H | Predetermined cycle test and retained-capacity interval |
| C-010 | The integrated process has favorable economics | H | Pilot mass/energy/waste data and reviewed cost basis |
| C-011 | Urine-derived cells create gold atoms | X | Claim is outside and incompatible with AURUM |
| C-012 | Example JSON values are experimental data | X | Examples are permanently labeled synthetic hypotheses |

## Result-labeling rules

1. `hypothesis` means one or more material performance inputs are assumed.
2. `bench-validated` requires gates G0–G5 in `VALIDATION_PLAN.md` and traceable underlying data.
3. `pilot-validated` requires G0–G7, an engineering run at declared scale, and independent review.
4. Model outputs inherit the weakest evidence status among their inputs.
5. A favorable economic output can never promote an evidence status.
6. Results with failed blanks, failed controls, or incomplete gold mass balance are invalid, not
   negative or positive.

## Language rules

Use:

- “recovered 3.2 mg of gold originally present in the feed”;
- “conditioned medium was associated with greater capture than the matched control”;
- “Au(0) was identified by [named orthogonal methods]”;
- “screening model under declared assumptions.”

Do not use:

- “the cells made gold”;
- “urine was converted into gold”;
- “proven” without a defined evidence level;
- “99% efficient” without numerator, denominator, uncertainty, and mass-balance closure;
- revenue projections that omit feed acquisition, refining, waste, labor, compliance, and capital.

