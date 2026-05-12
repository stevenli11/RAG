---
skill_id: emsa_v1
skill_name: Electrophoretic Mobility Shift Assay Complete Workflow Skill
version: 1.0
method_family: nucleic_acid_protein_interaction
tags: [emsa, gel_shift, gel_retardation, dna_binding, rna_binding, transcription_factor_binding, native_page, probe_labeling, cold_competition, supershift, nuclear_extract, binding_reaction, chemiluminescent_detection, fluorescent_detection]
applies_to: [dna_protein_binding, rna_protein_binding, nuclear_extract_binding, purified_protein_binding, native_page_binding_analysis, competition_assay, supershift_assay]
does_not_apply_to: [chip_seq, footprinting, surface_plasmon_resonance, isothermal_titration_calorimetry, denaturing_page, capillary_electrophoresis_only, in_vivo_binding_assays]
risk_level: medium
bsl_level: "BSL-2 for human-derived extracts unless institutional assessment permits lower containment"
last_updated: 2026-03-16
source_protocol: SOP-EMSA-001
---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I run an EMSA," "why is my shifted band weak," "how do I prepare a DNA probe," "how do I set up a supershift," "why do I see smeared EMSA bands," "how much nuclear extract should I use," "how do I run a cold competition assay," "my free probe runs badly," "what gel percentage should I use for EMSA," "how do I detect transcription factor binding," "why do I have nonspecific bands," or any question about electrophoretic mobility shift assay workflow design, execution, QC, and troubleshooting. This skill covers the complete EMSA workflow: probe design and labeling, protein extract preparation and QC, binding reaction assembly, competitor and supershift controls, native polyacrylamide gel preparation, electrophoresis, transfer or direct gel detection, and structured diagnostic rules for low shift signal, smeared bands, nonspecific complexes, failed supershifts, probe degradation, and overloading artifacts. This skill does NOT cover: chromatin immunoprecipitation, DNase I footprinting, SPR, ITC, capillary mobility assays, or denaturing nucleic acid electrophoresis. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| probe_type | enum: dsdna / ssdna / rna | Probe chemistry used in the assay |
| protein_source | enum: nuclear_extract / whole_cell_extract / purified_protein / recombinant_protein | Source of the binding protein |
| detection_mode | enum: biotin_chemiluminescent / fluorescent / radioactive / direct_dye | Probe detection method |
| workflow_goal | enum: binding_confirmation / competition_assay / supershift_assay / optimization / troubleshooting | Primary analytical objective |
| target_factor | string | Name of the transcription factor, RNA-binding protein, or protein complex under study |
| gel_format | enum: mini_native_page / midi_native_page / large_format_native_page | Gel size and running format |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| probe_length_bp | int | Length of the labeled probe in bp or nt |
| probe_label_position | enum: 5prime / 3prime / internal / both_ends | Position of probe labeling |
| probe_concentration_fmol_per_uL | float | Working probe concentration |
| extract_concentration_mg_per_mL | float | Protein concentration of the extract |
| protein_input_ug | float | Protein mass per binding reaction |
| binding_buffer_composition | string | Salt, glycerol, detergent, reductant, and carrier components used |
| poly_didc_input_ug | float | Nonspecific competitor amount per reaction |
| competitor_fold_excess | int | Fold excess of unlabeled competitor relative to labeled probe |
| antibody_input_ug | float | Antibody amount in supershift reactions |
| binding_reaction_volume | string | Total reaction volume in µL |
| incubation_time | string | Binding incubation duration and temperature |
| gel_percent | float | Native acrylamide percentage |
| running_buffer | string | Running buffer formulation |
| run_voltage | float | Electrophoresis voltage |
| pre_run_time | string | Native gel pre-run duration |
| free_probe_pattern | string | Description of free probe migration |
| shift_signal_strength | enum: absent / weak / moderate / strong | Observed shift intensity |
| smear_description | string | Description of smear or broad band pattern |
| membrane_transfer_used | enum: yes / no | Whether complexes were transferred after electrophoresis |

---

## 3. WORKFLOW MODULES

### Module 1: PROBE_DESIGN_AND_LABELING

**Preconditions:** The target binding sequence has been defined. Probe synthesis or oligo stocks are available. Labeling chemistry matches the detection platform.
**Pause point:** YES - annealed or labeled probes can be aliquoted and stored at -20°C for short-term use or -80°C for long-term use. Avoid more than 3 freeze-thaw cycles.

#### Steps:

1. Design probe sequence:
   - Use 18-30 bp for the labeled probe; shorter than 15 bp risks incomplete motif contact, and longer than 40 bp may generate double bands from secondary structure or internal nick.
   - Add 3-6 flanking bases on each side of the motif when motif-only probes produce weak binding.
2. For double-stranded probes:
   - Mix complementary oligos at equimolar concentration.
   - Example annealing mix: 10 µL forward oligo at 100 µM + 10 µL reverse oligo at 100 µM + 80 µL annealing buffer.
   - Heat to 95°C for 5 min, then cool to 20-25°C over 45-60 min.
3. Select label:
   - Biotin 5' label for chemiluminescent EMSA.
   - Fluorophore 5' label for direct gel imaging.
   - Radioactive end-labeling only in facilities approved for isotope work.
4. For biotin-labeled probes:
   - Use 5' biotinylated oligos or enzymatic end-labeling validated for EMSA.
   - Purify labeled probe if free label contamination is present.
5. For RNA probes:
   - Generate RNA by in vitro transcription from a sequence-verified template or order synthetic RNA with the validated label position.
   - Purify transcript by denaturing PAGE, spin-column cleanup, or kit-validated cleanup before EMSA use.
   - Refold RNA probe at 65°C for 5 min, then cool on ice for 2 min and equilibrate at 20-25°C for 10 min if the RNA target requires a defined secondary structure.
6. Quantify probe concentration and prepare working aliquots:
   - Use 5-20 fmol for quantitative studies where probe should remain at or below the estimated Kd.
   - Use 20-50 fmol for initial optimization or low-signal targets.
   - Probe concentration substantially above the Kd saturates binding sites and reduces the apparent shift fraction.
7. [CRITICAL] Confirm that unlabeled wild-type and mutant competitor probes are prepared from the same sequence backbone as the labeled probe.
8. [BEGINNER TRAP] Do not use probes with self-complementary secondary structure unless that structure is part of the biological target design.

#### Exit Criteria (must ALL be true to proceed):
- Probe sequence and length are documented
- Labeling chemistry matches detection mode
- Wild-type and mutant competitor probes are available when needed
- Probe working concentration is defined

---

### Module 2: PROTEIN_EXTRACT_PREPARATION_AND_QC

**Preconditions:** Cells, tissues, or purified proteins are available. Protease inhibitors and, when relevant, phosphatase inhibitors are prepared fresh. All extraction steps are performed on ice or at 4°C unless a specific step requires another temperature.
**Pause point:** YES - clarified extracts can be aliquoted and stored at -80°C. Avoid more than 2 freeze-thaw cycles for nuclear extracts used in EMSA.

#### Steps:

1. For cultured-cell nuclear extracts:
   - Harvest 5 × 10^6 to 2 × 10^7 cells per preparation.
   - Wash cells in ice-cold PBS.
   - Centrifuge at 500 ×g, 4°C, 5 min after each wash.
2. Resuspend cell pellet in hypotonic buffer:
   - Example: 400 µL hypotonic buffer per 1 × 10^7 cells.
   - Incubate on ice for 10 min.
3. Add nonionic detergent if the extraction method requires membrane lysis:
   - After the 10 min ice incubation, add NP-40 substitute directly to the cell suspension to a final concentration of 0.1-0.3%.
   - Example: add 4-12 µL of 10% NP-40 substitute to 400 µL swollen cell suspension.
   - Flick the tube 3 times and centrifuge immediately at 3,000 ×g, 4°C, 5 min.
   - This centrifugation separates nuclei as the pellet from cytoplasm in the supernatant; discard the cytoplasmic supernatant and proceed with the nuclear pellet.
   - Use the lowest detergent concentration that yields a clean nuclear pellet.
4. Extract nuclear proteins:
   - Resuspend nuclear pellet in 50-100 µL high-salt extraction buffer per 1 × 10^7 cells.
   - Incubate at 4°C for 20-30 min with intermittent mixing every 5 min.
5. Clarify extract:
   - Centrifuge at 16,000 ×g, 4°C, 15 min.
   - Transfer supernatant to a fresh low-protein-binding tube.
6. Determine protein concentration:
   - Use BCA or Bradford assay compatible with the extraction buffer.
   - Typical EMSA input: 1-5 µg nuclear extract per 20 µL reaction for most transcription factors; 5-10 µg for low-abundance factors.
   - Perform a titration at 1 µg, 3 µg, 5 µg, and 10 µg before committing to final conditions.
7. Validate extract quality before EMSA use:
   - Inspect nuclear pellet integrity during extraction.
   - Confirm enrichment of a nuclear marker and depletion of a cytoplasmic marker by immunoblot or a validated orthogonal assay when starting a new extract workflow.
8. For purified recombinant protein:
   - Verify purity by SDS-PAGE.
   - Exchange buffer before EMSA use when imidazole exceeds 10 mM, glycerol exceeds 20%, or NaCl/KCl exceeds 200 mM in the protein storage buffer.
   - Use Zeba desalting columns for proteins above 7 kDa or Amicon ultrafiltration for buffer exchange.
9. [CRITICAL] Add DTT, protease inhibitors, and phosphatase inhibitors immediately before extraction if the factor is redox-sensitive or phosphorylation-dependent.

#### Exit Criteria (must ALL be true to proceed):
- Extract source and preparation method are documented
- Protein concentration is measured
- Extract quality check is completed for new extract workflows
- Clarified extract is free of visible precipitate
- Storage aliquots and freeze-thaw count are defined

---

### Module 3: BINDING_REACTION_ASSEMBLY

**Preconditions:** Probe and protein inputs are defined. Binding buffer, carrier DNA or RNA, competitor probes, and antibody controls are ready.
**Pause point:** YES - assembled reactions can remain on ice for 5-10 min before incubation if all components except labeled probe are present. After labeled probe addition, proceed directly into the defined incubation window.

#### Steps:

1. Prepare 1× binding buffer:
   - Example final composition: 10 mM Tris-HCl pH 7.5, 50 mM KCl, 1 mM DTT, 5% glycerol, 0.05% NP-40 substitute if validated, 1 mM MgCl2 when the factor requires divalent cations.
   - For RNA EMSA: remove NP-40 substitute unless the protein has been validated to tolerate detergent, omit MgCl2 unless the complex is known to require divalent cations, and add 1-2 U/µL RNase inhibitor to reach 20-40 U per 20 µL reaction; confirm with the inhibitor product datasheet if using a different inhibitor format.
2. Typical 20 µL binding reaction for dsDNA EMSA:
   - 2 µL 10× binding buffer
   - 1-10 µg extract or validated purified protein amount
   - 0.5-2 µg poly(dI:dC) for nonspecific competition
   - 5-20 fmol labeled probe for quantitative studies or 20-50 fmol for initial optimization and low-signal targets
   - Water to 20 µL
3. Add components in order:
   - Water
   - Binding buffer
   - Carrier competitor such as poly(dI:dC)
   - Protein extract
   - Antibody or unlabeled competitor if used
   - Labeled probe last
4. Incubate reaction:
   - 20-25°C for 20-30 min for high-affinity DNA-binding proteins where complex stability is confirmed
   - 4°C for 20-30 min when the complex is unstable at room temperature or when protease sensitivity at 20-25°C has been a problem
   - When starting a new factor, test both temperatures in parallel
5. For purified proteins with low complexity background:
   - Reduce poly(dI:dC) or omit only after direct comparison confirms specific complex retention.
6. [CRITICAL] Keep the final glycerol concentration consistent across all reactions loaded on the same gel.
7. [DO NOT] Heat the reaction after probe addition. EMSA requires native complex preservation.

#### Exit Criteria (must ALL be true to proceed):
- Binding buffer composition is recorded
- Protein input and probe input are recorded
- Reaction volume is consistent across conditions
- Incubation time and temperature are defined

---

### Module 4: COMPETITION_AND_SUPERSHIFT_CONTROLS

**Preconditions:** Binding reaction composition has been defined. Specific and nonspecific competitor probes are available when specificity testing is planned. Antibody identity and epitope compatibility are known when supershift is planned.
**Pause point:** YES - competition reactions can be assembled in parallel with the main binding reactions. Supershift antibody pre-incubation can extend the workflow by 20-30 min.

#### Steps:

1. Set baseline lanes:
   - Free probe only
   - Probe + protein
2. Set specific competition:
   - Add unlabeled wild-type competitor at 25×, 50×, and 100× molar excess relative to labeled probe.
   - Pre-incubate unlabeled competitor with protein for 10 min at 20-25°C before adding labeled probe.
   - This 10 min pre-incubation is separate from and precedes the main binding incubation defined in Module 3 Step 4.
   - Record total incubation time as competitor pre-incubation plus the main binding window.
3. Set nonspecific or mutant competition:
   - Use a sequence-scrambled or motif-mutant competitor at the same molar excess as the wild-type competitor.
4. Set supershift:
   - Add 0.5-2 µg antibody per 20 µL reaction.
   - Pre-incubate protein and antibody at 20-25°C for 15-20 min before adding labeled probe.
   - Reduce pre-incubation to 10 min if longer antibody exposure weakens the baseline shift.
   - Include an isotype-matched control antibody at the same mass in an adjacent lane to confirm that the supershift is not caused by nonspecific antibody-probe interaction.
5. If antibody causes signal loss without a supershift:
   - Compare epitope-blocking versus complex-destabilizing behavior using an isotype control and a no-antibody reaction.
6. For multi-protein complexes:
   - Test antibodies one at a time before combining.
7. [CRITICAL] Keep total volume constant across competition and supershift conditions by balancing with water or carrier buffer.
8. [BEGINNER TRAP] Do not interpret a failed supershift as absence of the factor until you confirm that the antibody recognizes the native epitope under EMSA conditions.

#### Exit Criteria (must ALL be true to proceed):
- Free probe, protein, and control lanes are defined
- Competitor fold excess is recorded
- Antibody amount and pre-incubation time are recorded when supershift is used
- Reaction volumes are matched across all control conditions

---

### Module 5: NATIVE_GEL_PREPARATION_AND_PRE_RUN

**Preconditions:** Gel format, acrylamide percentage, and running buffer are selected. Gel apparatus is clean and leak-free. Samples are ready or will be ready by the end of the pre-run.
**Pause point:** YES - native gels can be cast in advance and held at 4°C in sealed wrap for several hours before use. Pre-run should occur immediately before sample loading.

#### Steps:

1. Select gel percentage:
   - 4-5% native acrylamide for probes above 30 bp or for high-molecular-weight complexes above 100 kDa.
   - 5-6% native acrylamide for 18-30 bp probes with transcription factor complexes in the 50-150 kDa range.
   - 6-8% native acrylamide for probes below 20 bp or compact small-protein complexes.
   - When complex size is unknown, start at 5%.
2. Select buffer system:
   - 0.5× TBE for dsDNA EMSA runs using transcription factor complexes in the 50-150 kDa range.
   - 0.25× TBE when excessive heating or poor resolution is observed with small complexes.
3. Prepare gel solution and polymerize according to gel size.
   - For RNA EMSA, decontaminate glass plates, combs, and spacers with RNase-decontamination solution and rinse with nuclease-free water before casting.
4. Chill running buffer to 4°C if heating-sensitive complexes are expected.
5. Pre-run the gel:
   - 80-120 V, 4°C, 30 min for mini gels in 0.5× TBE.
   - For midi and large-format gels: 100-150 V, 4°C, 45-60 min in 0.5× TBE.
   - Pre-run equilibrates the ionic gradient and removes polymerization artifacts before sample loading.
6. Use RNA-safe native loading dye for RNA EMSA:
   - Use sucrose-based native loading dye for RNA EMSA: 10-20% sucrose, 0.05% bromophenol blue, and RNase-free water.
   - Do not substitute glycerol in RNA EMSA loading buffer, because glycerol can alter RNA secondary structure and complex migration.
   - Load 1-3 µL native loading dye into one spare lane to confirm front migration if the system uses tracking dye.
7. [CRITICAL] Do not include SDS, urea, or reducing sample buffer designed for denaturing PAGE.

#### Exit Criteria (must ALL be true to proceed):
- Gel percentage matches probe and complex size
- Running buffer is prepared at the selected concentration
- Pre-run conditions are recorded
- Gel wells are intact and free of polymerization defects

---

### Module 6: ELECTROPHORESIS_AND_COMPLEX_SEPARATION

**Preconditions:** Native gel has been pre-run. Binding reactions are complete. Running buffer level and cooling conditions are stable.
**Pause point:** NO - once samples are loaded, begin electrophoresis immediately to avoid diffusion and lane distortion.

#### Steps:

1. Add native loading dye to each reaction if it is not already present:
   - Typical addition: 2 µL 10× native loading dye into a 20 µL reaction.
2. Load samples carefully:
   - Load free probe first, then binding reactions, then competition and supershift lanes in logical order.
3. Run the gel:
   - Mini gel in 0.5× TBE: 80-120 V at 4°C for 1-2 h.
   - Large gel formats may require 120-180 V with active cooling.
4. Monitor the free probe front:
   - Stop when the bromophenol blue dye front reaches 1-2 cm from the gel bottom, or when the free probe has migrated at least 60% of the gel length and shows clear separation from the shifted band.
5. If radioactive or fluorescent direct imaging is used:
   - Proceed directly to imaging or gel drying as the detection workflow requires.
6. If biotin chemiluminescent detection is used:
   - Proceed to transfer after electrophoresis without prolonged holding in buffer.
7. [CRITICAL] Keep gel temperature controlled. Excess heating broadens bands and destabilizes weak complexes.
8. [DO NOT] Overload extract to force a stronger shift. Excess extract increases nonspecific retention and smearing.

#### Exit Criteria (must ALL be true to proceed):
- Lane order is documented
- Voltage, time, and temperature are recorded
- Free probe and shifted complexes are separated
- Gel was not overheated during the run

---

### Module 7: DETECTION_TRANSFER_AND_SIGNAL_CAPTURE

**Preconditions:** Electrophoresis is complete. Detection method and transfer or direct imaging route are defined.
**Pause point:** YES - direct fluorescent or radioactive gels can be imaged immediately. Biotin-transfer workflows can pause after membrane crosslinking if the membrane is kept dry and protected according to the kit instructions.

#### Steps:

1. For biotin chemiluminescent EMSA:
   - Transfer complexes to positively charged nylon membrane using semi-dry transfer in 0.5× TBE.
   - Mini-gel starting condition: 300-380 mA constant current for 30-45 min.
   - Scale current for larger formats according to membrane area and apparatus specifications.
   - Do not use PVDF or neutral nylon for biotin-based EMSA.
   - Crosslink nucleic acids to membrane by UV or baking per the kit protocol.
2. For direct fluorescent EMSA:
   - Image the gel using the validated channel and exposure settings for the fluorophore.
3. For radioactive EMSA:
   - Dry the gel if the protocol requires drying.
   - Expose to phosphor screen for 1-16 h, starting at 2 h for moderately active probes.
   - Expose to X-ray film for 30 min to overnight.
   - Capture multiple exposures to ensure at least one image remains in the linear range.
4. For chemiluminescent detection:
   - Block and incubate membrane with streptavidin-HRP or the kit-specific conjugate.
   - Wash 4 times for 5 min each in the kit wash buffer or validated TBST-equivalent wash buffer.
   - Add substrate and image with multiple exposure lengths.
5. Save raw images and annotate lane identity separately from the raw image file.
6. [CRITICAL] Capture at least one unsaturated exposure so free probe and shifted complexes remain quantitatively interpretable.

#### Exit Criteria (must ALL be true to proceed):
- Detection workflow matches probe label
- Transfer or imaging conditions are recorded
- At least one raw unsaturated image is saved
- Lane identity map is preserved

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: binding_reaction
CONDITION: No shifted band is visible, while free probe is sharp and strong
DIAGNOSIS: Binding conditions do not support complex formation
CONFIDENCE: medium
LIKELY_CAUSES:
  - Protein input is too low
  - Salt concentration is too high or too low for the factor
  - Probe motif or flanking sequence is suboptimal
  - Factor is inactive in the extract
DISTINGUISH:
  - Strong free probe with no smear indicates probe integrity is likely preserved
  - A purified positive-control factor or known positive extract can separate protein inactivity from probe design failure
  - Reduced salt or altered glycerol content that restores binding supports a buffer problem
IMMEDIATE_FIX:
  - Increase protein input in a titration series
  - Test 25 mM, 50 mM, and 75 mM KCl in the binding buffer
  - Add a positive-control extract or positive-control probe
PREVENTION: Optimize buffer composition and protein input with a positive-control complex before testing unknown samples

---

### RULE DX-002
STAGE: binding_reaction
CONDITION: Shifted band is weak and inconsistent between repeats
DIAGNOSIS: Binding reaction stability is poor
CONFIDENCE: medium
LIKELY_CAUSES:
  - Extract activity is declining from freeze-thaw or long bench exposure
  - Complex incubation time is not controlled tightly
  - Carrier competitor amount is not consistent
DISTINGUISH:
  - Variability that tracks extract aliquot age implicates extract instability
  - Replicates assembled from the same master mix with tighter timing that improve consistency point to setup timing
  - Stable free probe with unstable shift suggests protein-side instability rather than probe degradation
IMMEDIATE_FIX:
  - Use a fresh extract aliquot
  - Assemble a master mix for all reaction components except protein and probe
  - Keep all reactions on ice until the final incubation step
PREVENTION: Aliquot extracts into single-use volumes; use the same incubation start and stop timing across all lanes

---

### RULE DX-003
STAGE: electrophoresis
CONDITION: Shifted complexes appear smeared or broad across several lanes
DIAGNOSIS: Complex instability or gel overheating during the run
CONFIDENCE: high
LIKELY_CAUSES:
  - Gel temperature is too high
  - Protein input is excessive
  - Binding buffer contains too much salt or glycerol
DISTINGUISH:
  - Broad free probe and broad shifts together implicate gel or running conditions
  - Sharp free probe with smeared shifts implicates unstable complexes or overloaded extract
  - Improvement after running at 4°C or lower voltage supports overheating as the major cause
IMMEDIATE_FIX:
  - Lower voltage and run at 4°C
  - Reduce extract input by 25-50%
  - Lower final glycerol to 2.5-5% and retest if the protocol permits
PREVENTION: Pre-chill buffer and apparatus; titrate protein input before scaling sample numbers

---

### RULE DX-004
STAGE: competition_assay
CONDITION: Unlabeled wild-type competitor fails to reduce the shifted band
DIAGNOSIS: Specificity control failed or competitor design is incorrect
CONFIDENCE: medium
LIKELY_CAUSES:
  - Competitor sequence does not match the labeled probe
  - Competitor concentration is too low
  - Binding is largely nonspecific
DISTINGUISH:
  - A correctly matched competitor at 100× excess should reduce a specific shift
  - If mutant competitor reduces the same band equally, the complex is likely nonspecific
  - Sequence verification of the competitor can separate design error from binding biology
IMMEDIATE_FIX:
  - Confirm competitor sequence and reanneal if needed
  - Increase wild-type competitor to 100× excess
  - Reduce extract input and increase poly(dI:dC) if nonspecific binding dominates
PREVENTION: Prepare competitor probes from the exact labeled sequence backbone; document fold excess per lane

---

### RULE DX-005
STAGE: supershift_assay
CONDITION: Antibody addition abolishes the shift but does not create a supershifted band
DIAGNOSIS: Antibody disrupts the complex or blocks the binding interface
CONFIDENCE: medium
LIKELY_CAUSES:
  - Antibody epitope overlaps the DNA-binding or RNA-binding interface
  - Antibody affinity is too low under native conditions
  - Antibody amount is too high and destabilizes the complex
DISTINGUISH:
  - Loss of signal without a slower band suggests complex disruption rather than a failed gel run
  - A second antibody targeting another epitope that does supershift supports epitope blocking by the first antibody
  - Isotype control that leaves the shift unchanged indicates the issue is antibody-specific
IMMEDIATE_FIX:
  - Reduce antibody input
  - Test an alternate antibody clone or epitope
  - Pre-incubate antibody with extract for 10 min instead of 20 min if long pre-incubation destabilizes the complex
PREVENTION: Validate antibodies for native EMSA use before relying on supershift interpretation

---

### RULE DX-006
STAGE: probe_quality
CONDITION: Free probe appears degraded, diffuse, or split into multiple lower bands
DIAGNOSIS: Probe degradation or incomplete annealing
CONFIDENCE: high
LIKELY_CAUSES:
  - Repeated freeze-thaw cycles
  - Nuclease contamination
  - Incomplete duplex annealing for dsDNA probes
DISTINGUISH:
  - Degraded free probe is visible even in probe-only lanes
  - Freshly annealed probe that restores a single sharp free band indicates annealing failure
  - RNase contamination is especially likely for RNA EMSA when the probe degrades rapidly
IMMEDIATE_FIX:
  - Prepare a fresh probe aliquot
  - Reanneal complementary strands using the programmed cooling step
  - Use nuclease-free tubes, water, and pipette tips
PREVENTION: Aliquot probes into single-run volumes; avoid more than 3 freeze-thaw cycles

---

### RULE DX-007
STAGE: extract_preparation
CONDITION: Binding is absent in all samples prepared from one extract batch, including positive controls
DIAGNOSIS: Extract preparation failed or factor activity was lost
CONFIDENCE: high
LIKELY_CAUSES:
  - Proteolysis during extraction
  - High-salt extraction buffer damaged activity
  - Factor localization or induction state was incorrect at harvest
DISTINGUISH:
  - Positive-control probe failing with the same extract implicates extract quality rather than probe sequence
  - Western blot or immunodetection of the factor in the extract can separate missing factor from inactive factor
  - A fresh batch prepared with inhibitors that restores signal confirms extract-prep failure
IMMEDIATE_FIX:
  - Prepare a fresh extract with inhibitors added immediately before use
  - Confirm harvest condition and cell stimulation state if the factor is inducible
  - Compare with a previously successful extract batch
PREVENTION: Use the same harvest timing, inhibitor set, and extraction salt conditions across all comparison groups

---

### RULE DX-008
STAGE: native_gel
CONDITION: Free probe runs poorly and shifted bands remain near the wells
DIAGNOSIS: Gel percentage or buffer system is mismatched to probe and complex size
CONFIDENCE: medium
LIKELY_CAUSES:
  - Gel percentage is too high for the complex
  - Buffer ionic strength is too high
  - Pre-run was omitted or too short
DISTINGUISH:
  - Free probe staying near the wells points to gel or buffer problems rather than binding specificity
  - Lowering gel percentage by 1-2% that restores migration confirms a matrix mismatch
  - A full pre-run that improves migration indicates ionic equilibration was a limiting factor
IMMEDIATE_FIX:
  - Reduce gel percentage
  - Pre-run for 30 min at the selected voltage
  - Test 0.25× TBE if 0.5× TBE produces excessive heat or poor resolution
PREVENTION: Match gel percentage to probe length and expected complex size before casting the gel

---

### RULE DX-009
STAGE: nonspecific_binding
CONDITION: Multiple shifted bands persist and are not reduced by mutant competitor
DIAGNOSIS: Nonspecific binding dominates the reaction
CONFIDENCE: medium
LIKELY_CAUSES:
  - Extract input is too high
  - poly(dI:dC) input is too low
  - Probe contains secondary motif content driving additional complexes
DISTINGUISH:
  - Nonspecific bands often change little with wild-type and mutant competitors alike
  - Increasing poly(dI:dC) that reduces extra bands while preserving the main shift supports nonspecific binding
  - Lower extract input that simplifies the lane pattern also supports this diagnosis
IMMEDIATE_FIX:
  - Increase poly(dI:dC) from 0.5 µg toward 1-2 µg per reaction
  - Reduce extract input
  - Test a shorter probe centered more tightly on the core motif
PREVENTION: Titrate extract and carrier competitor before interpreting complex multiplicity

---

### RULE DX-010
STAGE: transfer_detection
CONDITION: Biotin chemiluminescent EMSA shows weak membrane signal despite a visible fluorescent or radioactive gel control in prior runs
DIAGNOSIS: Transfer or chemiluminescent detection failure
CONFIDENCE: medium
LIKELY_CAUSES:
  - Transfer current, time, or buffer composition is outside the validated range
  - Crosslinking was omitted or weak
  - Streptavidin-HRP or substrate is degraded
DISTINGUISH:
  - A transferred membrane with no free probe signal suggests transfer failure
  - Strong free probe with absent shift suggests complex loss or weak binding, not transfer collapse
  - Fresh substrate that restores signal implicates reagent age rather than transfer
IMMEDIATE_FIX:
  - Repeat transfer with validated time and buffer
  - Crosslink immediately after transfer
  - Use fresh conjugate and fresh substrate
PREVENTION: Validate transfer on a positive-control probe before high-value experiments

---

### RULE DX-011
STAGE: radioactive_or_fluorescent_detection
CONDITION: Signal is strong but saturated, preventing comparison of free probe and shift intensity
DIAGNOSIS: Image acquisition settings are too aggressive
CONFIDENCE: high
LIKELY_CAUSES:
  - Exposure time is too long
  - Detector gain is too high
  - Probe input is excessive
DISTINGUISH:
  - Saturation in the free probe lane together with flat-topped band profiles indicates acquisition overload
  - Shorter exposures that restore lane detail confirm the imaging problem
  - If lower probe input also resolves saturation, sample loading contributed to the issue
IMMEDIATE_FIX:
  - Capture shorter exposures
  - Reduce gain or detector sensitivity
  - Lower probe input in repeat runs
PREVENTION: Save multiple exposure lengths for every gel; preserve at least one unsaturated raw image

---

### RULE DX-012
STAGE: reaction_setup
CONDITION: Shift intensity drops after adding detergent or reducing salt
DIAGNOSIS: Factor requires a narrower reaction window than the current optimization path
CONFIDENCE: medium
LIKELY_CAUSES:
  - Complex requires the original ionic environment
  - Detergent disrupts a weak native complex
  - Divalent cation dependence is not being met
DISTINGUISH:
  - A single-variable test that restores the shift identifies the destabilizing parameter
  - Purified protein behavior that differs from extract behavior indicates cofactor or matrix dependence
  - Mg2+ rescue of the shift points to divalent-cation dependence
IMMEDIATE_FIX:
  - Return to the last successful buffer composition
  - Reintroduce one variable at a time
  - Test MgCl2 at 0.5-2 mM if the factor is known to require divalent cations
PREVENTION: Change one binding variable at a time during optimization

---

## 5. RISK RULES

### Risk Matrix (RM-001 to RM-023) and Critical Findings (CF-001 to CF-003)

#### RISK RM-001
STAGE: probe_design
ITEM: Probe sequence lacks required flanking bases
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Motif placement and flanking sequence are documented before synthesis
MITIGATION: Use 3-6 flanking bases on each side of the core motif when initial motif-only probes bind weakly

---

#### RISK RM-002
STAGE: probe_handling
ITEM: Probe degradation from freeze-thaw cycling
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Probe aliquot count and freeze-thaw history are recorded
MITIGATION: Aliquot probes into single-run volumes and discard after 3 freeze-thaw cycles

---

#### RISK RM-003
STAGE: extract_preparation
ITEM: Proteolysis or dephosphorylation during extraction
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Inhibitors are added fresh and extraction remains on ice or at 4°C
MITIGATION: Add protease and phosphatase inhibitors immediately before extraction; minimize bench time

---

#### RISK RM-004
STAGE: extract_preparation
ITEM: Excess extraction salt damaging factor activity
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Extraction salt concentration is documented and matched to successful batches
MITIGATION: Use a validated high-salt extraction buffer and dialyze or dilute if carryover disrupts binding

---

#### RISK RM-005
STAGE: binding_reaction
ITEM: Protein overload causing nonspecific retention
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Protein titration was performed before large experiments
MITIGATION: Start at 1-2 µg extract for abundant factors and increase only if needed; use 1-10 µg range as an optimization window

---

#### RISK RM-006
STAGE: binding_reaction
ITEM: Inconsistent poly(dI:dC) input
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Carrier competitor amount is recorded for every lane group
MITIGATION: Prepare a master mix containing poly(dI:dC) for all comparable reactions

---

#### RISK RM-007
STAGE: competition_assay
ITEM: Competitor fold excess too low to challenge specific binding
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Competitor excess is calculated against labeled probe input
MITIGATION: Use 25×, 50×, and 100× excess for specificity testing

---

#### RISK RM-008
STAGE: supershift_assay
ITEM: Antibody disrupts complex instead of supershifting it
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Antibody clone and epitope are validated for native EMSA use
MITIGATION: Test alternate antibody clones and titrate antibody input from 0.5 µg to 2 µg

---

#### RISK RM-009
STAGE: native_gel
ITEM: Gel percentage too high for complex size
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Probe length and expected complex size are matched to gel percentage before casting
MITIGATION: Use 4-5% for larger complexes and 5-6% for most transcription factor DNA EMSA runs

---

#### RISK RM-010
STAGE: native_gel
ITEM: Gel overheating during electrophoresis
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Buffer temperature is monitored and apparatus cooling is used when needed
MITIGATION: Run at 4°C, lower voltage, and pre-chill running buffer

---

#### RISK RM-011
STAGE: electrophoresis
ITEM: Delayed run start after loading
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Time from last loaded lane to power-on is minimized
MITIGATION: Start electrophoresis immediately after loading the final lane

---

#### RISK RM-012
STAGE: detection
ITEM: Saturated image acquisition
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: At least one unsaturated raw image is saved
MITIGATION: Capture multiple exposures and keep detector settings below saturation

---

#### RISK RM-013
STAGE: transfer_detection
ITEM: Delayed transfer after native run
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Transfer starts immediately after electrophoresis in membrane-based workflows
MITIGATION: Prepare membrane and transfer apparatus before the run finishes

---

#### RISK RM-014
STAGE: detection_reagents
ITEM: Expired substrate or conjugate in chemiluminescent EMSA
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Reagent expiry and storage conditions are recorded
MITIGATION: Use fresh substrate and validated conjugate aliquots

---

#### RISK RM-015
STAGE: radioactive_detection
ITEM: Radioisotope handling without approved controls
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Radiation authorization, shielding, contamination monitoring, and waste routing are active
MITIGATION: Perform isotope labeling only in approved facilities under radiation SOPs

---

#### RISK RM-016
STAGE: extract_storage
ITEM: Repeated freeze-thaw of nuclear extracts
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Extract aliquot usage is tracked
MITIGATION: Use single-run aliquots and discard after 2 freeze-thaw cycles

---

#### RISK RM-017
STAGE: reaction_setup
ITEM: Unequal glycerol concentration across lanes
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Final glycerol percentage is constant in all reactions
MITIGATION: Add glycerol through a shared binding buffer master mix rather than lane-specific additions

---

#### RISK RM-018
STAGE: reaction_setup
ITEM: Divalent cation omission for cation-dependent complexes
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Factor-specific ion requirement is reviewed before optimization
MITIGATION: Test MgCl2 at 0.5-2 mM when the factor requires cation support

---

#### RISK RM-019
STAGE: competition_assay
ITEM: Mutant competitor design still retains partial motif activity
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Competitor mutations disrupt the core binding motif fully
MITIGATION: Redesign mutant competitor to alter the central contact residues rather than only flanking bases

---

#### RISK RM-020
STAGE: sample_identity
ITEM: Lane map mismatch during imaging and annotation
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Lane identity map is saved before imaging begins
MITIGATION: Keep a written loading order sheet and capture it with the raw image record

---

#### RISK RM-021
STAGE: extract_preparation
ITEM: Factor not induced or not nuclear at harvest
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Stimulation state or harvest condition is documented for inducible factors
MITIGATION: Validate nuclear localization or induction prior to extraction; harvest at the known activation timepoint

---

#### RISK RM-022
STAGE: native_gel
ITEM: Polymerization defects causing distorted lanes
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Gel wells and polymerization front are inspected before pre-run
MITIGATION: Discard gels with soft wells, visible gradients, or incomplete polymerization

---

#### RISK RM-023
STAGE: rna_emsa
ITEM: RNase contamination degrading RNA probes during setup or binding
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: RNase-free tubes, tips, water, and inhibitor usage are documented for RNA EMSA workflows
MITIGATION: Use RNase-free consumables, add RNase inhibitor to RNA binding reactions, keep RNA probes on ice during setup, and discard any RNA probe aliquot that shows a broadened free-probe band

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: specificity_control
ITEM: Binding claim made without wild-type competitor and probe-only controls
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Probe-only lane and wild-type competitor lanes are present in the same run
MITIGATION: (1) Repeat the assay with probe-only and wild-type competition controls. (2) Do not interpret a shifted band as specific binding until these controls are reviewed. (3) Add mutant competitor control when motif specificity is central to the conclusion.

---

#### RISK CF-002
STAGE: detection
ITEM: Quantitative comparison performed from saturated EMSA images
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Raw unsaturated image is available for every gel being compared
MITIGATION: (1) Reimage the gel or membrane with shorter exposure. (2) Exclude saturated images from quantitative interpretation. (3) Save multiple raw exposures for every EMSA experiment.

---

#### RISK CF-003
STAGE: extract_quality
ITEM: Negative EMSA result interpreted without positive-control extract or probe validation
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Positive-control extract or positive-control probe is included in the same optimization workflow
MITIGATION: (1) Add a positive-control extract or validated binding probe. (2) Confirm extract quality before concluding that the factor does not bind. (3) Verify factor presence by orthogonal assay when the EMSA is negative.

---

## 6. PARAMETER CONSTRAINTS

### Probe Input

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Labeled probe per reaction | 1 fmol | 5-20 fmol | 50 fmol | >50 fmol: free probe saturation and background increase |
| Probe length for motif-centered dsDNA EMSA | 12 bp | 18-30 bp | 40 bp | <12 bp: motif context may be too short; >40 bp: free probe resolution may decline |

### Protein Input

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Nuclear extract per 20 µL reaction | 0.5 µg | 1-5 µg | 10 µg | >10 µg: nonspecific binding and smearing rise sharply |
| Purified protein per 20 µL reaction | 10 ng | 25-200 ng | 1 µg | >1 µg: aggregation and lane distortion risk increase |
| poly(dI:dC) per 20 µL reaction | 0.25 µg | 0.5-1.0 µg | 2.0 µg | >2.0 µg: specific signal may be suppressed |

### Binding Reaction

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Binding reaction volume | 10 µL | 20 µL | 30 µL | >30 µL: lane loading and buffer matching become harder |
| Binding incubation at 20-25°C | 10 min | 20-30 min | 45 min | >45 min: unstable complexes and nonspecific binding can increase |
| Glycerol final concentration | 2.5% | 5% | 10% | >10%: free probe migration and lane shape may distort |

### Native Gel

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Gel acrylamide percentage | 4% | 5-6% | 8% | >8%: large complexes may stay near the wells |
| Pre-run time | 15 min | 30 min | 45 min | <15 min: ionic equilibration may be poor |
| Mini-gel voltage | 60 V | 80-120 V | 140 V | >140 V without cooling: overheating risk increases |

### Competition And Supershift

| Parameter | Value / Range | Notes |
|-----------|--------------|-------|
| Wild-type competitor excess | 25× to 100× | Use 100× when specificity remains uncertain |
| Antibody input for supershift | 0.5-2.0 µg per 20 µL reaction | Titrate downward if the complex disappears |
| Antibody pre-incubation | 10-20 min at 20-25°C | Longer exposure can destabilize some complexes |

---

## 7. QC GATES

### QC Gate 1: Before Binding Reaction

PASS criteria (ALL must be true):
  - Probe identity, label, and working concentration are documented
  - Protein concentration is measured
  - Binding buffer composition is defined
  - Required controls are planned

ACTION if FAIL: If probe concentration is unknown, requantify before use. If protein concentration is unknown, measure it before assembly. If controls are missing, revise the lane plan before assembling reactions.

---

### QC Gate 2: After Binding Reaction Assembly

PASS criteria (ALL must be true):
  - Probe and protein inputs are recorded
  - Reaction volumes are matched
  - Competition and supershift additives are documented where used
  - Reactions were incubated within the defined time window

ACTION if FAIL: If reaction inputs were not recorded, rebuild from a written worksheet before loading. If incubation time drifted widely between lanes, repeat the run with synchronized timing.

---

### QC Gate 3: After Gel Pre-Run And Loading

PASS criteria (ALL must be true):
  - Gel percentage matches expected complex size
  - Pre-run is complete
  - Lane order is documented
  - Samples were loaded without overflow or well damage

ACTION if FAIL: If wells are damaged or the gel percentage is clearly mismatched, recast the gel. If lane order is uncertain, do not proceed to interpretation.

---

### QC Gate 4: After Electrophoresis

PASS criteria (ALL must be true):
  - Free probe and shifted complexes are separated
  - Gel temperature remained controlled
  - No major smear or run distortion prevents interpretation
  - Transfer or imaging route is ready immediately after the run

ACTION if FAIL: If overheating occurred, rerun at lower voltage and 4°C. If complexes remain near the wells, lower gel percentage or revise buffer strength. If smearing dominates, revisit protein input and cooling.

---

### QC Gate 5: Before Final Interpretation

PASS criteria (ALL must be true):
  - Probe-only and protein-containing lanes are present
  - Specificity controls are present for binding claims
  - At least one unsaturated raw image is saved
  - Lane identity map is preserved

ACTION if FAIL: If controls are absent, treat the run as preliminary optimization only. If all exposures are saturated, reacquire before comparing intensities. If lane identity is uncertain, do not publish or quantify the result.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified EMSA issue and root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in the diagnosis based on controls and lane behavior |
| recommended_actions | list[string] | Ordered recovery and optimization actions |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass or fail status for each QC gate |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters linked to diagnostic rules |
| protocol_section_reference | string | Section of SOP-EMSA-001 relevant to the issue |
| specificity_status | enum: confirmed / unconfirmed / contradicted | Status of specificity control evidence |
| detection_status | enum: interpretable / saturated / weak / failed | Detection quality summary |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| western_blot_v1 | User needs factor abundance or phosphorylation validation for the same extract |
| rt_qpcr_v1 | User needs transcript-level confirmation of pathway activation tied to EMSA results |
| immunofluorescence_v1 | User needs localization of the factor before or after EMSA |
| chip_v1 | User needs chromatin occupancy validation in cells rather than in vitro binding |
| reporter_assay_v1 | User needs promoter or enhancer functional validation linked to the EMSA motif |
| protein_purification_v1 | User needs recombinant factor purification before EMSA |
| native_page_v1 | User needs native electrophoresis support outside EMSA-specific binding workflows |
