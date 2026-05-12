---
skill_id: transfection_v1
skill_name: Mammalian Cell Transfection Complete Workflow Skill
version: 1.0
method_family: gene_delivery
tags: [transfection, plasmid_dna, sirna, mrna, lipid_transfection, electroporation, reverse_transfection, forward_transfection, optimization, reporter_assay, cytotoxicity, gene_expression, knockdown, transgene_expression]
applies_to: [adherent_cells, suspension_cells, immortalized_cell_lines, primary_cells, plasmid_delivery, sirna_delivery, mrna_delivery]
does_not_apply_to: [lentiviral_packaging, stable_viral_transduction, in_vivo_gene_delivery, bacterial_transformation, plant_transformation, microinjection, embryo_manipulation]
risk_level: medium
bsl_level: "BSL-2 for human-derived material unless institutional assessment permits lower containment"
last_updated: 2026-03-16
source_protocol: SOP-TRANSFECTION-001
---

---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I transfect HEK293T cells," "my transfection efficiency is low," "why are my cells dying after transfection," "how much DNA should I use per well," "how do I deliver siRNA," "should I use lipid reagent or electroporation," "how do I set up reverse transfection," "my reporter signal is weak," "how long should I incubate transfection complexes," "how do I transfect suspension cells," "how do I optimize DNA:reagent ratio," "my cells look stressed after transfection," or any question about non-viral mammalian cell transfection workflow design, execution, QC, and troubleshooting. This skill covers the complete transfection workflow: cell preparation and seeding, nucleic acid QC, reagent preparation, forward transfection, reverse transfection, electroporation, post-transfection culture, endpoint timing, reporter-based optimization, and structured diagnostic rules for low delivery, cytotoxicity, poor knockdown, inconsistent expression, and contamination-like stress phenotypes after reagent exposure. This skill does NOT cover: lentiviral or retroviral production, stable viral transduction, bacterial transformation, plant transformation, embryo injection, or in vivo delivery. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| cell_type | enum: adherent / suspension | Growth modality of the target cell population |
| cell_line_name | string | Specific cell line or primary cell type (for example HEK293T, HeLa, U2OS, A549, CHO-K1, Jurkat, K562, THP-1, primary fibroblasts) |
| cargo_type | enum: plasmid_dna / sirna / mrna / cotransfection | Nucleic acid class being delivered |
| transfection_method | enum: lipid_forward / lipid_reverse / electroporation / polymer_reagent | Delivery approach selected for the experiment |
| workflow_goal | enum: transient_expression / knockdown / reporter_assay / optimization / troubleshooting | Primary experimental objective |
| assay_readout_time | string | Planned readout time after transfection (for example 24 h, 48 h, 72 h) |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| confluence_percent | int (0-100) | Cell density at the moment complexes were added |
| viability_percent | float (0-100) | Viability by dye exclusion or imaging after transfection |
| dna_concentration_ng_per_uL | float | DNA stock concentration from spectrophotometer or fluorometer |
| dna_a260_a280 | float | DNA purity ratio |
| dna_a260_a230 | float | DNA salt or solvent contamination indicator |
| sirna_stock_uM | float | siRNA stock concentration |
| reagent_name | string | Specific transfection reagent or electroporation kit used |
| dna_mass_per_well | string | DNA amount per well or per reaction |
| reagent_volume_per_well | string | Reagent volume per well or per reaction |
| dna_reagent_complex_time | string | Complex incubation time before addition to cells |
| complex_diluent | string | Buffer or medium used to form complexes |
| serum_present_during_complexing | enum: yes / no | Whether serum was present during complex formation |
| serum_present_during_delivery | enum: yes / no | Whether serum was present when complexes contacted cells |
| medium_change_time | string | Time from delivery to medium replacement |
| transfection_efficiency_percent | float (0-100) | Reporter-positive fraction or equivalent efficiency metric |
| knockdown_percent | float (0-100) | mRNA or protein knockdown level |
| incubator_temperature | float | Temperature during recovery |
| incubator_co2_percent | float | CO₂ during recovery |
| electroporation_program | string | Pulse code or custom electroporation setting if used |
| cell_density_cells_per_mL | float | Density at electroporation or suspension transfection |

---

## 3. WORKFLOW MODULES

### Module 1: CELL_PREPARATION_AND_SEEDING

**Preconditions:** Target cells are authenticated, free of mycoplasma, and in logarithmic growth. Complete medium and culture vessels are prepared. Passage history and doubling time are known or estimated from recent culture records.
**Pause point:** YES - cells can be seeded 18-24 h before forward transfection or used immediately in reverse-transfection formats. Do not hold trypsinized cells at room temperature longer than 15 min before seeding.

#### Steps:

1. Confirm culture health before transfection:
   - Adherent cells should show expected morphology and 90% or higher viability before seeding.
   - Suspension cells should be in single-cell suspension with minimal clumps and 90% or higher viability.
2. Select vessel and target cell number:
   - 96-well plate: 8 × 10^3 to 2 × 10^4 cells in 100 µL per well.
   - 24-well plate: 5 × 10^4 to 1.5 × 10^5 cells in 500 µL per well.
   - 6-well plate: 2 × 10^5 to 5 × 10^5 cells in 2 mL per well.
   - 10 cm dish: 2 × 10^6 to 5 × 10^6 cells in 10 mL.
3. Seed adherent cells to reach the recommended confluence at delivery:
   - Plasmid DNA lipid transfection: 60-80% confluence at complex addition.
   - siRNA lipid transfection: 30-60% confluence for rapidly dividing lines; 50-70% for slower lines.
   - mRNA lipid transfection: 50-70% confluence to reduce stress from rapid expression.
4. For suspension cells prior to electroporation:
   - Count cells and adjust to 1 × 10^6 to 2 × 10^7 cells/mL according to kit instructions.
   - Wash once in electroporation buffer or PBS if serum carryover must be minimized.
   - Centrifuge at 200 ×g, 20-25°C, 5 min before resuspension in electroporation buffer.
5. [CRITICAL] Use antibiotic-free medium during the transfection window for lipid and polymer reagents unless the validated protocol for that cell line and reagent explicitly permits antibiotics.
6. [BEGINNER TRAP] Do not transfect overgrown adherent cultures above 90% confluence. Contact inhibition reduces uptake and can alter promoter activity.
7. Record vessel type, seeding density, confluence target, and planned delivery time.

#### Exit Criteria (must ALL be true to proceed):
- Cells are healthy and in log-phase growth
- Seeding density matches the chosen vessel and cargo type
- Antibiotic status for the transfection window is defined
- Planned confluence or density at delivery has been recorded

---

### Module 2: NUCLEIC_ACID_AND_REAGENT_QC

**Preconditions:** DNA, siRNA, or mRNA stocks are available and labeled with concentration, date, and preparation method. Transfection reagent has not expired and has been stored at the recommended temperature.
**Pause point:** YES - nucleic acid aliquots can remain on ice for 1 h during setup. Do not leave mRNA or siRNA at 20-25°C longer than 30 min before complexing.

#### Steps:

1. Verify cargo identity and purity:
   - Plasmid DNA: confirm concentration and purity by fluorometer or spectrophotometer.
   - Acceptable plasmid A260/A280: >=1.8; values below 1.8 indicate protein or phenol contamination requiring repurification. No upper limit applies.
   - Acceptable plasmid A260/A230: >=1.8; values below 1.8 indicate solvent or salt carryover requiring repurification.
2. For plasmid DNA:
   - Use endotoxin-free preparation for primary cells, stem-cell-like cells, and toxicity-prone lines.
   - Preferred endotoxin level for sensitive transfection workflows: <0.1 EU/µg DNA when vendor certification or assay data are available.
   - Confirm supercoiled integrity by agarose gel if expression failures are recurrent.
3. For siRNA:
   - Prepare working aliquots at 5-20 µM in RNase-free buffer.
   - Avoid more than 3 freeze-thaw cycles.
4. For mRNA:
   - Use RNase-free tubes and tips.
   - Keep mRNA on ice during setup.
   - Confirm integrity by vendor QC or fragment analysis if available.
5. Inspect transfection reagent:
   - Mix by inversion 8-10 times if instructed by the vendor.
   - Do not vortex lipid reagents unless the manufacturer specifies vortexing.
   - Reagent-specific guidance:
     - Lipofectamine 2000: supports plasmid DNA and siRNA delivery; medium replacement at 4-6 h is often beneficial in toxicity-prone lines.
     - Lipofectamine 3000: supports plasmid DNA and cotransfection workflows; include the P3000-style enhancer only when the reagent system requires it for DNA delivery.
     - Lipofectamine RNAiMAX: use for siRNA or RNA delivery workflows; do not use RNAiMAX as the primary reagent for plasmid DNA transfection.
6. Select complex diluent:
   - Serum-free medium or vendor-provided buffer for lipid complexing.
   - Electroporation buffer supplied for the instrument kit for electroporation workflows.
7. [CRITICAL] Calculate total DNA, RNA, and reagent volumes per condition before pipetting. Prepare 10% excess complex volume to offset pipetting loss in multiwell formats.
8. [DO NOT] Combine plasmid DNA stocks in TE buffer with high EDTA if the reagent datasheet restricts chelators. Dilute into serum-free medium first if needed.

#### Exit Criteria (must ALL be true to proceed):
- Cargo concentration and purity have been checked
- Reagent storage status is acceptable
- Complexing diluent has been selected
- Working calculations for all conditions are complete

---

### Module 3: LIPID_OR_POLYMER_COMPLEX_FORMATION

**Preconditions:** Cells are prepared according to Module 1. Cargo QC is complete according to Module 2. Serum-free complexing diluent and low-retention tubes are ready.
**Pause point:** YES - lipid or polymer complexes can usually rest for 10-20 min at 20-25°C before addition to cells. Do not hold complexes longer than 30 min unless the reagent documentation specifies a longer window.

#### Steps:

1. Prepare separate tubes for nucleic acid and reagent.
2. Example plasmid DNA forward-transfection setup:
   - 24-well plate: dilute 0.5-1 µg DNA in 25-50 µL serum-free medium.
   - Add 1-3 µL lipid reagent to 25-50 µL serum-free medium in a separate tube.
   - Combine the diluted DNA and diluted reagent for a final complex volume of 50-100 µL.
   - For demanding targets, DNA may be raised to 1.5 µg with proportional reagent increase; see Section 6 parameter constraints.
3. Example siRNA setup:
   - 24-well plate: dilute siRNA to reach 5-100 nM final concentration in the well. Start at 10-25 nM; concentrations above 50 nM increase off-target risk.
   - Typical siRNA input: 0.25-1.5 µL of 10 µM stock into 25-50 µL diluent.
   - Dilute 1-3 µL lipid reagent separately, then combine.
4. Example 6-well plate plasmid setup:
   - Dilute 2-4 µg DNA in 125 µL serum-free medium.
   - Dilute 5-10 µL lipid reagent in 125 µL serum-free medium.
   - Combine to 250 µL and incubate at 20-25°C for 10-20 min.
5. For cotransfection:
   - Keep total nucleic acid mass constant across conditions.
   - Adjust vector ratios by mass or molar fraction and document the full composition.
6. For polymer-based reagents:
   - For PEI-based systems: starting N/P ratio of 5-10 is typical; for other polymer reagents, confirm the recommended range in the datasheet. N/P ratios above 20 often increase cytotoxicity without proportional efficiency gain.
   - Allow complexes to form at 20-25°C for 15-20 min unless the reagent uses immediate addition.
7. [CRITICAL] Add diluted reagent into diluted nucleic acid or follow the vendor-specified order exactly. Changing the order can alter particle size and reduce delivery.
8. [BEGINNER TRAP] Do not form complexes directly in complete medium containing serum unless the reagent is validated for serum-compatible complexing.
9. Label every complex tube with condition ID, cargo mass, reagent volume, and planned well assignment.

#### Exit Criteria (must ALL be true to proceed):
- Cargo and reagent were diluted separately before mixing when required
- Complex incubation time is defined
- Total cargo mass and reagent volume are recorded per condition
- Complexes have not exceeded the allowed hold time

---

### Module 4: FORWARD_AND_REVERSE_LIPID_TRANSFECTION

**Preconditions:** Complexes are ready. Cells are at the planned density. Plate map and controls are prepared.
**Pause point:** YES - reverse-transfection plates can be prepared immediately before cell seeding. Forward-transfection complexes should be added to cells without delay after the complexing window closes.

#### Steps:

1. Choose delivery format:
   - Forward transfection: add complexes to pre-seeded cells.
   - Reverse transfection: add complexes to wells first, then seed cells into the well.
2. Forward transfection procedure:
   - 24-well plate: add 50-100 µL complexes dropwise into 500 µL medium.
   - 6-well plate: add 200-250 µL complexes dropwise into 2 mL medium.
   - Swirl the plate in a front-back then left-right pattern 3 times each direction.
3. Reverse transfection procedure:
   - Dispense complexes into the empty well first.
   - Add cell suspension directly into the well to the final culture volume.
   - Example 24-well plate: 50-100 µL complexes + 400-450 µL cell suspension.
4. Include controls:
   - Mock transfection with reagent only.
   - Positive-control cargo such as GFP plasmid or validated siRNA.
   - Untreated cells.
5. Incubation after addition:
   - Return plates to 37°C, 5% CO₂ immediately.
   - Keep plates undisturbed for the first 2-6 h after forward transfection, matched to the planned medium-change window in Step 6.
6. Medium replacement:
   - Replace at 2-4 h for primary neurons, iPSC-derived cells, and immune cell lines.
   - Replace at 4-6 h for HeLa, A549, MCF-7, and other transformed lines showing mock toxicity.
   - Replace at 12-24 h for HEK293T, CHO-K1, and other robust lines when mock viability exceeds 90%.
7. [CRITICAL] Keep total well volume constant across comparison groups.
8. [DO NOT] Aspirate complexes from adherent cells earlier than 4 h unless the cell line requires early medium replacement, as listed in Step 6 for primary neurons, iPSC-derived cells, and immune cell lines, or acute toxicity is visible and the cell line is detaching.

#### Exit Criteria (must ALL be true to proceed):
- Delivery format is documented
- Positive, mock, and untreated controls are included
- Equal culture volume is maintained across conditions
- Post-delivery medium-change plan is defined

---

### Module 5: ELECTROPORATION_WORKFLOW

**Preconditions:** Electroporation-compatible cells are available at high viability. Instrument, cuvettes or nucleocuvette strips, and kit-specific buffer are ready. Electroporation program is selected.
**Pause point:** NO - once cells are resuspended in electroporation buffer, proceed without interruption. Do not hold cells in electroporation buffer at 20-25°C longer than 15 min before pulsing.

#### Steps:

1. Harvest cells and wash if serum or calcium carryover must be minimized.
2. Count cells and adjust to the kit-validated range:
   - Cell count per reaction: 0.5 × 10^6 to 2 × 10^6 for most 100 µL cuvette formats; scale proportionally for other volumes.
   - Cross-check with Module 1 Step 4 density guidelines and the instrument kit's cell-count recommendations.
3. Prepare cargo:
   - Plasmid DNA: 1-10 µg per reaction depending on cuvette volume and cell type.
   - siRNA: 50-200 pmol per reaction for most 100 µL cuvette formats, equivalent to approximately 500 nM-2 µM in the cuvette volume before dilution into recovery and culture medium; titrate downward from 100 pmol if cytotoxicity is observed.
   - mRNA: 0.5-5 µg per reaction; start at 1 µg and titrate downward, because excess mRNA increases innate immune activation risk.
4. Mix cells and cargo directly in electroporation buffer.
5. Transfer to the cuvette or strip without bubbles.
6. Apply the selected program and record the pulse code or voltage, pulse width, pulse count, and recovery solution volume.
7. If the electroporation kit supplies a recovery supplement or recovery medium:
   - Add the kit-specified recovery supplement volume immediately after pulsing.
   - Typical starting point for Lonza 4D or Amaxa Nucleofector formats: 500 µL per reaction.
   - Incubate the cuvette or strip at 37°C, 5% CO₂ for 10-15 min without transferring.
   - If no recovery medium is provided by the kit: proceed directly to the next step using pre-warmed antibiotic-free complete medium.
8. Recover cells immediately after pulsing:
   - Add 500 µL to 1 mL pre-warmed medium to small cuvettes or follow instrument kit volume.
   - Transfer cells into pre-warmed vessels containing complete medium.
9. Typical post-pulse handling:
   - 24-well plate: transfer into 500 µL to 1 mL medium per well.
   - 6-well plate: transfer into 2 mL medium per well.
10. [CRITICAL] Use low-retention tips and pipette slowly after pulsing. Electroporated cells are mechanically fragile for the first 10-30 min.
11. [BEGINNER TRAP] Do not reuse electroporation cuvettes or strips.

#### Exit Criteria (must ALL be true to proceed):
- Cell density and cargo mass are recorded per reaction
- Pulse settings are recorded
- Recovery supplement or recovery medium usage is recorded when supplied by the kit
- Post-pulse recovery occurred immediately
- No bubbles were visible in the reaction chamber before pulsing

---

### Module 6: POST_TRANSFECTION_CULTURE_AND_ENDPOINT_TIMING

**Preconditions:** Delivery is complete. Cells have returned to the incubator. Planned assays and timepoints are defined.
**Pause point:** YES - cells may require 6-72 h recovery depending on cargo type and assay. Do not evaluate expression or knockdown before the minimum biologically meaningful interval for the readout.

#### Steps:

1. Define the first assessment window:
   - Plasmid reporter expression: 16-24 h initial check.
  - Protein overexpression endpoint: 24-48 h for protein overexpression studies with moderate turnover.
   - siRNA mRNA knockdown: 24-48 h.
   - siRNA protein knockdown: 48-96 h depending on protein half-life.
  - mRNA expression: first detectable at 2-6 h; peak expression typically at 6-12 h; signal declines after 24 h for most unmodified mRNA reporters.
2. Inspect morphology at 4-6 h and 24 h post-delivery.
3. Replace medium if cells appear stressed or if the reagent protocol uses short-exposure transfection.
4. For plasmid expression studies:
   - Collect fluorescence or luminescence readout at 24 h and 48 h when unsure of kinetics.
5. For knockdown studies:
   - Harvest RNA at 24-48 h.
   - Harvest protein at 48-96 h depending on turnover.
6. Record both efficiency and viability:
   - Reporter-positive fraction or knockdown percent.
   - Viability by trypan blue, ATP assay, or imaging.
7. [CRITICAL] Compare transfected and control wells at the same timepoint and under identical acquisition settings.
8. [DO NOT] Interpret low reporter signal as low transfection efficiency unless plasmid sequence, promoter choice, and assay timing are compatible with the cell line.

#### Exit Criteria (must ALL be true to proceed):
- Endpoint timing matches cargo biology
- Morphology and viability have been assessed
- Controls are measured at the same timepoint as experimental conditions
- Efficiency metric and viability metric are both recorded

---

### Module 7: REPORTER_BASED_OPTIMIZATION

**Preconditions:** A reporter cargo or validated assay for delivered cargo is available. At least one adjustable variable has been selected for optimization.
**Pause point:** YES - optimization matrices can be split across multiple plates on the same day or repeated on consecutive days if cell seeding density is held constant.

#### Steps:

1. Optimize only one or two variables at a time:
   - DNA mass.
   - Reagent volume.
   - Cell density.
   - Complexing time.
   - Medium-change timing.
2. Example 24-well plasmid optimization matrix:
   - DNA: 0.5 µg, 0.75 µg, 1.0 µg.
   - Lipid reagent: 1 µL, 2 µL, 3 µL.
3. Example siRNA optimization matrix:
   - Final siRNA concentration: 5 nM, 10 nM, 25 nM, 50 nM, 100 nM.
   - Lipid reagent: 0.75 µL, 1.5 µL, 2.5 µL per 24-well condition.
4. Define the ranking metric before starting:
   - Efficiency only for reporter screening.
   - Efficiency normalized to viability for production experiments.
5. Use at least triplicate wells for each optimization point if the readout is plate-based.
6. Record the best-performing condition and repeat it on a separate day for confirmation.
7. [CRITICAL] Do not compare conditions across plates unless plate layout, cell density, incubation time, and acquisition settings are matched.
8. Freeze the optimization result into a written cell-line-specific transfection setup after confirmation.

#### Exit Criteria (must ALL be true to proceed):
- Variables under test are explicitly defined
- Replicates are included for comparison
- Ranking metric is defined before analysis
- Best condition has a confirmation run planned or completed

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: lipid_transfection
CONDITION: Reporter-positive cells are <20% at 24 h, but viability remains ≥85%
DIAGNOSIS: Delivery efficiency is low without overt toxicity
CONFIDENCE: medium
LIKELY_CAUSES:
  - DNA:reagent ratio is suboptimal
  - Cell confluence was outside the efficient range
  - Complexes were held too long before addition
  - Promoter is weak in the target cell line
DISTINGUISH:
  - If viability is high and morphology is normal, uptake failure is more likely than toxicity
  - Compare a GFP positive-control plasmid against the test plasmid; if GFP works and the test plasmid does not, construct design or promoter choice is implicated
  - Check whether efficiency rises when DNA mass and reagent volume are optimized in a matrix
IMMEDIATE_FIX:
  - Run a 3 × 3 DNA:reagent optimization matrix
  - Repeat at 60-80% confluence for plasmid lipid transfection
  - Use a validated positive-control plasmid in the same run
PREVENTION: Establish a cell-line-specific DNA:reagent ratio and confluence target; validate new plasmid constructs with a positive-control cargo in parallel

---

### RULE DX-002
STAGE: lipid_transfection
CONDITION: Viability falls below 70% within 24 h of complex addition
DIAGNOSIS: Transfection-associated cytotoxicity
CONFIDENCE: high
LIKELY_CAUSES:
  - Excess reagent volume
  - Excess cargo mass
  - Primary neurons, iPSC-derived cells, immune cell lines, or mock-toxicity-prone transformed lines remained exposed too long before medium replacement
  - Antibiotics present during transfection
DISTINGUISH:
  - Mock-transfected cells that also die implicate the reagent rather than the cargo
  - If toxicity improves after a 2-6 h medium change selected by cell class, exposure duration is a major factor
  - If toxicity is strongest in high-reagent wells and weak in low-reagent wells, reagent dose is the primary driver
IMMEDIATE_FIX:
  - Reduce reagent volume by 25-50%
  - Reduce DNA mass or siRNA concentration by 25-50%
  - Replace medium at 2-4 h for primary neurons, iPSC-derived cells, and immune cell lines, or at 4-6 h for transformed lines showing mock toxicity
  - Remove antibiotics during the transfection window
PREVENTION: Start optimization from the lower reagent volume; include mock-transfection controls in every new setup

---

### RULE DX-003
STAGE: nucleic_acid_qc
CONDITION: Multiple plasmids fail to express in the same cell line despite normal cell health
DIAGNOSIS: DNA quality problem
CONFIDENCE: medium
LIKELY_CAUSES:
  - Endotoxin contamination
  - Salt or ethanol carryover from plasmid prep
  - Nicked or linearized plasmid predominates
DISTINGUISH:
  - A260/A230 below 1.8 indicates salt or organic carryover requiring repurification
  - Endotoxin-sensitive cells often show low efficiency with modest toxicity
  - Agarose gel showing broad slow-migrating forms suggests degraded or nicked DNA
IMMEDIATE_FIX:
  - Use endotoxin-free plasmid prep
  - Re-precipitate or repurify DNA
  - Confirm integrity on gel before repeat transfection
PREVENTION: Use endotoxin-free prep for primary cells, stem-cell-like cells, and toxicity-prone lines; record purity ratios for each DNA batch used in transfection

---

### RULE DX-004
STAGE: assay_timing
CONDITION: Reporter signal is weak at 12 h post-transfection
DIAGNOSIS: Readout collected too early
CONFIDENCE: high
LIKELY_CAUSES:
  - Promoter-driven expression has not peaked
  - Protein maturation time is incomplete
  - Cargo type requires longer recovery before readout
DISTINGUISH:
  - Signal that increases markedly between 12 h and 24 h indicates timing rather than failed delivery
  - mRNA delivery often peaks earlier than plasmid DNA; compare timing to the cargo type
  - Fluorescent proteins with slower maturation lag behind luciferase readouts
IMMEDIATE_FIX:
  - Reassess at 24 h and 48 h
  - Match readout timing to cargo type and protein maturation kinetics
PREVENTION: Define assay windows before transfection; use known kinetics for the reporter and target cell line

---

### RULE DX-005
STAGE: sirna_transfection
CONDITION: Reporter uptake is acceptable, but target knockdown is <50% at 48 h
DIAGNOSIS: Functional knockdown failure despite delivery
CONFIDENCE: medium
LIKELY_CAUSES:
  - siRNA sequence has low potency
  - Protein half-life is long
  - mRNA harvest or protein harvest was mistimed
  - siRNA concentration was below the functional range
DISTINGUISH:
  - qPCR knockdown with weak protein knockdown suggests long protein half-life rather than delivery failure
  - A validated positive-control siRNA that succeeds in the same run argues against reagent failure
  - Increasing siRNA from 5 nM to 25 nM with improved knockdown indicates dose-limited activity
IMMEDIATE_FIX:
  - Test 3 siRNA concentrations and at least 2 siRNA sequences
  - Harvest protein at 72-96 h if the target is stable
  - Confirm mRNA depletion by qPCR at 24-48 h
PREVENTION: Use validated siRNA pools for initial optimization and align endpoint timing with target turnover

---

### RULE DX-006
STAGE: complex_formation
CONDITION: Complexes appear cloudy, stringy, or visibly aggregated before addition
DIAGNOSIS: Improper complex formation
CONFIDENCE: high
LIKELY_CAUSES:
  - Mixing order was incorrect
  - Salt concentration in the diluent was too high
  - Complexes were held too long
DISTINGUISH:
  - Freshly prepared complexes in serum-free medium that stay clear indicate the previous diluent or order was the problem
  - Aggregation before contact with cells points to a formulation issue rather than a cell issue
  - If only one reagent lot aggregates, lot quality may be compromised
IMMEDIATE_FIX:
  - Reprepare complexes in fresh serum-free diluent
  - Follow the vendor-specified order exactly
  - Add complexes within 10-20 min of formation
PREVENTION: Use low-salt diluent and a timed complexing workflow; label tubes with mix order for multistep setups

---

### RULE DX-007
STAGE: electroporation
CONDITION: Electroporated cells show severe death immediately after pulse
DIAGNOSIS: Electroporation setting is too harsh or buffer handling is poor
CONFIDENCE: high
LIKELY_CAUSES:
  - Pulse voltage or width is excessive
  - Cell density is outside the validated range
  - Bubbles were present in the cuvette
  - Cells remained too long in electroporation buffer before pulse
DISTINGUISH:
  - Immediate post-pulse death implicates the pulse or buffer conditions rather than delayed transgene toxicity
  - Arc marks or visible sparking implicate bubbles or salt carryover
  - A lower-energy program that restores viability indicates a pulse-setting problem
IMMEDIATE_FIX:
  - Drop to the next lower-energy validated program
  - Remove bubbles before pulsing
  - Shorten time in electroporation buffer to less than 15 min
PREVENTION: Validate one program per cell line and cargo type; keep post-harvest timing consistent

---

### RULE DX-008
STAGE: reverse_transfection
CONDITION: Reverse transfection performs worse than forward transfection in the same cell line
DIAGNOSIS: Cell attachment or settling issue during reverse setup
CONFIDENCE: medium
LIKELY_CAUSES:
  - Cells were seeded too sparsely
  - Cells were stressed from trypsinization or prolonged suspension
  - Reverse format is not optimal for the cell line
DISTINGUISH:
  - Poor attachment in reverse-transfection wells but not forward-transfection wells indicates the format is the variable
  - If cells settle unevenly, well-to-well variability increases
  - Some epithelial lines improve with reverse transfection, while fragile primary cells often do not
IMMEDIATE_FIX:
  - Increase seeding density by 20-30%
  - Minimize time between harvest and seeding
  - Compare forward and reverse formats side by side with identical complex ratios
PREVENTION: Choose format based on cell-line validation rather than convenience alone

---

### RULE DX-009
STAGE: post_transfection_culture
CONDITION: Cells detach 6-18 h after transfection while medium remains clear
DIAGNOSIS: Reagent stress, cargo overload, or medium incompatibility
CONFIDENCE: medium
LIKELY_CAUSES:
  - Reagent exposure is too long
  - DNA mass is too high
  - Serum-free condition was extended beyond the validated window
DISTINGUISH:
  - Mock wells that detach point to reagent exposure
  - DNA-bearing wells that detach more than mock wells implicate cargo overload
  - Recovery after early medium replacement indicates medium incompatibility rather than contamination
IMMEDIATE_FIX:
  - Replace medium at 4-6 h
  - Lower DNA mass or reagent volume
  - Restore serum-containing medium earlier
PREVENTION: Use 2-4 h replacement for primary neurons, iPSC-derived cells, and immune cell lines, and 4-6 h replacement for transformed lines showing mock toxicity; document detachment timing relative to medium replacement

---

### RULE DX-010
STAGE: assay_design
CONDITION: Transfection efficiency varies widely between replicates on the same plate
DIAGNOSIS: Setup inconsistency or uneven cell distribution
CONFIDENCE: medium
LIKELY_CAUSES:
  - Uneven seeding density
  - Inconsistent pipetting of complexes
  - Plate edge evaporation
  - Complexes settled during dispensing
DISTINGUISH:
  - Edge wells performing differently from inner wells implicate evaporation
  - Adjacent wells with alternating high and low signal implicate pipetting inconsistency
  - Imaging before transfection that shows uneven density indicates the problem started at seeding
IMMEDIATE_FIX:
  - Mix cell suspension before and during seeding
  - Dispense complexes in the same order and timing for every row
  - Use inner wells for experimental conditions and fill perimeter wells with PBS or medium
PREVENTION: Standardize plate map and pipetting order; use multichannel pipettes where practical for plate-based assays

---

### RULE DX-011
STAGE: construct_design
CONDITION: One plasmid expresses strongly but another plasmid fails in the same transfection run
DIAGNOSIS: Construct-specific problem
CONFIDENCE: high
LIKELY_CAUSES:
  - Promoter is weak in the cell line
  - Insert orientation or sequence integrity is wrong
  - Plasmid size is much larger and reduces uptake or expression
DISTINGUISH:
  - A GFP control that succeeds in the same wells shows the reagent and cell state are adequate
  - Restriction digest or sequencing abnormalities implicate the construct
  - Large plasmids above 10 kb often transfect less efficiently than small reporter plasmids
IMMEDIATE_FIX:
  - Confirm construct by sequencing or digest
  - Compare with an expression-positive control plasmid using the same backbone or promoter
  - Increase endpoint timing if the construct is large and expression is delayed
PREVENTION: Validate every new construct before functional interpretation; track plasmid size and promoter compatibility during assay design

---

### RULE DX-012
STAGE: medium_handling
CONDITION: Transfection efficiency drops sharply after switching serum lot or medium formulation
DIAGNOSIS: Medium-dependent shift in transfection performance
CONFIDENCE: medium
LIKELY_CAUSES:
  - Serum lot alters membrane tolerance or growth rate
  - Medium supplement change shifts cell physiology
  - Antibiotics or extra additives were reintroduced during the transfection window
DISTINGUISH:
  - Growth and morphology changes that coincide with the new lot suggest a media effect
  - Restoring the old serum lot or medium restores performance if the media change is causal
  - A mock-only viability drop after media switch implicates medium rather than the cargo
IMMEDIATE_FIX:
  - Compare old and new serum lots side by side for one transfection cycle
  - Remove additives not required for the transfection interval
  - Reoptimize DNA:reagent ratio if the medium change is permanent
PREVENTION: Requalify transfection conditions when serum lot or medium formulation changes

---

### RULE DX-013
STAGE: mrna_transfection
CONDITION: mRNA-transfected cells show rapid stress signaling, reduced viability, or weak expression despite prompt uptake
DIAGNOSIS: Innate immune activation after mRNA delivery
CONFIDENCE: medium
LIKELY_CAUSES:
  - Excess mRNA mass per reaction
  - mRNA chemistry lacks modifications that reduce innate sensing
  - Cell type is highly responsive to cytosolic RNA
  - Recovery timing or medium conditions amplify stress after delivery
DISTINGUISH:
  - Reporter expression may appear early, then collapse as viability or metabolic state worsens
  - mRNA conditions can perform worse than plasmid conditions in the same cells even when the delivery reagent is unchanged
  - Lowering mRNA mass from 5 µg toward 1 µg with improved viability and equal or better signal supports this diagnosis
IMMEDIATE_FIX:
  - Reduce mRNA input and repeat at 0.5 µg, 1 µg, and 2 µg per reaction
  - Replace medium at 4-6 h if the protocol allows short-exposure recovery
  - Use nucleoside-modified or vendor-optimized mRNA chemistry when available
PREVENTION: Start mRNA electroporation or lipid delivery at the lower end of the mass range; optimize mRNA dose separately from plasmid DNA dose

---

### RULE DX-014
STAGE: cotransfection
CONDITION: In a cotransfection run, one plasmid expresses at expected levels but a second co-delivered plasmid shows markedly lower or absent signal compared with its single-plasmid control
DIAGNOSIS: Competitive exclusion or mass-ratio imbalance in cotransfection
CONFIDENCE: medium
LIKELY_CAUSES:
  - Total DNA mass is not equalized across groups
  - One plasmid dominates complex formation due to size or charge differences
  - Empty-vector carrier was omitted, causing unequal total nucleic acid per well
DISTINGUISH:
  - Each plasmid should be run alone in parallel to confirm individual expression
  - If both fail when co-delivered but succeed alone, total DNA overload may reduce performance of both constructs
  - If only the smaller or weaker-promoter plasmid fails in co-delivery, ratio imbalance or competitive exclusion is the likely driver
IMMEDIATE_FIX:
  - Add empty vector to the lower-ratio condition to equalize total DNA mass
  - Reduce the dominant plasmid mass and re-run the cotransfection matrix
  - Confirm that the weaker plasmid expresses in its single-plasmid control before attributing failure to cotransfection competition
PREVENTION: Pre-define the total DNA mass per well; add empty vector whenever any plasmid is below its single-transfection amount; document the full mass composition for every cotransfection condition

---

## 5. RISK RULES

### Risk Matrix (RM-001 to RM-024)

#### RISK RM-001
STAGE: cell_preparation
ITEM: Transfecting cells outside log-phase growth
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Confluence or suspension density recorded before delivery
MITIGATION: Seed cells to 60-80% confluence for plasmid lipid transfection, 30-60% for siRNA lipid transfection in rapidly dividing lines, and validated density range for suspension workflows

---

#### RISK RM-002
STAGE: nucleic_acid_qc
ITEM: Endotoxin-contaminated plasmid DNA
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: DNA preparation method, endotoxin-free status, and endotoxin certification or assay result are recorded when available
MITIGATION: Use endotoxin-free plasmid prep for primary cells, stem-cell-like cells, and toxicity-prone lines; preferred endotoxin level is <0.1 EU/µg DNA for sensitive workflows; discard batches associated with repeated toxicity or low expression

---

#### RISK RM-003
STAGE: reagent_handling
ITEM: Repeated freeze-thaw of siRNA or mRNA
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Aliquot count and freeze-thaw history recorded
MITIGATION: Aliquot RNA cargo on first thaw; discard aliquots after 3 freeze-thaw cycles

---

#### RISK RM-004
STAGE: complex_formation
ITEM: Incorrect order of reagent mixing
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Complexing order written into the worksheet
MITIGATION: Follow vendor-specified order for each reagent; train operators to use the same order every time

---

#### RISK RM-005
STAGE: complex_formation
ITEM: Serum carryover during complex formation
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Complexes prepared in serum-free diluent unless the reagent permits serum-compatible complexing
MITIGATION: Use serum-free diluent for complex formation; prepare fresh diluent aliquots at room temperature before setup

---

#### RISK RM-006
STAGE: lipid_transfection
ITEM: Excess lipid reagent volume causing toxicity
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Mock-transfection viability compared with untreated control
MITIGATION: Start from the lower reagent volume in an optimization matrix; replace medium at 2-4 h for primary neurons, iPSC-derived cells, and immune cell lines, or at 4-6 h for transformed lines showing mock toxicity

---

#### RISK RM-007
STAGE: lipid_transfection
ITEM: Excess DNA mass causing overload and promoter artifacts
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: DNA mass per well recorded and held constant across comparable groups
MITIGATION: Use the lowest DNA mass that achieves interpretable expression; keep total DNA mass constant in cotransfection by balancing with empty vector

---

#### RISK RM-008
STAGE: cell_preparation
ITEM: Antibiotics present during transfection window
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Medium composition logged for the 24 h transfection interval
MITIGATION: Use antibiotic-free medium during complex exposure and early recovery unless a validated reagent protocol states otherwise for the same cell line

---

#### RISK RM-009
STAGE: assay_design
ITEM: Promoter mismatch with target cell line
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Positive-control construct with matched promoter used in the same cell line
MITIGATION: Use CMV, EF1a, CAG, or cell-line-validated promoters based on prior evidence; compare promoter choices when expression is weak

---

#### RISK RM-010
STAGE: reverse_transfection
ITEM: Poor cell attachment after reverse setup
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Cell attachment assessed 4-6 h after seeding
MITIGATION: Increase seeding density by 20-30% and reduce time between harvest and plating

---

#### RISK RM-011
STAGE: electroporation
ITEM: Arc formation from bubbles or salt carryover
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: No visible bubbles in cuvette; wash steps remove high-salt medium before pulsing
MITIGATION: Tap cuvette to release bubbles; use kit-specific buffer; limit serum carryover

---

#### RISK RM-012
STAGE: electroporation
ITEM: Overly harsh pulse program
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Viability assessed within 1 h post-pulse
MITIGATION: Use cell-line-validated programs; move to the next lower-energy program if immediate death is excessive

---

#### RISK RM-013
STAGE: post_transfection_culture
ITEM: Delayed medium replacement in early-change cell classes
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Medium change time recorded
MITIGATION: Replace medium at 2-4 h after lipid delivery for primary neurons, iPSC-derived cells, and immune cell lines, or at 4-6 h for transformed lines showing mock toxicity

---

#### RISK RM-014
STAGE: assay_timing
ITEM: Readout collected before biologically meaningful expression or knockdown window
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Planned readout time matches cargo type and target turnover
MITIGATION: Use 16-24 h for early reporter checks, 24-48 h for plasmid expression, 24-48 h for siRNA mRNA readouts, and 48-96 h for protein knockdown

---

#### RISK RM-015
STAGE: plate_handling
ITEM: Plate edge evaporation affecting efficiency
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Edge wells compared with inner wells for variability
MITIGATION: Fill perimeter wells with PBS or medium and use inner wells for key conditions

---

#### RISK RM-016
STAGE: optimization
ITEM: Changing multiple variables at once
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Optimization worksheet lists one or two variables only
MITIGATION: Change DNA mass and reagent volume first; hold cell density, timing, and medium conditions constant

---

#### RISK RM-017
STAGE: cotransfection
ITEM: Unequal total DNA mass between groups
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Total DNA mass per well is identical across groups
MITIGATION: Use empty vector to equalize total DNA mass in every cotransfection condition

---

#### RISK RM-018
STAGE: reagent_handling
ITEM: Complexes held too long before addition
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Complex start time and add-to-cell time recorded
MITIGATION: Add complexes within 10-20 min of formation unless the reagent has a validated longer hold window

---

#### RISK RM-019
STAGE: data_acquisition
ITEM: Comparing fluorescence images with different exposure settings
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Exposure and gain are identical across comparable groups
MITIGATION: Lock acquisition settings after control adjustment; save raw files before brightness modification

---

#### RISK RM-020
STAGE: cell_health
ITEM: Mycoplasma contamination reducing transfection performance
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Mycoplasma test within the past 30 days is negative
MITIGATION: Test before optimization campaigns and before publication-grade transfection experiments

---

#### RISK RM-021
STAGE: construct_design
ITEM: Large plasmid size reducing delivery efficiency
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Plasmid size documented for every construct
MITIGATION: Expect lower delivery for constructs above 10 kb; increase optimization attention or move to electroporation for difficult large constructs

---

#### RISK RM-022
STAGE: suspension_handling
ITEM: Cell clumping before electroporation or suspension transfection
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Single-cell suspension confirmed before delivery
MITIGATION: Filter through a 40 µm strainer or pipette to disperse clumps before counting and pulsing

---

#### RISK RM-023
STAGE: documentation
ITEM: Reagent lot and ratio not recorded
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Worksheet includes reagent lot, cargo lot, DNA:reagent ratio, and medium-change time
MITIGATION: Use a transfection worksheet template for every run; do not rely on memory for optimization history

---

#### RISK RM-024
STAGE: mrna_transfection
ITEM: Excess mRNA input causing innate immune activation and expression collapse
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: mRNA mass per reaction and post-delivery viability are recorded together for each condition
MITIGATION: Start at 0.5-1 µg mRNA per reaction and titrate upward only if expression remains below the target while viability stays acceptable; use modified mRNA or vendor-optimized chemistry for responsive cell types

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: optimization
ITEM: Low-efficiency conclusions drawn without a positive-control cargo
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Positive-control plasmid or validated siRNA is included in the same run
MITIGATION: (1) Repeat the run with a validated positive-control cargo. (2) Separate reagent failure from construct-specific failure before redesigning the experiment. (3) Use the control to define the upper performance bound for the cell line.

---

#### RISK CF-002
STAGE: data_acquisition
ITEM: Quantitative expression comparison performed with mismatched acquisition settings
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Imaging metadata or plate-reader settings match across all groups being compared
MITIGATION: (1) Reacquire all groups under one setting set. (2) Exclude mismatched files from quantitative analysis. (3) Save acquisition presets before measuring the plate or imaging wells.

---

#### RISK CF-003
STAGE: cell_health
ITEM: Transfection optimization attempted in mycoplasma-positive or untested cells
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm mycoplasma status before optimization or mechanistic experiments
MITIGATION: (1) Test all active lines before optimization campaigns. (2) Discard or treat contaminated cultures before interpreting transfection failures. (3) Do not publish transfection-based conclusions from untested cultures.

---

## 6. PARAMETER CONSTRAINTS

### Cell Density

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Adherent confluence at plasmid lipid addition | 50% | 60-80% | 85% | <50%: uptake may drop from low cell number; >85%: contact inhibition reduces performance |
| Adherent confluence at siRNA lipid addition for rapidly dividing lines | 30% | 30-60% | 75% | >75%: knockdown reproducibility often drops |
| Adherent confluence at siRNA lipid addition for slow-dividing or primary lines | 50% | 50-70% | 80% | <50%: cell number may be too low for reliable knockdown readout |
| Suspension density before electroporation | 1 × 10^6 cells/mL | 5 × 10^6 to 1 × 10^7 cells/mL | 2 × 10^7 cells/mL | Outside kit range: viability and delivery can collapse |

### Cargo Input

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| DNA mass per 24-well lipid transfection | 0.25 µg | 0.5-1.0 µg | 1.5 µg | >1.5 µg: overload and toxicity risk increase; if 1.5 µg is used, scale reagent proportionally and monitor mock viability closely |
| DNA mass per 6-well lipid transfection | 1 µg | 2-4 µg | 5 µg | >5 µg: excess DNA often lowers viability |
| siRNA final concentration | 5 nM | 10-25 nM | 100 nM | >50 nM: off-target risk rises; >100 nM: repeat optimization instead of increasing further |
| mRNA mass per 24-well reaction | 0.1 µg | 0.25-1.0 µg | 2.0 µg | >2.0 µg: rapid overexpression stress can increase |

### Complex Formation

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Lipid complex incubation | 5 min | 10-20 min | 30 min | >30 min: aggregation and activity loss risk increase |
| Polymer complex incubation | 10 min | 15-20 min | 30 min | >30 min: complex behavior can drift |
| Serum during complexing | 0% | 0% | 10% | Use serum only if the reagent documentation validates serum-compatible complexing |
| Medium change after early-change lipid delivery | 2 h | 2-6 h | 12 h | >12 h in primary neurons, iPSC-derived cells, immune cell lines, or mock-toxicity-prone transformed lines: toxicity risk increases |

### Electroporation

| Parameter | Value / Range | Notes |
|-----------|--------------|-------|
| Cell hold in electroporation buffer before pulse | <15 min | Longer hold lowers viability in primary and mock-toxicity-prone cells |
| Recovery supplement or recovery medium incubation after pulse | 10-15 min when supplied by the kit | Incubate in the cuvette or strip at 37°C, 5% CO₂ before transfer |
| Post-pulse transfer | within 5 min | Delayed transfer prolongs buffer stress |

### Readout Timing

| Parameter | Minimum | Optimal | Maximum | Notes |
|-----------|---------|---------|---------|-------|
| Plasmid reporter first check | 16 h | 24 h | 48 h | Use 48 h if expression is delayed |
| siRNA mRNA readout | 24 h | 24-48 h | 72 h | Later windows may add indirect effects |
| siRNA protein readout | 48 h | 48-96 h | 120 h | Match the window to protein half-life |
| mRNA expression readout | 2 h | 6-12 h | 24 h | First signal can appear at 2-6 h; signal often declines after 24 h for unmodified reporters |

---

## 7. QC GATES

### QC Gate 1: Before Complex Formation

PASS criteria (ALL must be true):
  - Cells are healthy and within the target confluence or density range
  - Cargo concentration and purity were checked
  - Transfection reagent is within expiry and has been stored at the required temperature
  - Antibiotic status for the transfection window is defined
  - Plate map or reaction map includes controls

ACTION if FAIL: If cells are outside density range, reseed or postpone the run. If DNA purity is poor, repurify before use. If the reagent is expired or storage history is uncertain, replace it before complex formation. If controls are missing, redesign the plate map before forming complexes.

---

### QC Gate 2: After Complex Formation

PASS criteria (ALL must be true):
  - Cargo and reagent amounts are recorded
  - Complexes were incubated within the allowed time window
  - Complexes are free of visible aggregation
  - Diluent matches the reagent requirements

ACTION if FAIL: If complexes aggregate, discard and reprepare in fresh serum-free diluent. If incubation exceeded 30 min, reprepare. If reagent order was uncertain, restart with written mixing order.

---

### QC Gate 3: After Delivery

PASS criteria (ALL must be true):
  - Delivery format or pulse program is recorded
  - Positive, mock, and untreated controls are present
  - Cells returned to 37°C, 5% CO₂ immediately after delivery
  - Medium-change timing is documented

ACTION if FAIL: If controls are missing, repeat the run before interpreting efficiency. If recovery was delayed after electroporation, treat the run as non-comparable. If medium-change timing was missed, document the deviation and monitor viability closely.

---

### QC Gate 4: Before Endpoint Analysis

PASS criteria (ALL must be true):
  - Endpoint timing matches cargo biology
  - Viability has been assessed
  - Readout settings are locked across comparable groups
  - Raw images or raw plate-reader exports are saved

ACTION if FAIL: If timing is too early, extend the assay window. If acquisition settings differ, reacquire before quantitative comparison. If viability data are absent, add a viability readout before ranking conditions.

---

### QC Gate 5: Optimization Confirmation

PASS criteria (ALL must be true):
  - Best-performing condition is defined by a preset ranking metric
  - Best condition was repeated on a separate day or has a confirmation run scheduled
  - Reagent lot, cargo lot, and ratio are documented
  - Mycoplasma status is current

ACTION if FAIL: If the best condition has only one run, repeat before locking the protocol. If documentation is incomplete, the condition cannot be treated as finalized. If mycoplasma status is overdue, test before further optimization.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified transfection issue and root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in the diagnosis based on controls and observed metrics |
| recommended_actions | list[string] | Ordered correction list with the first recovery action first |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass or fail status for each QC gate |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters linked to the relevant diagnostic rule |
| protocol_section_reference | string | Section of SOP-TRANSFECTION-001 relevant to the issue |
| delivery_status | enum: efficient / low_efficiency / toxic / indeterminate | Summary of the delivery outcome |
| assay_timing_status | enum: too_early / on_time / too_late / unknown | Timing interpretation for the selected readout |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | User needs plating density planning, culture health troubleshooting, or mycoplasma control before transfection |
| immunofluorescence_v1 | User wants to measure transgene localization or post-transfection marker expression by microscopy |
| western_blot_v1 | User needs post-transfection protein expression or knockdown confirmation |
| rt_qpcr_v1 | User needs mRNA knockdown or transgene transcript measurement |
| flow_cytometry_v1 | User needs reporter-positive fraction, viability dyes, or intracellular marker readout after transfection |
| lentiviral_transduction_v1 | User decides transient transfection is insufficient and needs viral delivery |
| crispr_editing_v1 | User needs Cas9, sgRNA, or HDR donor delivery design tied to editing outcomes |
| reporter_assay_v1 | User needs luciferase, dual-luciferase, or other promoter-reporter readout workflows |
