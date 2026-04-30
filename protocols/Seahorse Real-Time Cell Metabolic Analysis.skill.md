---
skill_id: seahorse_metabolic_analysis_v1
skill_name: Seahorse Real-Time Cell Metabolic Analysis Complete Workflow Skill
version: 1.0
method_family: cell_metabolism
tags: [seahorse, extracellular_flux, ocr, ecar, per, mito_stress_test, glycolysis_stress_test, atp_rate, metabolic_flexibility, assay_medium, sensor_cartridge, normalization, oligomycin, fccp, rotenone, antimycin_a, glucose, pyruvate, glutamine]
applies_to: [adherent_cells, weakly_adherent_cells, suspension_capture_workflows, xf24, xf96, xfp, mito_stress_test, glycolysis_stress_test, atp_rate_assay, custom_metabolic_perturbation]
does_not_apply_to: [isolated_mitochondria, perfused_tissue, whole_animal_respirometry, clark_electrode_assay, microbial_fermentation_only, noncellular_oxygen_chemistry_as_primary_topic]
risk_level: high
bsl_level: "BSL-2 for human-derived material unless institutional assessment permits lower containment"
last_updated: 2026-04-21
source_protocol: SOP-SEAHORSE-001
---

## 1. CONTEXT

#### Trigger Phrases

This skill is invoked when a user asks questions including but not limited to: "how do I run a Seahorse assay," "my OCR baseline is low," "why is my ECAR noisy," "how many cells should I seed in an XF96 plate," "how do I prepare Seahorse assay medium," "what oligomycin concentration should I use," "my FCCP response is weak," "how do I hydrate the sensor cartridge," "how do I normalize Seahorse data," "how do I run a Mito Stress Test," "how do I run a Glycolysis Stress Test," "why are my edge wells drifting," or any question about extracellular flux workflow design, execution, QC, troubleshooting, and interpretation in cell-based Seahorse assays.

This skill covers the complete Seahorse real-time metabolic workflow: assay planning, cell seeding and plate coating, sensor cartridge hydration, assay medium preparation and pH adjustment, compound preparation and port loading, analyzer run setup, post-run normalization, structured diagnostic rules for failed response patterns and unstable traces, and risk controls for pre-analytical, analytical, and interpretation failures.

#### Out of Scope

This skill does NOT cover isolated mitochondrial respiration workflows, perfused tissue measurements, whole-animal indirect calorimetry, non-cell Seahorse chemistry validation as a standalone topic, or microbial fermentation optimization. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| assay_type | enum: mito_stress_test / glycolysis_stress_test / atp_rate / custom_perturbation | Seahorse assay design selected for the run |
| analyzer_format | enum: XF24 / XF96 / XFp | Instrument and plate format used for the experiment |
| cell_type | enum: adherent / weakly_adherent / suspension_capture | Attachment behavior of the cell population on the Seahorse plate |
| cell_line_name | string | Specific cell line or primary cell type assayed |
| seeding_density | string | Planned cells per well or equivalent loaded biomass per well |
| workflow_goal | enum: comparative_study / optimization / perturbation_response / troubleshooting / baseline_profiling | Primary experimental objective |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| treatment_condition | string | Drug, nutrient, gene perturbation, or media condition tested |
| confluence_percent | int (0-100) | Estimated confluence at assay start for adherent cells |
| viability_percent | float (0-100) | Viability before assay medium exchange |
| assay_medium_base | enum: xf_base_medium / bicarbonate_free_dmem / custom_bicarbonate_free_medium | Base medium used during measurement |
| assay_medium_pH | float | pH after warming medium to 37°C |
| glucose_mM | float | Final glucose concentration in assay medium |
| glutamine_mM | float | Final glutamine concentration in assay medium |
| pyruvate_mM | float | Final pyruvate concentration in assay medium |
| equilibration_time | string | Time spent in non-CO2 equilibration before measurement |
| baseline_cv_percent | float | Coefficient of variation across baseline measurement cycles |
| ocr_baseline_pmol_min | float | Basal oxygen consumption rate |
| ecar_baseline_mpH_min | float | Basal extracellular acidification rate in mpH/min or matched acidification proxy |
| injection_a_compound | string | Compound loaded into port A |
| injection_b_compound | string | Compound loaded into port B |
| injection_c_compound | string | Compound loaded into port C |
| injection_d_compound | string | Compound loaded into port D when applicable |
| oligomycin_uM | float | Final oligomycin concentration in the well |
| fccp_uM | float | Final FCCP concentration in the well |
| rotenone_uM | float | Final rotenone concentration in the well |
| antimycin_a_uM | float | Final antimycin A concentration in the well |
| normalization_method | enum: cell_count / protein / dna / image_area | Method used after the run |
| edge_well_pattern | enum: absent / present / unknown | Whether perimeter wells show systematic drift or lower signal |
| cartridge_hydration_time | string | Total hydration time for the sensor cartridge before calibration |

---

## 3. WORKFLOW MODULES

### Module 1: ASSAY_DESIGN_AND_PLATE_MAP

**Preconditions:** Biological question, assay type, control groups, and analyzer format are defined. Reagents, cell stocks, and assay plates are available and within expiry.
**Pause point:** YES - experimental design can be finalized 1-7 days before the run. Do not begin cartridge hydration or cell seeding until the plate map and injection sequence are locked.

#### Steps:

1. Define the primary readout before run setup:
   - Mito Stress Test: basal respiration, ATP-linked respiration, proton leak, maximal respiration, spare respiratory capacity, non-mitochondrial respiration.
   - Glycolysis Stress Test: non-glycolytic acidification, glycolysis, glycolytic capacity, glycolytic reserve.
   - ATP Rate Assay: mitochondrial ATP production and glycolytic ATP production.
   - Custom perturbation: substrate dependence, inhibitor sensitivity, or metabolic switching.
2. Assign biological replicates:
   - Use at least 4 technical wells per condition for XF96.
   - Use at least 3 technical wells per condition for XF24 or XFp.
3. Reserve background wells:
   - Medium-only blanks on every plate.
   - Chemistry-only blanks for each drug condition when the compound can alter OCR or ECAR without cells.
4. Avoid placing the highest-priority comparison entirely on perimeter wells when the format is XF96.
5. Define the injection order before compound preparation and record final target concentrations in the well.
6. Record the normalization method before seeding so compatible post-run reagents are available.
7. Set the acceptance plan:
   - Baseline replicate CV target: ≤15% within each condition during baseline cycles.
   - Expected direction of post-injection response.
   - Criteria for excluding failed wells.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Assay type and success metric are defined
- [ ] Plate map includes blanks and all replicate assignments
- [ ] Injection order and final target concentrations are recorded
- [ ] Normalization method is selected

---

### Module 2: CELL_PREPARATION_AND_SEEDING

**Preconditions:** Cells are mycoplasma-negative, in log-phase growth, and at viability ≥90% unless a disease-model constraint has been documented. Coating reagents and Seahorse plates are available.
**Pause point:** YES - seeded plates can incubate before the assay according to the validated attachment window for the cell line. Do not hold dissociated cells at 20-25°C longer than 15 min before plating.

#### Steps:

1. Select the loading strategy:
   - Adherent cells: direct seeding onto Seahorse cell culture microplates.
   - Weakly adherent cells: apply coating plus extended attachment verification.
   - Suspension capture workflows: use Cell-Tak or a validated capture method with an explicit centrifugation-settling step.
2. Use starting seeding ranges:
   - XF96 adherent cells: 5,000-40,000 cells per well in 80-100 µL growth medium.
   - XF24 adherent cells: 20,000-100,000 cells per well in 150-250 µL growth medium.
   - XFp cells: 10,000-80,000 cells per well in 150-180 µL growth medium.
3. For weakly adherent cells, coat the plate before seeding:
   - Poly-D-lysine: 25 µL-50 µL per XF96 well or 100 µL per XF24 well, incubate at 20-25°C for 1 h, aspirate, then air-dry for 30 min in a sterile hood.
   - Cell-Tak: prepare a working solution at 25 µg/mL in 0.1 M sodium bicarbonate, pH 8.0, then adjust for lot-specific activity to achieve 3.5 µg/cm² surface loading; add 45 µL per XF96 well or 45 µL per XF24 well, incubate at 20-25°C for 20 min, rinse once with sterile water, then air-dry for 20 min.
4. Prepare cells:
   - Adherent cells: detach with validated dissociation reagent, neutralize, then centrifuge at 200 ×g, 20-25°C, 5 min before resuspension.
   - Suspension cells for capture workflow: centrifuge at 200 ×g, 20-25°C, 5 min, then resuspend in growth medium at the target concentration.
5. For suspension capture after Cell-Tak coating: dispense cells in assay medium at the target density, centrifuge the plate at 200 ×g, 20-25°C, 1 min, carefully aspirate the supernatant while leaving the settled cells on the Cell-Tak surface, then incubate at 20-25°C for 20-30 min before adding the planned assay volume.
6. For adherent and weakly adherent cell seeding only, dispense cells as follows:
   - XF96: 80-100 µL per well.
   - XF24: 150-250 µL per well.
   - XFp: 150-180 µL per well.
7. Rest the plate at 20-25°C for 20 min before incubator transfer to reduce center drift.
8. Incubate seeded adherent plates at 37°C, 5% CO2 for 16-24 h unless the validated attachment window for the cell line differs.
9. Verify attachment and distribution by microscopy before assay-medium exchange.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Cell viability and growth status are acceptable
- [ ] Coating status matches the attachment behavior of the cells
- [ ] Seeding volume and cell number are recorded
- [ ] Microscopy confirms even attachment or valid capture

---

### Module 3: SENSOR_CARTRIDGE_HYDRATION_AND_CALIBRANT_SETUP

**Preconditions:** Sensor cartridge and utility plate are at room temperature. Calibrant has equilibrated to 20-25°C before use. Analyzer maintenance status is current.
**Pause point:** YES - hydrated cartridges can remain at 37°C in a non-CO2 incubator for 12-24 h before calibration. Do not hydrate for less than 12 h unless the cartridge generation has a validated shorter interval.

#### Steps:

1. Add calibrant to the utility plate:
   - XF96: 200 µL calibrant per well.
   - XF24: 1.0 mL calibrant per well.
   - XFp: 200 µL calibrant per well.
2. Place the sensor cartridge onto the utility plate without trapping bubbles.
3. Incubate the assembled cartridge at 37°C in a non-CO2 incubator for 12-24 h.
4. On run day, inspect each well of the utility plate and cartridge for visible bubbles, liquid loss, or warped sensor ports.
5. Prepare the analyzer method with the correct cartridge type, plate format, mixing time, waiting time, measurement time, and injection sequence.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Cartridge hydration time is within the validated window
- [ ] Calibrant volume matches analyzer format
- [ ] No visible bubbles or liquid-loss defects are present
- [ ] Analyzer method file is prepared and matches the plate map

---

### Module 4: ASSAY_MEDIUM_PREPARATION_AND_EQUILIBRATION

**Preconditions:** Bicarbonate-free assay medium components are available. pH meter is calibrated. Supplements match the assay design.
**Pause point:** YES - assay medium can be prepared on the day of the run and held at 37°C in a non-CO2 incubator for up to 4 h after pH adjustment.

#### Steps:

1. Select medium composition by assay type:
   - Mito Stress Test: glucose 10 mM, pyruvate 1 mM, glutamine 2 mM.
   - Glycolysis Stress Test pre-glucose phase: glutamine 2 mM, no glucose, no pyruvate unless the validated protocol requires pyruvate.
   - ATP Rate Assay: glucose 10 mM, pyruvate 1 mM, glutamine 2 mM unless the cell-line-specific validation differs.
2. Warm assay medium to 37°C before pH adjustment.
3. Adjust pH to 7.40 ± 0.05 at 37°C.
4. Remove growth medium from the Seahorse cell plate and replace with warmed assay medium:
   - XF96: 180 µL per well after exchange.
   - XF24: 500 µL per well after exchange.
   - XFp: 180 µL per well after exchange.
5. Add matched medium-only background wells and chemistry-only blank wells using the same assay medium composition as sample wells.
6. Incubate the cell plate at 37°C in a non-CO2 incubator for 45-90 min before the run, with a 60 min target.
7. Inspect every well for trapped bubbles immediately before loading into the analyzer. Remove bubbles with a sterile pipette tip if present.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Assay medium composition matches the assay type
- [ ] pH is 7.40 ± 0.05 at 37°C
- [ ] Final assay volume per well is correct
- [ ] Non-CO2 equilibration time is complete
- [ ] No bubbles remain in measurement wells

---

### Module 5: COMPOUND_PREPARATION_AND_PORT_LOADING

**Preconditions:** Compound stocks are identity-verified, within expiry, and compatible with the assay medium. Final target concentrations are documented from Module 1.
**Pause point:** YES - loaded cartridge can remain at 37°C in a non-CO2 incubator during the interval between loading and calibration if the hold time is less than 1 h.

#### Steps:

1. Prepare fresh working solutions in assay medium or validated solvent-matched medium.
2. Use starting final concentration ranges for optimization:
   - Oligomycin: 0.5-2.0 µM.
   - FCCP: 0.25-2.0 µM.
   - Rotenone: 0.25-1.0 µM.
   - Antimycin A: 0.25-1.0 µM.
   - Glucose in glycolysis assay: final 10 mM.
   - 2-deoxy-D-glucose: final 50 mM; do not exceed 100 mM, and document osmolarity impact if the cell line is osmosensitive.
3. Load the hydrated sensor cartridge ports with explicit format-specific volumes:
   - XF96: 20 µL per port, producing an approximate 1:10 dilution into a 180 µL assay well.
   - XF24: 56 µL per port, producing an approximate 1:10 dilution into a 500 µL assay well.
   - XFp: 5 µL per port, producing an approximate 1:37 dilution into a 180 µL well; prepare the working stock accordingly.
4. Assign compounds in the planned sequence:
   - Mito Stress Test: oligomycin, FCCP, rotenone/antimycin A.
   - Glycolysis Stress Test: glucose, oligomycin, 2-deoxy-D-glucose.
5. Avoid introducing bubbles while loading ports.
6. Record stock concentration, working concentration, solvent, port identity, and final concentration in the well.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Working solutions were prepared from verified stocks
- [ ] Port identity matches the method file
- [ ] Final target concentrations are documented
- [ ] No visible bubbles are present in loaded ports

---

### Module 6: ANALYZER_RUN_AND_REAL_TIME_QC

**Preconditions:** Hydrated cartridge, loaded compounds, equilibrated cell plate, and method file are ready. Plate map and sample identifiers are confirmed.
**Pause point:** NO - after calibration begins, the run should proceed without interruption unless analyzer failure or plate failure is detected.

#### Steps:

1. Calibrate the loaded cartridge in the analyzer using the prepared method.
2. After calibration, replace the utility plate with the equilibrated cell plate.
3. Confirm plate orientation and method identity before starting measurement.
4. Use a format-specific measurement structure unless the assay validation specifies a different cycle design:
   - XF96 default: mix 3 min, wait 0 min, measure 3 min, with 3 baseline cycles.
   - XF24 default: mix 3 min, wait 2 min, measure 3 min, with 3 baseline cycles.
   - XFp: follow the validated method file for the installed instrument generation and cartridge type.
5. Monitor baseline wells:
   - Baseline replicate CV should remain at or below 15% within each condition; flag 15-25% for review and reject plate-wide CV above 25%.
   - Single-well outliers with abrupt drops or spikes should be flagged during the run log review.
6. After each injection, verify that control wells show the expected directional response.
7. If an instrument alarm, calibration failure, or widespread flatline occurs, stop interpretation and document the failure state before rerun planning.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Calibration completed without analyzer error
- [ ] Plate orientation and method identity were confirmed
- [ ] Baseline and post-injection traces were recorded for all wells
- [ ] Failed wells are flagged before downstream normalization

---

### Module 7: POST_RUN_NORMALIZATION_AND_DATA_HANDLING

**Preconditions:** Raw Seahorse output is available. The chosen normalization reagents or imaging workflow are ready.
**Pause point:** YES - raw data can be stored before normalization, but normalization should be completed the same day when protein or imaging endpoints are used.

#### Steps:

1. Select one normalization method for the primary analysis:
   - Cell count by imaging or nuclear stain.
   - Protein content.
   - DNA content.
   - Image-derived area only when validated for the cell type.
2. For protein normalization:
   - XF96: add 20-30 µL lysis buffer per well.
   - XF24: add 50-100 µL lysis buffer per well.
3. Keep lysis volume constant across all wells within one plate.
4. Exclude wells with documented pipetting error recorded during execution, no-cell regions confirmed by microscopy, severe edge artifacts, or persistent bubble-associated trace distortion spanning two or more measurement cycles.
5. Calculate derived parameters only after exclusion review and normalization review are complete.
6. Preserve both raw and normalized datasets, with a separate exclusion log.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Primary normalization method is documented
- [ ] Excluded wells are justified and logged
- [ ] Raw and normalized datasets are both retained
- [ ] Derived parameters are calculated only from accepted wells

---

### Module 8: RESULT_REVIEW_AND_RERUN_DECISION

**Preconditions:** Normalized data, raw traces, plate map, and run notes are available.
**Pause point:** YES - interpretation can pause after trace review and before rerun scheduling.

#### Steps:

1. Review trace shape before comparing endpoint metrics.
2. Confirm that control wells display the expected directional response for the assay type.
3. Compare technical replicate spread within each condition.
4. Review blanks:
   - Medium-only blanks for instrument and media background.
   - Chemistry-only blanks for compound-dependent non-cell signal.
5. Decide run status:
   - Accept for analysis.
   - Accept with limited interpretation.
   - Reject and rerun after corrective action.
6. Link any failure pattern to the matching diagnostic rule and risk rule before planning a repeat experiment.

#### Exit Criteria (must ALL be true to proceed):
- [ ] Trace-shape review is complete
- [ ] Control-response review is complete
- [ ] Replicate spread and blank behavior are evaluated
- [ ] Final run status is recorded

---

## 4. DIAGNOSTIC RULES

### DX-001 LOW_BASELINE_OCR

**Trigger:** Baseline OCR is uniformly lower than historical values across most sample wells.
**Likely cause:** Low viable cell mass, under-seeding, nutrient mismatch, over-equilibration stress, or severe mitochondrial suppression before the run.
**DISTINGUISH:** Uniform low OCR with proportionally low normalized signal suggests low cell mass; low raw OCR with normal cell count suggests metabolic suppression; low OCR only in treated wells suggests treatment-specific bioenergetic inhibition rather than setup failure.
**Immediate actions:** Verify cell number, viability, assay-medium composition, and treatment exposure timing. Check normalization data before repeating.
**Prevention:** Validate seeding density and assay-medium composition for each cell line before comparative runs.

### DX-002 HIGH_BASELINE_VARIABILITY

**Trigger:** Baseline replicate CV exceeds 15% within one condition across two or more replicate wells, or the trace drifts before any injection.
**Likely cause:** Uneven seeding, temperature drift, incomplete equilibration, well-to-well bubble artifact, or inconsistent attachment.
**DISTINGUISH:** Plate-wide drift points to equilibration or temperature issues; random well-specific instability points to seeding or bubbles; edge-only instability points to perimeter effects.
**Immediate actions:** Review microscopy images, equilibration time, and bubble inspection notes. Exclude mechanically failed wells.
**Prevention:** Rest the plate before incubator transfer, use 45-90 min non-CO2 equilibration with a 60 min target, and inspect every well for bubbles.

### DX-003 WEAK_OLIGOMYCIN_RESPONSE

**Trigger:** OCR falls minimally after oligomycin injection during a Mito Stress Test.
**Likely cause:** Oligomycin concentration too low, port loading failure, already ATP-synthase-limited baseline state, or wrong compound in the port.
**DISTINGUISH:** If all wells fail and port map review shows low dose, suspect underdosing; if only one sector fails, suspect loading failure; if oligomycin is active but ATP-linked respiration is biologically low, basal OCR may already be near proton-leak or non-mitochondrial range.
**Immediate actions:** Confirm port identity, stock concentration, and final dose in the well. Review baseline metabolic state and rerun with a titrated range if needed.
**Prevention:** Titrate oligomycin at 0.5, 1.0, and 2.0 µM before formal comparative studies.

### DX-004 WEAK_FCCP_RESPONSE

**Trigger:** OCR fails to rise or rises only marginally after FCCP injection.
**Likely cause:** FCCP underdosing, overdosing, low substrate support, treatment-induced mitochondrial damage, or expired FCCP stock.
**DISTINGUISH:** No rise at low doses with preserved viability suggests underdosing; OCR collapse after FCCP suggests overdosing; weak response only in one condition may be real biology if control wells show a valid rise.
**Immediate actions:** Review FCCP titration history, medium substrate composition, and stock handling.
**Prevention:** Perform cell-line-specific FCCP titration across 0.25, 0.5, 1.0, and 2.0 µM.

### DX-005 HIGH_NONCELLULAR_SIGNAL

**Trigger:** Background wells show OCR or ECAR greater than 10% of the mean sample baseline value, or chemistry-only blanks exceed the blank threshold documented in the method file.
**Likely cause:** Compound redox chemistry, media contamination, or blank-well setup mismatch.
**DISTINGUISH:** Signal in medium-only blanks suggests media or instrument background; signal only in chemistry-only blanks points to compound-driven non-cell activity.
**Immediate actions:** Subtract only when the subtraction method is validated for the assay type and signal magnitude. Rebuild matched blanks if absent.
**Prevention:** Include medium-only and chemistry-only blanks on every plate when compounds can alter oxygen consumption or acidification.

### DX-006 INJECTION_FAILURE

**Trigger:** Expected response is absent in one or more wells after a scheduled injection.
**Likely cause:** Port loading error, bubble in the port, incorrect method file, compound precipitation, or wrong port assignment.
**DISTINGUISH:** Sector-specific failure suggests loading or port issue; global failure suggests method mismatch or wrong reagent preparation.
**Immediate actions:** Review port map, loading worksheet, and raw instrument log. Do not interpret the affected injection endpoint from failed wells.
**Prevention:** Cross-check port identity against the method file before calibration and inspect loaded ports for bubbles.

### DX-007 EDGE_WELL_ARTIFACT

**Trigger:** Perimeter wells show systematically lower or noisier traces than interior wells.
**Likely cause:** Edge evaporation, temperature imbalance, or plate-handling asymmetry.
**DISTINGUISH:** If perimeter wells fail across multiple conditions while interior wells are stable, suspect edge artifact rather than biology.
**Immediate actions:** Exclude affected wells if the pattern is consistent and documented. Rebalance plate layout on rerun.
**Prevention:** Avoid placing the primary comparison exclusively on perimeter wells and keep plate handling time consistent.

### DX-008 DETACHMENT_DURING_ASSAY

**Trigger:** OCR and ECAR drop sharply with microscopy evidence of cell loss or aggregation.
**Likely cause:** Weak attachment, inadequate coating, harsh medium exchange, treatment toxicity, or mechanical disturbance during setup.
**DISTINGUISH:** Broad signal collapse with visible cell loss indicates detachment; stable microscopy with erratic trace suggests bubble or analyzer artifact instead.
**Immediate actions:** Review coating method, medium-exchange technique, and treatment toxicity controls. Reject detachment-driven wells.
**Prevention:** Validate coating chemistry and attachment window for each weakly adherent or suspension-capture workflow.

### DX-009 INVALID_PH_OR_MEDIUM_COMPOSITION

**Trigger:** Baseline is abnormal across the full plate or assay responses are inconsistent with validated historical behavior.
**Likely cause:** pH outside 7.40 ± 0.05 at 37°C, missing substrate, wrong medium base, or incorrect osmolar contribution from supplements.
**DISTINGUISH:** Plate-wide abnormality with correct seeding and hydration points to medium preparation rather than cell handling.
**Immediate actions:** Recheck pH at 37°C, verify supplement calculations, and rebuild assay medium.
**Prevention:** Prepare medium fresh on run day and document glucose, glutamine, pyruvate, and pH values.

### DX-010 NORMALIZATION_ARTIFACT

**Trigger:** Raw traces are consistent, but normalized results become highly discordant or biologically implausible.
**Likely cause:** Uneven lysis, saturated protein assay, incorrect cell counting, or mismatched normalization endpoint.
**DISTINGUISH:** If raw data support the trend but normalized data invert it, suspect normalization failure rather than Seahorse measurement failure.
**Immediate actions:** Recalculate using the stored raw data and review the normalization assay QC.
**Prevention:** Pre-validate normalization linearity and keep lysis or stain volume constant across all wells.

### DX-011 CALIBRATION_FAILURE

**Trigger:** Analyzer fails during calibration or aborts before plate measurement begins.
**Likely cause:** Incomplete cartridge hydration, incorrect calibrant volume, sensor damage, or analyzer maintenance issue.
**DISTINGUISH:** Recurrent failure before plate loading points to cartridge or analyzer status, not cell preparation.
**Immediate actions:** Verify hydration duration, calibrant volume, and analyzer maintenance logs before retry.
**Prevention:** Hydrate cartridges for 12-24 h and inspect for liquid loss or visible defects before calibration.

### DX-012 BIOLOGICAL_SUPPRESSION_NOT_TECHNICAL_FAILURE

**Trigger:** One treatment group shows persistently low OCR or ECAR, but controls and blanks behave correctly.
**Likely cause:** True treatment-induced metabolic suppression.
**DISTINGUISH:** Valid control response, stable blanks, replicate CV at or below the in-run acceptance gate, and intact normalization support a biological interpretation rather than setup failure.
**Immediate actions:** Confirm treatment identity and exposure time, then interpret with the matching biological controls.
**Prevention:** Include untreated, vehicle, and positive-control wells on every run.

### DX-013 BUBBLE_OR_MICROCHAMBER_SEALING_ARTIFACT

**Trigger:** One or a few wells show abrupt spikes, flatlining, or isolated low values inconsistent with neighboring wells and inconsistent with cell morphology.
**Likely cause:** Bubble trapped in the assay well, bubble introduced during port loading, or faulty transient microchamber sealing.
**DISTINGUISH:** Single-well or small-cluster failure with otherwise valid plate behavior and preserved microscopy strongly supports bubble or sealing artifact rather than true biology.
**Immediate actions:** Exclude the affected wells from analysis and document the pattern as mechanical artifact.
**Prevention:** Inspect assay wells and ports for bubbles immediately before calibration and before plate loading.

### DX-014 ABSENT_GLYCOLYTIC_RESPONSE

**Trigger:** ECAR fails to rise after glucose injection in a Glycolysis Stress Test.
**Likely cause:** Residual glucose in the pre-run medium, excessive substrate-free hold time, port loading failure, or incorrect assay-medium preparation.
**DISTINGUISH:** Elevated flat baseline ECAR before glucose injection suggests residual glucose; low flat ECAR through the run suggests loading failure or medium-preparation error; selective failure in one sector suggests port-specific loading error rather than plate-wide medium error.
**Immediate actions:** Verify substrate-free medium composition, confirm port A content and loading volume, and review the pre-run equilibration timeline.
**Prevention:** Use documented glucose-free assay medium for the pre-glucose phase and confirm port A loading before calibration.

---

## 5. RISK RULES

### 5.1 Risk Rules

#### RM-001

**Risk ID:** RM-001
**Category:** assay_design
**Risk:** Cell line not metabolically validated for the chosen Seahorse assay.
**Consequence:** Endpoint may be uninformative or misleading.
**Mitigation:** Run a pilot density and compound titration before comparative experiments.

#### RM-002

**Risk ID:** RM-002
**Category:** biosample_integrity
**Risk:** Mycoplasma-positive culture enters Seahorse workflow.
**Consequence:** OCR, ECAR, and treatment response become uninterpretable.
**Mitigation:** Use only mycoplasma-negative cultures with a documented recent test.

#### RM-003

**Risk ID:** RM-003
**Category:** cell_loading
**Risk:** Cells are over-confluent or under-confluent at assay start.
**Consequence:** Baseline and drug response shift independently of the intended variable.
**Mitigation:** Validate and record a target seeding density and confluence window for the cell line.

#### RM-004

**Risk ID:** RM-004
**Category:** attachment_control
**Risk:** Coating chemistry does not match cell attachment behavior.
**Consequence:** Partial detachment and noisy traces occur during the run.
**Mitigation:** Validate Poly-D-lysine or Cell-Tak use for weakly adherent or suspension-capture workflows.

#### RM-005

**Risk ID:** RM-005
**Category:** cell_loading
**Risk:** Uneven cell distribution during seeding.
**Consequence:** Replicate spread increases and plate-map comparisons weaken.
**Mitigation:** Rest the plate at 20-25°C for 20 min before incubator transfer and verify distribution by microscopy.

#### RM-006

**Risk ID:** RM-006
**Category:** cartridge_preparation
**Risk:** Cartridge hydration time is too short.
**Consequence:** Calibration failure or unstable sensor behavior occurs.
**Mitigation:** Hydrate cartridges for 12-24 h at 37°C in a non-CO2 incubator.

#### RM-007

**Risk ID:** RM-007
**Category:** cartridge_preparation
**Risk:** Calibrant volume is incorrect for the analyzer format.
**Consequence:** Calibration fails or sensor output drifts.
**Mitigation:** Use the exact format-specific calibrant volume recorded in the lab method.

#### RM-008

**Risk ID:** RM-008
**Category:** medium_control
**Risk:** Assay medium pH is not adjusted at 37°C.
**Consequence:** Plate-wide signal distortion occurs.
**Mitigation:** Warm medium first, then adjust to pH 7.40 ± 0.05 at 37°C.

#### RM-009

**Risk ID:** RM-009
**Category:** medium_control
**Risk:** Wrong substrate composition is used for the assay type.
**Consequence:** Baseline metabolism and injection response become misleading.
**Mitigation:** Record glucose, glutamine, pyruvate, and pH values on the run sheet before medium exchange.

#### RM-010

**Risk ID:** RM-010
**Category:** equilibration_control
**Risk:** Non-CO2 equilibration is too short.
**Consequence:** Baseline instability and drift occur.
**Mitigation:** Equilibrate the assay plate for 45-90 min at 37°C in a non-CO2 incubator, with a 60 min target.

#### RM-011

**Risk ID:** RM-011
**Category:** compound_control
**Risk:** Compounds are prepared from degraded or misidentified stock.
**Consequence:** Dose response and interpretation collapse.
**Mitigation:** Track lot, preparation date, storage condition, and stock identity before port loading.

#### RM-012

**Risk ID:** RM-012
**Category:** dose_optimization
**Risk:** Oligomycin concentration is not titrated for the cell line.
**Consequence:** ATP-linked respiration is underestimated or artifactual.
**Mitigation:** Titrate 0.5, 1.0, and 2.0 µM before formal data collection.

#### RM-013

**Risk ID:** RM-013
**Category:** dose_optimization
**Risk:** FCCP concentration is not titrated for the cell line.
**Consequence:** Maximal respiration is underestimated or collapsed by overdosing.
**Mitigation:** Titrate 0.25, 0.5, 1.0, and 2.0 µM before formal data collection.

#### RM-014

**Risk ID:** RM-014
**Category:** method_execution
**Risk:** Port map does not match the method file.
**Consequence:** Injection interpretation becomes invalid.
**Mitigation:** Cross-check port identity against the analyzer method immediately before calibration.

#### RM-015

**Risk ID:** RM-015
**Category:** background_control
**Risk:** Medium-only blanks are absent.
**Consequence:** Instrument and media background cannot be evaluated.
**Mitigation:** Reserve background wells on every plate.

#### RM-016

**Risk ID:** RM-016
**Category:** background_control
**Risk:** Chemistry-only blanks are absent when compounds consume oxygen or alter acidification.
**Consequence:** Non-cellular signal may be misattributed to cells.
**Mitigation:** Include matched chemistry-only blanks for each relevant condition.

#### RM-017

**Risk ID:** RM-017
**Category:** plate_layout
**Risk:** Edge wells are used without plate-position control.
**Consequence:** Perimeter artifacts bias condition comparisons.
**Mitigation:** Randomize layout or avoid assigning the entire primary comparison to perimeter wells.

#### RM-018

**Risk ID:** RM-018
**Category:** method_execution
**Risk:** Plate orientation is incorrect when loaded into the analyzer.
**Consequence:** Plate map and data file no longer match.
**Mitigation:** Confirm plate orientation physically and in the method file before run start.

#### RM-019

**Risk ID:** RM-019
**Category:** normalization_control
**Risk:** Post-run normalization method is not validated for the cell type.
**Consequence:** Real metabolic differences may be obscured or reversed.
**Mitigation:** Pre-validate linear range and keep normalization chemistry consistent across wells.

#### RM-020

**Risk ID:** RM-020
**Category:** data_review
**Risk:** Exclusion decisions are made after looking only at endpoint summaries.
**Consequence:** Biased data curation and false conclusions.
**Mitigation:** Review raw traces, microscopy, blanks, and normalization QC before excluding wells.

#### RM-021

**Risk ID:** RM-021
**Category:** treatment_toxicity
**Risk:** Treatment toxicity causes cell loss before or during the assay.
**Consequence:** Apparent metabolic suppression may reflect viability loss rather than pathway-specific regulation.
**Mitigation:** Pair Seahorse runs with viability or morphology controls at the same exposure time.

#### RM-022

**Risk ID:** RM-022
**Category:** cross_plate_comparison
**Risk:** Derived parameters are compared across plates without matched controls.
**Consequence:** Day-to-day drift is misread as biology.
**Mitigation:** Include internal control conditions on every plate and compare normalized control-relative values.

#### RM-023

**Risk ID:** RM-023
**Category:** bubble_artifact
**Risk:** Bubble remains in an assay well or sensor port.
**Consequence:** Single-well spikes, flatlining, or false low signals appear.
**Mitigation:** Inspect assay wells and loaded ports for bubbles immediately before calibration and plate loading.

### 5.2 Containment Failures

#### CF-001

**Failure ID:** CF-001
**Category:** calibration_failure
**Failure class:** Calibration failure before plate measurement.
**Containment action:** Stop the run, document hydration time and calibrant volume, and do not interpret any downstream data from the failed attempt.

#### CF-002

**Failure ID:** CF-002
**Category:** plate_invalidity
**Failure class:** Plate-wide invalid baseline caused by pH or equilibration error.
**Containment action:** Reject the plate for interpretation, rebuild assay medium, and repeat equilibration with documented pH at 37°C.

#### CF-003

**Failure ID:** CF-003
**Category:** injection_failure
**Failure class:** Injection sequence mismatch or widespread injection failure.
**Containment action:** Freeze interpretation at the raw-trace review stage, verify method and port map, and rerun with rebuilt compounds if mismatch is confirmed.

---

## 6. PARAMETER CONSTRAINTS

| Parameter | Minimum | Target | Maximum | Notes |
|-----------|---------|--------|---------|-------|
| Assay-medium pH at 37°C | 7.35 | 7.40 | 7.45 | Re-adjust at 37°C if outside range before plate loading |
| Non-CO2 equilibration time | 45 min | 60 min | 90 min | Beyond 90 min, verify that the cell line remains stable under the chosen medium |
| XF96 seeding volume | 80 µL | 100 µL | 100 µL | Do not exceed 100 µL; excess volume can overflow the well and disturb seeding uniformity |
| XF24 seeding volume | 150 µL | 250 µL | 250 µL | Do not exceed 250 µL; excess volume can overflow the well and disturb seeding uniformity |
| XF96 assay volume | 175 µL | 180 µL | 185 µL | Record the actual loaded value if outside target and repeat the exchange if outside range |
| XF24 assay volume | 490 µL | 500 µL | 510 µL | Record the actual loaded value if outside target and repeat the exchange if outside range |
| Oligomycin final concentration | 0.5 µM | 1.0 µM | 2.0 µM | Titrate per cell line |
| FCCP final concentration | 0.25 µM | 0.5-1.0 µM | 2.0 µM | Overdosing can collapse OCR |
| Rotenone final concentration | 0.25 µM | 0.5 µM | 1.0 µM | Validate with antimycin A pair |
| Antimycin A final concentration | 0.25 µM | 0.5 µM | 1.0 µM | Validate with rotenone pair |
| XF96 lysis volume for protein normalization | 20 µL | 25 µL | 30 µL | Keep constant across the plate |
| XF24 lysis volume for protein normalization | 50 µL | 75 µL | 100 µL | Match assay sensitivity to chosen volume |

---

## 7. QUALITY CONTROL AND ACCEPTANCE GATES

### 7.1 Pre-Run Gates

- Cartridge hydrated for 12-24 h at 37°C in a non-CO2 incubator
- Assay-medium pH is 7.40 ± 0.05 at 37°C
- Cells show even attachment or verified capture by microscopy, with no plate-wide detachment pattern
- Medium-only blanks and chemistry-only blanks are present when required
- Port map matches the analyzer method file

### 7.2 In-Run Gates

- Calibration completes without analyzer error
- Baseline CV across replicate wells is ≤15% per condition; flag 15-25% for review and reject plate-wide values above 25%
- Control wells show the expected directional response after injection
- No widespread flatline, sector failure, or global injection miss is observed

### 7.3 Post-Run Gates

- Raw traces reviewed before exclusion or normalization
- Excluded wells are documented with a technical justification
- Normalization QC is within the validated linear range for the chosen method, replicate normalization values show CV ≤20%, and no accepted well falls below the method detection limit
- Run status recorded as accepted, accepted with limits, or rejected

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified Seahorse issue and root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in the diagnosis based on trace pattern, blanks, and QC evidence |
| recommended_actions | list[string] | Ordered corrective-action list with the first recovery action first |
| linked_risks | list[{risk_id, category, severity, note}] | Active risk rules from Sections 4 and 5 relevant to the result |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| gate_status | dict {gate_id: pass / fail / limited} | Pass, fail, or limited status for each QC gate |
| parameter_violations | list[{param, observed, expected, dx_rule}] | Parameters outside the allowed range linked to the relevant diagnostic rule |
| protocol_section_reference | string | Section of SOP-SEAHORSE-001 relevant to the issue |
| signature_status | enum: expected / partial / failed / indeterminate | Whether injection responses matched the planned assay |
| normalization_status | enum: valid / questionable / failed / not_performed | Status of the selected normalization method |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|-------------------|
| cell_culture_placeholder_v1 | Related skill placeholder for cell-health recovery, seeding optimization, attachment rescue, or contamination control before Seahorse analysis |
| transfection_placeholder_v1 | Related skill placeholder for plasmid, siRNA, or mRNA perturbation of metabolic genes before Seahorse analysis |
| crispr_cas9_placeholder_v1 | Related skill placeholder for gene knockout or edited metabolic-pathway workflows linked to extracellular flux phenotypes |
| western_blot_placeholder_v1 | Related skill placeholder for AMPK, mTOR, OXPHOS, or other protein validation after Seahorse findings |
| immunofluorescence_placeholder_v1 | Related skill placeholder for mitochondrial morphology, membrane potential, or cell-count normalization by microscopy |
| flow_cytometry_placeholder_v1 | Related skill placeholder for viability, ROS, mitochondrial mass, or membrane-potential measurements linked to Seahorse results |
| elisa_placeholder_v1 | Related skill placeholder for secreted lactate, cytokine, or metabolite-linked immunoassay support after flux analysis |
| metabolomics_placeholder_v1 | Related skill placeholder for orthogonal metabolite profiling to confirm flux-derived pathway interpretation |
