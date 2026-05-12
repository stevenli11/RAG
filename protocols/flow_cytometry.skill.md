---
skill_id: flow_cytometry_v1
skill_name: Flow Cytometry Immunophenotyping Complete Workflow Skill
version: 1.0
method_family: cytometry
tags: [flow_cytometry, immunophenotyping, multicolor_panel, compensation, fmo, viability_dye, fc_block, intracellular_cytokine_staining, transcription_factor_staining, pbmc_isolation, tissue_dissociation, tandem_dye, gating, qc]
applies_to: [cultured_cells, pbmcs, mouse_spleen, mouse_bone_marrow, human_tissue_single_cell_suspensions, surface_marker_panels, intracellular_cytokines, nuclear_transcription_factors]
does_not_apply_to: [mass_cytometry, imaging_cytometry, ffpe_samples, automated_hematology, sterile_sort_release_testing, methanol_phospho_flow_without_panel_redesign]
risk_level: medium
bsl_level: "BSL-2 minimum for unfixed human blood, PBMCs, human tissue suspensions, and lentiviral-transduced material; follow institutional biosafety policy"
last_updated: 2026-03-16
source_protocol: FC-SOP-001
---

---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I design a flow panel," "why did my compensation fail," "why are all my cells dead after staining," "how do I stain PBMCs," "why is my FoxP3 signal absent," "why do I have high background on monocytes," "how many events should I acquire," "how do I set an FMO gate," "why is my tandem dye breaking down," "how do I process spleen or bone marrow," "why is my doublet rate high," or any question about multicolor flow cytometric immunophenotyping of cultured cells, PBMCs, mouse immune tissues, or tissue-derived single-cell suspensions. This skill covers the complete workflow: panel design, fluorophore assignment, required controls, daily instrument QC, single-cell suspension preparation, cell counting and viability QC, viability staining, Fc receptor blocking, surface staining, fixation, intracellular and intranuclear staining, compensation matrix generation, acquisition, gating hierarchy, FMO-based gate placement, and structured diagnostic rules for major failure modes including low viability, clumping, compensation artifacts, tandem dye degradation, high background, absent populations, and invalid data analysis. This skill does NOT cover: mass cytometry / CyTOF, imaging flow cytometry, FFPE tissue workflows, sterile sort product release testing, automated cell sorting biosafety cabinet certification, or methanol-based phospho-flow panels that require a dedicated BV-free and tandem-revalidated reagent set. Redirect those queries to the appropriate skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| sample_type | enum: adherent_cells / suspension_cells / mouse_spleen / mouse_bone_marrow / pbmc / human_tissue_digest | Source material entering the staining workflow |
| species | enum: human / mouse / other | Species identity used to select Fc block, antibody clones, and biosafety handling |
| instrument_platform | enum: facscanto_ii / lsrfortessa / facsaria_iii / cytoflex / other | Instrument used for QC, detector assignment, and compensation logic |
| panel_type | enum: surface_only / intracellular_cytokine / nuclear_transcription_factor / viability_only / troubleshooting | Staining path and fixation kit requirement |
| number_of_colors | int | Total number of fluorescence channels in the panel, excluding scatter parameters |
| workflow_goal | enum: panel_design / sample_preparation / staining / compensation / acquisition / analysis / troubleshooting | Primary task the user is performing |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| cell_viability_percent | float (0-100) | Trypan blue or equivalent viability before staining |
| cell_concentration_per_ml | float | Cell concentration before staining or acquisition |
| cells_per_tube | float | Number of cells allocated to each staining tube |
| viability_dye | enum: live_dead_aqua / live_dead_red / zombie_aqua / pi / 7aad / none | Viability reagent used |
| fc_block_type | enum: human_fcx / mouse_cd16_32 / serum_only / none | Fc blocking reagent used |
| fixation_kit | enum: none / bd_cytofix_cytoperm / foxp3_tf_kit / pfa_only / other | Fixation/permeabilization chemistry used |
| antibody_master_mix_status | enum: fresh / precipitated / reused / unknown | Condition of the antibody mix at use time |
| tandem_dye_ratio_status | enum: passed / caution / failed / not_checked | Donor:acceptor integrity result for tandem dyes |
| compensation_control_type | enum: bead_based / cell_based / mixed / missing | Compensation control format used that day |
| fmo_status | enum: complete / partial / missing / not_needed | Whether FMO controls were prepared for gated markers |
| daily_qc_status | enum: pass / fail / repeated_fail / not_run | Same-day instrument QC status |
| stain_index | float | SI value for the dimmest marker or channel of concern |
| doublet_rate_percent | float (0-100) | Doublet frequency after singlet gating |
| acquisition_flow_rate | enum: low / medium / high | Flow rate used during acquisition |
| event_count_in_parent | int | Events collected within the parent gate used for reporting |
| background_pattern | enum: uniform / myeloid_skewed / dead_cell_skewed / tandem_breakdown / none | Pattern of non-specific or unexpected signal |
| gating_issue | enum: missing_population / gate_shift / over_compensation / under_compensation / fmo_equals_unstained / inconsistent_replicates / none | Primary analysis problem observed |
| time_from_collection_hours | float | Time from sample collection to primary processing for blood or tissue workflows |

---

## 3. WORKFLOW MODULES

### Module 1: PANEL_DESIGN_AND_DAILY_INSTRUMENT_QC

**Preconditions:** Target populations, instrument laser lines, and antibody clone list are known. Detector map and laser/filter configuration are available. Same-day access to the instrument and QC beads has been confirmed.
**Pause point:** YES — panel design and daily QC documentation can be completed before sample preparation begins.

#### Steps:

**PANEL DESIGN:**
1. [CRITICAL] Assign bright fluorophores to dim or rare targets and dimmer fluorophores to highly expressed lineage markers. Use PE, BV421, or BV650 for dim targets such as FoxP3, IFN-gamma, or low-frequency cytokine-positive cells; reserve FITC, PerCP-Cy5.5, or APC-H7 for highly expressed markers such as CD45 or CD3.
2. Verify laser compatibility before finalizing the panel:
   - FACSCanto II: FITC, PE, PerCP-Cy5.5, PE-Cy7, APC, APC-H7 only.
   - LSRFortessa: full 405/488/561/640 nm and optional UV depending on configuration.
   - CytoFLEX: optimize gain from Daily QC fluorospheres; do not reuse BD PMT numbers.
3. [CRITICAL] Reserve controls for every run:
   - 1 unstained control.
   - 1 single-stain control per fluorophore.
   - 1 viability single-stain control.
   - 1 FMO per gated marker.
   - 1 positive biological control for each critical target if biological interpretation depends on band or gate identity.
4. [DECISION POINT] Select fixation path before staining:
   - Surface only: no fixative required, PI or 7-AAD permitted.
   - Intracellular cytokine: BD Cytofix/Cytoperm required.
   - Nuclear transcription factor: FoxP3/TF kit required; BD Cytofix/Cytoperm is not acceptable.
5. Check tandem dye integrity using same-day single-stain controls:
   - Donor signal <5% of acceptor signal: pass.
   - Donor signal 5-20% of acceptor signal: caution, document and consider replacement.
   - Donor signal >20% of acceptor signal: stop and replace reagent.

**DAILY INSTRUMENT QC:**
6. Warm up lasers:
   - FACSCanto II and LSRFortessa: 30 min.
   - FACSAria III: 45-60 min.
   - CytoFLEX: 15 min.
7. Run same-day QC:
   - BD instruments: add 3 drops of CS&T beads to 1 mL PBS in a 5 mL tube; run automated CS&T.
   - CytoFLEX: run Daily QC fluorospheres per instrument routine.
8. [CRITICAL] Accept the instrument only if all channels pass and fluorescence CV is <=3%. If one channel fails, repeat QC once. If a second run fails, do not proceed.
9. Acquire unstained cells and verify the autofluorescence peak is within the lowest log decade for all channels used. Save the acquisition template and lock voltages or gains before collecting single-stain controls.

#### Exit Criteria (must ALL be true to proceed):
- Fluorophore assignment matches antigen brightness and instrument laser availability
- Same-day required controls are planned and labeled
- Fixation path is selected before staining
- Tandem dye integrity check is complete for tandem channels in use
- Same-day instrument QC passed and the report is saved
- PMT voltages or gains are locked before compensation controls are collected

---

### Module 2: SAMPLE_PREPARATION_AND_SINGLE_CELL_SUSPENSION

**Preconditions:** Sample source is known. Reagents, strainers, centrifuge, and staining buffer are ready. BSL-2 workspace is available for human or lentiviral material. Staining buffer is PBS + 2% BSA or 2% heat-inactivated FBS + 2 mM EDTA, pH 7.2-7.4.
**Pause point:** YES — a clean single-cell suspension may be held on ice for up to 30 min before counting if the cells are in staining buffer and protected from light.

#### Steps:

**ADHERENT CELLS:**
1. For adherent cell lines, aspirate medium, wash twice with 10 mL PBS for a T75 or 5 mL PBS for a T25, then add 3 mL Trypsin-EDTA 0.25% to a T75 or 1.5 mL to a T25.
2. Incubate at 37°C for 3-5 min. If staining integrins, CD44, CD29, or CD49e, replace trypsin with enzyme-free dissociation buffer at 20-22°C for 5-10 min.
3. Neutralize trypsin with 3× volume complete medium, pipette 10 times, centrifuge at 300 × g, 20-22°C, 5 min, and resuspend in 5 mL staining buffer.

**SUSPENSION CELLS:**
4. For suspension cell lines, transfer the culture to a 15 mL tube, centrifuge at 300 × g, 20-22°C, 5 min, aspirate, and resuspend to 1-5 × 10^6 cells/mL in staining buffer.

**MOUSE SPLEEN OR BONE MARROW:**
5. For mouse spleen, place tissue into 3 mL cold staining buffer, mechanically disrupt through a 70 µm strainer, centrifuge at 350 × g, 4°C, 5 min, perform ACK lysis in 1 mL for exactly 1 min at 20-22°C, quench with 10 mL staining buffer, centrifuge again at 350 × g, 4°C, 5 min, then resuspend in 5 mL staining buffer.
6. For mouse bone marrow, flush each femur or tibia with 3 mL cold staining buffer using a 23-gauge needle, strain through 70 µm mesh, centrifuge at 350 × g, 4°C, 5 min, lyse RBCs in 1 mL ACK for exactly 1 min at 20-22°C, quench with 10 mL staining buffer, centrifuge again, and resuspend in 5 mL staining buffer.

**PBMC ISOLATION:**
7. For PBMCs, begin Ficoll within 4 h of blood draw. Warm Ficoll to 20-22°C for at least 30 min, add 15 mL Ficoll to a 50 mL tube, dilute blood 1:1 with PBS, then layer 30 mL diluted blood over Ficoll at approximately 1 mL every 2-3 sec.
8. Centrifuge at 400 × g, 20-22°C, 30 min with brake 0 and acceleration 3-4. Collect the buffy coat, wash once at 300 × g, 20-22°C, 10 min, then wash again at 200 × g, 20-22°C, 10 min to reduce platelet carryover.

**HUMAN TISSUE DIGEST:**
9. For human tissue digests up to 200 mg, mince to approximately 1 mm^3 fragments, digest in 3 mL RPMI + tissue-appropriate collagenase + DNase I 0.1 mg/mL, incubate at 37°C for 30-45 min on a rotating wheel at 20 rpm, pipette 5 times every 15 min, strain through 70 µm mesh, centrifuge at 350 × g, 4°C, 5 min, and resuspend in 5 mL staining buffer.
10. Pass all suspensions with visible clumps through a 70 µm strainer. For fixed or aggregation-prone samples, perform a final pass through a 40 µm strainer before counting.

#### Exit Criteria (must ALL be true to proceed):
- A single-cell suspension is present without large visible aggregates
- Sample processing followed the source-specific path
- RBC lysis, if used, was exactly 1 min in ACK at 20-22°C
- Ficoll separation, if used, was run with brake 0
- Final suspension is in staining buffer containing 2 mM EDTA
- Sample is ready for counting within 30 min of final resuspension

---

### Module 3: CELL_COUNTING_AND_PRE_STAIN_QC

**Preconditions:** Single-cell suspension is ready. Trypan blue, hemocytometer, and calculation worksheet are available. Cells are held at 4°C or on ice while waiting to be counted.
**Pause point:** YES — counted cells can be held on ice for up to 30 min before viability staining if they remain at 0-4°C.

#### Steps:

1. Mix 10 µL cell suspension with 10 µL 0.4% trypan blue, pipette 5 times, and load 10 µL into a hemocytometer.
2. Allow cells to settle for 30 sec and count the four corner squares under a 10× objective.
3. Calculate viable cell concentration using: viable cells/mL = (live cells counted / squares counted) × 2 × 10^4.
4. Calculate viability percentage using: viability = live cells / total cells × 100.
5. [DECISION POINT] Apply the viability threshold:
   - >=85%: proceed normally.
   - 70-84%: add one extra wash before staining and document reduced sample quality.
   - 50-69%: discuss with PI or supervisor, add extra washes, and consider dead-cell removal.
   - <50%: stop and do not stain.
6. Allocate cells for all tubes using: (experimental tubes + unstained + single-stains + FMO tubes + viability single-stain) × 1 × 10^6 cells × 1.2 overage factor.
7. Resuspend cells for staining at 0.5-5 × 10^6 cells per 100 µL. Do not exceed 5 × 10^6 cells per 100 µL before fixation.

#### Exit Criteria (must ALL be true to proceed):
- Viability is measured and recorded
- Cells per tube are calculated for all experimental and control tubes
- Cell density is within the recommended pre-stain range
- Any conditional sample quality issues are documented
- Samples failing the stop rule are excluded
- Tubes are labeled before viability dye is added

---

### Module 4: VIABILITY_STAINING_AND_FC_BLOCK

**Preconditions:** Cell counts are complete. Protein-free PBS, viability dye stock, staining buffer, and the correct species-matched Fc block are ready. No BSA- or FBS-containing reagent has contacted the cells after the final staining-buffer wash if an amine-reactive viability dye will be used.
**Pause point:** NO — once the viability dye is added, the workflow should proceed directly into Fc block and surface staining without extended idle time.

#### Steps:

**AMINE-REACTIVE VIABILITY DYE:**
1. Centrifuge cells at 350 × g, 4°C, 5 min and aspirate all staining buffer.
2. Wash once in 1 mL protein-free PBS, centrifuge at 350 × g, 4°C, 5 min, and aspirate completely.
3. Prepare the dye immediately before use:
   - LIVE/DEAD Aqua, Violet, Near-IR, or Zombie Aqua: 1:1,000 in protein-free PBS.
   - LIVE/DEAD Red: 1:500 in protein-free PBS.
4. Resuspend each pellet in 100 µL dye working solution and pipette 5 times.
5. Incubate at 20-22°C for 20-30 min protected from light. Mix by inversion or pipetting every 5 min.
6. Quench with 2 mL staining buffer and centrifuge at 350 × g, 4°C, 5 min. Aspirate to approximately 50 µL residual volume.

**FC BLOCK:**
7. For human samples, add 5 µL undiluted Human Fc Block to approximately 50 µL cell suspension and incubate at 4°C for 10-15 min.
8. For mouse samples, add 1 µL anti-CD16/32 clone 93 or 5 µL BD clone 2.4G2 working dilution and incubate at 4°C for 5-10 min.
9. [DO NOT] wash after Fc block. Add the surface antibody master mix directly into the blocked cells.
10. [DECISION POINT] If the sample will remain unfixed, PI or 7-AAD may be added later after surface staining. If fixation is planned, do not use PI or 7-AAD anywhere in the workflow.

#### Exit Criteria (must ALL be true to proceed):
- Viability dye was diluted in protein-free PBS
- Viability staining ran for 20-30 min at 20-22°C
- The correct species-matched Fc block was used
- Fc block incubation time is recorded
- No wash occurred between Fc block and surface staining
- Sample is ready for antibody master mix addition

---

### Module 5: SURFACE_STAINING

**Preconditions:** Viability staining and Fc block are complete. Surface antibody master mix has been calculated from titrated volumes. Master mix is clear and free of visible precipitate.
**Pause point:** YES — after the final surface-staining wash, samples may be held at 4°C for up to 30 min before fixation or acquisition.

#### Steps:

1. Prepare the antibody master mix from titrated volumes with 10% overage. If two or more Brilliant Violet dyes are present, include 50 µL Brilliant Stain Buffer per test within the 50 µL master mix calculation.
2. If visible particles are present in the mix, centrifuge at 10,000 × g, 4°C, 5 min and transfer only the clear supernatant to a new tube.
3. Add 50 µL antibody master mix directly to the approximately 50 µL Fc-blocked sample for a total staining volume of approximately 100 µL.
4. Pipette 5 times to fully resuspend the pellet.
5. Incubate at 4°C for 20-30 min protected from light.
6. Wash twice with 2 mL staining buffer, centrifuging each wash at 350 × g, 4°C, 5 min.
7. Aspirate carefully, leaving approximately 50 µL above the pellet after each wash. For small pellets, use a P1000 rather than vacuum.
8. [DECISION POINT] If the panel is surface only, resuspend in 300 µL staining buffer and proceed to PI/7-AAD addition or acquisition. If intracellular staining is required, continue immediately to the fixation module.

#### Exit Criteria (must ALL be true to proceed):
- Master mix matches the panel design and tube count
- Surface staining incubation ran at 4°C for 20-30 min
- Two post-stain washes are complete
- Pellet is preserved after aspiration
- Surface-only samples are resuspended for acquisition
- Intracellular samples are ready for the correct fixation path

---

### Module 6: FIXATION_AND_INTRACELLULAR_OR_INTRANUCLEAR_STAINING

**Preconditions:** Surface staining is complete. The correct fixation and permeabilization kit has been selected based on intracellular target class. Perm/Wash buffers are prepared at 1× concentration.
**Pause point:** YES — fixed cells may be stored at 4°C in 1× Perm/Wash buffer for up to 24 h before intracellular antibody addition; after final intracellular staining, acquisition should occur within 8 h.

#### Steps:

**CYTOPLASMIC CYTOKINES OR CYTOPLASMIC TARGETS:**
1. Add 250 µL BD Cytofix/Cytoperm to approximately 50 µL stained cells and pipette 5 times.
2. Incubate at 4°C for 20 min protected from light.
3. Wash twice with 2 mL 1× BD Perm/Wash buffer, centrifuging each wash at 350 × g, 4°C, 5 min.

**NUCLEAR TRANSCRIPTION FACTORS:**
4. Prepare FoxP3/TF Fixation/Permeabilization Working Solution at 1 part Component A to 3 parts Component B.
5. Add 1 mL working solution to approximately 50 µL stained cells and pipette 5 times.
6. Incubate at 4°C for a minimum of 4 h; 12-18 h is preferred for FoxP3 and similar nuclear targets.
7. Wash twice with 2 mL 1× kit permeabilization buffer, centrifuging each wash at 350 × g, 4°C, 5 min.

**INTRACELLULAR ANTIBODY STAINING:**
8. Prepare intracellular antibody master mix in 1× Perm/Wash or the kit-specific permeabilization buffer.
9. Add 50 µL intracellular antibody master mix to approximately 50 µL fixed/permeabilized cells.
10. Incubate at 20-22°C for 20-30 min protected from light.
11. Wash twice with 2 mL 1× Perm/Wash or kit-specific permeabilization buffer, centrifuging at 350 × g, 4°C, 5 min.
12. Resuspend in 300 µL staining buffer or PBS for acquisition.

**ICS STIMULATION PATH:**
13. For intracellular cytokine staining, stimulate cells for 4-6 h total using PMA 50 ng/mL + ionomycin 1 µg/mL or antigen-specific stimulus, then add Brefeldin A to 10 µg/mL final concentration 1 h after stimulation start and maintain BFA for 3-5 h before harvest.

#### Exit Criteria (must ALL be true to proceed):
- Fixation chemistry matches the target compartment
- Cytoplasmic fixation ran for 20 min at 4°C or nuclear fixation ran for >=4 h at 4°C
- All post-fix washes used the correct permeabilization buffer
- Intracellular antibody incubation is complete
- Final resuspension volume is 300 µL
- Acquisition is scheduled within the permitted post-stain window

---

### Module 7: COMPENSATION_SETUP_AND_DATA_ACQUISITION

**Preconditions:** Same-day QC passed. Unstained, single-stain, viability, and experimental tubes are ready. PMT voltages or gains are fixed and will not change for the run.
**Pause point:** NO — once single-stain controls are being collected, voltages, gains, and compensation context must remain fixed for the full session.

#### Steps:

**COMPENSATION:**
1. Acquire unstained cells first.
2. Acquire one single-stain control per fluorophore and one viability single-stain control. Use bead-based controls when all reagents are bead-compatible; use cell-based controls when brightness matching is required.
3. [CRITICAL] Ensure the positive single-stain population is at least as bright as the experimental sample in its primary detector.
4. Calculate compensation with automated software when controls are bead-based and clean; otherwise switch to manual inspection and adjustment.
5. Evaluate compensation:
   - Over-compensation: positive population is below the negative in an adjacent channel.
   - Under-compensation: positive population is above the negative in an adjacent channel.
6. Repeat a control rather than altering PMT voltages if compensation is wrong. Do not change detector settings after compensation has started.

**ACQUISITION:**
7. Immediately before loading each tube, invert 3 times and vortex 2 sec at medium speed.
8. Filter fixed samples through a 40 µm strainer before acquisition.
9. Acquire at low flow rate for dim populations and rare populations; use medium flow rate for routine phenotyping only if event resolution remains stable.
10. Collect:
   - 10,000-50,000 events in the parent gate for populations >=1%.
   - 50,000-100,000 events in the parent gate for populations <1%.
11. Apply the doublet decision rule:
   - <5%: proceed.
   - 5-10%: dilute 1:2 and re-check.
   - >10%: filter through 40 µm and acquire at low flow.
   - >25%: stop and do not interpret the sample.
12. If the event rate drops unexpectedly, remove the tube, vortex 2 sec, re-load, then filter and backflush if the rate does not recover.

#### Exit Criteria (must ALL be true to proceed):
- Compensation matrix was generated from same-day controls
- Detector settings did not change after compensation began
- Experimental samples were mixed immediately before loading
- Acquisition flow rate matches signal resolution requirements
- Required event counts in the parent gate were collected
- Doublet and clogging issues were resolved or documented

---

### Module 8: GATING_ANALYSIS_AND_REPORTING

**Preconditions:** FCS files, compensation matrix, lane or tube map, and FMO controls are available. The analysis workspace is linked to the correct compensation file and same-day acquisition batch.
**Pause point:** YES — analysis can be resumed later if the compensation matrix, raw FCS files, and workspace remain unchanged.

#### Steps:

1. Import FCS files and apply the correct same-day compensation matrix.
2. Build the gating hierarchy in this order:
   - FSC-A vs SSC-A scatter gate.
   - FSC-H vs FSC-W singlet gate.
   - Optional SSC-H vs SSC-W singlet refinement.
   - Live-cell gate using the viability dye-negative population.
   - CD45 or lineage parent gates.
   - Terminal phenotype or functional gates.
3. Use FMO controls to place positive/negative gates for every gated marker. Set the gate at the upper boundary of the FMO-negative population and apply the same gate to all experimental samples in the batch.
4. Report frequencies as percent of the immediate parent gate unless the figure explicitly states another denominator.
5. Report MFI as median fluorescence intensity, not mean fluorescence intensity, for skewed or broad distributions.
6. Export:
   - Full statistics table as CSV.
   - Gating strategy as PDF.
   - Workspace file.
   - Compensation matrix CSV.
7. Archive raw FCS, workspace, PDF gating tree, and batch record together.

#### Exit Criteria (must ALL be true to proceed):
- Compensation matrix is correctly linked to the workspace
- Gating hierarchy includes scatter, singlets, live cells, and lineage parent gates
- FMO controls were used for gated markers
- Statistics are reported with the correct denominator
- Exported data package includes raw, processed, and documentation files
- Results are traceable back to the same-day batch record

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: pre_stain_qc
CONDITION: Cell viability before staining is <70%
DIAGNOSIS: Poor starting sample quality
CONFIDENCE: high
LIKELY_CAUSES:
  - Processing delay exceeded the tolerated window
  - Temperature control failed during dissociation or isolation
  - ACK lysis or trypsin exposure was too long
DISTINGUISH:
  - If viability drops sharply immediately after ACK or trypsin, the damage occurred during processing rather than during staining
  - If PBMC viability is poor but blood was processed >4 h after draw, transport delay is more likely than staining failure
  - If viability is low before any antibody is added, the issue is upstream sample quality rather than dye toxicity
IMMEDIATE_FIX:
  - Add one extra wash in staining buffer
  - Consider dead-cell removal when viability is 50-69%
  - Stop the workflow if viability is <50%
PREVENTION: Maintain cold chain, start PBMC isolation within 4 h of blood draw, limit ACK to exactly 1 min, and neutralize trypsin promptly

---

### RULE DX-002
STAGE: sample_preparation
CONDITION: Visible clumps remain in suspension or the sample rapidly clogs the instrument
DIAGNOSIS: Aggregated single-cell suspension
CONFIDENCE: high
LIKELY_CAUSES:
  - EDTA absent from buffer
  - DNase I inactive in tissue digests
  - Cell concentration too high
  - Fixed cells aggregated during storage
DISTINGUISH:
  - If clumps are visible before staining, preparation buffer and tissue digestion are the main suspects
  - If clumps appear after fixation, over-dense fixation or post-fix storage aggregation is more likely
  - If filtration immediately improves event rate, fluidics failure is less likely than sample aggregation
IMMEDIATE_FIX:
  - Filter through 70 µm, then 40 µm
  - Adjust to 1-5 × 10^6 cells/mL
  - Add EDTA to 2 mM and DNase I 0.1 mg/mL for tissue digestion repeats
PREVENTION: Keep EDTA in all buffers, avoid fixation above 5 × 10^6 cells per 100 µL, and filter fixed samples before acquisition

---

### RULE DX-003
STAGE: viability_staining
CONDITION: Nearly all cells appear dead after viability staining
DIAGNOSIS: Viability dye preparation or upstream viability failure
CONFIDENCE: medium
LIKELY_CAUSES:
  - Cells were already dead before staining
  - Viability dye was too concentrated
  - Residual serum or BSA altered dye behavior
DISTINGUISH:
  - If unstained scatter looks normal but viability-dye tube is uniformly positive, dye concentration or preparation is more likely than biology
  - If trypan blue viability was already poor, upstream cell death is more likely than dye failure
  - If heat-killed controls and live cells overlap, the dye preparation is more likely wrong than the gating strategy
IMMEDIATE_FIX:
  - Re-prepare dye at the correct dilution in protein-free PBS
  - Repeat the double PBS wash before dye addition
  - Verify trypan blue viability before repeating the stain
PREVENTION: Prepare viability dye immediately before use, use protein-free PBS only, and validate new dye lots on live and heat-killed controls

---

### RULE DX-004
STAGE: viability_staining
CONDITION: Live and dead populations overlap strongly in the viability channel
DIAGNOSIS: Poor live/dead separation
CONFIDENCE: high
LIKELY_CAUSES:
  - Residual protein quenched the amine-reactive dye
  - Dye was too dilute
  - Dye was reconstituted or stored incorrectly
DISTINGUISH:
  - If live:dead MFI ratio is <10:1, separation chemistry is limiting rather than gate placement
  - If a heat-killed control also fails to separate, the dye or buffer is the primary problem
  - If only one sample has poor separation while others look normal, sample handling is more likely than reagent failure
IMMEDIATE_FIX:
  - Repeat with two PBS washes and fresh dye
  - Increase dye concentration within the validated working range
  - Use a fresh aliquot reconstituted correctly
PREVENTION: Validate each dye on the target cell type, keep DMSO stocks frozen, and never stain amine-reactive dyes in BSA- or FBS-containing buffer

---

### RULE DX-005
STAGE: surface_staining
CONDITION: Expected positive population is absent
DIAGNOSIS: Antibody, detector, or biological-expression failure
CONFIDENCE: medium
LIKELY_CAUSES:
  - Antibody was omitted
  - Detector assignment is wrong
  - Target antigen was not expressed or was damaged during preparation
DISTINGUISH:
  - If the single-stain control is also negative, reagent or detector assignment is more likely than biology
  - If the positive biological control is positive but the test sample is negative, biological absence is more likely than technical failure
  - If trypsinized samples lose integrin-family markers while enzyme-free samples do not, epitope loss is more likely than antibody failure
IMMEDIATE_FIX:
  - Verify detector and fluorophore assignment
  - Repeat with a positive biological control
  - Switch to enzyme-free dissociation for trypsin-sensitive markers
PREVENTION: Include positive controls, validate detector maps before acquisition, and protect trypsin-sensitive epitopes during sample prep

---

### RULE DX-006
STAGE: surface_staining
CONDITION: High non-specific background is concentrated in monocytes or macrophage-like populations
DIAGNOSIS: Fc blocking failure
CONFIDENCE: high
LIKELY_CAUSES:
  - Fc block was omitted
  - Wrong species Fc block was used
  - Fc block incubation was too short
DISTINGUISH:
  - If background is strongest on CD14+ or myeloid-like cells rather than all cells, Fc receptors are the main suspect rather than dead-cell binding
  - If repeating with the correct species block resolves the issue, Fc mismatch is confirmed
  - If background remains high across all cell types, dead cells or antibody aggregates are more likely than Fc receptors alone
IMMEDIATE_FIX:
  - Repeat staining with the correct species-matched Fc block
  - Extend incubation to 10-15 min for human or 5-10 min for mouse
  - Do not wash after Fc block
PREVENTION: Match Fc block to sample species, document the reagent in the worksheet, and train operators not to wash after blocking

---

### RULE DX-007
STAGE: surface_staining
CONDITION: Uniform high background is present across multiple populations
DIAGNOSIS: Dead-cell binding, aggregated antibody, or antibody over-titration
CONFIDENCE: medium
LIKELY_CAUSES:
  - Sample contains too many dead cells
  - Antibody stock contains precipitates
  - Antibody concentration is too high
DISTINGUISH:
  - If bead-based single-stains are clean but cells are noisy, cell biology or dead cells are more likely than reagent purity
  - If centrifuging the antibody stock removes background, precipitated antibody is more likely than Fc binding
  - If lowering antibody concentration restores specificity, over-titration is more likely than compensation error
IMMEDIATE_FIX:
  - Tighten live-cell gating
  - Centrifuge antibody stocks at 10,000 × g, 4°C, 5 min
  - Re-titrate the antibody downward
PREVENTION: Use viable samples, centrifuge new antibody stocks, and document titration data for every lot

---

### RULE DX-008
STAGE: fixation_intracellular
CONDITION: FoxP3 or other nuclear transcription factor signal is absent or extremely dim
DIAGNOSIS: Wrong fixation/permeabilization chemistry for nuclear targets
CONFIDENCE: high
LIKELY_CAUSES:
  - BD Cytofix/Cytoperm was used instead of a transcription-factor kit
  - Nuclear fixation time was <4 h
  - Component A was stored incorrectly
DISTINGUISH:
  - If BD Cytofix/Cytoperm was used, the cause is methodological rather than antibody titration
  - If the correct kit was used but incubation was <4 h, under-fixation is more likely than panel design failure
  - If a same-lot repeat with properly stored kit restores signal, storage failure is confirmed
IMMEDIATE_FIX:
  - Repeat with the dedicated FoxP3/TF kit
  - Fix for >=4 h at 4°C, preferably 12-18 h
  - Replace incorrectly stored kit components
PREVENTION: Decide the target compartment before staining, store kit components exactly as directed, and never substitute cytoplasmic fixation kits for nuclear antigens

---

### RULE DX-009
STAGE: compensation
CONDITION: Positive events fall below the negative population in a spillover channel
DIAGNOSIS: Over-compensation
CONFIDENCE: high
LIKELY_CAUSES:
  - Single-stain control is much brighter than the experimental sample
  - Spillover coefficient was set too high
  - Old matrix was reused under different voltages
DISTINGUISH:
  - If the same artifact appears across all samples and controls in that pair, matrix calculation is the issue rather than biology
  - If voltages changed after controls were acquired, the matrix is invalid rather than the fluorophore pairing alone
  - If a dimmer cell-based single-stain resolves the problem, brightness mismatch is confirmed
IMMEDIATE_FIX:
  - Re-acquire a matched-brightness single-stain control
  - Recalculate compensation without changing voltages
  - Discard any prior-session matrix
PREVENTION: Match single-stain brightness to the experiment, lock detector settings before controls, and never reuse matrices across sessions

---

### RULE DX-010
STAGE: compensation
CONDITION: Positive events remain above the negative population in a spillover channel after compensation
DIAGNOSIS: Under-compensation
CONFIDENCE: high
LIKELY_CAUSES:
  - Single-stain control is dimmer than the experimental sample
  - Spillover coefficient is too low
  - Single-stain control failed to capture the correct antibody species or fluorophore
DISTINGUISH:
  - If the single-stain primary channel is dim relative to the sample, brightness mismatch is more likely than wrong gating
  - If bead capture failed for one antibody species, the single-stain will lack a clear positive peak and the matrix will be underfit
  - If manual increase of the coefficient fixes the adjacency pattern without changing biological populations, compensation is the true problem
IMMEDIATE_FIX:
  - Acquire a brighter single-stain control
  - Use the correct bead type or cell-based single-stain
  - Recalculate the matrix from scratch
PREVENTION: Verify bead compatibility by antibody host species, ensure single-stain brightness meets or exceeds the sample, and review compensation visually before samples are interpreted

---

### RULE DX-011
STAGE: panel_qc
CONDITION: Tandem dye single-stain shows donor-channel spillover >20% of acceptor signal
DIAGNOSIS: Tandem dye degradation
CONFIDENCE: high
LIKELY_CAUSES:
  - Antibody was frozen or repeatedly warmed
  - Reagent is old or light-damaged
  - Storage temperature was incorrect
DISTINGUISH:
  - If donor-channel leakage is visible in the single-stain control itself, tandem failure is more likely than compensation error
  - If a fresh lot restores the donor:acceptor ratio, reagent degradation rather than instrument drift is confirmed
  - If only one tandem lot fails while others are intact, storage or lot-specific failure is more likely than panel design
IMMEDIATE_FIX:
  - Stop and replace the tandem reagent
  - Rebuild the panel around a stable fluorophore if no replacement is available
  - Repeat the single-stain check before restarting
PREVENTION: Store tandem dyes at 4°C in the dark, never freeze them, and run donor:acceptor checks every experiment day

---

### RULE DX-012
STAGE: acquisition
CONDITION: Doublet rate exceeds 10%
DIAGNOSIS: High aggregate or coincidence burden
CONFIDENCE: high
LIKELY_CAUSES:
  - Cell concentration is too high
  - Post-fixation aggregation occurred
  - Sample was not mixed or filtered before loading
DISTINGUISH:
  - If dilution and filtering reduce the doublet cloud, sample handling is the issue rather than instrument electronics
  - If fixed samples are worse than unfixed samples from the same prep, fixation density is more likely than poor dissociation
  - If doublets persist >25% after filtering, sample integrity is too poor for reliable interpretation
IMMEDIATE_FIX:
  - Dilute 1:2
  - Filter through 40 µm mesh
  - Acquire at low flow rate
PREVENTION: Keep samples at 1-5 × 10^6 cells/mL, filter fixed samples immediately before loading, and do not fix dense pellets

---

### RULE DX-013
STAGE: data_analysis
CONDITION: Expected population cannot be found or varies widely between replicates
DIAGNOSIS: Gating hierarchy or control strategy failure
CONFIDENCE: medium
LIKELY_CAUSES:
  - Wrong parent gate
  - FMO controls missing or misapplied
  - Gate order is incorrect
  - Batch-to-batch staining drift occurred
DISTINGUISH:
  - If backgating places the missing population outside the expected parent, hierarchy is wrong rather than biology absent
  - If FMO and unstained are identical for a truly low-spread channel, the issue may be minimal spread rather than incorrect control prep
  - If replicate gates drift only because different operators moved them, analytic subjectivity is more likely than biology
IMMEDIATE_FIX:
  - Backgate the expected positive population
  - Rebuild the template from FMO controls
  - Lock gate positions across the batch
PREVENTION: Use FMOs for gated markers, predefine gating order, and create analysis templates before looking at experimental outcomes

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-020)

#### RISK RM-001
STAGE: sample_preparation
ITEM: Cell pellet loss during aspiration after staining or fixation
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm pellets are visible after each 350 × g wash and aspiration stops 2-3 mm above the pellet
MITIGATION: Use controlled aspiration with a P1000 for small pellets; leave approximately 50 µL residual volume; train operators on pellet position awareness

---

#### RISK RM-002
STAGE: data_analysis
ITEM: Unstained control used instead of FMO for gate placement in a multicolor panel
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Verify an FMO exists for every gated marker in panels with 3 or more colors
MITIGATION: Make FMO controls mandatory for gated markers; allocate cells for FMOs during experimental planning; archive FMO-based gate figures with the batch record

---

#### RISK RM-003
STAGE: compensation
ITEM: Compensation matrix reused from a previous session
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm same-day single-stain controls and same-day QC report exist for the matrix linked to the workspace
MITIGATION: Recalculate compensation every session; tie matrix files to the same-day instrument QC report and batch record; reject any cross-session matrix

---

#### RISK RM-004
STAGE: panel_qc
ITEM: Tandem dye degradation creates false donor-channel signal
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify donor:acceptor signal ratio is <5% in tandem single-stain controls
MITIGATION: Store tandem antibodies at 4°C in the dark, never freeze them, and replace any lot with donor leakage >20%

---

#### RISK RM-005
STAGE: viability_staining
ITEM: Amine-reactive viability dye added in protein-containing buffer
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm two PBS washes were performed and the dye was diluted in protein-free PBS
MITIGATION: Use protein-free PBS only for amine-reactive dyes; never add the dye directly to staining buffer with BSA or FBS

---

#### RISK RM-006
STAGE: fc_block
ITEM: Wrong species Fc block used
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Match sample species against Fc block reagent before use
MITIGATION: Use human Fc block for human samples, anti-CD16/32 for mouse samples, and dual block for mixed-species xenograft material

---

#### RISK RM-007
STAGE: fixation
ITEM: PI or 7-AAD used in a fixed-sample workflow
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Confirm viability dye choice before fixation begins
MITIGATION: Restrict PI and 7-AAD to unfixed surface-only workflows; use fixable LIVE/DEAD or Zombie dyes whenever fixation is planned

---

#### RISK RM-008
STAGE: fixation
ITEM: Cytoplasmic fixation kit used for nuclear transcription factors
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify panel_type and fixation_kit match before fixation
MITIGATION: Route FoxP3, T-bet, RORgt, GATA3, BCL6, and Helios to a transcription-factor kit only

---

#### RISK RM-009
STAGE: safety
ITEM: Formaldehyde exposure during fixation handled outside engineering controls
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify fixation is performed in a BSC or fume hood and waste is segregated
MITIGATION: Perform all fixation steps inside engineering controls, double glove, and collect fixative waste separately for EHS pickup

---

#### RISK RM-010
STAGE: instrument_qc
ITEM: Daily instrument QC not run on the same day as acquisition
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm the QC report date matches the experimental date
MITIGATION: Make same-day QC a hard prerequisite; reject acquisition when same-day QC is absent

---

#### RISK RM-011
STAGE: data_analysis
ITEM: Doublet exclusion omitted from the gating hierarchy
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Review the analysis template for FSC-H vs FSC-W or equivalent singlet gates
MITIGATION: Lock singlet gating into all templates; include the singlet gate in exported gating strategy figures

---

#### RISK RM-012
STAGE: fixation
ITEM: Post-fixation aggregation caused by fixing dense cell suspensions
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Verify cell density before fixation is <=5 × 10^6 cells per 100 µL
MITIGATION: Dilute dense samples before fixative addition and fully resuspend pellets during the first 30 sec of fixation

---

#### RISK RM-013
STAGE: compensation
ITEM: Compensation bead species mismatch for the antibody host species
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Confirm bead capture chemistry matches the antibody species for each single-stain control
MITIGATION: Label compensation tubes with antibody species; use species-compatible beads or cell-based controls when bead capture is not possible

---

#### RISK RM-014
STAGE: sample_preparation
ITEM: PBMC processing delay exceeds 4 h from blood draw
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Record blood collection time and Ficoll start time in the batch record
MITIGATION: Process within 4 h; use transport-stabilization methods only when validated for the assay

---

#### RISK RM-015
STAGE: panel_design
ITEM: BV dyes included in a methanol-based phospho-flow panel
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Review fluorophore choices before any methanol-compatible phospho-flow workflow
MITIGATION: Remove BV dyes from methanol workflows and redesign the panel before starting

---

#### RISK RM-016
STAGE: sample_preparation
ITEM: Cell concentration above 5 × 10^6 cells/mL causes clumping and poor staining uniformity
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Confirm cell concentration before staining and acquisition
MITIGATION: Keep suspension at 1-5 × 10^6 cells/mL and mix immediately before every centrifugation or acquisition step

---

#### RISK RM-017
STAGE: pbmc_isolation
ITEM: Ficoll gradient run with brake engaged
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Verify brake 0 is set before centrifuge start
MITIGATION: Include brake setting in the PBMC worksheet; do not start the centrifuge until brake and acceleration are confirmed

---

#### RISK RM-018
STAGE: sample_preparation
ITEM: Trypsin overexposure destroys surface epitopes
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Record trypsin exposure time for adherent samples with surface-marker panels
MITIGATION: Limit trypsin to 3-5 min; use enzyme-free dissociation for trypsin-sensitive epitopes

---

#### RISK RM-019
STAGE: panel_qc
ITEM: Tandem dye donor:acceptor ratio not checked on the day of the run
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Review single-stain QC plots for all tandem channels before experimental samples are interpreted
MITIGATION: Require same-day tandem integrity review as part of pre-run signoff

---

#### RISK RM-020
STAGE: data_analysis
ITEM: FMO control prepared from the wrong donor, wrong cell type, or wrong fixation state
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm each FMO shares the same sample source and same fixation/permeabilization state as the experimental samples
MITIGATION: Build FMOs from the same donor or same cell source and through the same processing path as the experiment

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: data_analysis
ITEM: Rare-population interpretation attempted without FMO controls
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm FMO controls exist for every gated low-frequency or dim marker before the data are reported
MITIGATION: (1) Make FMOs mandatory for rare or dim populations. (2) Rebuild the analysis only after FMOs are collected. (3) Reject any figure that labels a rare population without an FMO-supported gate.

---

#### RISK CF-002
STAGE: compensation
ITEM: Cross-session compensation matrix used under different voltages or gains
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Match the matrix date, instrument, and detector settings to the raw FCS batch before analysis
MITIGATION: (1) Generate a same-day matrix every run. (2) Lock detector settings before collecting controls. (3) Discard and regenerate compensation if settings change at any point.

---

#### RISK CF-003
STAGE: instrument_qc
ITEM: Experimental samples acquired after failed or skipped daily instrument QC
PROBABILITY: low
IMPACT: high
SCORE: CRITICAL
CHECK: Verify a passing same-day QC report is archived with the experiment
MITIGATION: (1) Stop acquisition when same-day QC is absent or failed twice. (2) Notify the facility manager or service contact. (3) Reacquire samples only after a passing QC report is obtained.

---

## 6. PARAMETER CONSTRAINTS

### Sample Quality

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Pre-stain viability | 70% | >=85% | — | 50-69%: conditional proceed with warning; <50%: stop |
| Cells per staining tube | 0.5 × 10^6 | 1 × 10^6 | 5 × 10^6 | >5 × 10^6 raises aggregation risk |
| Cell concentration before staining | 0.5 × 10^6/mL | 1-5 × 10^6/mL | 5 × 10^6/mL | Dilute if above maximum |
| Time from blood draw to Ficoll start | — | <=4 h | 4 h | >4 h: viability and phenotype drift risk |

### Staining Timing

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Viability dye incubation | 15 min at 20-22°C | 20-30 min at 20-22°C | 30 min at 20-22°C | >30 min increases handling time without benefit |
| Human Fc block | 5 min at 4°C | 10-15 min at 4°C | 30 min at 4°C | <5 min may be inadequate |
| Mouse Fc block | 5 min at 4°C | 5-10 min at 4°C | 15 min at 4°C | >15 min adds no routine benefit |
| Surface staining | 15 min at 4°C | 20-30 min at 4°C | 30 min at 4°C | >30 min increases internalization risk |
| Cytofix/Cytoperm fixation | 20 min at 4°C | 20 min at 4°C | 45 min at 4°C | >60 min impairs some intracellular signals |
| FoxP3/TF fixation | 4 h at 4°C | 12-18 h at 4°C | 24 h at 4°C | <4 h gives incomplete nuclear access |
| Intracellular antibody incubation | 20 min at 20-22°C | 20-30 min at 20-22°C | 30 min at 20-22°C | >30 min increases background risk |
| Post-fix storage before intracellular stain | — | within 24 h | 24 h | >24 h degrades tandem dye signal |
| Post-intracellular acquisition window | — | within 8 h | 24 h | >8 h reduces tandem and dim-signal quality |

### Instrument and Acquisition

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| BD laser warm-up | 30 min | 30 min | — | Do not run QC before warm-up completes |
| FACSAria III warm-up | 45 min | 45-60 min | — | Do not run QC before warm-up completes |
| CytoFLEX warm-up | 15 min | 15 min | — | Do not run QC before warm-up completes |
| Daily QC CV | — | <=3% | 3% | >3% requires repeat QC or service decision |
| Event count in parent gate for common populations | 10,000 | 50,000 | — | Below minimum weakens statistical confidence |
| Event count in parent gate for rare populations | 50,000 | 100,000 | — | Below minimum weakens rare-population analysis |
| Doublet rate | — | <5% | 10% | >10% requires dilution/filtering; >25% stop |

### Compensation and Panel QC

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Stain Index | 3 | >=5 | — | 2-3: troubleshoot; <2: stop |
| Tandem donor:acceptor ratio | — | <5% | 20% | 5-20% caution; >20% reject reagent |
| FMO requirement for gated markers | complete | complete | complete | Missing FMO invalidates low-frequency gate placement |

---

## 7. QC GATES

### QC Gate 1: Pre-Staining Sample Quality

PASS criteria (ALL must be true):
  - Viability is >=70%
  - At least 1 × 10^6 cells are allocated per tube unless the assay design justifies less
  - No visible aggregates remain after final filtration
  - Sample source-specific prep is complete and documented

ACTION if FAIL: If viability is 50-69%, document conditional proceed and add extra washes. If viability is <50%, stop. If clumps remain, filter again and reassess before staining.

---

### QC Gate 2: Daily Instrument QC

PASS criteria (ALL must be true):
  - Same-day instrument QC passed
  - Fluorescence CV is <=3%
  - QC report is saved with date stamp
  - Detector settings are locked before single-stain controls

ACTION if FAIL: Repeat QC once. If the second run fails, do not proceed and contact the facility manager or service contact.

---

### QC Gate 3: Compensation Adequacy

PASS criteria (ALL must be true):
  - Same-day single-stain controls were acquired for every fluorophore
  - Single-stain positive populations are clear and bright enough
  - No visible over-compensation or under-compensation remains in adjacent channels
  - Tandem donor:acceptor ratio is within acceptable limits

ACTION if FAIL: Recollect the faulty control, rebuild compensation without changing voltages, and replace degraded tandem reagents before running experiments.

---

### QC Gate 4: Acquisition Quality

PASS criteria (ALL must be true):
  - Event rate is stable
  - Required event count in the parent gate is met
  - Doublet rate is <10%
  - No unresolved clogging or flow instability occurred

ACTION if FAIL: Dilute, filter, or backflush according to the acquisition workflow. Stop and document if doublets remain >25% or clogging persists.

---

### QC Gate 5: Analysis Quality

PASS criteria (ALL must be true):
  - Compensation matrix matches the batch
  - Gating hierarchy includes scatter, singlets, and live cells
  - FMO controls are used for gated markers
  - Statistics are reported using the correct parent gate
  - Raw FCS, workspace, matrix, and PDF gating strategy are archived together

ACTION if FAIL: Rebuild the analysis template from the correct controls, repeat gate placement with FMOs, and do not report findings until the archive package is complete.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified flow cytometry problem and root cause, or "QC PASS — proceed" |
| confidence | enum: high / medium / low | Confidence in diagnosis based on controls, QC, and sample state |
| recommended_actions | list[string] | Ordered action list; immediate corrective action first, prevention second |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Status for each of the 5 QC gates |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters linked to diagnostic rules |
| protocol_section_reference | string | Section of FC-SOP-001 relevant to the issue |
| compensation_status | enum: valid / over_compensated / under_compensated / missing / invalidated_by_voltage_change | Status of the compensation workflow |
| acquisition_status | enum: acceptable / low_events / high_doublets / clogging / stopped | Status of the acquisition run |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | Sample generation from cultured cells is required before flow staining |
| western_blot_v1 | Protein-level validation of flow phenotypes is needed from matched lysates |
| rt_qpcr_v1 | Gene-expression confirmation is needed for sorted or phenotyped populations |
| immunofluorescence_v1 | Spatial localization of a marker is required instead of suspension-based measurement |
| transfection_v1 | Genetic perturbation is required before downstream flow cytometry readout |
| cell_sorting_v1 | User needs preparative or analytical sorting rather than analysis-only acquisition |
| cytokine_elisa_v1 | Secreted cytokine quantification is needed in supernatant rather than intracellular staining |
| single_cell_rna_seq_v1 | High-dimensional transcriptomic profiling is needed after flow-defined population selection |
