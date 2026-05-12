---
skill_id: lentiviral_transduction_v1
skill_name: Lentiviral Transduction Complete Workflow Skill
version: 1.0
method_family: gene_delivery
tags: [lentiviral_transduction, lentivirus, stable_expression, shRNA, CRISPR_delivery, antibiotic_selection, polybrene, spinoculation, MOI, titering, biosafety, mammalian_cells, packaging_supernatant, transgene_expression]
applies_to: [adherent_cells, suspension_cells, immortalized_cell_lines, primary_cells, pooled_perturbation_screens, stable_knockdown, stable_overexpression]
does_not_apply_to: [aav_delivery, adenoviral_delivery, transient_plasmid_transfection_only, in_vivo_vector_administration, GMP_vector_manufacturing, replication_competent_lentivirus_testing_for_release, large_scale_bioreactor_packaging]
risk_level: high
bsl_level: "BSL-2 or BSL-2+ per institutional biosafety committee and vector design"
last_updated: 2026-03-17
source_protocol: SOP-LENTI-001
---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I transduce my cells with lentivirus," "what MOI should I use," "my lentiviral infection failed," "how do I select stable cells," "how much polybrene should I add," "how do I transduce suspension cells," "how do I use spinoculation," "my cells died after transduction," "how do I calculate viral volume from titer," "how long do I leave virus on the cells," "how do I start puromycin selection," "my reporter is weak after lentiviral delivery," "how do I make a stable knockdown line," or any question about lentiviral transduction planning, viral handling, target-cell preparation, MOI calculation, enhancer use, adherent or suspension cell transduction, post-transduction recovery, antibiotic selection, and troubleshooting. This skill covers the complete target-cell lentiviral transduction workflow: biosafety and vector-use checks, MOI and dose planning from functional titer, target-cell preparation, lentiviral thawing and handling, transduction of adherent and suspension cells, spinoculation where indicated, post-transduction medium exchange and recovery, antibiotic kill-curve use, stable pool generation, and structured diagnostic rules for low transduction efficiency, excess cytotoxicity, failed selection, weak expression, and contamination. This skill does NOT cover: lentiviral packaging and producer-cell transfection workflows (use SOP-LENTI-PACK-001), GMP or preclinical manufacturing, in vivo administration, replication-competent lentivirus release testing for clinical material, or non-lentiviral delivery systems. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| cell_type | enum: adherent / suspension | Growth modality of the target cells |
| cell_line_name | string | Specific target cell line or primary cell type |
| vector_payload | enum: fluorescent_reporter / cDNA_overexpression / shRNA / sgRNA / CRISPR_effector / barcoded_library | Payload class delivered by lentivirus |
| vector_system | enum: transfer_vector_only / transfer_plus_packaging_known / unknown_generation | Whether vector generation and safety design are documented |
| workflow_goal | enum: transient_assessment / stable_pool / clonal_line / pooled_screen / rescue_experiment / troubleshooting | Primary objective of the transduction |
| viral_titer | string | Functional titer in TU/mL, IFU/mL, or "unknown" |
| selection_marker | enum: none / puromycin / blasticidin / hygromycin / neomycin_G418 / fluorescent_sort | Planned enrichment method after delivery |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| target_cell_count | int | Number of cells seeded per well, dish, or flask at transduction |
| plate_format | string | Vessel used for transduction (e.g., 24-well, 6-well, T-25) |
| confluence_percent | int (0–100) | Estimated confluence for adherent cells at virus addition |
| cell_density | float (cells/mL) | Density for suspension-cell transduction |
| moi_target | float | Intended MOI |
| viral_volume_added | float (µL or mL) | Volume of lentiviral stock added per vessel |
| enhancer_used | enum: none / polybrene / protamine_sulfate / retronectin / vectofusin_1 | Entry enhancer used during transduction |
| enhancer_concentration | string | Final concentration of enhancer in µg/mL |
| exposure_time | string | Time virus remained on cells before medium exchange |
| spinoculation_used | enum: yes / no | Whether centrifugation-assisted transduction was used |
| viability_percent_24h | float (0–100) | Viability 24 h after transduction |
| reporter_percent_48h | float (0–100) | Reporter-positive fraction at 48–96 h |
| antibiotic_kill_curve_available | enum: yes / no | Whether a prior kill curve exists for the target cells |
| selection_start_time | string | Time from transduction to antibiotic selection |
| mycoplasma_status | enum: positive / negative / untested / unknown | Most recent mycoplasma result for target cells |
| freeze_thaw_count_virus | int | Number of freeze-thaw cycles experienced by the viral stock |
| storage_condition_virus | enum: minus80_single_use_aliquot / minus80_reused_aliquot / wet_ice / room_temperature / unknown | Viral stock handling history |

---

## 3. WORKFLOW MODULES

### Module 1: BIOSAFETY_AND_EXPERIMENT_PLANNING

**Preconditions:** Institutional biosafety approval for lentiviral work is active. Vector map, transfer plasmid record, and target-cell identity are available. BSC is certified within the past 12 months. Disinfectant effective against enveloped virus is available: freshly prepared 10% bleach with 10 min contact time or 70% ethanol after bleach.
**Pause point:** YES — planning can stop after risk review and resume once approvals, vector records, and reagent lot tracking are complete.

#### Steps:

**SAFETY REVIEW:**
1. [CRITICAL] Confirm the lentiviral system generation, promoter, transgene, and selection cassette before opening any viral stock. Unknown vector design is a stop condition.
2. [CRITICAL] Verify whether the payload contains oncogenes, toxins, CRISPR nucleases, cytokines, or shRNAs targeting essential genes. These payloads increase personnel and target-cell risk and may require added containment.
3. Confirm institutional PPE and containment requirements for the vector class. Minimum baseline: lab coat, double gloves, eye protection, closed-toe shoes, and BSC work for all open handling steps.
4. Label a dedicated liquid waste container with 10% bleach inside the BSC. Final bleach contact time must be 10 min before disposal.
5. [DO NOT] Perform open lentiviral manipulations on the benchtop. All aliquoting, dilution, addition to cells, and waste decontamination must occur in the BSC.

**EXPERIMENT DESIGN:**
6. Define the biological objective:
   - Stable pool with high expression: plan MOI 2–10 depending on cell permissiveness and copy-number tolerance.
   - Single-copy pooled screen: plan MOI 0.2–0.5 with antibiotic selection and representation tracking.
   - Hard-to-transduce primary cells: plan MOI 5–20 plus enhancer optimization and possibly spinoculation.
7. [CRITICAL] Choose the readout time based on the payload:
   - Fluorescent reporter only: initial readout at 48–72 h after transduction.
   - Antibiotic selection marker: selection start at 24–72 h after transduction, after verifying a kill curve.
   - CRISPR knockout phenotype: functional readout commonly at 5–10 days after transduction and selection.
8. Confirm that target cells are mycoplasma negative within the past 30 days. Untested or positive cultures are stop conditions for transduction.
9. Create a worksheet recording: cell count, vessel, target MOI, viral titer, calculated viral volume, enhancer and concentration, exposure time, selection start time, and operator initials.

#### Exit Criteria (must ALL be true to proceed):
- Biosafety approval and vector identity are confirmed
- Viral payload risk level is documented
- Target cells are mycoplasma negative or freshly tested negative
- MOI target and readout schedule are defined
- Calculation worksheet is prepared before thawing virus

---

### Module 2: TARGET_CELL_PREPARATION

**Preconditions:** Target cells are healthy, contamination-free, and in log-phase growth. Complete growth medium is pre-warmed to 37°C for 15–30 min. Culture vessels are labeled before use.
**Pause point:** YES — seeded target cells can rest in the incubator before transduction. Use seeded cells within 18–24 h for adherent cultures and within 2 h for suspension setup.

#### Steps:

**CELL HEALTH CHECK:**
1. [VISUAL CHECK] Examine cells under the microscope at 10× before seeding or dilution:
   - Adherent cells should be spread, evenly attached, and free of debris.
   - Suspension cells should be mostly single cells or clusters of 2–4 cells.
2. [CRITICAL] Do not transduce cultures with viability <90% for immortalized lines or <85% for primary cells. Suboptimal input health lowers expression and inflates toxicity.
3. Confirm target cells are in log-phase growth:
   - Adherent cells: seed to reach 30–50% confluence at virus addition 16–24 h later.
   - Suspension cells: adjust to 0.2–1.0 × 10⁶ cells/mL at virus addition, depending on cell line.

**SEEDING GUIDANCE:**
4. Seed adherent cells in antibiotic-free complete medium using these starting points:

| Vessel | Target cells at virus addition | Seeding volume |
|--------|-------------------------------|----------------|
| 24-well plate | 3.0–8.0 × 10⁴ cells/well | 500 µL |
| 12-well plate | 0.8–1.5 × 10⁵ cells/well | 1 mL |
| 6-well plate | 2.0–4.0 × 10⁵ cells/well | 2 mL |
| 10 cm dish | 1.0–2.5 × 10⁶ cells/dish | 10 mL |
| T-25 flask | 4.0–8.0 × 10⁵ cells/flask | 5 mL |

5. Adjust suspension cells into antibiotic-free complete medium at these starting points:

| Vessel | Cell density at virus addition | Working volume |
|--------|-------------------------------|----------------|
| 24-well plate | 0.2–0.5 × 10⁶ cells/mL | 500 µL |
| 12-well plate | 0.3–0.8 × 10⁶ cells/mL | 1 mL |
| 6-well plate | 0.3–1.0 × 10⁶ cells/mL | 2 mL |
| T-25 flask | 0.3–0.8 × 10⁶ cells/mL | 5 mL |

6. [CRITICAL] Omit Pen/Strep and other routine antibiotics from transduction medium. Antibiotics increase stress during viral exposure and can mask contamination signals.
7. If the experiment will use antibiotic selection, reserve one non-transduced control well or flask for the kill-curve verification and one mock-transduced control for toxicity monitoring.

#### Exit Criteria (must ALL be true to proceed):
- Cells are healthy and in log-phase growth
- Adherent cultures are projected to be 30–50% confluent at transduction
- Suspension cultures are within target density range
- Transduction medium is antibiotic-free
- Required control wells or flasks are prepared

---

### Module 3: VIRUS_THAWING_HANDLING_AND_MOI_CALCULATION

**Preconditions:** Single-use viral aliquots are available at −80°C. Viral titer documentation is available or the titer is explicitly recorded as unknown. Ice bucket, low-retention tips, and calculation worksheet are ready.
**Pause point:** NO — once the aliquot begins thawing, complete dilution and addition without interruption. Freeze-thaw cycles reduce infectivity sharply.

#### Steps:

**ALIQUOT HANDLING:**
1. Retrieve one single-use viral aliquot from −80°C immediately before setup. Keep on wet ice during transport to the BSC.
2. [CRITICAL] Thaw the aliquot on wet ice or at 4°C until just liquid, typically 5–15 min for 50–200 µL aliquots. Do not thaw at 22°C for prolonged periods.
3. Wipe the tube exterior with 70% ethanol before placing it in the BSC.
4. Mix by pipetting slowly 3 times with a low-retention tip. [DO NOT] Vortex lentiviral stock.
5. [CRITICAL] Do not refreeze a thawed working aliquot. Any unused portion after setup must be bleach-decontaminated and discarded.

**MOI CALCULATION:**
6. Use the functional-titer formula:

   Required transducing units (TU) = target cell number × target MOI

   Viral volume (mL) = required TU ÷ viral titer (TU/mL)

7. Convert to practical units:
   - 0.001 mL = 1 µL
   - 0.01 mL = 10 µL
   - 0.1 mL = 100 µL
8. Example calculation: 2.0 × 10⁵ cells in one well, target MOI 5, viral titer 1.0 × 10⁸ TU/mL.

   Required TU = 2.0 × 10⁵ × 5 = 1.0 × 10⁶ TU

   Viral volume = 1.0 × 10⁶ ÷ 1.0 × 10⁸ = 0.01 mL = 10 µL

9. [BEGINNER TRAP] If the calculated viral volume is <2 µL, first dilute the viral stock into pre-warmed medium to enable accurate pipetting. A 1:10 intermediate dilution is practical for many small-volume wells.
10. [CRITICAL] If viral titer is unknown, do not guess a single condition. Run a titration panel with at least 4 viral doses spanning a 10-fold range.
11. Record freeze-thaw count, aliquot identifier, titer source, calculated viral volume, and final volume per vessel before opening the plate or flask.

#### Exit Criteria (must ALL be true to proceed):
- A single-use aliquot was thawed once and kept cold until use
- Viral stock was mixed without vortexing
- MOI and viral volume were calculated and recorded
- If titer is unknown, a titration panel is planned instead of one guessed dose
- All required additions are prepared before cells are opened

---

### Module 4: ADHERENT_CELL_TRANSDUCTION

**Preconditions:** Adherent target cells are 30–50% confluent at the time of transduction. Viral dose has been calculated. Enhancer stock and pre-warmed antibiotic-free medium are available.
**Pause point:** NO — once virus is added, maintain the exposure interval exactly as planned and proceed to the recovery step on schedule.

#### Steps:

**SETUP:**
1. [VISUAL CHECK] Confirm even monolayer distribution and absence of detached zones before virus addition.
2. Prepare transduction medium volume per vessel:
   - 24-well plate: 250–500 µL final volume
   - 12-well plate: 500 µL–1 mL final volume
   - 6-well plate: 1–2 mL final volume
   - 10 cm dish: 5–8 mL final volume
   - T-25 flask: 3–5 mL final volume
   - T-75 flask: 8–12 mL final volume
   - T-150 flask: 15–25 mL final volume
3. [DECISION POINT] Select enhancer when compatible with the cells:
   - Polybrene: 4–8 µg/mL final for many immortalized lines
   - Protamine sulfate: 50–100 µg/mL final for some primary or hematopoietic cells after cell-type-specific validation
   - VectoFusin-1: 5–20 µg/mL final for target cells validated for this additive; pre-mix per manufacturer-compatible workflow and use immediately after mixing
   - No enhancer: use when the cell line is known to be enhancer-sensitive
4. [CRITICAL] Run an enhancer-only control whenever working with a new cell type. Enhancer toxicity can be mistaken for viral toxicity.

**VIRUS ADDITION:**
5. Add viral stock directly to the medium already covering the cells or pre-mix virus into a small transduction master mix, then add dropwise across the vessel.
6. Gently rock front-to-back and side-to-side 3 times to distribute. [DO NOT] Swirl in a circular pattern.
7. Exposure times:
   - Robust immortalized adherent lines: 12–18 h exposure at 37°C, 5% CO₂
   - Sensitive primary adherent cells: 6–12 h exposure at 37°C, 5% CO₂
   - Very fragile lines: 4–6 h exposure at 37°C, 5% CO₂, then immediate medium replacement
8. Return the plate or flask to 37°C for 12–18 h with 5% CO₂ unless a shorter planned exposure is being tested.
9. [CRITICAL] Do not disturb the culture during the exposure interval unless the protocol includes spinoculation recovery handling.

#### Exit Criteria (must ALL be true to proceed):
- Adherent cells were within the target confluence range
- Enhancer concentration and control condition were recorded
- Viral stock was distributed evenly without circular swirling
- Exposure interval was defined before incubation
- Plate or flask returned promptly to 37°C with 5% CO₂

---

### Module 5: SUSPENSION_CELL_TRANSDUCTION_AND_SPINOCULATION

**Preconditions:** Suspension cells are in a single-cell state and within the target density range. Viral dose has been calculated. A centrifuge with plate carriers or sealed buckets is available if spinoculation will be used.
**Pause point:** NO — once virus is mixed with suspension cells, proceed directly through incubation or spinoculation and then recovery.

#### Steps:

**SUSPENSION SETUP:**
1. Resuspend cells by pipetting up and down 3–5 times at low speed immediately before aliquoting to prevent settling bias and avoid foam.
2. Dispense cells into the transduction vessel at the target density:
   - 24-well plate: 500 µL at 0.2–0.5 × 10⁶ cells/mL
   - 12-well plate: 1 mL at 0.3–0.8 × 10⁶ cells/mL
   - 6-well plate: 2 mL at 0.3–1.0 × 10⁶ cells/mL
3. Add virus directly to the cell suspension and mix by pipetting up and down 2–3 times without generating foam.
4. If using polybrene, protamine sulfate, or VectoFusin-1, add it last so the final concentration is exact in the full working volume.

**SPINOCULATION OPTION:**
5. [DECISION POINT] Use spinoculation for cell types known to resist passive exposure, such as some T cells, B cells, hematopoietic progenitors, and other non-adherent populations.
6. Spinoculation settings:
   - Plates: 800 × g at 22°C for 60 min
   - Conical tubes: 1,000 × g at 22°C for 60 min
7. [CRITICAL] Seal plates with breathable film or place them in plate carriers with lids before centrifugation to prevent aerosol escape.
8. After spinoculation, place cells directly into 37°C for 6–18 h with 5% CO₂.
9. Non-spinoculation exposure interval:
   - Immortalized suspension lines: 12–18 h exposure at 37°C, 5% CO₂
   - Primary suspension cells: 6–12 h exposure at 37°C, 5% CO₂
10. [DO NOT] Centrifuge fragile primary lymphocytes at >1,000 × g during spinoculation testing. Higher force increases apoptosis and lowers recovery.

#### Exit Criteria (must ALL be true to proceed):
- Suspension cells were evenly resuspended before dosing
- Viral and enhancer additions were mixed without foam
- If spinoculation was used, centrifugation force, temperature, and time were recorded
- Exposure interval after spinoculation or passive exposure was defined
- Cells were returned promptly to 37°C with 5% CO₂

---

### Module 6: POST_TRANSDUCTION_MEDIUM_EXCHANGE_AND_RECOVERY

**Preconditions:** Exposure interval is complete. Fresh pre-warmed complete medium without virus is available. Recovery vessel capacity is available if cells need dilution or transfer.
**Pause point:** YES — after medium exchange and initial recovery, cells can remain in culture until the scheduled readout or selection start.

#### Steps:

**ADHERENT RECOVERY:**
1. At the planned endpoint, aspirate viral supernatant from adherent cultures inside the BSC into bleach-containing waste.
2. Add fresh pre-warmed complete medium:
   - 24-well plate: 500 µL
   - 12-well plate: 1 mL
   - 6-well plate: 2 mL
   - 10 cm dish: 10 mL
   - T-25 flask: 5 mL
   - T-75 flask: 15–20 mL
   - T-150 flask: 30–40 mL
3. Return adherent cells to 37°C for 24–48 h with 5% CO₂ before the first reporter assessment or selection start.

**SUSPENSION RECOVERY:**
4. For suspension cells, choose recovery method:
   - Dilution method: add 2–4 volumes of fresh medium directly to reduce free virus and enhancer concentration.
   - Wash method: centrifuge at 300 × g at 22°C for 5 min, aspirate supernatant, and resuspend in fresh medium.
5. [CRITICAL] Use the wash method when enhancer toxicity is suspected or when exposure time exceeded the original plan.
6. After recovery, adjust suspension cultures back to the target maintenance density for the cell line.

**INITIAL READOUT:**
7. Assess viability and morphology at 18–24 h after medium exchange.
8. Reporter-based expression checks:
   - Fluorescent protein: first screen at 48–72 h after transduction
   - Surface marker or drug-resistance cassette expression: confirm at 48–96 h after transduction
9. Record both toxicity and expression, not only reporter percentage. High reporter with major cell loss is a failed condition for most experiments.

#### Exit Criteria (must ALL be true to proceed):
- Viral supernatant was removed or diluted at the planned time
- Recovery medium volume and composition were recorded
- Viability and morphology check was scheduled within 24 h
- First expression readout was scheduled for the payload type
- Cultures resumed growth in fresh virus-free medium

---

### Module 7: ANTIBIOTIC_SELECTION_AND_STABLE_POOL_GENERATION

**Preconditions:** Kill-curve data for the target cells and antibiotic are available, or a parallel kill-curve control is running. Cells have recovered after transduction and remain viable.
**Pause point:** YES — once selection is established and cells are recovering, the pool can be expanded across multiple passages.

#### Steps:

**SELECTION START:**
1. [CRITICAL] Start antibiotic selection only after recovery:
   - Fast-growing immortalized lines: 24–48 h after transduction
   - Primary or fragile cells: 48–72 h after transduction
2. Use kill-curve-defined concentrations:
   - Puromycin: 0.5–10 µg/mL depending on cell line
   - Blasticidin: 2–15 µg/mL depending on cell line
   - Hygromycin: 50–300 µg/mL depending on cell line
   - G418: 200–1,000 µg/mL depending on cell line
3. Maintain a non-transduced control under the same antibiotic. The control must die within the kill-curve window to validate selection pressure.

**POOL EXPANSION:**
4. Replace selection medium every 2–3 days with fresh antibiotic-containing medium.
5. Monitor for full control-cell death:
   - Puromycin: often 2–5 days
   - Blasticidin: often 5–10 days
   - Hygromycin: often 7–14 days
   - G418: often 7–14 days
6. [CRITICAL] Continue selection until the non-transduced control is completely dead and the surviving transduced cells resume active proliferation.
7. After stable pool formation, maintain cultures in a maintenance dose defined by the kill curve, commonly 25–50% of the full selection dose.
8. Expand a backup stock and freeze cells once the stable pool reaches >90% viability and target expression is confirmed. Freeze at least 3 vials of ≥2 × 10⁶ cells per vial. Plan cryopreservation within 1–2 passages after confirmed selection to limit genetic drift during pool expansion.

#### Exit Criteria (must ALL be true to proceed):
- Selection start time matched target-cell recovery status
- Antibiotic concentration came from a kill curve or validated parallel control
- Non-transduced control confirmed effective killing
- Surviving transduced pool resumed proliferation
- Backup cryostocks were planned after confirmation

---

### Module 8: TITRATION_VALIDATION_AND_DOCUMENTATION

**Preconditions:** A reporter, selectable marker, qPCR assay, or phenotypic assay is available to quantify delivery success. Data capture template is available.
**Pause point:** YES — readout and documentation can proceed after the first expression or selection window.

#### Steps:

**FUNCTIONAL READOUT:**
1. Quantify delivery success using one or more of the following:
   - Flow cytometry for fluorescent reporter percent positive and median fluorescence intensity
   - Antibiotic-resistant fraction after selection
   - qPCR copy-number estimate on genomic DNA
   - Immunoblot or RT-qPCR for target knockdown or overexpression
2. [CRITICAL] For pooled screening workflows, aim for low-copy delivery:
   - MOI 0.2–0.5
   - Representation maintained at each step
   - Post-selection reporter or marker-positive fraction commonly 20–40%
3. For stable overexpression pools, compare at least 2 MOIs or viral doses if expression variability affects phenotype.
4. Record: cell input, vessel, viral aliquot ID, freeze-thaw count, enhancer, MOI, exposure time, spin settings if used, viability, reporter percent, selection outcome, and final interpretation.
5. [DO NOT] Treat one successful well as the final condition without documenting the full dose-response context. Viral performance shifts between batches and cell passages.

#### Exit Criteria (must ALL be true to proceed):
- Functional delivery metric was measured and recorded
- Viability and delivery efficiency were interpreted together
- Pooled workflows documented low-copy assumptions
- Viral aliquot traceability was preserved
- Final condition for future repeats was defined from data

---

### Module 9: CLONAL_ISOLATION_AND_EXPANSION

**Preconditions:** Stable pool or enriched reporter-positive population is available. Single-cell cloning is required for the workflow goal. Sorting access or limiting-dilution supplies are available.
**Pause point:** YES — once single cells are deposited or plated, clonal outgrowth proceeds over multiple days to weeks with scheduled monitoring.

#### Steps:

**DECISION POINT:**
1. If the goal is a clonal_line rather than a stable pool, transition after stable enrichment and viability recovery. Do not begin clonal isolation from a population still under acute selection stress.
2. Choose the isolation method:
   - Flow sorting: route to `cell_sorting_v1` for single-cell deposition into conditioned medium
   - Limiting dilution: proceed when sorting is unavailable and the cells tolerate low-density growth

**LIMITING DILUTION:**
3. Prepare conditioned medium using 50% fresh complete medium + 50% filtered spent medium from the same healthy culture.
4. Calculate the dilution for 0.5 cells per well in a 96-well plate:

   Required cell concentration = 0.5 cells / 200 µL = 2.5 cells/mL

5. Dispense 200 µL per well into a 96-well plate, aiming for Poisson-distributed single-cell occupancy.
6. Mark wells containing exactly 1 cell by microscope inspection within 12–24 h of plating. Exclude wells with 0 cells or >1 cell from clonal tracking.
7. Feed clones by replacing 50–100 µL medium every 3–4 days without disturbing the colony center.
8. Expand confirmed single-cell-derived clones from 96-well to 24-well to 6-well to flask format while preserving clone identity records.
9. Freeze at least 3 backup vials of each validated clone at ≥1 × 10⁶ cells per vial once growth and expression are confirmed.

#### Exit Criteria (must ALL be true to proceed):
- Clonal workflow was initiated only after pool recovery
- Isolation method was documented
- Single-cell origin was recorded for retained clones
- Clone identity and expansion history were tracked
- Backup cryostocks were planned for validated clones

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: transduction_setup
CONDITION: Reporter-positive cells are <10% at 72 h despite target-cell viability meeting the preset threshold
DIAGNOSIS: Viral dose too low for the cell permissiveness level
CONFIDENCE: high
LIKELY_CAUSES:
  - MOI target was too low for the cell line
  - Viral titer was functional titer from a permissive line that overestimates performance in the current target cells
  - Calculated viral volume was inaccurate because small volumes were pipetted without pre-dilution
DISTINGUISH:
  - Compare reporter percent across the viral-dose series. A monotonic increase with dose indicates underdosing rather than complete entry failure
  - Review calculation worksheet for viral volumes <2 µL. These conditions often show high setup error
  - If a positive-control cell line transduces well with the same aliquot while the target line does not, the main issue is cell permissiveness rather than stock failure
IMMEDIATE_FIX:
  - Repeat with a 3–5 point viral titration spanning at least 10-fold total range
  - Pre-dilute virus so each addition is ≥5 µL
  - Increase MOI stepwise while tracking viability
PREVENTION: Always pilot a dose series in a new cell type; use functional titer generated in a relevant target line when possible; avoid sub-2 µL additions by intermediate dilution

---

### RULE DX-002
STAGE: virus_handling
CONDITION: Reporter-positive cells are low in every target cell type using one viral aliquot, including permissive controls
DIAGNOSIS: Viral stock lost infectivity during storage or handling
CONFIDENCE: high
LIKELY_CAUSES:
  - Multiple freeze-thaw cycles
  - Viral aliquot spent prolonged time at 22°C
  - Viral stock was refrozen after partial use
  - Storage occurred in a reused aliquot tube with adsorption losses
DISTINGUISH:
  - Compare aliquot histories. A single compromised aliquot failing across targets points to stock handling rather than biology
  - Check freeze-thaw count and time outside −80°C. Infectivity loss is common after repeated thaw cycles
  - If a fresh aliquot from the same batch performs well, the issue is aliquot-specific handling
IMMEDIATE_FIX:
  - Discard the compromised aliquot
  - Re-run transduction with a fresh single-use aliquot
  - Re-document batch performance with a permissive control line
PREVENTION: Store virus in single-use low-binding aliquots at −80°C; keep aliquots on wet ice during setup; never refreeze a thawed working aliquot

---

### RULE DX-003
STAGE: enhancer_use
CONDITION: Viability falls by >30% within 24 h of transduction while reporter-positive fraction remains low
DIAGNOSIS: Enhancer toxicity exceeds the benefit to viral entry
CONFIDENCE: high
LIKELY_CAUSES:
  - Polybrene concentration too high for the cell type
  - Protamine sulfate concentration too high
  - Exposure interval was too long in the presence of enhancer
DISTINGUISH:
  - Compare enhancer-only control against mock-transduced cells. Similar toxicity indicates enhancer rather than virus
  - If toxicity improves sharply after reducing enhancer concentration while reporter stays comparable, enhancer excess was the main problem
  - Some epithelial and primary cells show rounding within 4–8 h from enhancer exposure before viral expression is measurable
IMMEDIATE_FIX:
  - Repeat with an enhancer titration, such as polybrene 2, 4, 6, and 8 µg/mL
  - Shorten exposure to 4–6 h before medium replacement
  - Use no enhancer or a different enhancer if the target cells remain sensitive
PREVENTION: Run enhancer-only controls for each new target cell type; validate concentration on a pilot plate before scale-up; remove viral medium promptly on schedule

---

### RULE DX-004
STAGE: target_cell_preparation
CONDITION: Cells detach, clump, or stop proliferating after transduction across both viral and mock conditions
DIAGNOSIS: Target cells were not healthy enough at the start of transduction
CONFIDENCE: medium
LIKELY_CAUSES:
  - Over-confluent or under-seeded adherent cultures
  - Suspension cultures were outside the preferred density range
  - Cells were recently stressed by passage, thawing, or serum lot change
  - Mycoplasma contamination or chronic low viability before viral exposure
DISTINGUISH:
  - Review the microscope check before transduction. Abnormal morphology before virus addition points to pre-existing stress
  - If mock-transduced controls fail together with viral conditions, the main problem lies in starting culture health
  - Check mycoplasma record and viability count from the day of setup
IMMEDIATE_FIX:
  - Expand a fresh healthy culture and repeat once cells return to log-phase growth
  - Re-seed adherent cells for 30–50% confluence at virus addition
  - Adjust suspension cells to the validated density range before retrying
PREVENTION: Transduce only healthy log-phase cells; avoid using cells within 24 h of harsh passaging; verify mycoplasma-negative status before setup

---

### RULE DX-005
STAGE: selection
CONDITION: All cells, including visibly transduced cells, die rapidly within 48 h of starting antibiotic selection
DIAGNOSIS: Selection pressure started too early or at an excessive concentration
CONFIDENCE: high
LIKELY_CAUSES:
  - Kill curve was not performed in the current cell line
  - Selection started before marker expression reached a protective level
  - Antibiotic stock concentration or dilution was incorrect
DISTINGUISH:
  - Compare the start time to transduction. Starting puromycin at 6–12 h often kills cells before resistance protein accumulates
  - If the non-transduced control and transduced wells die at the same rate, the dose or timing is too severe
  - Check the antibiotic stock label and dilution worksheet for 10-fold mixing errors
IMMEDIATE_FIX:
  - Stop selection and allow surviving cells 24–48 h of recovery if enough viable cells remain
  - Repeat with a validated kill curve and selection start at 24–72 h depending on cell sensitivity
  - Prepare a fresh antibiotic working stock from the original vial
PREVENTION: Run a kill curve for every new cell line; verify antibiotic dilutions independently; do not start selection before the chosen marker-expression window

---

### RULE DX-006
STAGE: selection
CONDITION: Non-transduced control survives selection with minimal cell death
DIAGNOSIS: Selection pressure is too low or inactive
CONFIDENCE: high
LIKELY_CAUSES:
  - Antibiotic concentration below the lethal threshold for the cell line
  - Antibiotic stock lost potency through repeated freeze-thaw or prolonged storage
  - Wrong antibiotic was used for the resistance cassette
DISTINGUISH:
  - Review plasmid map and cassette identity against the drug added to the culture
  - If prior kill-curve records used a higher dose than the current run, underdosing is likely
  - If multiple cell lines show the same weak killing from the same bottle, stock potency is suspect
IMMEDIATE_FIX:
  - Replace antibiotic stock and repeat the kill curve
  - Confirm the resistance marker on the transfer vector
  - Raise the dose to the validated lethal range for the cell line
PREVENTION: Maintain lot-tracked antibiotic stocks; confirm marker-drug pairing before setup; include a non-transduced kill control in every selection run

---

### RULE DX-007
STAGE: suspension_transduction
CONDITION: Suspension cells show very low reporter-positive fraction after passive exposure, but viability remains above the preset threshold
DIAGNOSIS: Cell-entry limitation in a low-permissiveness suspension population
CONFIDENCE: medium
LIKELY_CAUSES:
  - Passive contact between virus and cells was too limited
  - Cell surface receptor abundance is low
  - Enhancer concentration or contact geometry was suboptimal
DISTINGUISH:
  - Compare passive exposure against spinoculation. Improvement after centrifugation indicates contact-limitation rather than stock failure
  - If a higher cell density lowers transduction, virus-to-cell contact may be diluted across too many cells
  - If permissive adherent control cells transduce well with the same aliquot, the issue centers on suspension-cell entry
IMMEDIATE_FIX:
  - Test spinoculation at 800 × g at 22°C for 60 min
  - Compare two densities and two enhancer concentrations in a matrix
  - Increase MOI while monitoring viability
PREVENTION: Pilot spinoculation for difficult suspension targets; validate density and enhancer together; keep cells evenly resuspended during setup

---

### RULE DX-008
STAGE: readout
CONDITION: Reporter-positive fraction is high at 48 h, but expression falls sharply by day 7 without selection
DIAGNOSIS: Initial delivery occurred, but stable integration or retention was not maintained in the population analyzed
CONFIDENCE: medium
LIKELY_CAUSES:
  - Readout captured transient carryover of reporter protein from incoming particles or early expression before stable enrichment
  - Non-integrated forms diluted out as cells proliferated
  - Strong negative selection against transgene-expressing cells
DISTINGUISH:
  - Compare day-2 and day-7 reporter data with and without antibiotic selection
  - If selected cells retain signal while non-selected cells lose it, the issue is enrichment rather than entry failure
  - If high-expression cells disappear while low-expression cells persist, the payload may impair growth
IMMEDIATE_FIX:
  - Add or optimize selection to enrich integrated cells
  - Lower expression burden using a weaker promoter or lower MOI if payload toxicity is suspected
  - Confirm integration or target perturbation by genomic or molecular assay
PREVENTION: Match readout timing to the biological endpoint; use selection when the vector includes a selectable cassette; compare reporter and functional assays over time

---

### RULE DX-009
STAGE: calculation
CONDITION: Replicates in the same experiment show highly variable transduction efficiency
DIAGNOSIS: Setup inconsistency in viral dilution, cell number, or dispensing
CONFIDENCE: medium
LIKELY_CAUSES:
  - Unequal cell seeding between wells
  - Virus not mixed after dilution
  - Dispensed viral master mix settled or adsorbed to plastic during setup
  - Edge evaporation altered effective concentration in small wells
DISTINGUISH:
  - Check whether variation tracks plate position. Outer wells often drift first when evaporation is present
  - Review seeding counts and timing between wells for staggered setup bias
  - If replicate variability disappears in a larger vessel, small-volume handling was the main issue
IMMEDIATE_FIX:
  - Prepare a homogeneous viral master mix and mix every 2–3 dispenses
  - Use larger working volumes when possible
  - Fill unused outer wells with sterile PBS or medium in plate-based pilots
PREVENTION: Normalize cell seeding carefully; use intermediate viral dilutions; minimize setup delay across wells; avoid tiny additions into dry or low-volume wells

---

### RULE DX-010
STAGE: post_transduction_recovery
CONDITION: Cells look healthy at 24 h, but extensive death appears after medium exchange
DIAGNOSIS: Recovery medium or wash step introduced stress
CONFIDENCE: medium
LIKELY_CAUSES:
  - Abrupt centrifugation or aspiration damaged cells
  - Recovery medium lacked a required supplement
  - Cells were washed too aggressively after a short exposure
DISTINGUISH:
  - Compare dilution recovery against centrifugation recovery. If death follows only the wash method, handling stress is dominant
  - Review whether the recovery medium matched the routine culture formulation except for virus and enhancer removal
  - If adherent cells detach immediately after aspiration, mechanical disturbance contributed
IMMEDIATE_FIX:
  - Switch to direct dilution for robust suspension cells; for adherent cells, aspirate at reduced vacuum using a 200 µL tip held against the vessel wall
  - Use recovery medium matching routine culture conditions exactly
  - Reduce handling steps during the first 24 h after exposure
PREVENTION: Choose dilution with 2–4× fresh medium addition or low-speed centrifugation at 300 × g at 22°C for 5 min to remove most free virus and enhancer; aspirate slowly; validate wash vs dilution in new cell types

---

### RULE DX-011
STAGE: payload_expression
CONDITION: Transduction efficiency is measurable, but target knockdown or overexpression phenotype is absent
DIAGNOSIS: Delivery occurred, but payload function is ineffective
CONFIDENCE: medium
LIKELY_CAUSES:
  - Incorrect shRNA or sgRNA design
  - Promoter not active in the target cell type
  - Readout was performed before enough time elapsed for protein turnover
  - Transgene sequence or cloning junction contains an error
DISTINGUISH:
  - Reporter-positive cells with no molecular phenotype indicate a payload-design issue rather than entry failure
  - Compare promoter behavior in the target cells against a validated control construct
  - Check protein half-life of the target. Long-lived proteins can require several days after selection for phenotype emergence
IMMEDIATE_FIX:
  - Verify construct by sequencing
  - Test an independent shRNA or sgRNA
  - Extend the post-selection readout window based on target protein turnover
PREVENTION: Validate payload sequence before virus production; use more than one guide or shRNA; align assay timing to target depletion kinetics

---

### RULE DX-012
STAGE: biosafety
CONDITION: Unplanned spill, splash, or aerosol-generating event occurs during lentiviral handling
DIAGNOSIS: Containment breach requiring immediate decontamination response
CONFIDENCE: high
LIKELY_CAUSES:
  - Loose tube caps or plate seals
  - Rapid pipetting causing droplets
  - Centrifuge handling without sealed carriers
DISTINGUISH:
  - Determine whether the event occurred inside the BSC or outside containment; response scope differs
  - Identify whether skin, eyes, or open surfaces were exposed
  - Check whether centrifuge buckets remained sealed until inside the BSC after the run
IMMEDIATE_FIX:
  - Stop work immediately and follow institutional spill response
  - Cover the area with absorbent material and apply 10% bleach for 10 min contact time, then wipe and follow with 70% ethanol if compatible
  - Report the incident to biosafety personnel and document exposed materials and personnel
PREVENTION: Use sealed centrifuge carriers; pipette slowly with secure caps; decontaminate transport surfaces; review spill response before each viral session

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-020)

#### RISK RM-001
STAGE: biosafety
ITEM: Handling lentiviral stock outside the BSC
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm all open-tube manipulations, dilutions, and additions occur in a certified BSC
MITIGATION: Restrict all viral handling to the BSC; decontaminate surfaces with 10% bleach for 10 min followed by 70% ethanol where surface-compatible; train all personnel on aerosol-control technique

---

#### RISK RM-002
STAGE: biosafety
ITEM: Unknown vector design or payload hazard
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Verify transfer-vector map, payload identity, promoter, and generation are documented before use
MITIGATION: Stop work when vector identity is incomplete; review map and biosafety classification before thawing virus; escalate oncogene, toxin, cytokine, and nuclease payloads for added review

---

#### RISK RM-003
STAGE: target_cell_preparation
ITEM: Transducing mycoplasma-positive or untested cells
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm a negative mycoplasma result within the past 30 days for target cells
MITIGATION: Test cells before transduction; quarantine positive cultures; restart with a negative culture before viral work

---

#### RISK RM-004
STAGE: calculation
ITEM: MOI miscalculation from unit confusion
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Verify whether the stock titer is in TU/mL, IFU/mL, or physical particles/mL and confirm the cell number used in the formula
MITIGATION: Record formula on the worksheet for every run; perform an independent second check of calculations; avoid using physical-particle counts as if they were functional titer

---

#### RISK RM-005
STAGE: virus_handling
ITEM: Infectivity loss from repeated freeze-thaw cycles
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Freeze-thaw count must be 0 before the current use of a single-use aliquot
MITIGATION: Store virus in single-use aliquots of 20–100 µL or 100–500 µL depending on scale; discard leftover thawed stock; keep aliquots on wet ice during setup

---

#### RISK RM-006
STAGE: virus_handling
ITEM: Viral adsorption to plastic and low-volume dispensing error
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Review whether calculated additions were <2 µL and whether low-binding tubes and tips were used
MITIGATION: Prepare intermediate dilutions for small additions; use low-retention consumables; mix diluted virus before and during dispensing

---

#### RISK RM-007
STAGE: target_cell_preparation
ITEM: Adherent cells too confluent at transduction
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Confirm adherent cultures are 30–50% confluent when virus is added
MITIGATION: Seed cells 16–24 h ahead to land within the target range; avoid transducing near-confluent monolayers; re-seed rather than forcing a compromised run

---

#### RISK RM-008
STAGE: target_cell_preparation
ITEM: Suspension cells outside the validated density range
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Measure cell density immediately before viral addition
MITIGATION: Adjust cells to the tested density range; avoid over-dense cultures that lower virus-to-cell contact and under-dense cultures that weaken recovery

---

#### RISK RM-009
STAGE: enhancer_use
ITEM: Polybrene or protamine sulfate toxicity
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Include enhancer-only control for each new cell type and record the final enhancer concentration
MITIGATION: Run enhancer titration before scale-up; shorten exposure interval for sensitive cells; switch enhancers or omit enhancer when toxicity dominates

---

#### RISK RM-010
STAGE: transduction_setup
ITEM: Circular swirling causing uneven viral distribution
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Observe distribution pattern immediately after setup, especially in plate wells
MITIGATION: Rock front-to-back and side-to-side 3 times; avoid circular motion; place the plate on a flat shelf in the incubator

---

#### RISK RM-011
STAGE: suspension_transduction
ITEM: Excessive spinoculation force damaging cells
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Record centrifugation as ×g, temperature, and time for every run; compare with the validated window for the cell type
MITIGATION: Start with 800 × g at 22°C for 60 min for plate spinoculation unless target-cell data support a different setting; do not exceed 1,000 × g during pilot optimization for fragile cells

---

#### RISK RM-012
STAGE: recovery
ITEM: Viral supernatant left on cells too long
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Confirm planned exposure interval and actual medium-change time were recorded
MITIGATION: Define exposure length before setup; use timers; replace medium at the planned endpoint; shorten to 4–6 h for fragile cells if toxicity emerges

---

#### RISK RM-013
STAGE: recovery
ITEM: Overly aggressive wash or centrifugation after transduction
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Review whether suspension cells were pelleted at >400 × g or whether adherent cells detached during aspiration
MITIGATION: Use 300 × g at 22°C for 5 min for routine suspension recovery washes; aspirate adherent wells slowly; choose dilution recovery when cell fragility is evident

---

#### RISK RM-014
STAGE: selection
ITEM: Starting antibiotic selection before resistance marker expression
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Compare selection-start time against the vector design and target-cell sensitivity
MITIGATION: Delay selection to 24–72 h after transduction based on cell type; verify expression window in a pilot run; monitor the non-transduced control in parallel

---

#### RISK RM-015
STAGE: selection
ITEM: Antibiotic concentration chosen without a kill curve
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Confirm kill-curve data exist for the exact cell line and antibiotic lot or that a parallel control kill curve is running
MITIGATION: Run a kill curve for every new cell line; re-check when serum lot, medium, or passage state changes; do not rely on values from unrelated cell lines

---

#### RISK RM-016
STAGE: pooled_screen
ITEM: MOI too high for pooled perturbation work
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: For pooled libraries, verify planned MOI is 0.2–0.5 and representation targets are documented
MITIGATION: Use low-copy delivery design; track cell numbers through selection; avoid high MOI that creates multi-integrant cells and confounds phenotype assignment

---

#### RISK RM-017
STAGE: documentation
ITEM: Loss of viral-batch traceability between experiments
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Confirm aliquot ID, titer source, freeze-thaw count, and operator are recorded for each transduction
MITIGATION: Use a batch log with aliquot identifiers; link each experiment to the exact aliquot used; retire batches with drifting performance

---

#### RISK RM-018
STAGE: biosafety
ITEM: Inadequate decontamination of liquid waste and disposables
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify bleach contact time of 10 min for liquid waste and contaminated absorbent material
MITIGATION: Collect viral liquid waste into 10% bleach in the BSC; allow 10 min contact time before final disposal; decontaminate solid waste per institutional procedures

---

#### RISK RM-019
STAGE: target_cell_preparation
ITEM: Using routine antibiotics during transduction medium exposure
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Review medium composition at the time of virus addition
MITIGATION: Use antibiotic-free transduction medium; return to routine maintenance additives only after recovery if required by the cell culture plan

---

#### RISK RM-020
STAGE: payload_expression
ITEM: High-level transgene expression imposes growth disadvantage and skews the surviving pool
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare proliferation, viability, and reporter intensity over time after transduction
MITIGATION: Test lower MOI, weaker promoter options, or inducible designs; compare short-term expression with post-selection pool composition; avoid selecting only the brightest survivors without understanding growth bias

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: biosafety
ITEM: Lentiviral work started without documented vector identity and approval
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm biosafety authorization, vector map, payload annotation, and generation before thawing any viral aliquot
MITIGATION: (1) Stop work immediately. (2) Quarantine all open materials and decontaminate surfaces. (3) Obtain vector records and biosafety review before restarting. (4) Retrain personnel on the pre-run checklist. (5) Require signed worksheet completion before each viral session.

---

#### RISK CF-002
STAGE: pooled_screen
ITEM: Library transduction performed at high MOI, creating widespread multi-integrant cells
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Review planned and measured infection rate before large-scale screening; pooled workflows must document low-copy design assumptions
MITIGATION: (1) Re-titrate the library to MOI 0.2–0.5. (2) Rebuild the screened population from fresh cells if high MOI was used. (3) Track representation from transduction through selection. (4) Freeze an early backup after validated low-copy delivery.

---

#### RISK CF-003
STAGE: selection
ITEM: Stable-line generation performed without a kill curve and without non-transduced kill controls
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Verify kill-curve record and non-transduced control presence before selection starts
MITIGATION: (1) Stop scale-up until the kill curve is defined. (2) Re-run selection with matched controls. (3) Validate drug potency and marker identity. (4) Capture complete timing and dose records for future repeats.

---

## 6. PARAMETER CONSTRAINTS

### Target-Cell State at Virus Addition

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Adherent confluence | 20% | 30–50% | 70% | <20%: weak recovery; >70%: reduced access and altered growth state |
| Suspension density | 0.2 × 10⁶ cells/mL | 0.3–0.8 × 10⁶ cells/mL | 1.0 × 10⁶ cells/mL | <0.2 × 10⁶ cells/mL: poor recovery; >1.0 × 10⁶ cells/mL: lower virus-to-cell contact |
| Viability before transduction (immortalized) | 90% | ≥95% | 100% | <90%: recover culture before transduction |
| Viability before transduction (primary) | 85% | ≥90% | 100% | <85%: recover culture before transduction |

### Enhancer Use

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Polybrene | 2 µg/mL | 4–8 µg/mL | 10 µg/mL | >10 µg/mL: marked toxicity risk; re-titrate |
| Protamine sulfate | 25 µg/mL | 50–100 µg/mL | 120 µg/mL | Outside a validated cell-type-specific window: re-titrate before scale-up |
| VectoFusin-1 | 5 µg/mL | 10–15 µg/mL | 20 µg/mL | >20 µg/mL: increased aggregation and toxicity risk; re-titrate |
| Exposure with enhancer | 4 h | 6–16 h | 18 h | >18 h: replace medium and assess toxicity |

### Spinoculation

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Plate spin force | 600 × g | 800 × g | 1,000 × g | >1,000 × g: rising apoptosis risk in fragile cells |
| Tube spin force | 800 × g | 1,000 × g | 1,200 × g | >1,200 × g: avoid unless validated for the cell type |
| Spin temperature | 20°C | 22°C | 25°C | Outside range: repeat with controlled room-temperature centrifugation |
| Spin duration | 30 min | 60 min | 90 min | >90 min: increased stress with limited added benefit |

### Recovery Washes and Handling

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Suspension recovery centrifugation | 200 × g at 22°C for 5 min | 300 × g at 22°C for 5 min | 400 × g at 22°C for 7 min | Above maximum: increased mechanical stress |
| Adherent exposure before medium exchange | 4 h | 12–16 h | 18 h | >18 h: change medium immediately and assess viability |
| Suspension exposure before wash or dilution | 4 h | 8–16 h | 18 h | >18 h: recover immediately and log deviation |

### Selection

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Selection start time | 24 h | 24–72 h | 96 h | <24 h: resistance marker may not protect cells; >96 h: non-transduced cells can overgrow |
| Maintenance selection dose | 25% of validated kill dose | 25–50% of validated kill dose | 60% of validated kill dose | >60%: long-term growth suppression risk |
| Puromycin starting range | 0.5 µg/mL | cell-line-specific kill curve | 10 µg/mL | Outside validated range: re-run kill curve |
| Blasticidin starting range | 2 µg/mL | cell-line-specific kill curve | 15 µg/mL | Outside validated range: re-run kill curve |
| Hygromycin starting range | 50 µg/mL | cell-line-specific kill curve | 300 µg/mL | Outside validated range: re-run kill curve |
| G418 starting range | 200 µg/mL | cell-line-specific kill curve | 1,000 µg/mL | Outside validated range: re-run kill curve |

---

## 7. QC GATES

### QC Gate 1: Before Virus Thaw

PASS criteria (ALL must be true):
  - Biosafety approval is active for the vector and payload
  - Vector identity, selection marker, and titer record are available
  - Target cells are mycoplasma negative and healthy
  - MOI calculation worksheet is complete
  - Control conditions are labeled before the aliquot is removed from −80°C

ACTION if FAIL: Do not thaw virus. Resolve missing approval, vector records, mycoplasma status, or calculations first.

---

### QC Gate 2: At Virus Addition

PASS criteria (ALL must be true):
  - Adherent cells are 30–50% confluent or suspension cells are within the target density range
  - Viral aliquot has experienced one thaw only
  - Enhancer concentration is recorded and control condition included
  - Viral dose or titration matrix is documented
  - Transduction medium is antibiotic-free

ACTION if FAIL: Re-seed cells, replace the aliquot, correct the enhancer setup, or postpone the run until the setup is exact.

---

### QC Gate 3: After Recovery Medium Exchange

PASS criteria (ALL must be true):
  - Viral supernatant was removed or diluted at the planned time
  - Viability at 18–24 h is ≥80% for immortalized lines or ≥75% for primary cells after medium exchange
  - Morphology is comparable to mock-transduced control
  - First expression readout time is scheduled
  - Recovery medium matches the intended culture formulation

ACTION if FAIL: If toxicity is present, reduce enhancer or exposure duration in the next run. If recovery handling caused loss, switch to direct dilution or recovery centrifugation at 300 × g at 22°C for 5 min.

---

### QC Gate 4: Before Selection Scale-Up

PASS criteria (ALL must be true):
  - Reporter or other delivery evidence is measurable at the planned time
  - Kill curve exists for the cell line and antibiotic
  - Non-transduced control is present
  - Selection start time matches the vector-expression window
  - Cell viability is adequate to tolerate selection

ACTION if FAIL: Delay selection, run the kill curve, or repeat transduction with optimized conditions before committing to a stable-pool workflow.

---

### QC Gate 5: Final Stable Pool or Screen Entry

PASS criteria (ALL must be true):
  - Delivery efficiency and viability meet the workflow goal
  - Non-transduced control died within the expected kill window
  - Stable pool resumed active proliferation
  - Viral batch, dose, and conditions are fully documented
  - Backup cryostocks are planned or already created for the validated population

ACTION if FAIL: Do not advance the pool into screening or downstream assays. Re-titrate dose, adjust selection, or restart from a healthier culture and fresh aliquot.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified problem and root cause, or "QC PASS — proceed" |
| confidence | enum: high / medium / low | Confidence in diagnosis based on available inputs |
| recommended_actions | list[string] | Ordered action list; immediate fix first, then prevention |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass/fail status for each of the 5 QC gates |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters with linked diagnostic rule |
| transduction_summary | dict | Captures cell input, MOI, viral volume, enhancer, exposure time, and selection plan |
| viral_batch_status | enum: validated / pilot_only / suspect / failed | Current confidence in the viral aliquot or batch |
| stable_line_readiness | enum: not_ready / selection_in_progress / ready_for_expansion | Status of downstream expansion readiness |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | Target-cell maintenance, passaging, thawing, cryopreservation, or contamination diagnosis is needed before or after transduction |
| transfection_v1 | User needs plasmid delivery to producer cells for packaging or a non-viral DNA delivery route |
| flow_cytometry_v1 | Reporter quantification, viability dye gating, or sort-based enrichment is needed |
| rt_qpcr_v1 | User needs transgene expression, knockdown validation, or viral-copy quantification by qPCR |
| western_blot_v1 | Protein-level confirmation of overexpression or knockdown is needed |
| crispr_screen_v1 | User is moving from low-MOI lentiviral delivery into pooled perturbation screening analysis |
| cell_sorting_v1 | User wants fluorescent enrichment or single-cell isolation after transduction; route clonal_line workflows here for sorter-based single-cell deposition |
| lentiviral_packaging_v1 | User needs producer-cell transfection, harvest, clarification, concentration, or packaging QC |
| mycoplasma_testing_v1 | User needs contamination testing before transduction or before bank creation |
