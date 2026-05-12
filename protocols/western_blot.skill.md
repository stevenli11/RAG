---
skill_id: western_blot_v1
skill_name: Western Blot Complete Workflow Skill
version: 1.0
method_family: protein_analysis
tags: [western_blot, immunoblot, sds_page, protein_transfer, pvdf, nitrocellulose, antibody_incubation, chemiluminescence, fluorescent_detection, protein_quantification, membrane_stripping, loading_control, phosphoprotein]
applies_to: [mammalian_cell_lysate, tissue_lysate, bacterial_lysate, recombinant_protein, phosphoprotein_analysis, total_protein_analysis]
does_not_apply_to: [mass_spectrometry_proteomics, elisa_quantitation, immunohistochemistry, live_cell_imaging, native_page_complex_analysis, capillary_western_platforms, clinical_diagnostic_ivd]
risk_level: medium
bsl_level: "BSL-2 for mammalian or human-derived lysates; follow source material biosafety controls"
last_updated: 2026-03-15
source_protocol: SOP-WB-001
---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I run a western blot," "my bands are weak," "why is my transfer uneven," "how do I prepare lysis buffer," "my phospho-signal disappeared," "why do I have high background," "how much protein should I load," "how do I block a membrane," "what transfer conditions should I use for a 150 kDa protein," "how do I strip and reprobe," "my housekeeping control changed," or any question about protein extraction, quantification, denaturation, SDS-PAGE separation, transfer to PVDF or nitrocellulose, membrane blocking, primary and secondary antibody incubation, signal detection, image capture, densitometry, stripping, and structured troubleshooting for western blot and immunoblot workflows. This skill covers the complete workflow from experimental planning and sample preparation through lysis, quantification, gel casting or gel selection, electrophoresis, transfer to PVDF or nitrocellulose, membrane blocking, primary and secondary antibody incubation, signal detection, image capture, densitometry, stripping, and interpretation of common failure modes including weak signal, saturated bands, non-specific bands, smiling, transfer loss, and phosphoprotein instability. This skill does NOT cover capillary western systems, clinical diagnostic assays under regulated IVD frameworks, mass-spectrometry-based proteomics, ELISA quantitation, immunohistochemistry, or native PAGE for intact protein complexes. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| sample_source | enum: cultured_cells / tissue / bacteria / purified_protein | Biological source of the protein sample |
| target_protein | string | Protein of interest to detect |
| expected_mw_kda | float | Expected molecular weight in kDa for the target band |
| sample_count | int | Number of samples to compare on the blot |
| detection_goal | enum: presence_absence / relative_expression / phospho_status / cleavage_product / isoform_comparison | Analytical goal of the blot |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| lysis_buffer_type | enum: ripa / triton_based / sds_based / urea_based / unknown | Extraction chemistry used for the sample |
| reducing_agent | enum: dtt / beta_mercaptoethanol / none / unknown | Reducing condition used in sample buffer |
| protein_concentration_mg_ml | float | Measured protein concentration after quantification |
| loaded_protein_ug | float | Protein mass loaded per lane |
| gel_percent | string | Gel percentage or gradient range used for separation |
| membrane_type | enum: pvdf_0_45 / pvdf_0_2 / nitrocellulose_0_45 / nitrocellulose_0_2 | Transfer membrane used |
| transfer_method | enum: wet / semi_dry / dry / unknown | Protein transfer platform |
| transfer_condition | string | Voltage or current, duration, and temperature used for transfer |
| blocking_reagent | enum: milk_5 / bsa_5 / casein / commercial_buffer / unknown | Blocking chemistry used before antibody incubation |
| primary_antibody_dilution | string | Primary antibody dilution ratio, for example 1:1000 |
| primary_incubation | string | Primary antibody incubation temperature and time |
| secondary_antibody_dilution | string | Secondary antibody dilution ratio |
| wash_buffer_type | enum: tbst / pbst / tbs / pbs / unknown | Buffer used for membrane washing |
| wash_cycles | string | Number and duration of wash steps |
| detection_method | enum: ecl / femto_ecl / fluorescent / colorimetric | Signal detection chemistry |
| exposure_time_s | float | Imaging exposure time in seconds |
| loading_control | string | Reference protein or total protein stain used for normalization |
| band_pattern | string | Observed band pattern, for example smear, laddering, multiple bands, blank lanes, edge distortion |

---

## 3. WORKFLOW MODULES

### Module 1: EXPERIMENT_PLANNING_AND_REAGENT_SETUP

**Preconditions:** Target protein identity, expected molecular weight, species reactivity, and sample list are defined. Primary and secondary antibodies are available with datasheets. Gel system, transfer device, membrane, and detection chemistry are available. Ice bucket, protease inhibitors, phosphatase inhibitors if relevant, and calibrated pipettes are ready.
**Pause point:** YES - planning can stop after lane map and reagent checklist are completed. Do not begin lysis until all reagents are labeled and chilled where required.

#### Steps:

**ASSAY DESIGN:**
1. Define the analytical question: presence or absence, relative abundance, phospho-state, cleavage product, or isoform shift. Select one primary endpoint per blot to avoid loading lanes without a comparison plan.
2. Record target protein expected molecular weight in kDa, host species of the primary antibody, clonality, validated application, and recommended dilution range from the datasheet.
3. [CRITICAL] Select the membrane and gel percentage from expected molecular weight:
   - 0.2 µm PVDF or nitrocellulose for proteins <20 kDa
   - 15% gel for proteins 10-40 kDa
   - 12% gel for proteins 15-70 kDa
   - 10% gel for proteins 20-100 kDa
   - 7.5% to 8% gel for proteins 80-250 kDa
   - 4% to 15% gradient gel for mixed targets or when the expected size is uncertain
   - When the target falls within an overlapping range, use the lower gel percentage for better resolution of the target band relative to nearby proteins.
4. Decide normalization strategy before starting:
   - Total protein stain for broad linearity and treatment conditions that may alter housekeeping proteins
   - Housekeeping protein only when its stability has been verified under the exact treatment conditions
5. Build a lane map listing molecular weight marker, positive control, negative control if available, blank lane if contamination tracking is needed, and each experimental sample.
6. Calculate total reagent volumes from lane count plus 10% overage. Example for 10 lanes at 20 µL/lane: sample buffer mix volume per sample 22 µL; running buffer 1 L; transfer buffer 1 L; blocking buffer 20 mL to 30 mL per membrane.
7. [CRITICAL] For phosphoproteins, plan to keep samples at 0-4°C during extraction and add phosphatase inhibitors immediately before lysis. For labile phospho-epitopes, avoid milk and use 5% BSA in TBST for blocking and antibody dilution.

**REAGENT PREPARATION:**
8. Prepare 10× Tris-Glycine-SDS running buffer or use a ready-made stock. Dilute to 1× before electrophoresis.
9. Prepare transfer buffer:
   - Wet transfer: 25 mM Tris, 192 mM glycine, 10% to 20% methanol, 0.1% SDS only for proteins >120 kDa if transfer efficiency is poor
   - Semi-dry transfer: follow manufacturer-compatible ionic strength; methanol 10% to 20%
10. Prepare TBST: 20 mM Tris, 150 mM NaCl, 0.1% Tween-20, pH 7.4 to 7.6. Prepare at least 500 mL per blot for wash capacity.
11. Pre-label microtubes for lysates, aliquots, sample buffer mixes, and antibody solutions. Pre-cool centrifuge to 4°C if lysates will be clarified.

#### Exit Criteria (must ALL be true to proceed):
- Target protein, expected molecular weight, and antibody species are documented
- Lane map is complete
- Membrane type and gel percentage were selected from the target size range
- Running buffer, transfer buffer, and TBST are prepared
- Normalization method is defined
- Phosphatase inhibitor plan is defined if phospho-signal is the target

---

### Module 2: SAMPLE_LYSIS_AND_PROTEIN_EXTRACTION

**Preconditions:** Samples are harvested or ready for harvest. Lysis buffer and inhibitors are chilled. Collection tubes are labeled. Module 1 is complete.
**Pause point:** YES - clarified lysates can be stored at -80°C after aliquoting. Minimize freeze-thaw cycles; do not freeze-thaw more than twice to preserve protein integrity and labile modifications.

#### Steps:

**CELL OR TISSUE HANDLING:**
1. Place samples on ice before lysis. Aspirate culture medium completely from adherent cells and wash with ice-cold PBS 2 times using 1 mL to 10 mL per wash depending on vessel size.
2. Prepare lysis buffer immediately before use:
   - RIPA buffer for broad extraction of membrane and cytosolic proteins
   - Triton X-100 or NP-40-based buffer for complexes that are detergent-sensitive
   - SDS-based buffer for highly insoluble proteins when compatibility with downstream assay has been verified
3. Add inhibitors fresh per 1 mL lysis buffer:
   - Protease inhibitor cocktail: 10 µL to 20 µL from 50× to 100× stock
   - Phosphatase inhibitor cocktail: 10 µL to 20 µL from 50× to 100× stock if phosphoproteins are being studied
   - PMSF if used: 10 µL of 100 mM stock for 1 mM final; prepare fresh because it hydrolyzes rapidly in aqueous buffer
4. [CRITICAL] Do NOT add DTT or beta-mercaptoethanol to the lysis buffer before protein quantification. Reducing agents distort BCA and Bradford measurements and must be added only in the 4× sample buffer after concentration has been measured.
5. Add lysis buffer volume matched to sample size:
   - 6-well plate well: 100 µL to 200 µL
   - 10 cm dish: 300 µL to 600 µL
   - T-75 flask: 400 µL to 800 µL
   - Tissue: 10 mL lysis buffer per g tissue, then homogenize on ice
6. Scrape adherent cells into the buffer using a cold cell scraper and transfer to chilled microtubes. For tissue, homogenize with 10-20 strokes or instrument setting validated for the tissue type while keeping the sample at 0-4°C.
7. Incubate lysates on ice for 20-30 min at 0-4°C with vortex pulses of 1 s or manual inversion every 5-10 min to improve solubilization.
8. [CRITICAL] Clarify lysates by centrifugation at 16,000 ×g, 4°C, 15 min. Transfer the supernatant to a new chilled tube without disturbing the pellet.
9. If the lysate remains viscous from genomic DNA, shear using a 21G needle for 5 passes or sonicate with 3 pulses of 2 s on ice. Do not foam the sample.
10. For SDS-based lysates that cannot be clarified conventionally, heat only after the aliquot for quantification strategy has been defined. BCA compatibility must be checked before proceeding.
11. Aliquot clarified lysate into single-use volumes, for example 20 µL to 50 µL aliquots, and store at -80°C if not used the same day.

#### Exit Criteria (must ALL be true to proceed):
- Lysis buffer type is recorded
- Protease inhibitors were added; phosphatase inhibitors were added when required
- Lysate was kept at 0-4°C during extraction
- Clarification was completed at 16,000 ×g, 4°C, 15 min or a documented equivalent compatible with the buffer
- Supernatant is transferred without pellet carryover
- Aliquots are labeled with sample ID and date

---

### Module 3: PROTEIN_QUANTIFICATION_AND_SAMPLE_NORMALIZATION

**Preconditions:** Clarified lysates are available. Quantification assay reagents are equilibrated. A plate reader or spectrophotometer is available. Sample buffer is ready.
**Pause point:** YES - quantified lysates can be held on ice for up to 2 h before denaturation or stored at -80°C in aliquots.

#### Steps:

**QUANTIFICATION:**
1. Select the assay compatible with the lysis chemistry:
   - BCA assay for RIPA, NP-40, and Triton X-100 lysates; most commercial BCA kits tolerate up to 5% SDS, but verify with the specific kit datasheet before use with SDS-based lysis buffers
   - Bradford assay when reducing agents are absent or within assay tolerance
   - Direct A280 only for purified proteins with low contaminant carryover
2. Prepare a BSA calibration curve with 8 standards: a blank (0 µg/mL) and 7 non-zero concentrations, for example 125, 250, 500, 750, 1000, 1500, and 2000 µg/mL.
3. Accept the calibration curve only if R² is ≥0.99. If R² is <0.99, remake the calibrators and repeat the assay.
4. Dilute lysates so the measured absorbance falls within the calibration curve. Record dilution factors exactly.
5. Measure samples in technical duplicate or triplicate. Accept the reading only if replicate CV is ≤10%.
6. Calculate protein concentration in mg/mL and total available protein per sample.

**NORMALIZATION AND SAMPLE BUFFERING:**
7. Define the lane load based on target abundance:
   - 5-10 µg for highly abundant proteins such as ACTB, GAPDH, and alpha-tubulin
   - 10-20 µg for moderate-abundance proteins such as ERK1 or ERK2, AKT, and abundant transcription factors in stimulated lysates
   - 20-40 µg for low-abundance signaling proteins, phosphoproteins, and low-expression receptors when the gel and transfer capacity support it
8. Calculate loading volumes so every lane contains equal protein mass. Use the same final sample volume per lane, typically 15 µL to 30 µL.
9. Prepare 4× Laemmli sample buffer mix per sample:
   - Lysate volume calculated from concentration
   - 4× sample buffer to 1× final
   - Reducing agent to final 50 mM DTT or 2% beta-mercaptoethanol
   - Water to equalize volume if needed
10. Denature reduced samples at 95°C, 5 min for soluble proteins from cytosolic, nuclear, or recombinant preparations. Use 70°C, 10 min for large membrane proteins or aggregation-prone proteins if 95°C causes precipitation.
11. Cool samples on ice for 2 min, then centrifuge at 10,000 ×g, 20°C, 1 min to collect condensate and remove insoluble material.
12. Keep denatured samples at 20-25°C if they contain SDS and will be loaded within 30 min. Reheat at the same temperature and time profile only once if precipitation is observed.

#### Exit Criteria (must ALL be true to proceed):
- Quantification assay is compatible with the lysis buffer
- Calibration curve and dilution factors are recorded
- Calibration curve R² is ≥0.99
- Replicate CV is ≤10%
- Equal protein mass per lane is calculated
- Sample buffer is at 1× final concentration
- Denaturation condition is recorded for each sample class

---

### Module 4: SDS_PAGE_GEL_PREPARATION_AND_ELECTROPHORESIS

**Preconditions:** Normalized samples are ready. Gel cassette or precast gel, running buffer, marker, and electrophoresis tank are available. Module 3 is complete.
**Pause point:** NO - once samples are loaded and voltage is applied, complete the separation in one session.

#### Steps:

**GEL SETUP:**
1. Select gel format:
   - 7.5% resolving gel for 80-250 kDa
   - 10% resolving gel for 20-100 kDa
   - 12% resolving gel for 15-70 kDa
   - 15% resolving gel for 10-40 kDa
   - 4-15% gradient gel for wide molecular weight coverage
2. For hand-cast gels, after pouring the resolving layer, overlay with isopropanol or water-saturated n-butanol until the surface is level. Allow the resolving layer to polymerize for 30-45 min and the stacking layer for 20-30 min before use.
3. [CRITICAL] Do NOT combine Bis-Tris precast gels with Tris-glycine running buffer. Bis-Tris gels require MES or MOPS running buffer compatible with the manufacturer system; buffer mismatch causes distorted migration and incorrect apparent molecular weight.
4. Assemble the gel tank and fill inner and outer chambers with 1× running buffer. Remove comb carefully and flush wells with running buffer using a pipette.
5. Load molecular weight marker according to the manufacturer volume, typically 3 µL to 10 µL per lane.
6. Load each sample slowly into the well, keeping the tip below the buffer surface and above the well bottom to prevent puncturing the gel.

**ELECTROPHORESIS:**
7. Run the gel at 80 V through the stacking layer for 15-20 min until the dye front enters the resolving layer.
8. Increase to 120-140 V for the resolving phase and continue until the dye front is 5-10 mm from the gel bottom, usually 45-70 min depending on gel thickness and buffer system.
9. For temperature-sensitive targets or long runs, run the tank at 4°C or with an ice pack around the tank when current-generated heat causes smiling.
10. [VISUAL CHECK] Confirm that the dye front is horizontal across all lanes. If the front is tilted early, stop and inspect for buffer imbalance, leakage, or poor cassette seating.
11. When the run ends, open the cassette and trim the stacking gel away. If transfer will not start immediately, hold the gel in transfer buffer for up to 10 min at 20-25°C.

#### Exit Criteria (must ALL be true to proceed):
- Gel percentage matches the target size range
- Marker and all samples were loaded per lane map
- Stacking and resolving voltages were recorded
- Dye front reached the planned stop point without lane crossover
- Wells remained intact during loading
- Gel is ready for transfer without visible tears

---

### Module 5: PROTEIN_TRANSFER_TO_MEMBRANE

**Preconditions:** Electrophoresis is complete. Membrane, filter papers, sponges or transfer stacks, transfer buffer, and blotting device are ready. Module 4 is complete.
**Pause point:** NO - once the transfer sandwich is assembled, complete transfer and immediate membrane verification before stopping.

#### Steps:

**MEMBRANE PREPARATION:**
1. Cut the membrane and filter papers to gel size. Mark one membrane corner with pencil for orientation.
2. Activate PVDF in 100% methanol for 15-30 s, then equilibrate in water for 1 min or until the membrane is uniformly translucent; if white opaque patches remain, extend equilibration or re-immerse briefly in methanol before returning to water. Nitrocellulose goes directly into water or transfer buffer for 5 min.
3. [CRITICAL] After PVDF activation, do not allow the membrane to dry at any point before transfer or antibody incubation. Dry PVDF binds antibodies unevenly and produces persistent background artifacts.
4. Equilibrate the gel in transfer buffer for 10 min. For proteins >120 kDa, include 0.1% SDS in transfer buffer and keep methanol at 10%; for proteins <20 kDa, reduce or omit SDS and use 20% methanol to limit blow-through.

**TRANSFER ASSEMBLY AND RUN:**
5. Assemble the sandwich in transfer buffer with no trapped air: sponge, filter paper, gel, membrane, filter paper, sponge. Roll a clean pipette or roller across each layer to remove bubbles.
6. [CRITICAL] Orient the membrane toward the anode and the gel toward the cathode for SDS-PAGE transfer. A reversed stack yields complete signal loss.
7. Select transfer condition:
   - Wet transfer, low-medium MW proteins: 100 V, 4°C, 60 min
   - Wet transfer, high MW proteins (>120 kDa): 100 V, 4°C, 90-120 min with 0.1% SDS and 10% methanol, or 30 V, 4°C, 16 h for overnight transfer
   - Semi-dry transfer, 10-100 kDa proteins: 0.8-1.0 mA/cm² membrane area, 20-35 min if compatible with the platform and membrane
8. Fill the transfer unit with chilled transfer buffer. For wet transfer at 4°C, use a pre-chilled module, cold room, or ice block with buffer temperature maintained at 4-10°C.
9. After transfer, stain the membrane with Ponceau S for 1-5 min and rinse with water until protein bands are visible.
10. [VISUAL CHECK] Check total protein pattern and marker transfer:
   - Even ladder across all lanes
   - No bubble-shaped blank regions
   - No lane loss at edges
11. Document the membrane image before destaining. If transfer is incomplete, retain the gel and stain it with Coomassie to assess residual protein.

#### Exit Criteria (must ALL be true to proceed):
- Membrane type and pore size are recorded
- Transfer orientation was verified before the run
- Transfer conditions include voltage or current, temperature, and time
- Ponceau S or another transfer check confirms protein on the membrane
- No major bubble voids are visible
- Membrane orientation mark is preserved

---

### Module 6: BLOCKING_AND_PRIMARY_SECONDARY_ANTIBODY_INCUBATION

**Preconditions:** Transfer verification is complete. Blocking reagent, antibody diluent, wash buffer, and rocker are available. Module 5 is complete.
**Pause point:** YES - the membrane can pause after blocking or after overnight primary incubation if kept sealed in buffer at 4°C.

#### Steps:

**BLOCKING:**
1. Destain the membrane fully with TBST or TBS until Ponceau signal no longer interferes with target detection.
2. Select block:
   - 5% milk in TBST for non-phospho targets validated to perform cleanly with casein-containing blockers
   - 5% BSA in TBST for phosphoproteins and when milk-derived phosphoproteins increase background
   - Casein or commercial blocker when validated for the antibody pair
3. Incubate membrane in 20 mL to 30 mL blocking solution per mini blot or 0.1 mL/cm² membrane area at 20-25°C, 30-60 min with rocking. Ensure the membrane is fully submerged.

**PRIMARY ANTIBODY:**
4. Dilute the primary antibody in fresh blocking buffer or antibody diluent according to the datasheet and pilot data, usually within 1:500 to 1:5000.
5. Incubate membrane with 5 mL to 15 mL primary solution:
   - 20-25°C, 1-2 h for robust antibodies and abundant targets
   - 4°C, 16 h for low-abundance targets or when specificity is a concern

   Note: Regardless of incubation temperature, use a sealable incubation bag or a small box sized to the membrane to conserve antibody while keeping the membrane fully submerged.
6. For phospho-targets, keep the membrane in 5% BSA and minimize time at 20-25°C after transfer to preserve epitope integrity.
7. Wash 3 times in 20 mL to 30 mL TBST, 20-25°C, 5-10 min each with rocking.

**SECONDARY ANTIBODY:**
8. Dilute HRP- or fluorophore-conjugated secondary antibody, usually within 1:5000 to 1:20,000, in blocking buffer validated for the system.
9. [CRITICAL] Do NOT use sodium azide in any buffer used to dilute HRP-conjugated secondary antibody or HRP substrate components. Sodium azide inhibits HRP activity and can eliminate chemiluminescent signal completely.
10. Incubate at 20-25°C, 45-60 min with rocking in light-protected trays for fluorescent secondaries.
11. Wash 3-5 times in 20 mL to 30 mL TBST, 20-25°C, 5-10 min each. Use 5 washes when background has been problematic or the secondary concentration exceeds 1:10,000.
12. If using fluorescent detection, perform a final rinse in TBS without Tween-20 for 5 min to reduce residual detergent fluorescence artifacts.

#### Exit Criteria (must ALL be true to proceed):
- Blocking reagent matches target class and antibody chemistry
- Primary and secondary dilutions are recorded
- Incubation temperature and time are recorded for both antibodies
- Wash number and duration are recorded
- Membrane remained fully submerged on a rocker throughout incubations
- Fluorescent blots were protected from light when applicable

---

### Module 7: DETECTION_IMAGING_ANALYSIS_AND_REPROBING

**Preconditions:** Antibody incubations are complete. Imaging system and detection reagents are available. Normalization plan is defined. Module 6 is complete.
**Pause point:** YES - membranes can pause after washing in TBS at 4°C for up to 16 h before detection if sealed to prevent drying.

#### Steps:

**DETECTION:**
1. Prepare ECL substrate immediately before use if using a 2-component system. Mix equal volumes and protect from strong light.
2. Drain excess wash buffer without letting the membrane dry. Apply 0.1 mL/cm² ECL substrate for 1-5 min at 20-25°C.
3. For fluorescent detection, dry the membrane surface edges only, avoid pooled liquid, and scan with the correct channel settings and no signal clipping.

**IMAGING:**
4. Capture a short exposure series rather than one long exposure:
   - Chemiluminescence: 1 s, 5 s, 10 s, 30 s, 60 s, then longer only if needed
   - Fluorescence: scan at low, medium, and high detector intensity while checking saturation masks
5. [CRITICAL] Select the image in the linear range where the target band and normalization signal are both below saturation.
6. Save raw image files, processed export, lane map, antibody lot numbers, and exposure settings in the experiment record.

**ANALYSIS AND REPROBING:**
7. Quantify bands using consistent background subtraction windows and identical lane boundaries across the compared samples.
8. Normalize the target band to total protein stain or validated loading control from the same membrane.
9. If stripping is required:
   - Mild stripping buffer: 25 mM glycine-HCl, pH 2.0, 1% SDS; incubate at 20-25°C for 2 × 10 min using fresh buffer each time
   - Harsh stripping buffer: 62.5 mM Tris-HCl, pH 6.8, 2% SDS, 100 mM beta-mercaptoethanol; incubate at 50°C for 30 min only when target loss risk is acceptable. Handle beta-mercaptoethanol in a chemical fume hood; volatility increases at 50°C.
10. Wash stripped membranes 3 times in TBST, 20-25°C, 10 min each, then re-block for 20-30 min before re-probing.
11. Verify stripping efficiency by imaging the membrane after stripping and before re-probing, or by incubating with the same secondary antibody used in the previous detection round at the same dilution for 45-60 min at 20-25°C, then imaging at the same exposure setting used for the original target. Residual signal must be absent or below 5% of the original band intensity before re-probing.
12. Limit full stripping cycles to 1-2 rounds. Signal loss and epitope damage accumulate with each stripping cycle.

#### Exit Criteria (must ALL be true to proceed):
- Detection reagent and imaging mode are recorded
- At least one exposure in the linear range is saved
- Raw data files are stored
- Quantification uses the pre-defined normalization strategy
- Any stripping condition is recorded with temperature and time
- Membrane was never allowed to dry before imaging or reprobing

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: sample_extraction
CONDITION: Protein yield is low across all samples; lysates are watery; target and loading control are both weak
DIAGNOSIS: Incomplete lysis or low extraction efficiency
CONFIDENCE: high
LIKELY_CAUSES:
  - Lysis buffer volume was too low for the cell or tissue mass
  - Incubation on ice was shorter than 10 min or homogenization was incomplete
  - Detergent chemistry did not solubilize the target compartment
  - Protease inhibitors were omitted and partial degradation reduced measured protein
DISTINGUISH:
  - Compare pellet size after clarification. A large opaque pellet with low supernatant protein suggests under-extraction
  - Check whether membrane proteins or nuclear proteins are the target; RIPA or fractionation may be required instead of a mild Triton buffer
  - Review lysis volume per vessel and whether scraping or homogenization was complete
  - If total protein stain is weak in every lane, the problem started before electrophoresis rather than during antibody incubation
IMMEDIATE_FIX:
  - Re-lyse replicate material with higher lysis buffer volume and extended on-ice extraction of 30-45 min, mixing every 5-10 min
  - Switch to RIPA or SDS-compatible extraction if the target is insoluble in the current buffer
  - Add fresh protease inhibitors and clarify again at 16,000 ×g, 4°C, 15 min
PREVENTION: Match lysis chemistry to target localization, define vessel-specific lysis volumes in the worksheet, and keep extraction at 0-4°C with fresh inhibitors.

---

### RULE DX-002
STAGE: quantification
CONDITION: Replicate protein concentration readings show CV >10% or concentrations are not plausible relative to sample mass
DIAGNOSIS: Protein quantification assay interference or pipetting error
CONFIDENCE: high
LIKELY_CAUSES:
  - Reducing agent, detergent, or buffer component exceeded assay tolerance
  - Calibrators and samples were not mixed or timed consistently
  - Sample dilution was outside the linear range of the assay
  - Pipetting volumes below 5 µL introduced large relative error
DISTINGUISH:
  - Compare assay chemistry with the lysis buffer composition; BCA is more tolerant of detergents than Bradford, while reducing agents can distort both
  - If calibrators are linear but sample replicates diverge, sample handling or insoluble material is the problem
  - If all absorbance values cluster near the top or bottom of the curve, dilution range is wrong
  - Check whether clarified lysates were mixed before aliquoting into the assay plate
IMMEDIATE_FIX:
  - Re-run quantification with assay-compatible dilutions and duplicate calibrators
  - Remove incompatible components by dilution or buffer exchange if sample volume permits
  - Increase technical replicate count to triplicate and use pipetting volumes ≥10 µL
PREVENTION: Validate assay compatibility for each lysis buffer, keep samples homogeneous, and record dilution factors at the time of plate setup.

---

### RULE DX-003
STAGE: electrophoresis
CONDITION: Precast Bis-Tris gel was run with Tris-glycine running buffer, or Tris-glycine gel was run with MES or MOPS Bis-Tris buffer
DIAGNOSIS: Gel and running buffer system incompatibility
CONFIDENCE: high
LIKELY_CAUSES:
  - Precast gel chemistry was not matched to the running buffer system
  - Buffer bottle was reused from a different gel platform without relabeling
  - Operator assumed all SDS-PAGE gels use interchangeable running buffers
DISTINGUISH:
  - Migration is often globally distorted across every lane rather than limited to one sample
  - Marker apparent sizes are shifted or compressed relative to the manufacturer reference image
  - Repeating the same samples on the correct matched buffer system restores expected migration
  - Review the cassette label for Bis-Tris, Tris-glycine, MES, or MOPS system wording
IMMEDIATE_FIX:
  - Stop interpretation of molecular weight and repeat electrophoresis with the manufacturer-matched buffer system
  - Discard or relabel any ambiguous running buffer stock before the next run
  - Re-run the marker and a positive control to re-establish migration behavior on the correct system
PREVENTION: Store Bis-Tris and Tris-glycine buffers separately, label gel cassettes by chemistry, and verify compatibility before the tank is assembled.

---

### RULE DX-004
STAGE: electrophoresis
CONDITION: Bands curve upward at the edges or lanes are distorted with a smile pattern
DIAGNOSIS: Overheating during electrophoresis or ionic imbalance in the running system
CONFIDENCE: high
LIKELY_CAUSES:
  - Voltage was too high for the gel thickness and tank geometry
  - Running buffer was old, incorrectly diluted, or unevenly filled between chambers
  - Gel ran too warm at 20-25°C for too long without heat control
  - Salt concentration in samples was very high
DISTINGUISH:
  - If outer lanes distort more than center lanes, heat buildup is the main factor
  - If the dye front tilts early, buffer level or chamber assembly is the main factor
  - If only one sample lane is distorted, high salt or particulate carryover is likely
  - Check whether the run exceeded 150 V for a mini gel without cooling
IMMEDIATE_FIX:
  - Repeat the gel at 80 V through stacking and 120-140 V through resolving with fresh 1× running buffer
  - Run at 4°C or with active cooling for long separations
  - Desalt high-salt samples or reduce loaded volume
PREVENTION: Use fresh 1× running buffer, balance chamber fill volumes, and avoid excessive voltage on mini gel systems.

---

### RULE DX-005
STAGE: electrophoresis
CONDITION: Protein appears as a smear rather than discrete bands across multiple lanes
DIAGNOSIS: Overloaded lanes, protein degradation, or incomplete denaturation or reduction
CONFIDENCE: medium
LIKELY_CAUSES:
  - Loaded protein mass exceeded gel capacity
  - Samples degraded before or during lysis
  - Reducing agent or SDS concentration was too low
  - Genomic DNA increased viscosity and prevented clean entry into the gel
DISTINGUISH:
  - If the smear originates near the well and extends downward, overload or DNA viscosity is likely
  - If low-MW streaks appear below the expected band, proteolysis is likely
  - If non-reduced dimers remain near the top, denaturation or reduction was incomplete
  - Compare total protein stain and marker appearance; a clean marker with smeared samples points to sample preparation rather than gel chemistry
IMMEDIATE_FIX:
  - Reduce load to 10-20 µg per lane and shear DNA before buffering
  - Add fresh reducing agent and re-denature at 95°C, 5 min or 70°C, 10 min for aggregation-prone proteins
  - Re-extract with fresh inhibitors and minimize room-temperature hold time
PREVENTION: Keep lysates cold, quantify accurately, and stay within the load range supported by the gel thickness and well size.

---

### RULE DX-006
STAGE: transfer
CONDITION: Ponceau S shows strong signal in some regions and blank circular or oval areas in others
DIAGNOSIS: Air bubbles or poor contact in the transfer sandwich
CONFIDENCE: high
LIKELY_CAUSES:
  - Air was trapped between the gel and membrane during assembly
  - Filter papers were not fully wetted in transfer buffer
  - Sponge pressure was uneven or stack alignment shifted during cassette closure
DISTINGUISH:
  - Bubble artifacts usually create sharply bounded blank zones with protein visible around the perimeter
  - If the blank region matches a visible trapped bubble after the run, assembly error is confirmed
  - If blank regions are at the same position on repeated blots, inspect the cassette hardware for warped pressure surfaces
IMMEDIATE_FIX:
  - Re-run transfer with a freshly assembled sandwich and a roller to remove bubbles
  - Pre-wet every layer in transfer buffer before stacking
  - If protein remains in the gel, re-transfer immediately using a fresh membrane
PREVENTION: Assemble the sandwich under transfer buffer, roll each layer flat, and inspect the stack from the side before closing the cassette.

---

### RULE DX-007
STAGE: transfer
CONDITION: High-MW target is absent or weak while low-MW marker bands transferred well
DIAGNOSIS: Incomplete transfer of high molecular weight proteins
CONFIDENCE: high
LIKELY_CAUSES:
  - Transfer duration was too short
  - Methanol concentration was too high for large proteins
  - Gel percentage was too high for the target size
  - Transfer buffer lacked SDS support for proteins >120 kDa
DISTINGUISH:
  - Stain the post-transfer gel; residual high-MW bands confirm incomplete elution from the gel
  - If the marker high-MW bands are also weak on the membrane, the issue is transfer efficiency rather than antibody binding
  - Review whether transfer was 100 V for 60 min; this often under-transfers proteins >150 kDa
IMMEDIATE_FIX:
  - Repeat with 100 V, 4°C, 90-120 min using 0.1% SDS and 10% methanol in transfer buffer, or use 30 V, 4°C, 16 h overnight transfer if same-day completion is not required
  - Reduce methanol to 10% for large proteins
  - Use 7.5% gel or gradient gel for targets above 120 kDa
PREVENTION: Match gel percentage and transfer duration to target size, and verify residual protein in the gel when optimizing a new large target.

---

### RULE DX-008
STAGE: transfer
CONDITION: Low-MW target is absent or very weak while mid- and high-MW proteins appear normal
DIAGNOSIS: Blow-through of low molecular weight proteins or membrane pore mismatch
CONFIDENCE: medium
LIKELY_CAUSES:
  - Membrane pore size was 0.45 µm instead of 0.2 µm for a small target
  - Transfer time or current was too high for the target size
  - SDS concentration in transfer buffer increased passage through the membrane
DISTINGUISH:
  - Check whether the target is <20 kDa; small proteins are the most vulnerable to membrane loss
  - If a second membrane placed behind the first contains the target, blow-through is confirmed
  - Review whether the transfer used semi-dry conditions optimized for larger proteins
IMMEDIATE_FIX:
  - Use 0.2 µm PVDF or nitrocellulose and shorten transfer time
  - Remove SDS from transfer buffer for small proteins unless a specific validation shows benefit
  - Increase methanol to 20% if compatible with the target
PREVENTION: Select 0.2 µm membranes for proteins below 20 kDa and optimize transfer using duplicate membranes during method setup.

---

### RULE DX-009
STAGE: antibody_incubation
CONDITION: Entire membrane has high background haze or diffuse signal, obscuring bands
DIAGNOSIS: Excess antibody concentration, inadequate washing, or blocking mismatch
CONFIDENCE: high
LIKELY_CAUSES:
  - Primary or secondary antibody was too concentrated
  - Wash count or wash duration was too low
  - Milk was used for a phospho-antibody or the blocker was otherwise incompatible
  - Membrane dried during handling, increasing non-specific binding
DISTINGUISH:
  - If background is uniform across every lane and marker region, antibody or wash chemistry is the main factor
  - If background is worse at the membrane edges, incomplete rocking coverage or drying is likely
  - Compare signal on the no-primary control if available; strong no-primary signal points to secondary-driven background
  - Review secondary dilution. HRP secondaries from widely used vendors often perform best at 1:10,000 to 1:20,000 rather than 1:1000
IMMEDIATE_FIX:
  - Increase washes to 5 cycles, 20-25°C, 10 min each in TBST
  - Reduce primary or secondary concentration by 2-fold to 5-fold
  - Switch from milk to 5% BSA for phospho-targets
PREVENTION: Validate the antibody titration on a pilot blot, keep membranes wet at every step, and use wash volumes of 20 mL to 30 mL per mini blot.

---

### RULE DX-010
STAGE: antibody_incubation
CONDITION: Target band is absent but loading control and total protein are present
DIAGNOSIS: Target-specific detection failure
CONFIDENCE: medium
LIKELY_CAUSES:
  - Primary antibody does not recognize the species, isoform, or denatured epitope in the sample
  - Loaded protein mass is too low for target abundance
  - Blocking reagent or incubation temperature reduced antibody binding
  - Phospho-epitope was lost through dephosphorylation or phosphatase inhibitor omission
DISTINGUISH:
  - Verify species reactivity and application validation on the datasheet; some antibodies work in IP but not western blot
  - Check positive control lane. If positive control is also blank, antibody or epitope preservation is the issue
  - If only phospho-signal is lost while total protein band remains, inhibitor omission or milk blocking is likely
  - Review expected molecular weight and whether the band may be outside the imaging crop
IMMEDIATE_FIX:
  - Increase loaded protein within gel capacity, for example from 10 µg to 25 µg
  - Use a validated positive control and re-test the primary at 4°C, 16 h
  - Re-extract with fresh phosphatase inhibitors and block in 5% BSA for phospho-targets
PREVENTION: Confirm antibody validation before the first experiment, preserve labile modifications at 0-4°C, and include a positive control during setup.

---

### RULE DX-011
STAGE: detection
CONDITION: Bands are extremely dark with flat-topped peaks or image software flags saturation
DIAGNOSIS: Overexposure and loss of quantitative linearity
CONFIDENCE: high
LIKELY_CAUSES:
  - Exposure time was too long
  - Loaded protein amount exceeded the linear range
  - Secondary antibody concentration was too high
  - Detection substrate sensitivity was stronger than required for the target abundance
DISTINGUISH:
  - Saturated bands remain the same intensity across longer exposures while band width expands
  - If housekeeping control saturates before the target, normalization becomes unreliable
  - Compare 1 s to 10 s exposures; if both are clipped, the problem begins before imaging
IMMEDIATE_FIX:
  - Re-image with shorter exposures and lower detector gain
  - Dilute secondary antibody and lower lane load
  - Use a less sensitive substrate when target abundance is high
PREVENTION: Capture a defined exposure series from short to long and select analysis images only from the unsaturated range.

---

### RULE DX-012
STAGE: detection
CONDITION: Multiple unexpected bands appear in addition to the expected target
DIAGNOSIS: Non-specific binding, isoform complexity, or proteolytic processing
CONFIDENCE: medium
LIKELY_CAUSES:
  - Primary antibody cross-reacts with related proteins
  - Sample contains splice variants, cleavage products, or post-translationally modified forms
  - Proteolysis occurred during extraction
  - Secondary antibody cross-reacts with endogenous immunoglobulins in tissue samples
DISTINGUISH:
  - Compare the pattern with positive control and knockdown or knockout control if available
  - If extra bands disappear when primary dilution is increased, non-specific primary binding is likely
  - If a lower band intensifies after long room-temperature handling, proteolysis is likely
  - Tissue samples rich in immunoglobulin can generate heavy and light chain bands near 50 kDa and 25 kDa
IMMEDIATE_FIX:
  - Increase stringency: dilute primary further, lengthen washes, and switch blocker if required
  - Add fresh protease inhibitors and reduce pre-lysis handling time
  - Use knockout or knockdown validation or peptide competition where available
PREVENTION: Validate antibody specificity with biological controls and preserve samples at 0-4°C with inhibitors from the start of lysis.

---

### RULE DX-013
STAGE: normalization
CONDITION: Loading control changes strongly between conditions and does not match total protein staining
DIAGNOSIS: Unstable normalization reference
CONFIDENCE: high
LIKELY_CAUSES:
  - Housekeeping protein expression is altered by treatment
  - Membrane was overexposed for the control band
  - Uneven transfer or lane loading created false control shifts
DISTINGUISH:
  - Compare housekeeping band pattern with total protein stain; if total protein is even but housekeeping shifts, biology or antibody response is driving the change
  - If the control is saturated, densitometry cannot recover true differences
  - Treatments affecting metabolism, cytoskeleton, or stress often alter GAPDH, ACTB, or tubulin
IMMEDIATE_FIX:
  - Re-normalize using total protein stain from the same membrane
  - Re-image the loading control within the linear range
  - Select a different reference protein validated for the treatment context
PREVENTION: Verify reference stability under each treatment class and prefer total protein normalization during pathway perturbation experiments.

---

### RULE DX-014
STAGE: transfer
CONDITION: Semi-dry transfer yields weak signal across all lanes, especially near gel edges, despite a normal electrophoresis pattern
DIAGNOSIS: Semi-dry transfer stack dehydration or incompatible transfer program
CONFIDENCE: high
LIKELY_CAUSES:
  - Filter papers or proprietary stack pads were under-wetted before the run
  - Transfer time exceeded the buffer-holding capacity of the stack
  - Current or voltage program was selected for a different membrane or gel thickness
  - Gel equilibration in transfer buffer was skipped
DISTINGUISH:
  - Edge lanes often fail first when the stack dries during the run
  - If Ponceau S shows a weak global ladder but the post-transfer gel retains protein in every lane, transfer failure occurred before antibody incubation
  - If the same samples transfer well by wet transfer, the issue is specific to the semi-dry setup rather than lysis or gel separation
  - Review whether the semi-dry run was set in mA/cm² membrane area rather than a copied voltage program from a different platform
  - Review whether the membrane, paper layers, and gel were all equilibrated in transfer buffer for the specified time before assembly
IMMEDIATE_FIX:
  - Re-run the blot with fully soaked stack materials and a manufacturer-matched semi-dry program
  - Reduce transfer duration or switch to wet transfer for proteins >100 kDa or for thick gels
  - Verify gel and membrane compatibility with the selected semi-dry cassette and buffer system
PREVENTION: Use semi-dry transfer only within validated MW and gel-thickness ranges, pre-equilibrate every layer, and document the exact program used for each membrane type.

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-023) and Critical Findings (CF-001 to CF-003)

#### RISK RM-001
STAGE: planning
ITEM: Using an antibody without verified western blot validation for the sample species
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm the datasheet lists western blot and the sample species or cross-reactive species
MITIGATION: Use antibodies with validated western blot data, species reactivity, and expected molecular weight guidance before committing lysate and membrane resources.

---

#### RISK RM-002
STAGE: planning
ITEM: Selecting gel percentage incompatible with target molecular weight
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare expected target size to gel percentage or gradient range before casting or opening the precast gel
MITIGATION: Use 7.5% to 8% for high-MW proteins, 10% for mid-range proteins, 12% to 15% for low-MW proteins, or a 4-15% gradient for mixed targets.

---

#### RISK RM-003
STAGE: sample_extraction
ITEM: Proteolysis during lysis from delayed inhibitor addition
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Verify inhibitor addition was recorded before buffer touched the sample
MITIGATION: Add protease inhibitors immediately before lysis, keep extraction at 0-4°C, and move clarified lysate to fresh tubes without delay.

---

#### RISK RM-004
STAGE: sample_extraction
ITEM: Phospho-signal loss from omitted phosphatase inhibitors
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm phosphatase inhibitor addition for every phospho-target experiment
MITIGATION: Add phosphatase inhibitors fresh to lysis buffer, keep samples at 0-4°C, and use 5% BSA for blocking and antibody dilution.

---

#### RISK RM-005
STAGE: sample_extraction
ITEM: Cross-sample mix-up during tube labeling and aliquoting
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Match sample IDs, tube labels, and lane map before quantification and loading
MITIGATION: Pre-label tubes, work in sample order, and perform a two-person or checklist verification before loading the gel.

---

#### RISK RM-006
STAGE: quantification
ITEM: Assay interference from detergent or reducing agent
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Compare lysis buffer composition with the assay compatibility table before reading concentrations
MITIGATION: Choose BCA or Bradford based on buffer chemistry, dilute incompatible samples, or use buffer exchange where sample volume allows.

---

#### RISK RM-007
STAGE: quantification
ITEM: Unequal protein loading between lanes
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Review calculated lane loads, sample concentrations, and final lane volumes before denaturation
MITIGATION: Normalize all samples to the same protein mass and total lane volume, then verify by total protein stain after transfer.

---

#### RISK RM-008
STAGE: sample_preparation
ITEM: Sample aggregation from excessive heating
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Confirm whether the target class is aggregation-prone and whether 95°C heating was used
MITIGATION: Use 70°C, 10 min for large membrane proteins or aggregation-prone targets and inspect for precipitation after heating.

---

#### RISK RM-009
STAGE: electrophoresis
ITEM: Gel well puncture or spill during loading
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Inspect wells after loading and verify marker remained in its lane
MITIGATION: Load slowly with the pipette tip above the well bottom, stabilize the hand on the tank edge, and use loading dye density to track fill.

---

#### RISK RM-010
STAGE: electrophoresis
ITEM: Running buffer dilution error
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm the lot, dilution calculation, and conductivity of 1× running buffer before use
MITIGATION: Prepare fresh 1× running buffer, label containers clearly, and discard leftover buffer with uncertain composition.

---

#### RISK RM-011
STAGE: electrophoresis
ITEM: Bis-Tris gel used with Tris-glycine running buffer, or Tris-glycine gel used with MES or MOPS buffer
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify gel chemistry on the cassette label and confirm the running buffer system before the tank is assembled
MITIGATION: Match Bis-Tris gels only with the manufacturer-compatible MES or MOPS buffer and Tris-glycine gels only with Tris-glycine buffer; store the two systems separately and relabel any ambiguous buffer stock.

---

#### RISK RM-012
STAGE: electrophoresis
ITEM: Overheating-driven smiling and distorted migration
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Review voltage, run duration, and tank temperature during separation
MITIGATION: Use 80 V through stacking, 120-140 V through resolving, and cool the system for long or high-current runs.

---

#### RISK RM-013
STAGE: transfer
ITEM: Reversed gel-membrane orientation causing complete target loss
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Verify cathode-gel-membrane-anode order before closing the cassette
MITIGATION: Mark the membrane corner, read the device orientation diagram before assembly, and perform verbal orientation confirmation during setup.

---

#### RISK RM-014
STAGE: transfer
ITEM: Bubble trapping between gel and membrane
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Inspect the stack visually under buffer before starting transfer
MITIGATION: Wet all layers fully, assemble under buffer, and roll across the sandwich to remove trapped air.

---

#### RISK RM-015
STAGE: transfer
ITEM: Incomplete transfer of proteins >120 kDa
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare target size to transfer duration, methanol percentage, and SDS inclusion
MITIGATION: Use 100 V, 4°C, 90-120 min with 10% methanol and 0.1% SDS for same-day transfer, or 30 V, 4°C, 16 h overnight; verify with post-transfer gel staining.

---

#### RISK RM-016
STAGE: transfer
ITEM: Blow-through of proteins <20 kDa
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Verify membrane pore size and transfer duration for small targets
MITIGATION: Use 0.2 µm membrane, shorter transfer times, and avoid SDS in transfer buffer for small proteins unless validated.

---

#### RISK RM-017
STAGE: antibody_incubation
ITEM: High background from excessive secondary antibody concentration
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Review secondary dilution and no-primary control signal
MITIGATION: Titrate secondary within 1:5000 to 1:20,000 and increase wash count when background persists.

---

#### RISK RM-018
STAGE: antibody_incubation
ITEM: Blocking mismatch for phospho-targets
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm whether milk was used with a phospho-specific antibody
MITIGATION: Use 5% BSA in TBST for phospho-targets and keep all post-transfer handling compatible with phospho-epitope preservation.

---

#### RISK RM-019
STAGE: antibody_incubation
ITEM: Membrane drying between washes or incubations
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Inspect trays and workflow timing to confirm the membrane remained wet continuously
MITIGATION: Keep transfer containers ready before each step and move membranes directly from one solution to the next without exposed dry intervals.

---

#### RISK RM-020
STAGE: detection
ITEM: Signal saturation leading to invalid quantification
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Review imaging software saturation masks or pixel intensity histograms before analysis
MITIGATION: Capture a short-to-long exposure series, choose unsaturated images only, and lower lane load or secondary concentration when needed.

---

#### RISK RM-021
STAGE: normalization
ITEM: Housekeeping protein altered by experimental treatment
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare housekeeping control to total protein stain across conditions
MITIGATION: Use total protein normalization when treatments affect metabolism, cytoskeleton, proliferation, or stress pathways.

---

#### RISK RM-022
STAGE: reprobing
ITEM: Target loss after repeated stripping
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Count the number of stripping cycles performed on the membrane
MITIGATION: Limit stripping to 1-2 cycles, image the membrane after each strip, and prioritize low-abundance targets before abundant controls.

---

#### RISK RM-023
STAGE: documentation
ITEM: Missing raw image files, exposure settings, or antibody lot records
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm that raw image, processed export, lane map, lot numbers, and exposure metadata are saved together
MITIGATION: Use a capture template that stores raw files and metadata immediately after imaging, before densitometry begins.

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: transfer
ITEM: Membrane orientation reversed relative to electrode direction
SEVERITY: stop_work
CHECK: If the membrane was placed on the cathode side of the gel, target proteins migrated away from the membrane
RESPONSE: Stop interpretation, re-run electrophoresis and transfer on new gel and membrane, and document the failed orientation event.

---

#### RISK CF-002
STAGE: sample_extraction
ITEM: Phospho-target experiment performed without phosphatase inhibitors
SEVERITY: stop_work
CHECK: If phosphatase inhibitors were absent at the moment of lysis, phosphorylation-state conclusions are unreliable
RESPONSE: Stop analysis for phospho-status claims, repeat extraction from fresh material with inhibitor-added buffer, and retain the failed run only as a process record.

---

#### RISK CF-003
STAGE: detection
ITEM: Quantitative comparison attempted on saturated bands
SEVERITY: stop_work
CHECK: If target or normalization bands contain clipped pixels, densitometric ratios are not valid
RESPONSE: Stop quantification, re-image within the linear range or repeat the blot with lower protein load or shorter exposure.

---

## 6. PARAMETER CONSTRAINTS

### Antibody Incubation Conditions

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Primary incubation for rapid screen | 20°C | 20-25°C, 1 h | 25°C | >25°C can increase non-specific binding; <20°C slows association |
| Primary incubation duration for sensitivity at 4°C | 12 h | 14-16 h | 20 h | Shorter than 12 h can reduce low-abundance target binding; longer than 20 h can increase background |
| Secondary incubation | 20°C | 20-25°C, 45-60 min | 25°C | >60 min may increase background without gain in specific signal |

ABSOLUTE PROHIBITION: Sodium azide must never be present in any buffer used for HRP-conjugated secondary antibodies or HRP substrates. This is not a parameter constraint - it is a system incompatibility.

### Sample Denaturation And Reduction

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Sample denaturation temperature for soluble proteins from cytosolic or nuclear lysates | 70°C | 95°C, 5 min | 95°C | If aggregation occurs at 95°C, switch to 70°C, 10 min |
| Sample denaturation temperature for membrane proteins | 60°C | 70°C, 10 min | 75°C | >75°C may aggregate hydrophobic targets and reduce entry into the gel |
| Reducing agent final DTT concentration | 25 mM | 50 mM | 100 mM | <25 mM may leave disulfide-linked species unresolved |

### Clarification And Spin Conditions

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Lysate clarification | 12,000 ×g, 4°C, 10 min | 16,000 ×g, 4°C, 15 min | 20,000 ×g, 4°C, 20 min | Below range leaves debris; above range is acceptable for robust tubes but may compact soft lipid layers |
| Post-denaturation spin | 5,000 ×g, 20°C, 1 min | 10,000 ×g, 20°C, 1 min | 16,000 ×g, 20°C, 2 min | Below range may leave condensate and particulate material in the sample |

### Loading, Blocking, And Stripping Volumes

| Parameter | Value / Range | Notes |
|-----------|--------------|-------|
| Loaded protein per lane | 5-50 µg | Use lower end for abundant proteins and upper end for low-abundance targets |
| Sample volume per lane | 10-30 µL | Keep constant across compared lanes |
| Blocking volume per mini membrane | 20-30 mL or 0.1 mL/cm² membrane area | Membrane must remain fully submerged on rocker |
| Wash volume per mini membrane | 20-30 mL | Use fresh buffer for each wash cycle |
| ECL substrate coverage | 0.1 mL/cm² | Complete membrane coverage without dry edges |
| Stripping cycles | 0-2 | More than 2 cycles risks epitope loss and uneven background |

### Electrophoresis, Transfer, And Wash Conditions

| Parameter | Minimum | Optimal | Notes |
|-----------|---------|---------|-------|
| Gel resolving voltage | 100 V | 120-140 V | Above 150 V on mini gels often increases smiling |
| Wet transfer for 10-100 kDa proteins | 80 V, 4°C, 45 min | 100 V, 4°C, 60 min | Verify with Ponceau S and post-transfer gel staining during optimization |
| Wet transfer for >120 kDa proteins | 100 V, 4°C, 90 min | 100 V, 4°C, 90-120 min with 0.1% SDS and 10% methanol | Overnight alternative: 30 V, 4°C, 16 h |
| Semi-dry transfer current density for 10-100 kDa proteins | 0.6 mA/cm² | 0.8-1.0 mA/cm², 20-35 min | Use membrane area rather than copied voltage settings when moving between platforms |
| TBST wash duration | 5 min | 5-10 min | Use 5 cycles when background is high |

---

## 7. QC GATES

### QC Gate 1: Before Sample Lysis

PASS criteria (ALL must be true):
  - Target protein, expected molecular weight, and species reactivity are documented
  - Lane map includes marker, controls, and all experimental samples
  - Gel percentage and membrane pore size match the target size range
  - Running buffer, transfer buffer, and wash buffer are prepared
  - Inhibitor plan is defined before lysis begins

ACTION if FAIL: Stop before sample lysis. Correct antibody, gel, membrane, or buffer planning gaps, then restart the setup checklist.

---

### QC Gate 2: Before Gel Loading

PASS criteria (ALL must be true):
  - Lysates are clarified and free of visible particulates
  - Quantification assay is compatible with the lysis buffer
  - Calibration curve R² is ≥0.99
  - Replicate concentration CV is ≤10%
  - Equal protein mass per lane has been calculated
  - Sample buffer and reducing conditions are recorded

ACTION if FAIL: Re-clarify lysates at 16,000 ×g, 4°C, 15 min if debris remains. Re-run quantification with compatible chemistry if CV is high or buffer interference is suspected.

---

### QC Gate 3: After Electrophoresis

PASS criteria (ALL must be true):
  - Gel percentage matches the target size range
  - Marker and all samples were loaded according to the lane map
  - Running voltage and duration were recorded
  - Dye front remained level across the gel
  - No lane leakage or punctured wells were observed

ACTION if FAIL: If smiling or lane distortion occurred, repeat electrophoresis with fresh running buffer, lower heat load, and corrected loading technique before transferring critical samples.

---

### QC Gate 4: After Transfer And Before Antibody Incubation

PASS criteria (ALL must be true):
  - Transfer orientation was verified before the run
  - Ponceau S or equivalent total protein check confirms protein on the membrane
  - No major bubble voids are visible
  - Blocking reagent matches the target class
  - Primary and secondary incubation conditions are recorded fully

ACTION if FAIL: If orientation is reversed, stop and repeat the blot. If transfer is incomplete or bubble voids are present, re-transfer immediately if protein remains in the gel.

---

### QC Gate 5: After Imaging And Quantification Review

PASS criteria (ALL must be true):
  - Raw image files, processed exports, lane map, antibody lots, and exposure settings are archived together
  - Quantification was performed only on unsaturated images
  - Normalization method is justified and stable for the treatment context
  - Stripping efficiency was verified before any re-probing cycle
  - Any stripping cycle count is documented
  - Positive and negative control performance is reviewed for recurring assay drift

ACTION if FAIL: Re-image if saturation invalidated quantification. Re-analyze with total protein normalization if housekeeping controls were unstable. Refresh antibody titrations and transfer conditions if drift is detected over consecutive runs.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified problem and root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in diagnosis based on available inputs |
| recommended_actions | list[string] | Ordered action list; immediate fix first, then prevention |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass or fail status for each of the 5 QC gates |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters with linked diagnostic rule |
| protocol_section_reference | string | Section of SOP-WB-001 relevant to the issue |
| normalization_status | enum: validated / unstable / total_protein_required | Suitability of the selected normalization strategy |
| transfer_status | enum: complete / partial / failed / suspected_blowthrough | Transfer assessment after membrane check |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | Protein samples are being prepared from cultured cells and upstream culture health may explain blot artifacts |
| immunofluorescence_v1 | Protein localization in intact cells is required rather than membrane-based detection |
| elisa_v1 | Protein quantitation in solution is required without gel separation |
| rt_qpcr_v1 | mRNA-level confirmation of the same pathway or target is required |
| protein_extraction_v1 | User needs subcellular fractionation or specialized extraction before blotting |
| phosphoproteomics_v1 | User needs site-level phosphorylation mapping beyond antibody-based detection |
| native_page_v1 | User needs intact complex separation without SDS denaturation |
| imaging_analysis_v1 | User needs structured densitometry, inter-gel normalization using a common reference sample, loading series linear range validation, ROI placement guidance, statistical comparison of band intensities across multiple gels, or figure assembly for publication |
