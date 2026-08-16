# Techno-economic model

## Scope

The included model is a deterministic screening tool. It answers “what follows from these declared
assumptions?” It does not answer “will AURUM work?” and it does not optimize a wet-lab process.

## Batch mass balance

Let:

- \(V_f\): feed batch volume in L;
- \(C_{Au}\): assayed feed-gold concentration in mg/L;
- \(f_a\): accessible gold fraction;
- \(V_s\): cell-free capture-phase volume in L;
- \(q_s\): binding capacity in mg Au/L capture phase;
- \(f_s\): active capture-phase fraction;
- \(r\): capacity retained per reuse;
- \(n\): reuse index starting at zero;
- \(f_c\): affinity capture fraction;
- \(f_r\), \(f_h\), \(f_p\): reduction, harvest, and refining yields.

Then:

\[
m_{feed}=V_fC_{Au}
\]

\[
m_{accessible}=m_{feed}f_a
\]

\[
q_n=V_sq_sf_sr^n
\]

\[
m_{captured}=\min(m_{accessible}f_c,q_n)
\]

\[
m_{refined}=m_{captured}f_rf_hf_p
\]

Every subtraction is retained as an explicit residual stream. The model raises an internal error
if total accounted gold differs from feed gold by more than \(10^{-18}\) mg under its decimal
arithmetic context.

## Campaign calculation

Mean recovered gold per batch is calculated over the declared capture-phase reuse cycle. Annual
batches equal batches per day multiplied by operating days. Product mass is larger than contained
gold when product purity is below one:

\[
m_{product}=\frac{m_{Au}}{purity}
\]

Annual screening margin is:

\[
M = m_{Au,annual}P_{Au}
-N_b(E_bP_E+C_b)-C_{fixed}
\]

where \(P_{Au}\) is gold price, \(N_b\) is annual batches, \(E_b\) is energy per batch,
\(P_E\) is energy price, \(C_b\) is batch consumables, and \(C_{fixed}\) is annual fixed cost.

## Costs intentionally not inferred

The model accepts a compact fixed-cost term but does not pretend to know:

- donor recruitment, consent, screening, and cell-banking cost;
- cell-line engineering and characterization;
- culture facility, quality system, or analytical laboratory cost;
- feed acquisition or pretreatment;
- capture-medium production and purification;
- labor, maintenance, downtime, depreciation, taxes, insurance, or financing;
- refining fees, payable-metal deductions, or assay disputes;
- hazardous-waste treatment and disposal;
- regulatory, environmental, occupational, or transport compliance;
- capital expenditure and working capital.

A commercial analysis must model these explicitly. A positive `annual_screening_margin_usd` is not
a profit claim.

## Evidence discipline

- Values in `examples/reference_scenario.json` are synthetic.
- Use current, cited price data only for a time-stamped market scenario.
- Replace each yield with a distribution once replicated measurements exist.
- Preserve failed runs and downtime in pilot availability.
- Compare against nonbiological recovery baselines on the same feed.
- Report cost per gram of recovered gold and cost per liter of treated feed.
- Report environmental burdens per gram recovered; do not infer “green” from the word biological.

## CLI

```bash
aurum validate examples/reference_scenario.json
aurum run examples/reference_scenario.json --pretty
aurum sensitivity examples/reference_scenario.json \
  --concentration-mg-l 0.001 0.01 0.1 1 \
  --affinity 0.25 0.50 0.75 0.95
```

All decimal outputs are serialized as strings to prevent downstream conversion to imprecise binary
floating-point values.

