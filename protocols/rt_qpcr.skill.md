---
skill_id: rt_qpcr_v1
skill_name: RT-qPCR Complete Workflow Skill
version: 1.0
method_family: gene_expression
tags: [rt_qpcr, reverse_transcription, qpcr, sybr_green, taqman, rna_extraction, rnase_control, dnase_treatment, reference_gene_validation, delta_ct, delta_delta_ct, pfaffl, melt_curve, standard_curve, inter_run_calibration, troubleshooting]
applies_to: [cultured_cells, fresh_tissue, frozen_tissue, relative_mrna_quantification, sybr_assays, taqman_assays]
does_not_apply_to: [ffpe, single_cell_rt_qpcr, blood_pbmc_protocols, digital_pcr, absolute_quantification_with_certified_standards]
risk_level: medium
bsl_level: "BSL-1 for non-human samples and BSL-2 minimum for human-derived material; chemical fume hood required for TRIzol, chloroform, and beta-mercaptoethanol steps"
last_updated: 2026-03-16
source_protocol: SOP-RTQPCR-CODEX-001
---

---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "my qPCR is not working," "how do I extract RNA," "why is my No-RT positive," "why is my NTC amplifying," "how do I choose reference genes," "why are my Ct replicates inconsistent," "how do I do reverse transcription," "why is my melt curve messy," "how do I set up a standard curve," "why is my efficiency outside range," or any question about relative mRNA quantification by RT-qPCR from cultured cells, fresh tissue, or frozen tissue. This skill covers the complete workflow: pre-experiment planning, RNA extraction by TRIzol or column method, RNA quantification and integrity assessment, DNase treatment, reverse transcription, SYBR Green or TaqMan qPCR setup, plate loading and thermal cycling, amplification curve review, melt curve review, reference gene validation, delta Ct and delta delta Ct analysis, Pfaffl efficiency-corrected analysis, inter-run calibration, and structured diagnostic rules for the major failure modes including low RNA yield, poor purity, RNA degradation, genomic DNA carryover, RT inhibition, contamination, poor efficiency, primer-dimers, unstable reference genes, and invalid statistics. This skill does NOT cover FFPE samples, single-cell RT-qPCR, digital PCR, blood or PBMC stabilization workflows, or absolute quantification with certified external standards. Redirect those queries to the appropriate skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| sample_type | enum: cultured_cells / fresh_tissue / frozen_tissue | Biological input source for RNA extraction |
| extraction_method | enum: trizol / rneasy_column / other | RNA extraction chemistry used for the samples |
| detection_chemistry | enum: sybr_green / taqman | qPCR chemistry used for signal detection |
| instrument_platform | enum: biorad_cfx / quantstudio / lightcycler_480 / other | Real-time instrument used for optical and ROX decisions |
| target_genes | list[string] | Target genes to quantify in the experiment |
| reference_genes | list[string] | Candidate or validated reference genes used for normalization |
| workflow_goal | enum: full_rt_qpcr / extraction_only / rna_qc / reverse_transcription / qpcr_setup / analysis / troubleshooting | Primary task the user is performing |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| rna_concentration_ng_per_ul | float | RNA concentration after extraction or DNase treatment |
| a260_280 | float | NanoDrop A260/A280 purity ratio |
| a260_230 | float | NanoDrop A260/A230 purity ratio |
| rin_or_rqn | float | RNA integrity metric from Bioanalyzer or TapeStation |
| rna_input_ng_for_rt | float | Mass of RNA used per reverse transcription reaction |
| nort_ct | float or "undetermined" | No-RT control Ct value for a specific assay |
| ntc_ct | float or "undetermined" | No-template control Ct value for a specific assay |
| target_ct_values | dict {gene: [ct1, ct2, ct3]} | Technical replicate Ct values for target genes |
| reference_ct_values | dict {gene: [ct1, ct2, ct3]} | Technical replicate Ct values for reference genes |
| technical_replicate_sd | float | Standard deviation of technical replicate Ct values |
| melt_peak_count | int | Number of peaks in SYBR melt analysis |
| melt_peak_pattern | enum: single / multiple / broad / ntc_peak / no_peak | Melt-curve interpretation pattern |
| amplification_efficiency_percent | float | Efficiency calculated from standard curve or equivalent |
| standard_curve_r2 | float | R squared of the standard curve |
| reference_gene_m_value | float | geNorm M value or equivalent stability metric |
| calibrator_condition | string | Sample group used as the delta delta Ct calibrator |
| inter_run_calibrator_status | enum: present / missing / not_needed | Whether pooled cDNA calibrator wells were included |

---

## 3. WORKFLOW MODULES

### Module 1: PRE_EXPERIMENT_PLANNING_AND_CONTROL_DESIGN

**Preconditions:** Target genes, biological groups, sample type, and instrument platform are known. Primers or probes are available or in design. ROX requirements and plate format are known.
**Pause point:** YES — experiment planning, plate map, and control assignment can be completed before wet-lab work begins.

#### Steps:

1. [CRITICAL] Define the analysis scope as relative quantification only. If the study requires FFPE handling, single-cell workflows, blood stabilization, or certified absolute quantification, stop and route to another protocol.
2. Select at least 3 candidate reference genes for initial validation. Do not commit to a single reference gene before stability testing.
3. Assign mandatory controls for every primer pair:
   - 1 NTC per plate minimum; 3 NTC wells preferred.
   - 1 No-RT control per RNA sample class or per representative sample set.
   - 1 inter-run calibrator set of 3 wells per gene if data from multiple plates will be combined.
4. [DECISION POINT] Select detection chemistry:
   - SYBR Green for cost-efficient assays with melt-curve validation.
   - TaqMan for higher sequence specificity or difficult primer-dimer backgrounds.
5. Verify ROX requirement:
   - Bio-Rad CFX instruments: do not use ROX normalization.
   - QuantStudio / StepOnePlus: use master mix with passive reference compatible with the platform.
   - LightCycler 480: follow platform-specific dye normalization settings.
6. Define the calibrator condition, typically untreated control or baseline timepoint, before any data are generated.
7. Prepare the plate layout so that technical replicates are adjacent and controls are clearly separated from high-copy samples.
8. [CRITICAL] For every new primer pair, schedule a standard curve before experimental quantification begins.

#### Exit Criteria (must ALL be true to proceed):
- Sample type is within protocol scope
- Detection chemistry and instrument platform are matched
- Candidate reference genes are defined
- NTC, No-RT, and inter-run calibrator strategy is documented
- Calibrator condition is defined before data generation
- Plate layout and primer-validation plan are complete

---

### Module 2: RNA_EXTRACTION_AND_RNASE_CONTROL

**Preconditions:** Sample is available in processable form. RNase-free workspace has been prepared. Chemical fume hood is available for TRIzol, chloroform, and beta-mercaptoethanol steps. Microcentrifuge rotor is chilled if cold spins are required.
**Pause point:** YES — extracted RNA can be stored at -80°C in RNase-free water with single-use aliquots.

#### Steps:

**WORKSPACE CONTROL:**
1. Wipe bench and pipette exteriors with RNase decontamination solution, wait 1 min, then wipe with RNase-free water.
2. Prepare fresh 75% ethanol from molecular biology grade ethanol and RNase-free water.
3. Change into new nitrile gloves before touching tubes or columns.

**TRIZOL PATH:**
4. For tissue up to 30 mg, add 1,000 µL TRIzol and homogenize for 30 sec at maximum homogenizer speed until no visible fragments remain.
5. For cell pellets, add 1,000 µL TRIzol directly to a dry pellet and pipette 10 times.
6. Incubate 5 min at 20-22°C.
7. Add 200 µL chloroform per 1,000 µL TRIzol, vortex 15 sec, incubate 2-3 min at 20-22°C, then centrifuge at 12,000 × g, 4°C, 15 min.
8. Transfer approximately 600 µL aqueous phase to a new tube in small aliquots without touching the interphase.
9. Add 500 µL isopropanol, invert 10 times, incubate 10 min at 20-22°C then 30 min at -20°C, then centrifuge at 12,000 × g, 4°C, 10 min.
10. Wash pellet in 1,000 µL 75% ethanol, centrifuge at 7,500 × g, 4°C, 5 min, remove residual ethanol, air-dry 5-8 min, and resuspend in 30-50 µL RNase-free water.

**RNEASY COLUMN PATH:**
11. For cells up to 5 × 10^6, lyse in 350 µL Buffer RLT plus beta-mercaptoethanol; for tissue up to 30 mg, use 600 µL Buffer RLT plus beta-mercaptoethanol.
12. Homogenize through a QIAshredder at 16,000 × g, 20-22°C, 2 min.
13. Add the matching volume of 100% ethanol, load onto the RNeasy column, and centrifuge at 8,000 × g, 20-22°C, 15 sec.
14. Perform on-column DNase treatment with 10 µL DNase I plus 70 µL Buffer RDD for 15 min at 20-22°C.
15. Wash with RW1 and RPE according to column workflow, then perform a final dry spin at 16,000 × g, 20-22°C, 1 min with cap open.
16. Elute in 30-50 µL RNase-free water, incubate 1 min at 20-22°C, and centrifuge at 8,000 × g, 20-22°C, 1 min.

#### Exit Criteria (must ALL be true to proceed):
- RNA is in RNase-free solution
- Interphase or column carryover is not visibly present
- Pellet is not over-dried or glassy
- Extraction method is recorded
- RNA tube is transferred to a fresh labeled RNase-free vessel
- Sample is on ice or at -80°C after extraction

---

### Module 3: RNA_QUALITY_ASSESSMENT

**Preconditions:** Extracted RNA is in RNase-free water. NanoDrop and Bioanalyzer or TapeStation are available. Correct blank solution is known.
**Pause point:** YES — RNA may be returned to -80°C after QC. Recheck integrity if storage exceeds 1 week before RT.

#### Steps:

1. Blank the NanoDrop with 2 µL of the same solution used for RNA elution.
2. Measure 2 µL RNA and record concentration, A260/A280, and A260/A230.
3. [CRITICAL] Perform integrity assessment:
   - Bioanalyzer: denature 1 µL RNA at 70°C for 2 min, chill on ice 2 min, load 1 µL per chip well.
   - TapeStation: mix 2 µL RNA with 2 µL sample buffer, vortex 1 min at 2,000 rpm, heat 72°C for 3 min, chill, then load.
4. Record RIN or RQN plus the visual electropherogram pattern.
5. [DECISION POINT] Apply QC thresholds:
   - A260/A280 acceptable: 1.8-2.1.
   - A260/A230 acceptable: 1.8-2.2; minimum 1.5.
   - RIN/RQN acceptable: >=7; 5-6.9 only with explicit limitation.
6. If A260/A230 is <1.7 or contamination is suspected, perform cleanup through a MinElute or equivalent silica cleanup workflow and re-measure purity.
7. [CRITICAL] Do not proceed to RT when one comparison group contains high-integrity RNA and another contains severely degraded RNA.

#### Exit Criteria (must ALL be true to proceed):
- RNA concentration is recorded
- Purity ratios are recorded
- Integrity metric is recorded
- Sample passes minimum purity and integrity thresholds or has documented exception
- Cleanup is complete if contamination was suspected
- RNA quality decision is documented before DNase or RT

---

### Module 4: DNASE_TREATMENT_AND_GDNA_CONTROL

**Preconditions:** RNA passed QC. Solution-phase DNase treatment is required for TRIzol-extracted RNA and for any sample with suspected gDNA carryover. Turbo DNase, DNase buffer, EDTA, and heat block are ready.
**Pause point:** YES — DNase-treated RNA can be stored at -80°C for up to 1 week before RT.

#### Steps:

1. Prepare a 50 µL Turbo DNase reaction:
   - RNA sample: up to 44 µL.
   - 10× Turbo DNase buffer: 5 µL.
   - Turbo DNase I: 1 µL.
2. Incubate at 37°C for 30 min.
3. [DECISION POINT] If previous No-RT was positive or the sample is gDNA-rich tissue, use a two-step addition: 15 min at 37°C, add a fresh 1 µL DNase, then 15 min more at 37°C.
4. Add 5 µL 25 mM EDTA and incubate at 75°C for exactly 10 min to inactivate the enzyme.
5. Chill on ice for 2 min and remeasure concentration if yield tracking is required.
6. Plan or set up a No-RT control for downstream qPCR confirmation of DNA removal.

#### Exit Criteria (must ALL be true to proceed):
- DNase incubation was completed
- EDTA and 75°C heat inactivation were both used
- Two-step DNase was used when indicated by gDNA risk
- Post-DNase sample is documented
- No-RT strategy is defined for the run
- RNA is on ice or back at -80°C

---

### Module 5: REVERSE_TRANSCRIPTION_AND_CDNA_STANDARDIZATION

**Preconditions:** RNA quality and DNase status are acceptable. RT enzyme, priming strategy, dNTPs, RNase inhibitor, and thermal cycler are ready. Input RNA is quantified.
**Pause point:** YES — cDNA can be stored at -20°C for short-term use or -80°C for long-term storage after dilution.

#### Steps:

1. Standardize RNA input to 250-500 ng total RNA per 20 µL RT reaction unless the assay requires lower input.
2. [DECISION POINT] Select priming strategy:
   - Random hexamers for broad transcript coverage.
   - Oligo-dT for polyA-biased mRNA workflows.
   - Mixed priming when the assay is validated for it.
3. Prepare the RT reaction using enzyme-appropriate buffer, RNase inhibitor, dNTPs, primers, and RNA input. Keep enzyme on ice during setup.
4. Run the manufacturer-validated RT program and record temperature and time. Use the same RT conditions for all samples within one experiment.
5. Prepare matched No-RT reactions by omitting reverse transcriptase enzyme while keeping all other components constant.
6. Dilute completed cDNA to a consistent working dilution, typically 1:5 or 1:10, before qPCR setup.
7. Aliquot cDNA to avoid repeated freeze-thaw cycles.

#### Exit Criteria (must ALL be true to proceed):
- RNA input per RT reaction is standardized
- Priming strategy is documented
- RT and No-RT reactions were both prepared
- RT conditions are recorded
- cDNA is diluted to a consistent working range
- cDNA storage state is documented

---

### Module 6: QPCR_MASTER_MIX_PREPARATION_AND_PLATE_SETUP

**Preconditions:** Primers or probes are validated or in validation mode. qPCR master mix matches the instrument ROX requirement. Plate map is finalized. Optical plate and seal are instrument-compatible.
**Pause point:** NO — once the master mix is prepared and dispensed, the plate should be sealed and centrifuged without extended delay.

#### Steps:

**SYBR GREEN REACTION:**
1. Prepare a 20 µL SYBR reaction per well:
   - 2× SYBR master mix: 10 µL.
   - Forward primer: final 200 nM.
   - Reverse primer: final 200 nM.
   - cDNA: 2 µL.
   - Water: to 20 µL total volume.

**TAQMAN REACTION:**
2. Prepare a 20 µL TaqMan reaction per well:
   - 2× probe master mix: 10 µL.
   - 20× assay or validated primer-probe mix: 1 µL.
   - cDNA: 2 µL.
   - Water: to 20 µL total volume.

**MASTER MIX AND LOADING:**
3. Calculate total wells including samples, NTC, No-RT, standards, and calibrators, then add 10% overage.
4. Dispense 18 µL master mix into each well.
5. Add 2 µL cDNA to sample wells and 2 µL RNase-free water to NTC wells.
6. Seal the plate with optical film, centrifuge briefly at approximately 300 × g, 20-22°C, 1 min to remove bubbles, and inspect for liquid at the bottom of every well.

#### Exit Criteria (must ALL be true to proceed):
- Chemistry matches instrument and assay type
- Controls are included on the plate
- Master mix includes 10% overage
- Each well contains the correct final volume
- Plate is sealed and bubble-free
- Plate map matches the loaded wells

---

### Module 7: THERMAL_CYCLING_AND_RUN_REVIEW

**Preconditions:** Plate is sealed, centrifuged, and correctly oriented. Run file is configured for chemistry and instrument. Same threshold logic will be used across comparable plates.
**Pause point:** YES — after the run, raw files can be reviewed before formal analysis, but they must remain linked to the original plate identity.

#### Steps:

1. Verify run method before starting:
   - SYBR Green: include a melt curve.
   - TaqMan: no melt curve required.
2. Use a standard SYBR program unless assay-specific validation requires another program:
   - Initial denaturation: 95°C for 2-3 min.
   - 40 cycles: 95°C 10 sec, 60°C 30 sec.
   - Melt curve: 65-95°C with controlled ramp.
3. Use the validated TaqMan program for the selected master mix and instrument.
4. Do not exceed 45 amplification cycles.
5. After the run, review amplification curves before any quantitative calculations.
6. For SYBR runs, review melt curves immediately and reject wells with multiple peaks from quantification.
7. Save raw files with plate ID, date, and instrument ID before exporting any data.

#### Exit Criteria (must ALL be true to proceed):
- Correct chemistry-specific run method was used
- Cycle count did not exceed 45
- Amplification curves were reviewed before export
- Melt curves were reviewed for SYBR assays
- Raw run file was saved with traceable naming
- Plate identity is preserved through export

---

### Module 8: DATA_ANALYSIS_REFERENCE_GENE_VALIDATION_AND_REPORTING

**Preconditions:** Raw Ct data, control outcomes, and run review are complete. Reference gene candidate data are available across all groups. Analysis software and statistical plan are defined.
**Pause point:** YES — analysis can be resumed later if the same threshold logic, raw files, and metadata are preserved.

#### Steps:

1. Exclude failed wells before calculation:
   - Technical replicate SD >0.5 Ct.
   - SYBR wells with multiple melt peaks.
   - Wells with obvious curve artifacts.
2. Validate reference genes across all biological conditions using geNorm or equivalent. Require M <0.5 for robust stability and do not proceed if no acceptable reference gene exists.
3. Calculate delta Ct using validated reference normalization.
4. [DECISION POINT] Select quantification method:
   - Delta delta Ct when target and reference efficiencies are both 90-110% and closely matched.
   - Pfaffl when efficiency mismatch exceeds approximately 5-10%.
5. Apply statistics to delta Ct values, not fold-change values.
6. For multi-plate studies, normalize with the inter-run calibrator before final cross-plate comparison.
7. Export final tables, control summary, efficiency values, reference-gene validation metrics, and the analysis record.

#### Exit Criteria (must ALL be true to proceed):
- Failed wells are excluded by defined criteria
- Reference genes are validated
- Quantification method matches assay efficiency behavior
- Statistics are applied to delta Ct
- Inter-run calibration is applied when needed
- Final outputs include controls, QC metrics, and normalized results

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: extraction
CONDITION: RNA yield is low but purity ratios are near acceptable range
DIAGNOSIS: Incomplete lysis, poor homogenization, or pellet loss
CONFIDENCE: high
LIKELY_CAUSES:
  - Tissue or cells were not fully homogenized
  - Pellet was lost during wash or aspiration
  - Elution volume was too high for the sample mass
DISTINGUISH:
  - If purity is acceptable but yield is low, extraction completeness is more likely than chemical carryover
  - If the pellet was barely visible after precipitation, biomass or precipitation efficiency is more likely the driver than downstream inhibition
  - If repeated elution increases total mass recovered, column elution inefficiency is more likely than upstream lysis failure
IMMEDIATE_FIX:
  - Re-extract from remaining material with improved homogenization
  - Use glycogen for low-yield precipitation workflows
  - Reduce elution volume for column-based recovery
PREVENTION: Match lysis volume to sample size, homogenize completely, and track pellet position during every wash

---

### RULE DX-002
STAGE: extraction
CONDITION: A260/A280 is <1.8 and A260/A230 is also low
DIAGNOSIS: Phenol, protein, or interphase carryover
CONFIDENCE: high
LIKELY_CAUSES:
  - Interphase was disturbed in TRIzol extraction
  - Organic carryover entered the aqueous phase
  - Column wash was incomplete
DISTINGUISH:
  - Low A260/A280 with low A260/A230 points more strongly to extraction carryover than to RNA degradation alone
  - If No-RT is also positive, interphase carryover is more likely than isolated protein contamination
  - If cleanup improves both ratios, carryover rather than sample-intrinsic chemistry is confirmed
IMMEDIATE_FIX:
  - Perform cleanup with silica-column cleanup or re-precipitate the RNA
  - Re-extract if severe contamination persists
PREVENTION: Do not aspirate near the interphase, complete all column washes, and include the dry-spin step

---

### RULE DX-003
STAGE: rna_qc
CONDITION: RIN or RQN is <7
DIAGNOSIS: RNA degradation
CONFIDENCE: high
LIKELY_CAUSES:
  - RNase contamination
  - Delayed tissue stabilization
  - Repeat freeze-thaw cycles
DISTINGUISH:
  - Low integrity with acceptable NanoDrop ratios indicates degradation rather than solvent carryover
  - If all samples from one operator are degraded, handling error is more likely than biology
  - If degradation correlates with collection delay, pre-analytical tissue handling is more likely than extraction chemistry
IMMEDIATE_FIX:
  - Re-extract from preserved source material if available
  - Restrict interpretation to degraded-sample-compatible comparisons only when all groups are similarly degraded
PREVENTION: Use RNase control, snap-freeze tissue promptly, and store single-use RNA aliquots at -80°C

---

### RULE DX-004
STAGE: dnase
CONDITION: No-RT control is positive within 10 cycles of the sample
DIAGNOSIS: Residual genomic DNA contamination
CONFIDENCE: high
LIKELY_CAUSES:
  - DNase treatment was skipped or too short
  - High-copy genomic DNA remained in the sample
  - Primer design allows genomic DNA amplification
DISTINGUISH:
  - If No-RT is positive while NTC is clean, gDNA is more likely than reagent contamination
  - If exon-spanning primers still show No-RT positivity, DNA burden or assay design failure is more likely than post-PCR contamination
  - If a second DNase round improves the No-RT gap, residual genomic DNA is confirmed
IMMEDIATE_FIX:
  - Repeat DNase treatment with two-step enzyme addition
  - Redesign primers to span exon junctions where possible
PREVENTION: Use mandatory No-RT controls, treat TRIzol RNA with DNase, and design assays against spliced transcripts when feasible

---

### RULE DX-005
STAGE: reverse_transcription
CONDITION: Reference gene Ct is unexpectedly >35 or all assays are delayed
DIAGNOSIS: RT failure or strong inhibition
CONFIDENCE: medium
LIKELY_CAUSES:
  - RT enzyme lost activity
  - RNA input was wrong
  - Inhibitors remained in the RNA
DISTINGUISH:
  - If all targets and reference genes shift together, RT failure or inhibition is more likely than a gene-specific issue
  - If diluted cDNA performs better than neat cDNA, inhibition is more likely than complete RT failure
  - If a positive-control RNA also fails, reagent or setup failure is more likely than sample-specific inhibition
IMMEDIATE_FIX:
  - Repeat RT with fresh enzyme and freshly thawed reagents
  - Dilute cDNA 1:10 to reduce inhibitor concentration
  - Clean up RNA if purity is poor
PREVENTION: Keep enzyme on ice, standardize RNA input, and clean low-A260/A230 RNA before RT

---

### RULE DX-006
STAGE: qpcr
CONDITION: NTC amplifies within 10 cycles of the lowest sample Ct and has the same melt peak as the sample
DIAGNOSIS: Amplicon carryover contamination
CONFIDENCE: high
LIKELY_CAUSES:
  - Post-PCR product contaminated the pre-PCR area
  - Reagents or pipettes were contaminated
  - Workspace segregation failed
DISTINGUISH:
  - If NTC has the same Tm as samples, carryover contamination is more likely than primer-dimer
  - If multiple primer pairs show similar NTC behavior, workspace contamination is more likely than assay-specific chemistry
  - If fresh reagents in a clean area eliminate the signal, contamination source is confirmed
IMMEDIATE_FIX:
  - Stop the run interpretation
  - Decontaminate workspace and replace reagents
  - Rebuild the assay in a clean pre-PCR area
PREVENTION: Separate pre- and post-PCR areas, use filter tips, and never open amplicon-containing tubes near qPCR setup

---

### RULE DX-007
STAGE: qpcr
CONDITION: NTC amplifies late and has a lower Tm than the sample peak
DIAGNOSIS: Primer-dimer formation
CONFIDENCE: high
LIKELY_CAUSES:
  - Primer concentration is too high
  - Annealing temperature is too low
  - Primer design is suboptimal
DISTINGUISH:
  - Lower Tm in NTC indicates primer-dimer more strongly than amplicon carryover
  - If sample wells show a clean high-Tm peak and NTC shows only a low-Tm peak, specific amplification may still be usable after assay optimization
  - If reducing primer concentration suppresses the NTC peak, primer-dimer is confirmed
IMMEDIATE_FIX:
  - Reduce primer concentration
  - Raise annealing temperature if validated by optimization
  - Redesign the primer pair if the problem persists
PREVENTION: Validate every primer pair by melt curve and standard curve before main experiments

---

### RULE DX-008
STAGE: sybr_analysis
CONDITION: Sample wells show multiple melt peaks
DIAGNOSIS: Non-specific amplification
CONFIDENCE: high
LIKELY_CAUSES:
  - Primer design is non-specific
  - Annealing conditions are too permissive
  - Template complexity increased off-target binding
DISTINGUISH:
  - Multiple peaks in sample wells but not NTCs point more to non-specific sample amplification than primer-dimer alone
  - If gel electrophoresis shows more than one band, non-specific amplification is confirmed
  - If only a subset of samples shows the issue, template-specific off-target amplification is more likely than universal assay failure
IMMEDIATE_FIX:
  - Exclude affected wells from quantification
  - Optimize annealing conditions or redesign primers
  - Confirm product size on a gel when needed
PREVENTION: Use primer validation before production runs and reject wells with multi-peak melts from analysis

---

### RULE DX-009
STAGE: qpcr
CONDITION: Technical replicate SD is >0.5 Ct
DIAGNOSIS: Pipetting, bubble, or well-specific setup error
CONFIDENCE: high
LIKELY_CAUSES:
  - Poor mixing of master mix
  - Bubbles or sealing failure
  - Inconsistent template addition
DISTINGUISH:
  - If one outlier replicate deviates while amplification shape is otherwise normal, well handling is more likely than assay design
  - If replicate scatter affects every assay on the plate, plate sealing or loading consistency is more likely than a single primer issue
  - If centrifugation before the run resolves the issue in repeats, bubble artifact is confirmed
IMMEDIATE_FIX:
  - Exclude outlier wells only under predefined criteria
  - Re-run the affected sample set
  - Centrifuge the sealed plate before the repeat run
PREVENTION: Use calibrated pipettes, prepare master mix with overage, centrifuge the plate, and inspect wells for bubbles

---

### RULE DX-010
STAGE: analysis
CONDITION: All target genes shift in the same direction and magnitude across groups
DIAGNOSIS: Unstable reference gene normalization
CONFIDENCE: medium
LIKELY_CAUSES:
  - Reference gene is regulated by the condition
  - Only one reference gene was used
  - geNorm validation was skipped
DISTINGUISH:
  - If reference gene Ct differs by >1 cycle across groups, normalization failure is more likely than true parallel biology
  - If switching to alternate stable references changes the result pattern, the original normalization was invalid
  - If target genes from unrelated pathways all move together, reference-gene artifact is more likely than real coordinated regulation
IMMEDIATE_FIX:
  - Revalidate candidate reference genes
  - Renormalize using the geometric mean of stable references
PREVENTION: Validate at least 2 reference genes in the full biological system before the main run

---

### RULE DX-011
STAGE: efficiency_validation
CONDITION: Amplification efficiency is <90% or >110%
DIAGNOSIS: Assay efficiency is outside acceptable range
CONFIDENCE: high
LIKELY_CAUSES:
  - Primer-dimer or non-specific product
  - Poor primer design or bad annealing condition
  - gDNA contamination in the standard curve
DISTINGUISH:
  - Efficiency >120% suggests contaminating DNA or bad baseline more strongly than low primer concentration
  - Poor slope with low R squared suggests dilution or pipetting error rather than a true primer design problem alone
  - If target and reference efficiencies differ substantially, delta delta Ct is invalid even if both amplify
IMMEDIATE_FIX:
  - Re-run the standard curve with clean dilutions
  - Optimize primer concentration and annealing temperature
  - Switch to the Pfaffl method only after valid efficiency measurement is obtained
PREVENTION: Validate every new primer pair and re-check after master mix or instrument changes

---

### RULE DX-012
STAGE: multi_plate_analysis
CONDITION: Ct values shift by plate or RT batch rather than by biological group
DIAGNOSIS: Batch effect or missing inter-run calibration
CONFIDENCE: medium
LIKELY_CAUSES:
  - Inter-run calibrator was omitted
  - RT reactions were split across different days
  - Plate-specific threshold placement drifted
DISTINGUISH:
  - If calibrator wells differ by plate, cross-plate technical variance is more likely than biological change
  - If inconsistency tracks RT date rather than condition, RT batch effect is more likely than sample biology
  - If applying a common threshold reduces plate differences, analysis drift is contributing
IMMEDIATE_FIX:
  - Normalize with an inter-run calibrator where possible
  - Reanalyze with consistent threshold placement
  - Repeat RT for a unified batch if the study is decision-critical
PREVENTION: Run one experiment's RT on the same day and include pooled calibrator wells on every plate

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-020)

#### RISK RM-001
STAGE: extraction
ITEM: RNase contamination before lysis
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm bench, pipettes, and gloves were RNase-controlled before opening sample tubes
MITIGATION: Perform RNase decontamination before each extraction session, change gloves frequently, and minimize pre-lysis handling time

---

#### RISK RM-002
STAGE: extraction
ITEM: Interphase carryover during TRIzol extraction
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Review aqueous-phase transfer technique and post-extraction purity ratios
MITIGATION: Transfer aqueous phase in small aliquots, keep the tube vertical, and leave residual volume above the interphase

---

#### RISK RM-003
STAGE: extraction
ITEM: Residual ethanol after column wash or pellet wash
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Confirm the final dry spin or pellet-drying step was completed
MITIGATION: Always include a dry spin or controlled air-dry step before elution or resuspension

---

#### RISK RM-004
STAGE: extraction
ITEM: Over-dried RNA pellet becomes insoluble
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Inspect whether the pellet appeared glassy or difficult to dissolve
MITIGATION: Air-dry for 5-8 min only, never exceed 10 min, and do not use a speed-vac

---

#### RISK RM-005
STAGE: rna_qc
ITEM: Proceeding without integrity assessment
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm every experimental sample has a recorded RIN or RQN
MITIGATION: Make Bioanalyzer or TapeStation assessment mandatory before RT

---

#### RISK RM-006
STAGE: rna_qc
ITEM: Poor A260/A230 interpreted as acceptable without cleanup
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Review whether cleanup was performed when A260/A230 was <1.7
MITIGATION: Perform cleanup or functional inhibition checks before RT when A260/A230 is low

---

#### RISK RM-007
STAGE: dnase
ITEM: Genomic DNA persists after incomplete DNase treatment
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm No-RT controls and DNase conditions for every RNA batch
MITIGATION: Use two-step DNase for high-gDNA samples and require No-RT review before final interpretation

---

#### RISK RM-008
STAGE: dnase
ITEM: DNase overexposure reduces RNA integrity
PROBABILITY: low
IMPACT: medium
SCORE: MEDIUM
CHECK: Review whether incubation exceeded the validated duration
MITIGATION: Limit DNase treatment to the defined 30 min workflow and use fresh enzyme addition instead of prolonged single-step incubation

---

#### RISK RM-009
STAGE: reverse_transcription
ITEM: RNA input mass varies between samples
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Verify standardized RNA input for every RT reaction
MITIGATION: Normalize all RNA samples before RT setup and track input mass in the batch record

---

#### RISK RM-010
STAGE: reverse_transcription
ITEM: RT enzyme loses activity during setup
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Confirm enzyme handling temperature and reagent age
MITIGATION: Keep RT enzyme on ice, minimize bench time, and avoid repeated freeze-thaw cycles

---

#### RISK RM-011
STAGE: qpcr_setup
ITEM: Wrong master mix selected for instrument ROX requirement
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Match master mix passive reference requirement to the instrument before plate setup
MITIGATION: Use platform-specific master mix selection as a hard pre-run check

---

#### RISK RM-012
STAGE: qpcr_setup
ITEM: NTC or No-RT wells omitted
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Verify the plate map contains NTC and No-RT wells before loading
MITIGATION: Make NTC and No-RT controls mandatory on every relevant assay plate

---

#### RISK RM-013
STAGE: qpcr_setup
ITEM: Primer concentration not validated for a new assay
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Review whether the assay has prior efficiency and melt data
MITIGATION: Validate new assays by standard curve and primer-titration workflow before main experiments

---

#### RISK RM-014
STAGE: thermal_cycling
ITEM: SYBR run started without melt curve
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Review the method file before starting the run
MITIGATION: Require melt curve in every SYBR protocol template

---

#### RISK RM-015
STAGE: qpcr
ITEM: NTC contamination from amplicon carryover in the pre-PCR area
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Monitor NTC behavior and physical separation of pre- and post-PCR work
MITIGATION: Maintain strict area separation, use filter tips, and replace reagents immediately after contamination

---

#### RISK RM-016
STAGE: analysis
ITEM: Technical replicate variation accepted without review
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Flag any assay with replicate SD >0.5 Ct
MITIGATION: Exclude outlier wells under predefined rules and repeat affected assays when replicate spread remains high

---

#### RISK RM-017
STAGE: analysis
ITEM: Unstable reference gene used for normalization
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Verify geNorm M or equivalent stability metric before final normalization
MITIGATION: Validate at least 2 reference genes across all conditions and normalize with their geometric mean

---

#### RISK RM-018
STAGE: efficiency_validation
ITEM: Delta delta Ct used despite target-reference efficiency mismatch
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Compare target and reference efficiencies before selecting the calculation method
MITIGATION: Use Pfaffl when efficiency mismatch exceeds approximately 5-10% and revalidate assay behavior

---

#### RISK RM-019
STAGE: multi_plate_analysis
ITEM: Multi-plate data combined without inter-run calibration
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm pooled cDNA calibrator wells are present on every plate in multi-plate studies
MITIGATION: Create a pooled calibrator at the RT stage and include triplicate calibrator wells for each gene on every plate

---

#### RISK RM-020
STAGE: statistics
ITEM: Statistical testing applied to fold-change rather than delta Ct values
PROBABILITY: medium
IMPACT: medium
SCORE: HIGH
CHECK: Review the analysis script or worksheet before reporting p-values
MITIGATION: Apply statistical tests to delta Ct and report fold change as effect size only

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: analysis
ITEM: Reference gene not validated before normalization
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm at least 2 reference genes were evaluated across all experimental conditions and that stability metrics are on file
MITIGATION: (1) Validate multiple candidate reference genes before the main experiment. (2) Reject normalization based on unvalidated GAPDH or beta-actin defaults. (3) Reanalyze only after stable references are identified.

---

#### RISK CF-002
STAGE: rna_qc
ITEM: Experiment proceeds without RNA integrity measurement
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm every sample has a recorded RIN or RQN before RT
MITIGATION: (1) Make Bioanalyzer or TapeStation assessment mandatory. (2) Stop experiments lacking integrity data. (3) Document integrity values in all reports and publications.

---

#### RISK CF-003
STAGE: qpcr
ITEM: NTC contamination ignored and quantitative data still reported
PROBABILITY: low
IMPACT: high
SCORE: CRITICAL
CHECK: Review NTC Ct and melt identity before any target result is interpreted
MITIGATION: (1) Stop interpretation when NTC contamination is present. (2) Differentiate carryover contamination from primer-dimer by melt or probe behavior. (3) Rebuild the plate with fresh reagents in a decontaminated area before reporting data.

---

## 6. PARAMETER CONSTRAINTS

### RNA Quality

| Parameter | Minimum | Recommended | Maximum | Notes |
|-----------|---------|-------------|---------|-------|
| A260/A280 | 1.8 | 1.9-2.1 | 2.1 | Below range suggests protein or phenol carryover |
| A260/A230 | 1.5 | 1.8-2.2 | 2.2 | <1.7 often merits cleanup |
| RIN/RQN | 7.0 | >=8.0 | n/a | 5.0-6.9 only with explicit limitation |
| RNA concentration before RT | 10 ng/µL | assay-specific | n/a | Lower concentrations may require concentration or lower-input RT |

### DNase and RT

| Parameter | Minimum | Recommended | Maximum | Notes |
|-----------|---------|-------------|---------|-------|
| DNase incubation | 30 min at 37°C | 30 min at 37°C | 30 min single-step | Use fresh-enzyme second addition for high-gDNA samples instead of prolonged single-step incubation |
| DNase inactivation | 75°C for 10 min | 75°C for 10 min | 75°C for 10 min | Requires EDTA plus heat |
| RNA input per 20 µL RT | 50 ng | 250-500 ng | 500 ng | >500 ng increases inhibition risk in routine workflows |
| cDNA working dilution | 1:5 | 1:5 to 1:10 | 1:10 | Use consistent dilution across all samples |

### qPCR Performance

| Parameter | Minimum | Recommended | Maximum | Notes |
|-----------|---------|-------------|---------|-------|
| Technical replicate SD | n/a | <=0.25 Ct | 0.5 Ct | >0.5 Ct requires review or repeat |
| Amplification efficiency | 90% | 95-105% | 110% | Outside range requires optimization |
| Standard curve R squared | 0.98 | >=0.99 | 1.00 | Lower values suggest dilution or assay issues |
| Cycle number | 40 | 40 | 45 | >45 invalidates routine control interpretation |
| Reference gene stability M | n/a | <0.5 | 1.0 | >1.0 is unacceptable |

---

## 7. QC GATES

### QC Gate 1: RNA Quality

PASS criteria (ALL must be true):
  - A260/A280 is >=1.8
  - A260/A230 is >=1.5 and preferably >=1.8
  - RIN or RQN is >=7 or an exception is documented
  - RNA concentration is adequate for planned RT input

ACTION if FAIL: Clean up contaminated RNA, re-extract degraded samples if source material remains, and stop if integrity is severely compromised.

---

### QC Gate 2: Genomic DNA Control

PASS criteria (ALL must be true):
  - DNase treatment was completed when required
  - No-RT control is undetermined or at least 10 cycles later than the sample
  - Primer design does not obviously favor gDNA amplification

ACTION if FAIL: Repeat DNase treatment, redesign primers if necessary, and do not quantify gDNA-compromised assays.

---

### QC Gate 3: qPCR Control Performance

PASS criteria (ALL must be true):
  - NTC is undetermined or at least 10 cycles later than the lowest sample Ct
  - SYBR assays show acceptable melt behavior
  - Technical replicates are within allowed spread
  - Plate map and control placement match the loaded plate

ACTION if FAIL: Differentiate contamination from primer-dimer, repeat affected assays, and reject failed wells from quantification.

---

### QC Gate 4: Assay Efficiency

PASS criteria (ALL must be true):
  - Amplification efficiency is 90-110%
  - Standard curve R squared is acceptable
  - Target and reference efficiencies are close enough for the selected analysis method

ACTION if FAIL: Optimize assay conditions, repeat standard curves, and switch to efficiency-corrected analysis only after valid efficiency measurement.

---

### QC Gate 5: Analysis Validity

PASS criteria (ALL must be true):
  - Reference genes are validated
  - Delta Ct, not fold change, is used for statistics
  - Inter-run calibration is applied when plates are combined
  - Final report includes controls, efficiencies, and QC outcomes

ACTION if FAIL: Revalidate references, correct the statistical workflow, and withhold final interpretation until the analysis is repaired.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified RT-qPCR problem and root cause, or "QC PASS — proceed" |
| confidence | enum: high / medium / low | Confidence in diagnosis based on controls and QC status |
| recommended_actions | list[string] | Ordered action list with immediate corrective step first |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Status of the 5 RT-qPCR QC gates |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range measurements linked to diagnostic rules |
| protocol_section_reference | string | Section of SOP-RTQPCR-CODEX-001 relevant to the issue |
| control_status | enum: valid / ntc_failed / nort_failed / melt_failed / replicate_failed | Summary of control performance |
| normalization_status | enum: valid / reference_unstable / efficiency_mismatch / batch_effect_risk | Summary of normalization and analysis validity |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | User needs upstream cell maintenance or treatment before RNA harvest |
| flow_cytometry_v1 | User needs protein-level or population-level validation of transcriptional changes |
| western_blot_v1 | User needs protein-level confirmation of gene-expression changes |
| rna_extraction_v1 | User wants a standalone extraction-focused workflow without full qPCR analysis |
| primer_design_v1 | User needs primer or probe design and assay validation before qPCR |
| rnaseq_v1 | User needs transcriptome-wide profiling rather than targeted RT-qPCR |
| digital_pcr_v1 | User needs absolute nucleic acid quantification rather than relative qPCR |
