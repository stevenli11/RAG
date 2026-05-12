---
skill_id: method_seven_elisa_v1
skill_name: ELISA Complete Workflow Skill
version: 1.0
method_family: immunoassay
tags: [elisa, sandwich_elisa, indirect_elisa, direct_elisa, competitive_elisa, plate_coating, blocking, sample_preparation, standard_curve, wash_steps, tmb, hrp, absorbance, assay_validation, qc, troubleshooting]
applies_to: [protein_quantification, cytokine_quantification, biomarker_measurement, serum_samples, plasma_samples, cell_culture_supernatants, lysates, purified_antigen]
does_not_apply_to: [multiplex_bead_assays, lateral_flow_assays, western_blot_only, immunohistochemistry, mass_spectrometry, flow_cytometry_only, point_of_care_cartridge_assays]
risk_level: medium
bsl_level: "BSL-2 for human-derived specimens; BSL-1 for purified non-infectious reagents"
last_updated: 2026-03-17
source_protocol: SOP-ELISA-007
---

---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I run an ELISA," "my calibrator curve looks wrong," "why is my blank high," "how do I prepare samples for ELISA," "my duplicate wells do not match," "how do I set up a sandwich ELISA," "why is my plate edge signal higher," "how long do I incubate the substrate," "how do I calculate concentrations from a 4PL curve," "my samples are out of range," "how do I validate recovery or dilution linearity," "how many washes should I do," or any question about enzyme-linked immunosorbent assay setup, execution, quantification, troubleshooting, and quality control. This skill covers complete ELISA workflow planning and execution for sandwich ELISA, indirect ELISA, direct ELISA, and competitive ELISA, including plate map design, reagent equilibration, plate coating, blocking, sample and calibrator preparation, incubation planning, wash execution, detection reagent handling, substrate development, plate reading, curve fitting, acceptance criteria, and structured diagnostic rules for high background, weak signal, hook effect, poor precision, edge effects, drift, carryover, and matrix interference. This skill does NOT cover multiplex bead assays, chemiluminescent immunoassays requiring dedicated automation, lateral-flow cartridge methods, Western blot confirmation workflows, immunohistochemistry, or mass-spectrometry-based biomarker quantification. Redirect those queries to the correct skill when those assay families are requested.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| elisa_format | enum: sandwich / indirect / direct / competitive | Assay architecture driving reagent order and interpretation |
| analyte_name | string | Target molecule being quantified or detected |
| sample_matrix | enum: serum / plasma_edta / plasma_heparin / plasma_citrate / cell_culture_supernatant / lysate / urine / csf / purified_buffer | Matrix affects dilution, interference, and recovery expectations |
| assay_goal | enum: absolute_quantification / relative_quantification / titer / screening / validation / troubleshooting | Primary use case for the assay run |
| plate_type | enum: pre_coated_96 / high_binding_96 / strip_well_96 | Plate format determines coating step and handling plan |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| standard_top_concentration | float | Highest calibrator concentration in pg/mL, ng/mL, or IU/mL |
| dilution_series | string | Calibrator dilution pattern such as "1:2 serial, 8 points" |
| replicate_scheme | string | Single / duplicate / triplicate layout used for standards and samples |
| blank_od | float | Optical density of substrate blank or zero calibrator |
| highest_standard_od | float | Optical density of the highest calibrator |
| cv_percent | float | Replicate coefficient of variation |
| wash_cycles | int | Number of full wash cycles performed between steps |
| wash_volume_per_well | float | Volume dispensed per wash in µL |
| incubation_profile | string | Recorded incubation temperatures and times for assay steps |
| sample_dilution | string | Sample dilution ratio such as "1:5" or "neat" |
| substrate_development_time | float (min) | Time from TMB addition to stop solution addition |
| reader_wavelength_nm | string | Primary and reference wavelengths such as "450/570" |
| storage_history | string | Freeze-thaw count and storage temperature for samples and reagents |
| curve_fit_model | enum: linear / 4pl / 5pl / log_log / unknown | Fitting model used for concentration interpolation |
| plate_seal_status | enum: sealed_all_incubations / partly_sealed / unsealed / unknown | Evaporation control during incubations |

---

## 3. WORKFLOW MODULES

### Module 1: ASSAY_PLANNING_AND_PLATE_MAP

**Preconditions:** Assay format, analyte, dynamic range target, and sample matrix have been defined. A validated kit insert or in-house assay design document is available. Calibrated single-channel and multichannel pipettes are available with matching tips.
**Pause point:** YES — assay plan and plate map may be prepared up to 24 h before the run if reagents remain refrigerated at 2–8°C and the plate remains sealed in original packaging.

#### Steps:

**PLATE MAP DESIGN:**
1. Define the assay objective before touching reagents: absolute concentration, relative rank-ordering, endpoint titer, or screen/fail. This determines calibrator density and dilution plan.
2. [CRITICAL] Allocate wells for blank, zero calibrator, full calibrator curve, matrix control, positive control, negative control, and unknown samples before loading any liquids.
3. Use duplicate wells for all standards and controls. Use duplicate or triplicate wells for unknown samples when sample volume permits. Duplicate layout is the minimum for quantification claims.
4. Keep one full calibrator curve on each plate. Do not interpolate unknown concentrations across plates using a curve generated on a different plate.
5. Reserve outer wells for buffer or lower-priority samples when the incubation environment is prone to evaporation. If edge positions are used for unknowns, fill all unused wells with 300 µL wash buffer or assay diluent.
6. Arrange standards from low to high concentration left to right or top to bottom and maintain the same order on every plate in the project.
7. [BEGINNER TRAP] Do not place high-concentration samples adjacent to blanks when using manual pipetting. Aerosol or splash carryover inflates nearby low-signal wells.
8. Record the exact identity, dilution factor, and intended well position for every sample in a plate map table before starting.
9. Define acceptance criteria in advance:
   - Blank OD at 450 nm after reference subtraction: ≤0.150
   - Duplicate CV for standards and controls: ≤10%
   - Duplicate CV for unknowns: ≤15%
   - Back-calculated calibrator recovery: 80–120% for non-zero points
   - Control recovery: within assigned range
10. Select the fitting model before data collection:
   - Sandwich ELISA: 4PL default
   - Competitive ELISA: 4PL with inverse slope
   - Indirect ELISA titer readout: endpoint threshold or log-log
   - Use 5PL only if asymmetry is validated on at least 6 independent runs

#### Exit Criteria (must ALL be true to proceed):
- Plate map includes blanks, zero calibrator, standards, controls, and unknowns
- Acceptance criteria are defined in writing
- Replicate strategy is fixed before reagent dispensing
- A fitting model has been selected
- Outer-well handling plan is documented

---

### Module 2: REAGENT_EQUILIBRATION_AND_BUFFER_PREPARATION

**Preconditions:** Required kit reagents, wash buffer concentrate, assay diluent, standards, capture reagent, detection reagent, substrate, and stop solution are present and within expiry. Deionized water with resistivity ≥18 MΩ·cm is available for buffer preparation.
**Pause point:** YES — prepared wash buffer may be stored at 2–8°C for 7 days. Reconstituted protein standards and working detection mixes follow the storage window in the assay insert or this module.

#### Steps:

**TEMPERATURE EQUILIBRATION:**
1. Remove kit reagents from 2–8°C storage and equilibrate at 20–25°C for 30 min before opening containers.
2. Keep TMB substrate protected from light during equilibration. Do not warm substrate above 25°C.
3. Mix liquid reagents by inversion 10 times or by low-speed roller mixing for 2 min. Do not vortex HRP conjugates or capture antibodies.

**WASH BUFFER PREPARATION:**
4. Prepare 1× wash buffer from concentrate using exact volumes. Example for 1,000 mL from 20× concentrate:

| Component | Volume |
|-----------|--------|
| 20× wash concentrate | 50 mL |
| Deionized water | 950 mL |
| **Total** | **1,000 mL** |

5. If crystals are visible in wash concentrate, incubate the sealed bottle at 25°C for 20 min and invert 15 times until dissolved.
6. For one 96-well plate with manual washing, prepare at least 800 mL 1× wash buffer when running 5 wash cycles after four reagent additions. This supports 300 µL/well/cycle plus dead volume.

**CALIBRATOR AND CONTROL RECONSTITUTION:**
7. Reconstitute lyophilized calibrator with the exact volume stated in the assay design. Example: add 500 µL calibrator diluent to a lyophilized vial labeled for 2,000 pg/mL top concentration.
8. Incubate the reconstituted calibrator at 20–25°C for 15 min, then mix by inversion 15 times.
9. Prepare serial dilutions in low-protein-binding tubes using exact transfer volumes. Example 1:2 series from 2,000 pg/mL:

| Tube | Diluent | Transfer | Final concentration |
|------|---------|----------|--------------------|
| S1 | 0 µL | stock | 2,000 pg/mL |
| S2 | 250 µL | 250 µL from S1 | 1,000 pg/mL |
| S3 | 250 µL | 250 µL from S2 | 500 pg/mL |
| S4 | 250 µL | 250 µL from S3 | 250 pg/mL |
| S5 | 250 µL | 250 µL from S4 | 125 pg/mL |
| S6 | 250 µL | 250 µL from S5 | 62.5 pg/mL |
| S7 | 250 µL | 250 µL from S6 | 31.25 pg/mL |
| S8 | 250 µL | 250 µL from S7 | 15.625 pg/mL |
| Zero | 250 µL | none | 0 pg/mL |

10. Change tips between every dilution transfer. Mix each dilution by pipetting 8 times with 200 µL strokes before moving to the next tube.
11. Prepare controls at the same matrix or diluent composition used for the assigned target values.

**WORKING DETECTION REAGENT:**
12. Prepare detection antibody or conjugate only for the current run. Example: 12 mL working solution for one plate plus dead volume using a 100× stock:

| Component | Volume |
|-----------|--------|
| 100× detection stock | 120 µL |
| assay diluent | 11.88 mL |
| **Total** | **12.00 mL** |

13. Protect HRP-containing working reagent from prolonged light exposure and use within 2 h at 20–25°C.

#### Exit Criteria (must ALL be true to proceed):
- All reagents reached 20–25°C for 30 min before use
- Wash buffer is fully dissolved and prepared at the exact dilution
- Standards were reconstituted with exact volumes and mixed in sequence
- Detection working solution is freshly prepared for the run
- Enough wash buffer is available for the full plate and dead volume

---

### Module 3: PLATE_COATING_AND_BLOCKING

**Preconditions:** High-binding 96-well plate is available for in-house ELISA, or pre-coated plate identity has been verified for kit workflow. Capture antibody concentration and coating buffer composition are defined.
**Pause point:** YES — coated and blocked plates may be stored sealed at 2–8°C for up to 7 days only if assay validation has shown equivalent performance. If no validation exists, use the plate on the same day after blocking.

#### Steps:

**CAPTURE COATING FOR SANDWICH ELISA OR ANTIGEN COATING FOR INDIRECT ELISA:**
1. If using a pre-coated kit plate, skip to Step 8 and verify lot number before opening the foil pouch.
2. Prepare coating solution in carbonate-bicarbonate buffer, pH 9.6. Example for capture antibody at 2 µg/mL in 12 mL:

| Component | Volume |
|-----------|--------|
| capture antibody stock at 0.5 mg/mL | 48 µL |
| coating buffer | 11.952 mL |
| **Total** | **12.000 mL** |

3. Dispense 100 µL per well using a multichannel pipette. Avoid touching the well bottom with the tip.
4. Seal the plate with adhesive film.
5. Incubate at 4°C for 16 h or at 20–25°C for 2 h. Use one condition per validated assay and keep it fixed across runs.
6. Remove coating solution by aspiration or inversion, then wash 3 times with 300 µL/well 1× wash buffer.
7. Tap the inverted plate firmly on lint-free absorbent towels after the final wash to remove residual liquid.

**BLOCKING:**
8. Prepare blocking buffer validated for the assay. Example: 1% BSA in PBS, 12 mL total:

| Component | Volume |
|-----------|--------|
| 10% BSA stock | 1.2 mL |
| PBS | 10.8 mL |
| **Total** | **12.0 mL** |

9. Add 200 µL blocking buffer per well.
10. Seal the plate and incubate at 20–25°C for 1 h.
11. Remove blocking buffer and wash 3 times with 300 µL/well wash buffer unless the validated method specifies direct sample addition without a post-block wash.
12. [VISUAL CHECK] Inspect wells after aspiration. No well should contain residual droplets larger than approximately 20 µL after tapping.

#### Exit Criteria (must ALL be true to proceed):
- Coating concentration, buffer, volume, temperature, and time were recorded
- Plate remained sealed for the full incubation
- Blocking buffer volume was 200 µL/well
- Post-block residual liquid was minimized by aspiration and tapping
- Plate lot and coating lot are documented

---

### Module 4: SAMPLE_HANDLING_AND_DILUTION

**Preconditions:** Samples are labeled, storage history is known, and freeze-thaw count has been recorded. Biosafety controls for the sample matrix are in place.
**Pause point:** YES — aliquoted samples may remain on wet ice for up to 2 h before dilution. Diluted samples should be loaded to the plate within 30 min unless assay validation supports longer bench stability.

#### Steps:

**SAMPLE THAW AND CLARIFICATION:**
1. Thaw frozen serum, plasma, supernatant, or lysate samples at 2–8°C overnight or at 20–25°C for 20–30 min.
2. Mix samples by inversion 10 times after thawing. Do not vortex serum or plasma intended for low-abundance analytes.
3. Clarify particulate material before loading:
   - serum or plasma: centrifuge at 2,000 ×g, 4°C, 10 min
   - cell culture supernatant: centrifuge at 500 ×g, 4°C, 5 min
   - lysate: centrifuge at 10,000 ×g, 4°C, 10 min
4. Transfer clarified supernatant to a fresh low-binding tube without disturbing the pellet.

**DILUTION STRATEGY:**
5. Start with matrix-specific screening dilutions when the concentration is unknown:
   - serum cytokine target: 1:2 to 1:10
   - plasma cytokine target: 1:2 to 1:10
   - cell culture supernatant: neat to 1:20
   - lysate: normalize to total protein, then begin at 100 µg/mL total protein equivalent
6. Prepare dilutions using assay diluent that matches the calibrator matrix when available.
7. Example 1:5 dilution:

| Component | Volume |
|-----------|--------|
| sample | 50 µL |
| assay diluent | 200 µL |
| **Total** | **250 µL** |

8. Example 1:20 dilution:

| Component | Volume |
|-----------|--------|
| sample | 15 µL |
| assay diluent | 285 µL |
| **Total** | **300 µL** |

9. Mix each dilution by pipetting 8 times with complete aspiration and dispense cycles.
10. For high-risk hook-effect targets, prepare at least two dilutions per sample separated by at least 10-fold.
11. Keep samples covered during bench handling to limit evaporation and contamination.

#### Exit Criteria (must ALL be true to proceed):
- Freeze-thaw count is recorded for every sample
- Samples were clarified with matrix-matched centrifugation settings
- At least one justified dilution was prepared for each sample
- Dilution factors are documented in the plate map
- Diluted samples are scheduled for loading within 30 min

---

### Module 5: SAMPLE_AND_STANDARD_LOADING_WITH_INCUBATION

**Preconditions:** Plate has completed coating/blocking or a pre-coated plate is ready. Standards, controls, and diluted samples are prepared. Timer, plate seal, and loading order are ready before dispensing begins.
**Pause point:** NO — once the first calibrator or sample is added, complete loading of the full plate without interruption. Timing differences during loading shift signal across the plate.

#### Steps:

**LOADING:**
1. Load wells in the pre-written plate map order using fresh tips for every transfer.
2. Dispense 100 µL/well for standards, controls, and unknowns unless the validated assay volume differs. Keep the dispense angle and immersion depth consistent.
3. Touch tips only to the upper side wall of the well, not the coated bottom.
4. Use a multichannel pipette for row- or column-based loading whenever possible to reduce elapsed loading time.
5. Complete loading of one 96-well plate within 10 min. If loading takes longer than 10 min, note the elapsed time and rotate loading direction on future runs to evaluate drift.
6. Seal the plate immediately after loading.

**INCUBATION:**
7. Incubate sample-loaded plate at one validated setting:
   - 20–25°C for 2 h
   - 37°C for 1 h
   - 4°C for 16 h
8. Keep the plate on a microplate shaker only if the validated method includes shaking. Example validated setting: 500 rpm orbital, 20–25°C, 1 h.
9. Do not stack plates during sample incubation unless the shaker and validation data show equivalent mixing across positions.
10. At the end of incubation, remove liquid completely and begin washes within 2 min.

#### Exit Criteria (must ALL be true to proceed):
- Every loaded well received the intended volume
- Plate loading time is recorded
- Plate remained sealed during incubation
- Incubation temperature and time match the validated setting
- Wash step begins within 2 min of incubation end

---

### Module 6: WASH_EXECUTION

**Preconditions:** Wash buffer is prepared and at 20–25°C. Manual wash bottle or automated plate washer settings are verified. Waste reservoir is empty enough for the planned run.
**Pause point:** NO — wash cycles are part of the active assay sequence and should continue directly into the next reagent step.

#### Steps:

**MANUAL WASHING:**
1. Aspirate or flick plate contents into a waste container lined with absorbent material containing 10% bleach.
2. Add 300 µL 1× wash buffer to each well for every cycle.
3. Let wash buffer remain in wells for 20 sec on cycle 1 of each wash block when background has historically been high. For all other cycles, immediate aspiration is acceptable.
4. Perform 4 wash cycles after sample incubation and 5 wash cycles after HRP-conjugate incubation unless validation sets another number.
5. After the final cycle of each wash block, invert the plate and tap firmly on fresh lint-free absorbent towels 3 times.
6. Inspect three representative wells for residual liquid. If droplets exceed approximately 10 µL, repeat one full wash cycle.

**AUTOMATED WASHER SETTINGS:**
7. Example validated washer profile:
   - dispense volume: 300 µL/well
   - soak time: 20 sec
   - aspiration height: 1.5 mm from well bottom
   - dispense height: 6.0 mm
   - cycles: 4 or 5 per block
8. Prime washer lines with 50 mL wash buffer before starting the plate.
9. At the end of the run, flush washer lines with 200 mL deionized water to reduce salt buildup.

#### Exit Criteria (must ALL be true to proceed):
- Wash volume was 300 µL/well for every cycle
- Correct cycle count was applied for the assay stage
- Residual liquid after the final tap is minimal
- No wells overflowed or dried out during the wash block
- Washer settings or manual method were recorded

---

### Module 7: DETECTION_REAGENT_AND_SUBSTRATE_DEVELOPMENT

**Preconditions:** Plate wash after sample incubation is complete. Detection reagent and substrate are prepared or equilibrated. Stop solution is ready for immediate use.
**Pause point:** NO — substrate development must be monitored continuously and stopped at the planned endpoint.

#### Steps:

**DETECTION REAGENT:**
1. Add 100 µL/well detection antibody or HRP conjugate working solution.
2. Seal the plate and incubate:
   - detection antibody without enzyme label: 20–25°C for 1 h, then wash 4 times and continue with streptavidin-HRP at 100 µL/well for 20–25°C, 30 min
   - directly labeled HRP detection reagent: 20–25°C for 1 h
3. After HRP-containing incubation, wash 5 times with 300 µL/well wash buffer.

**SUBSTRATE DEVELOPMENT:**
4. Add 100 µL/well TMB substrate. Start the timer at the moment TMB reaches the first well.
5. Incubate protected from light at 20–25°C for 5–20 min depending on signal development.
6. Monitor color in the highest calibrator and blank:
   - target for highest calibrator before stop: medium to strong blue without visible saturation
   - blank should remain colorless to very pale blue
7. Stop the reaction by adding 100 µL/well 1 N sulfuric acid or validated stop solution in the same order and pace used for TMB addition.
8. Mix plate contents by tapping the plate frame 5 times after stop solution addition.

#### Exit Criteria (must ALL be true to proceed):
- Detection reagent volume was 100 µL/well
- HRP-containing incubation received 5 wash cycles afterward
- TMB development time is recorded to the minute
- Stop solution was added to every well in the same sequence as TMB
- Highest calibrator is not visibly overdeveloped before reading

---

### Module 8: PLATE_READING_AND_DATA_ANALYSIS

**Preconditions:** Reaction has been stopped and the plate bottom is clean. Plate reader wavelength settings and reader path are verified.
**Pause point:** NO — read the plate within 30 min after adding stop solution unless the assay validation supports a longer post-stop window.

#### Steps:

**PLATE READ:**
1. Wipe the underside of the plate with lint-free tissue to remove fingerprints or droplets.
2. Read absorbance at 450 nm with reference correction at 570 nm or 620 nm when the reader supports it.
3. Complete plate read within 30 min of stop solution addition.

**DATA PROCESSING:**
4. Subtract reference wavelength from primary wavelength for every well if dual-read mode is used.
5. Average replicate ODs only after checking replicate agreement.
6. Calculate replicate CV:
   - CV% = (SD / mean) × 100
7. Fit a 4PL curve for sandwich or competitive ELISA unless assay validation has established another model.
8. Back-calculate calibrator concentrations and confirm 80–120% recovery for non-zero calibrators.
9. Interpolate unknowns from the accepted curve and multiply by the recorded dilution factor.
10. Re-run samples above the top calibrator after higher dilution. Re-run samples below the lower quantifiable point as lower dilution or report below quantifiable range according to the assay objective.
11. For validation or batch release runs, review dilution linearity and spike recovery:
   - dilution linearity target: 80–120%
   - spike recovery target: 80–120%

#### Exit Criteria (must ALL be true to proceed):
- Plate was read within 30 min after stop solution
- Reader wavelength and reference settings are recorded
- Replicate CV was checked before averaging
- Curve fit and back-calculation meet assay acceptance criteria
- Final reported concentrations include dilution factor correction

---

### Module 9: POST_RUN_QC_AND_STORAGE

**Preconditions:** Data analysis is complete and raw files are saved. Remaining reagents and plate waste are still available for disposition.
**Pause point:** YES — records may be finalized after the bench cleanup, but raw data and plate map must be saved before discarding the plate.

#### Steps:

**QC REVIEW:**
1. Review blank OD, control recovery, calibrator curve shape, replicate CV, and sample range placement.
2. Flag any sample that required extrapolation beyond the validated quantifiable range.
3. Compare current plate control values against the previous 10 runs when historical data exist.

**STORAGE AND DISPOSAL:**
4. Store unused concentrated reagents at 2–8°C immediately after the run.
5. Discard diluted standards, diluted detection working solutions, and used substrate at the end of the run unless the assay insert defines a short validated hold time.
6. Decontaminate liquid waste containing human specimens with 10% bleach for 20 min before drain disposal if institutional policy allows drain disposal.
7. Dispose of used plates, seals, and contaminated tips as biohazardous solid waste when human-derived specimens were loaded.
8. Save the following records in the assay folder: plate map, raw reader file, analyzed spreadsheet, lot numbers, operator, run date, and deviations.

#### Exit Criteria (must ALL be true to proceed):
- Raw data and plate map are saved
- QC review was completed and deviations were logged
- Remaining stock reagents were returned to 2–8°C storage
- Human-derived waste received bleach contact time of 20 min or approved equivalent disposal
- Final report includes lot numbers and operator identity

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: plate_readout
CONDITION: Blank wells show OD >0.150 after reference subtraction and the zero calibrator is elevated across the plate
DIAGNOSIS: High background from inadequate washing, contaminated substrate, or non-specific binding
CONFIDENCE: high
LIKELY_CAUSES:
  - Residual HRP conjugate remained in wells because wash cycles were too few or aspiration was incomplete
  - Blocking chemistry is mismatched to plate surface or sample matrix
  - TMB substrate was contaminated by HRP carryover or exposed to oxidizing contaminants
  - Plate dried between wash and reagent addition, increasing non-specific adsorption
DISTINGUISH:
  - Compare blank OD pattern across the plate: uniformly high suggests substrate or reagent contamination; row-specific or column-specific elevation suggests washer or pipetting issue
  - Inspect unused TMB in the reservoir: if it is already pale blue before dispensing, substrate contamination is likely
  - Review wash logs: <4 cycles after sample incubation or <5 cycles after HRP incubation strongly supports incomplete washing
  - Check whether blanks lacking detection reagent are low while full blanks are high; this points to conjugate-driven background rather than plate coating alone
IMMEDIATE_FIX:
  - Prepare fresh TMB and detection working solution
  - Increase wash count by 1 cycle and confirm 300 µL/well volume with firm final tapping
  - Repeat the assay with fresh blocking buffer and sealed incubations
PREVENTION: Validate blocking chemistry for the matrix; flush washer lines daily; protect TMB from light and contamination; never allow wells to dry between assay steps

---

### RULE DX-002
STAGE: plate_readout
CONDITION: Highest calibrator OD is weak, top point is <0.600, and unknowns cluster near blank values
DIAGNOSIS: Low signal from degraded capture or detection reagents, under-incubation, or incorrect reagent preparation
CONFIDENCE: high
LIKELY_CAUSES:
  - Capture antibody or coated antigen concentration is too low
  - Detection reagent was diluted too far or prepared with incorrect buffer
  - Incubation time or temperature was below the validated target
  - Stop solution was added after very short substrate development
DISTINGUISH:
  - Compare blank and top calibrator: low blank plus low top signal favors reagent or incubation failure rather than background
  - Review reconstitution math for standards and detection reagent preparation
  - Confirm incubation profile from bench notes: 20–25°C for 30 min instead of 60 min often halves signal
  - Check whether the issue appears only on one plate lot; this raises a coating failure hypothesis
IMMEDIATE_FIX:
  - Reprepare detection working solution and repeat the assay with fresh standards
  - Extend validated substrate development toward the upper end of the allowed window, such as 15 min instead of 8 min
  - Verify capture coating concentration and remake coated plate if using an in-house format
PREVENTION: Use second-person verification for dilution setup; record every incubation start and stop time; qualify new plate and antibody lots against a reference lot

---

### RULE DX-003
STAGE: sample_quantification
CONDITION: Replicate wells show CV >15% for unknowns or >10% for standards and controls
DIAGNOSIS: Poor precision driven by pipetting inconsistency, incomplete mixing, evaporation, or particulate interference
CONFIDENCE: high
LIKELY_CAUSES:
  - Pipette calibration drift or mismatch between pipette range and transfer volume
  - Standards or diluted samples were not mixed fully before loading
  - Plate remained unsealed during incubation causing well-to-well evaporation
  - Bubbles or particulates in selected wells altered optical readout
DISTINGUISH:
  - If poor precision is worst in one row or one column, multichannel pipetting or washer alignment is implicated
  - If only viscous matrices show poor precision, matrix mixing and particulate load are primary suspects
  - Inspect raw well images or plate after reading for bubbles adhering to the light path
  - Compare duplicate CV before and after excluding a well with a visible bubble; a sharp improvement supports optical artifact
IMMEDIATE_FIX:
  - Reassay the affected samples after fresh dilution and complete 8-cycle mixing
  - Centrifuge problematic diluted samples at 2,000 ×g, 4°C, 5 min before reloading
  - Recalibrate the pipette range used for 50–200 µL transfers
PREVENTION: Use duplicates at minimum; pre-wet tips for transfers ≤100 µL; seal all incubations; inspect wells for bubbles before reading

---

### RULE DX-004
STAGE: standard_curve
CONDITION: Calibrator curve is non-monotonic, one or more middle points are higher or lower than adjacent points, and 4PL fit residuals are poor
DIAGNOSIS: Serial dilution error or mislabeled calibrator sequence
CONFIDENCE: high
LIKELY_CAUSES:
  - One dilution transfer used the wrong source tube
  - A tube was not mixed before the next serial transfer
  - Calibrator positions on the plate map were transposed
  - High-concentration carryover contaminated a low calibrator
DISTINGUISH:
  - Examine duplicate agreement: if both replicates of one point are displaced in the same direction, the dilution tube rather than loading precision is implicated
  - Check back-calculated recoveries: a single failing point surrounded by acceptable points often identifies the transfer error position
  - Review tube labeling and transfer order against bench notes
  - If repeated runs fail at the same calibrator position across lots, plate artifact or reader problem becomes more likely
IMMEDIATE_FIX:
  - Prepare a new calibrator series from the top stock and rerun the plate
  - Use fresh tips and mix each calibrator dilution 8 times before the next transfer
  - Remove the failing point from the fit only if the assay validation permits outlier removal and a documented reason exists
PREVENTION: Label dilution tubes before adding liquid; work in one direction only; require an audible callout of each transfer in regulated runs

---

### RULE DX-005
STAGE: sample_quantification
CONDITION: Neat sample gives lower signal than a 1:10 or 1:100 dilution in sandwich ELISA
DIAGNOSIS: High-dose hook effect or matrix interference causing false low values
CONFIDENCE: high
LIKELY_CAUSES:
  - Analyte concentration exceeds the capture-detection sandwiching capacity
  - Matrix proteins, heterophilic antibodies, or lipids interfere with binding
  - Sample viscosity impairs diffusion to the coated surface
DISTINGUISH:
  - Compare serial sample dilutions: a rising interpolated concentration with dilution is the classic hook-effect pattern
  - If spiked recovery is poor but dilution linearity improves after dilution, matrix interference is favored
  - Competitive ELISA should show the opposite direction of signal change, so confirm assay architecture before interpreting
  - Extremely high analyte targets in inflammatory samples or purified stocks are common hook-effect contexts
IMMEDIATE_FIX:
  - Reassay the sample at 1:10, 1:100, and 1:1,000 dilutions
  - Report the concentration only from the dilution range showing linear recovery
  - Add heterophilic antibody blocker or matrix-matched diluent if validated for the assay
PREVENTION: Screen unknown high-abundance samples across at least two dilutions separated by 10-fold; validate parallelism for each new matrix type

---

### RULE DX-006
STAGE: plate_readout
CONDITION: Outer wells show systematically higher or lower OD than inner wells for standards and controls
DIAGNOSIS: Edge effect from evaporation, uneven temperature exposure, or incomplete sealing
CONFIDENCE: high
LIKELY_CAUSES:
  - Plate seal failed or incubations occurred in low-humidity air
  - Outer wells were used for critical standards without buffer-filled unused wells
  - Plate sat near a cold or warm airflow source during incubation
DISTINGUISH:
  - Compare outer vs inner blanks and standards; consistent perimeter shift confirms location-driven artifact
  - If the effect is strongest on one side only, local airflow or incubator shelf gradient is likely
  - If only the last loaded wells differ, loading-time drift rather than evaporation may be the dominant factor
IMMEDIATE_FIX:
  - Repeat the assay with all unused wells filled with 300 µL buffer and all incubations sealed
  - Keep the plate flat and away from vents during 20–25°C incubations
  - Move critical standards and controls away from perimeter wells on the rerun
PREVENTION: Use adhesive seals for every incubation; equilibrate reagents to 20–25°C; employ buffer-filled edge wells when the room humidity is variable

---

### RULE DX-007
STAGE: sample_quantification
CONDITION: Spiked recovery is <80% or >120% in one matrix while standards perform acceptably in assay diluent
DIAGNOSIS: Matrix interference affecting analyte recovery or antibody binding
CONFIDENCE: high
LIKELY_CAUSES:
  - Endogenous binding proteins mask the analyte
  - Anticoagulants or hemolysis products interfere with binding or enzyme activity
  - Sample pH, salt, or detergent composition differs sharply from calibrator diluent
DISTINGUISH:
  - Compare serum, EDTA plasma, heparin plasma, and supernatant performance when parallel specimens exist
  - Evaluate dilution linearity: improvement after dilution supports matrix interference over stock calibration error
  - Hemolyzed, lipemic, or icteric appearance points to specimen quality as a contributor
  - If both spike recovery and dilution linearity fail, matrix mismatch is more likely than random pipetting error
IMMEDIATE_FIX:
  - Increase sample dilution and recalculate concentration with the dilution factor
  - Move to a matrix-matched calibrator diluent or validated sample pretreatment if available
  - Reject visibly clotted, highly hemolyzed, or grossly lipemic specimens when acceptance limits are exceeded
PREVENTION: Validate each matrix separately; set specimen acceptance criteria; use parallelism and spike recovery during method transfer

---

### RULE DX-008
STAGE: plate_readout
CONDITION: There is a gradient from the first loaded wells to the last loaded wells across standards, controls, and unknowns
DIAGNOSIS: Time-dependent loading drift or staggered incubation artifact
CONFIDENCE: high
LIKELY_CAUSES:
  - Plate loading exceeded 10 min and incubation timing effectively differed across positions
  - TMB or stop solution was added too slowly across the plate
  - Manual loading order was not matched by stop-solution order
DISTINGUISH:
  - Plot OD against loading order rather than concentration; a monotonic order trend indicates timing drift
  - If the gradient reverses between sample incubation and substrate development runs, compare the step that changed speed
  - Uniformly affected blanks and controls implicate reagent timing rather than sample biology
IMMEDIATE_FIX:
  - Repeat the run using a multichannel pipette and complete each full-plate dispense within 10 min
  - Match stop-solution addition order to TMB addition order
  - Use a repeating pipette or automation for substrate and stop addition when available
PREVENTION: Limit full-plate loading, TMB addition, and stop addition to ≤10 min each; record elapsed times for every timed step

---

### RULE DX-009
STAGE: standard_curve
CONDITION: Back-calculated recovery for low calibrators fails while high standards remain acceptable
DIAGNOSIS: Lower limit instability from excessive background, curve overfitting, or dilution inaccuracy near the lower range
CONFIDENCE: medium
LIKELY_CAUSES:
  - Background consumes dynamic range at the lower end
  - Lowest calibrator dilutions were prepared inaccurately
  - 5PL was used without validated asymmetry and distorted the low-end fit
DISTINGUISH:
  - Review blank-corrected signal difference between zero and lowest non-zero point; if the gap is minimal, assay sensitivity is the issue
  - If the same low points fail across multiple runs, the assigned lower limit may be set below the validated quantifiable range
  - Compare 4PL vs 5PL residuals; worse low-end recovery with 5PL suggests unjustified asymmetry
IMMEDIATE_FIX:
  - Reprepare the low calibrators from the mid-range stock rather than from repeated serial transfers
  - Use 4PL fit and exclude points below the validated lower quantifiable limit
  - Reduce blank by improving wash performance and blocking chemistry
PREVENTION: Establish lower quantifiable limit from validation data; keep serial dilution chains short near the low end when feasible

---

### RULE DX-010
STAGE: plate_readout
CONDITION: Color develops in blank wells before TMB has been in the plate for 5 min
DIAGNOSIS: HRP contamination of substrate reservoir or reagent carryover during dispensing
CONFIDENCE: high
LIKELY_CAUSES:
  - TMB reservoir or pipette contacted HRP-containing reagent
  - Reused reagent trough carried over detection conjugate
  - Splashing occurred from high-dispense force into adjacent wells
DISTINGUISH:
  - Fresh TMB in a clean tube should remain colorless at 20–25°C; any blue tint supports contamination
  - If the first blank wells exposed to TMB are colorless but later blanks turn blue, carryover during dispensing is likely
  - If all blanks are blue immediately, reservoir or stock substrate contamination is more likely
IMMEDIATE_FIX:
  - Discard TMB and reservoir immediately
  - Repeat substrate addition with a clean trough and new tips or clean dispensing cassette
  - Decontaminate the dispensing path that previously handled HRP reagents
PREVENTION: Dedicate separate reservoirs and channels for substrate; never place substrate on the bench beside HRP conjugate without clear labeling

---

### RULE DX-011
STAGE: sample_handling
CONDITION: Control recovery drifts downward with each freeze-thaw cycle while fresh calibrators remain stable
DIAGNOSIS: Sample or control degradation from repeated freeze-thaw exposure
CONFIDENCE: high
LIKELY_CAUSES:
  - Protein target is unstable during repeated thawing
  - Protease activity persists in incompletely inhibited lysate or specimen
  - Adsorption losses occurred in non-low-binding storage tubes
DISTINGUISH:
  - Compare first-thaw aliquots with third-thaw aliquots from the same source material
  - If calibrators stored per kit instructions remain stable while specimens fall, specimen stability rather than assay failure is favored
  - Protease-sensitive cytokines and phosphoproteins are especially affected in lysates and supernatants
IMMEDIATE_FIX:
  - Reassay using first-thaw aliquots only
  - Aliquot future specimens into single-use volumes such as 50 µL to 200 µL
  - Add validated protease inhibitors during lysate preparation when compatible with the assay
PREVENTION: Limit freeze-thaw cycles to 1 whenever possible; store aliquots at −80°C in low-binding tubes; document freeze-thaw count in every run

---

### RULE DX-012
STAGE: plate_readout
CONDITION: Optical density exceeds the reader upper limit or the top calibrator is visibly saturated bright yellow after stop solution
DIAGNOSIS: Overdevelopment or excessive analyte/conjugate concentration
CONFIDENCE: high
LIKELY_CAUSES:
  - TMB incubation exceeded the validated window
  - Detection reagent concentration is too high
  - Standards or samples were insufficiently diluted for the dynamic range
DISTINGUISH:
  - If all wells including blanks are high, overdevelopment or contaminated substrate is likely
  - If only top calibrators and high samples are saturated while blanks remain low, concentration range mismatch is the primary issue
  - Compare timing records for TMB addition and stop addition to identify excess development duration
IMMEDIATE_FIX:
  - Shorten TMB development to a validated earlier endpoint, such as 8 min instead of 15 min
  - Increase dilution of top calibrators or high samples and rerun
  - Reconfirm working concentration of HRP conjugate
PREVENTION: Monitor TMB continuously; define stop criteria tied to highest calibrator appearance; screen unknown high-abundance samples at multiple dilutions

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-022)

#### RISK RM-001
STAGE: assay_planning
ITEM: Plate map omission of blanks, zero calibrator, or controls
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm plate map contains blank, zero, full calibrator curve, positive control, and negative or matrix control before reagent setup
MITIGATION: Lock plate map before opening reagents; use a checklist requiring signoff of all mandatory controls

---

#### RISK RM-002
STAGE: reagent_preparation
ITEM: Incorrect wash buffer dilution producing background or weak signal
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Verify concentrate factor and final volume math. Confirm crystals are dissolved before dilution
MITIGATION: Use written dilution tables; have a second operator verify concentrate math for every new batch; label buffer with date and factor

---

#### RISK RM-003
STAGE: reagent_preparation
ITEM: Serial dilution transfer error in calibrator curve setup
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Compare dilution tube labels, transfer sequence, and back-calculated recoveries for all non-zero standards
MITIGATION: Prepare standards in a single direction with fresh tips; mix each tube 8 times before the next transfer; require bench note entry for every dilution step

---

#### RISK RM-004
STAGE: coating
ITEM: Capture antibody concentration too low or too high for the validated range
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Record stock concentration, dilution math, and final coating concentration for every coated plate lot
MITIGATION: Prepare coating master mix from validated stock; run lot bridging when changing antibody lots; store coating records with plate lot identifiers

---

#### RISK RM-005
STAGE: blocking
ITEM: Blocking buffer incompatible with assay matrix leading to non-specific signal
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Review background performance by matrix and blocker composition over the previous validated runs
MITIGATION: Validate blocker separately for serum, plasma, supernatant, and lysate matrices; keep blocker formulation fixed once selected

---

#### RISK RM-006
STAGE: sample_handling
ITEM: Repeated freeze-thaw degradation of analyte in specimens or controls
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Record freeze-thaw count for every sample and control aliquot
MITIGATION: Store single-use aliquots at −80°C; discard aliquots after one thaw when analyte stability is limited

---

#### RISK RM-007
STAGE: sample_handling
ITEM: Matrix mismatch between standards and unknowns causing biased recovery
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Compare spike recovery and dilution linearity for each matrix under evaluation
MITIGATION: Use matrix-matched diluent or stripped matrix when validated; set matrix-specific acceptance criteria

---

#### RISK RM-008
STAGE: sample_loading
ITEM: Plate loading time exceeds 10 min and creates time-dependent drift
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Record start and end time of sample loading, TMB loading, and stop-solution addition
MITIGATION: Use multichannel or repeating pipettes; reduce plate count per operator; automate timed dispenses when possible

---

#### RISK RM-009
STAGE: incubation
ITEM: Plate left unsealed during incubation causing evaporation and edge effects
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Verify seal application at the start of each incubation and inspect corners before moving the plate
MITIGATION: Use adhesive film on every incubation; replace seals between steps; fill unused edge wells with 300 µL buffer when needed

---

#### RISK RM-010
STAGE: washing
ITEM: Incomplete aspiration leaving residual HRP conjugate in wells
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Inspect representative wells after the final wash for droplets larger than approximately 10 µL
MITIGATION: Increase wash cycles, confirm aspiration height, and tap plate firmly on lint-free absorbent towels after final wash

---

#### RISK RM-011
STAGE: washing
ITEM: Washer manifold misalignment or clogged channels causing row or column artifacts
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare blank and control patterns by row and column; run washer dispense verification with dyed water weekly
MITIGATION: Prime and flush washer lines before each run; service clogged manifolds immediately; document preventive maintenance

---

#### RISK RM-012
STAGE: detection
ITEM: HRP conjugate working solution prepared at the wrong dilution
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify stock factor, transfer volume, and total working volume in bench notes
MITIGATION: Prepare one master mix per plate set; use second-person verification for stock-to-working dilution math

---

#### RISK RM-013
STAGE: substrate_development
ITEM: TMB substrate contamination by HRP carryover
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Inspect substrate for any blue tint before dispensing and review whether substrate tools contacted HRP reagent paths
MITIGATION: Use dedicated clean reservoirs for TMB; never reuse HRP reagent troughs for substrate; discard tinted substrate immediately

---

#### RISK RM-014
STAGE: substrate_development
ITEM: Overdevelopment before stop solution causes signal saturation
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Compare highest-calibrator OD and reader upper-limit flags to the planned development window
MITIGATION: Monitor the plate continuously during TMB incubation; define a stop window such as 8–12 min for the assay and keep it fixed once validated

---

#### RISK RM-015
STAGE: plate_reading
ITEM: Reader wavelength or reference setting incorrect
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm the plate reader method uses 450 nm with 570 nm or 620 nm reference where validated
MITIGATION: Lock reader methods in software; verify settings with a pre-run checklist before inserting the plate

---

#### RISK RM-016
STAGE: data_analysis
ITEM: Use of an unjustified fit model causing inaccurate concentration interpolation
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare residuals and back-calculated recoveries under the selected fit model against validation records
MITIGATION: Default to validated 4PL for sandwich and competitive ELISA; use 5PL only after demonstrating consistent asymmetry across validation runs

---

#### RISK RM-017
STAGE: sample_quantification
ITEM: Hook effect in high-abundance samples producing false low results
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Review serial dilutions for increasing calculated concentration with dilution
MITIGATION: Screen unknown high-concentration samples at multiple dilutions separated by at least 10-fold; report values only from the linear range

---

#### RISK RM-018
STAGE: sample_handling
ITEM: Particulate material or fibrin in specimens causes poor precision and optical interference
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Inspect samples visually and clarify by centrifugation before dilution
MITIGATION: Centrifuge serum or plasma at 2,000 ×g, 4°C, 10 min before loading; reject heavily clotted material when criteria are exceeded

---

#### RISK RM-019
STAGE: biosafety
ITEM: Human-derived specimen exposure during manual plate handling
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Gloves, coat, and eye protection worn; waste handling plan includes bleach contact time of 20 min
MITIGATION: Treat all human-derived materials as potentially infectious; use BSL-2 practices; decontaminate liquid waste with 10% bleach for 20 min

---

#### RISK RM-020
STAGE: storage
ITEM: Reagent lot drift between runs goes unnoticed
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Trend positive-control recovery and blank OD by reagent lot over time
MITIGATION: Bridge new lots against the current lot with at least 3 comparative runs before full adoption

---

#### RISK RM-021
STAGE: post_run_qc
ITEM: Raw files or plate maps not saved before plate disposal
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm raw reader file, plate map, and analyzed output are present in the run folder before cleanup
MITIGATION: Make data save confirmation a required closeout step; use automatic export from the reader when available

---

#### RISK RM-022
STAGE: environment
ITEM: Room airflow or temperature gradient affects plate incubations at 20–25°C
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Review plate position, vent proximity, and edge-effect trend when perimeter wells deviate across runs
MITIGATION: Incubate plates on a stable bench away from vents and direct sun; keep room temperature within 20–25°C during the assay

---

### Critical Findings (CF-001 to CF-004)

#### RISK CF-001
STAGE: assay_planning
ITEM: Quantitative ELISA run performed without a full calibrator curve and acceptance controls
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Verify blank, zero, non-zero calibrators, and positive control are present on every quantitative plate
MITIGATION: Do not release quantitative data from a plate lacking the complete control structure; rerun the plate with the full curve and controls

---

#### RISK CF-002
STAGE: sample_quantification
ITEM: High-abundance samples reported from neat wells without dilution assessment
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm at least two dilutions were assessed for unknown samples expected near or above the assay upper range
MITIGATION: Reassay high-signal or clinically extreme samples at multiple dilutions; release only values confirmed in the linear range

---

#### RISK CF-003
STAGE: washing
ITEM: Plate washer or manual wash process leaves residual HRP conjugate causing false high signal on the full plate
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Inspect residual liquid after the last wash and trend blank OD across recent runs
MITIGATION: Stop reporting data from plates with uncontrolled blank elevation; verify aspiration performance, repeat wash validation, and rerun affected specimens

---

#### RISK CF-004
STAGE: biosafety
ITEM: Human-derived ELISA waste discarded without validated decontamination contact time
PROBABILITY: low
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm liquid waste reached 10% bleach for 20 min or approved institutional equivalent before disposal
MITIGATION: Suspend disposal until decontamination is complete; retrain staff and add documented waste-contact timers at the bench

---

## 6. PARAMETER CONSTRAINTS

### Plate Coating and Blocking

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Coating volume | 75 µL/well | 100 µL/well | 150 µL/well | <75 µL: incomplete surface coverage; >150 µL: spill risk and wasted reagent |
| Coating incubation | 20–25°C, 2 h | 4°C, 16 h | 4°C, 24 h | Shorter time: reduced capture density; longer time: no routine gain and higher contamination risk |
| Blocking volume | 150 µL/well | 200 µL/well | 300 µL/well | <150 µL: incomplete coverage; >300 µL: overflow risk |
| Blocking incubation | 20–25°C, 30 min | 20–25°C, 60 min | 20–25°C, 120 min | Shorter time: more non-specific binding; longer time: rarely improves background |

### Sample and Calibrator Loading

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Sample or calibrator load volume | 50 µL/well | 100 µL/well | 150 µL/well | Keep one validated volume only; changing volume requires recalibration of the assay |
| Full-plate loading time | 0 min | ≤10 min | 15 min | >10 min: timing drift likely; >15 min: rerun recommended |
| Sample hold after dilution | 0 min | ≤30 min at 20–25°C | 60 min at 20–25°C | Longer hold can alter adsorption and stability in low-abundance targets |
| Freeze-thaw count | 0 | 1 | 2 | >2 cycles: recovery bias likely for many proteins |

### Washing

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Wash volume | 250 µL/well | 300 µL/well | 350 µL/well | <250 µL: incomplete rinsing; >350 µL: overflow risk |
| Wash cycles after sample incubation | 3 | 4 | 6 | <3: background risk; >6: no routine benefit unless validated |
| Wash cycles after HRP incubation | 4 | 5 | 7 | <4: conjugate carryover risk; >7: no routine benefit unless validated |
| Residual droplet after final wash | 0 µL | <10 µL | 20 µL | >20 µL: repeat wash block |

### Detection and Substrate

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Detection reagent volume | 75 µL/well | 100 µL/well | 150 µL/well | Outside validated volume changes kinetics and signal |
| Detection incubation | 20–25°C, 30 min | 20–25°C, 60 min | 37°C, 90 min | Longer or hotter incubation may raise background |
| TMB volume | 75 µL/well | 100 µL/well | 150 µL/well | Outside validated volume changes path length and endpoint timing |
| TMB incubation | 20–25°C, 5 min | 20–25°C, 10–15 min | 20–25°C, 20 min | >20 min: saturation risk rises sharply |
| Stop-solution delay after final TMB dispense | 0 min | ≤10 min across the plate | 12 min | Longer delay increases plate-position drift |

### Plate Reading and Data Quality

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Time from stop solution to read | 0 min | ≤15 min | 30 min | >30 min: rerun or justify with validation data |
| Blank OD | 0.000 | ≤0.150 | 0.200 | >0.200: reject run unless validation allows |
| Calibrator/control replicate CV | 0% | ≤10% | 15% | >15%: repeat point or rerun plate |
| Unknown replicate CV | 0% | ≤15% | 20% | >20%: reprepare dilution and reassay |
| Back-calculated calibrator recovery | 80% | 90–110% | 120% | Outside 80–120%: investigate fit or dilution setup |

---

## 7. QC GATES

### QC Gate 1: Before Plate Setup

PASS criteria (ALL must be true):
  - Plate map includes blank, zero calibrator, non-zero standards, positive control, and unknowns
  - Reagent lots and expiry dates are recorded
  - Acceptance criteria are written before loading
  - Pipettes required for 50–300 µL transfers are within calibration status

ACTION if FAIL: Do not begin the run. Complete plate map and control assignment, replace expired reagents, or swap out out-of-calibration pipettes before proceeding.

---

### QC Gate 2: After Reagent and Calibrator Preparation

PASS criteria (ALL must be true):
  - Wash buffer dilution math was verified and buffer is clear
  - Standards were reconstituted with exact volumes and serially diluted in sequence
  - Detection working solution is fresh and labeled with preparation time
  - Enough wash buffer and detection reagent exist for the full plate plus dead volume

ACTION if FAIL: Discard questionable working reagents and reprepare from stock. If calibrator preparation sequence is uncertain, rebuild the entire curve from the top stock.

---

### QC Gate 3: After Sample Loading and Incubation

PASS criteria (ALL must be true):
  - Every loaded well received the validated volume
  - Plate loading completed within 10 min
  - Plate remained sealed throughout incubation
  - Incubation temperature and time match the assay design

ACTION if FAIL: If loading exceeded 10 min or seal integrity failed, mark the plate at risk for drift or edge effect and rerun if controls later show positional bias.

---

### QC Gate 4: After Wash and Detection Steps

PASS criteria (ALL must be true):
  - Wash cycles met the stage-specific requirement
  - Residual liquid after final wash is minimal
  - Detection reagent and substrate volumes were 100 µL/well or validated equivalent
  - TMB development time is documented and within the validated window

ACTION if FAIL: If residual liquid remains or background rises early in blanks, stop data release and rerun after wash-process correction.

---

### QC Gate 5: Final Run Acceptance

PASS criteria (ALL must be true):
  - Blank OD is ≤0.150
  - Calibrator and control duplicate CV is ≤10%
  - Unknown duplicate CV is ≤15%
  - Back-calculated calibrator recovery is 80–120% for accepted curve points
  - Positive control recovery falls within assigned range
  - Reported unknowns come from the validated quantifiable range and corrected dilution factors

ACTION if FAIL: Reject the plate for quantitative reporting. Reassay with corrected reagent setup, dilution plan, or wash process depending on the failure pattern.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified assay problem and root cause, or "QC PASS — proceed" |
| confidence | enum: high / medium / low | Confidence in the diagnosis based on observed controls and run history |
| recommended_actions | list[string] | Ordered action list with immediate correction first, then preventive controls |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings linked to Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass/fail status for each QC gate |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range conditions with linked diagnostic rule |
| reportable_range_status | enum: within_range / below_range / above_range / requires_redilution | Status of each sample result relative to validated quantifiable limits |
| fit_model_status | enum: accepted / rejected / alternate_model_used | Outcome of curve-model review |
| specimen_integrity_status | enum: acceptable / hemolyzed / lipemic / particulate / excess_freeze_thaw | Specimen suitability summary |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| western_blot_v1 | Orthogonal protein confirmation by band size and immunoblot detection is needed |
| flow_cytometry_v1 | Single-cell protein expression, viability, or surface-marker quantification is needed |
| rt_qpcr_v1 | Transcript-level confirmation of analyte regulation is needed |
| cell_culture_v1 | User needs upstream cell stimulation, conditioned-medium generation, or supernatant collection planning |
| immunofluorescence_v1 | Spatial localization of the target protein in cells or tissue is needed |
| multiplex_bead_assay_v1 | User needs simultaneous multi-analyte cytokine or biomarker quantification from small sample volume |
| protein_extraction_v1 | User needs lysate generation and total-protein normalization before ELISA sample loading |

