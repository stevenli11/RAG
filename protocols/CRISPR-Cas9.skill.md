---
skill_id: crispr_cas9_v1
skill_name: CRISPR-Cas9 Genome Editing Complete Workflow Skill
version: 1.0
method_family: genome_editing
tags: [crispr, crispr_cas9, genome_editing, sgrna, guide_rna, ribonucleoprotein, plasmid_editing, hdr, nhej, knockout, knockin, indel_analysis, amplicon_sequencing, single_cell_clone, editing_qc]
applies_to: [mammalian_cells, adherent_cells, suspension_cells, primary_cells, immortalized_cell_lines, plasmid_delivery, rnp_delivery, knockout_workflows, knockin_workflows, clonal_isolation]
does_not_apply_to: [cas12_workflows, base_editing_only, prime_editing_only, embryo_microinjection, plant_transformation, bacterial_genome_engineering, viral_packaging_only, pooled_library_screens]
risk_level: high
bsl_level: "BSL-2 for human-derived material unless institutional assessment permits lower containment"
last_updated: 2026-04-21
source_protocol: SOP-CRISPR-CAS9-001
---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I design a CRISPR-Cas9 knockout," "why is my editing efficiency low," "how do I deliver Cas9 RNP," "how do I design an HDR donor," "why do I get no clones," "how do I genotype edited cells," "how do I enrich edited cells," "why are my cells dying after nucleofection," "how do I set up a single-cell clone workflow," "how do I confirm a frameshift knockout," "how do I reduce off-target editing," or any question about CRISPR-Cas9 workflow design, execution, QC, and troubleshooting in mammalian cell systems. This skill covers the complete CRISPR-Cas9 workflow: experimental objective definition, sgRNA and donor design, reagent QC, RNP or plasmid preparation, cell preparation, lipid delivery or electroporation, post-edit recovery, bulk-population screening, clonal isolation, and structured diagnostic rules for low editing, high toxicity, failed HDR, mixed genotypes, and misleading genotyping outcomes. Support for pooled guide-screen work is limited to single-guide validation steps before library-scale workflows. This skill does NOT cover: Cas12 workflows, base editors, prime editors, embryo microinjection, plant transformation, bacterial engineering, viral packaging workflows as the primary topic, or pooled CRISPR library screens with library design, selection modeling, and deep-sequencing analysis. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| editing_goal | enum: knockout / precise_knockin / tag_insertion / deletion / pool_enrichment / troubleshooting | Primary experimental objective |
| target_gene | string | Gene symbol or locus name targeted for editing |
| cell_type | enum: adherent / suspension / primary | Growth modality of the target cell population |
| delivery_mode | enum: cas9_rnp_electroporation / cas9_rnp_lipid / plasmid_transfection / dual_vector_delivery | Editing reagent delivery route |
| edit_readout | enum: indel_assay / amplicon_sequencing / restriction_digest / flow_cytometry / immunoblot / clone_genotyping | Planned primary validation method |
| harvest_plan | string | Planned bulk or clone harvest window after delivery |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| guide_sequence | string | 20 nt protospacer sequence excluding PAM |
| pam_sequence | string | PAM used by the Cas9 enzyme |
| target_exon | string | Exon number or targeted genomic interval |
| on_target_score | float | Guide ranking score from the selected design tool |
| predicted_off_targets | int | Number of high-priority off-target loci carried into review |
| donor_type | enum: none / ssodn / dsdna_plasmid / pcr_donor | Repair template format |
| donor_homology_arm_length_bp | int | Homology arm length for knockin workflows |
| cas9_format | enum: protein / plasmid / mrna | Cas9 cargo format |
| guide_format | enum: synthetic_sgRNA / crRNA_tracrRNA / plasmid_sgRNA | Guide RNA format |
| cas9_amount_ug | float | Cas9 protein or plasmid mass per reaction |
| guide_amount_ug_or_pmol | string | Guide RNA amount per reaction |
| donor_amount_ug_or_pmol | string | Donor amount per reaction |
| complex_incubation | string | RNP assembly time and temperature |
| electroporation_program | string | Pulse code or custom program used |
| cell_count_per_reaction | float | Cell count per editing reaction |
| viability_percent_24h | float | Viability 24 h after delivery |
| bulk_editing_percent | float | Editing frequency from the first bulk assay |
| hdr_percent | float | Precise repair frequency from sequence or reporter readout |
| clone_expansion_success_percent | float | Fraction of isolated clones that expanded |
| pcr_amplicon_size_bp | int | Size of the genotyping amplicon |
| selection_marker_used | enum: none / puromycin / blasticidin / fluorescence_sort / surface_marker | Enrichment route used after delivery |

---

## 3. WORKFLOW MODULES

### Module 1: EXPERIMENTAL_OBJECTIVE_AND_LOCUS_STRATEGY

**Preconditions:** The biological question, target gene, and required edit class are defined. A current gene model and transcript structure are available for the target locus.
**Pause point:** YES - design review can pause before ordering reagents. Do not proceed to reagent purchase until the edit class, target exon, and validation readout are aligned.

#### Steps:

1. Define the required edit outcome:
   - Knockout: target an early constitutive exon shared by the transcript isoforms that matter for the phenotype.
   - Tag insertion: place the cut site within 10 bp of the intended insertion junction when possible.
   - Small precise edit: place the cut site within 5-15 bp of the variant position to support HDR.
2. Review transcript structure:
   - Confirm which exons are constitutive versus isoform-specific.
   - Avoid exons skipped in the cell model used for the experiment.
3. Define the evidence plan before editing:
   - Bulk indel assay at 48-96 h for first-pass screening.
   - Amplicon sequencing for final edit-frequency confirmation.
   - Protein or flow-based confirmation when the edit is expected to change abundance or surface expression.
4. For knockout workflows:
   - Prefer exons upstream of catalytic domains or upstream of the last 30% of the coding sequence.
   - Avoid the final exon when nonsense-mediated decay evidence is central to the interpretation.
5. For knockin workflows:
   - Confirm insertion frame, linker sequence, and recoding plan if the donor overlaps the guide site.
   - Plan a PAM-disrupting silent mutation or protospacer-disrupting recoding within the donor.
6. Define the comparison groups:
   - Untreated cells.
   - Delivery-only control if the workflow includes toxicity-sensitive delivery.
   - Non-targeting guide control when phenotypic interpretation needs matched delivery background.
7. [CRITICAL] Write the success metric before the run starts:
   - Knockout bulk screen: target indel frequency at or above 40%.
   - Single-cell clone campaign: at least 24 clones carried into genotyping for a moderate-difficulty knockout, or 48 clones for a precise knockin.
8. [BEGINNER TRAP] Do not treat a DNA-level edit alone as a complete success when the project requires protein loss, isoform loss, or a precise junction.

#### Exit Criteria (must ALL be true to proceed):
- Editing goal is explicitly defined
- Target exon or locus interval is selected
- Validation readout is linked to the biological question
- Control groups and success metrics are documented

---

### Module 2: SGRNA_AND_DONOR_DESIGN

**Preconditions:** The locus strategy from Module 1 is complete. Reference sequence, PAM requirements, and genome build are fixed for the project.
**Pause point:** YES - oligo ordering and donor synthesis can pause after design approval. Do not mix genome builds or transcript versions once guide ordering starts.

#### Steps:

1. Design 3-6 candidate sgRNAs per target locus.
2. For SpCas9 editing:
   - Use 20 nt protospacer sequences followed by NGG PAM.
   - Favor guides with predicted on-target score at or above 50 if the design platform uses a 0-100 scale.
3. Prioritize cut-site placement:
   - Knockout indels: place the cut within the first 50% of the coding sequence and inside a constitutive exon.
   - HDR point edit: keep the cut within 10 bp of the edit whenever possible.
   - Short tag insertion: keep the cut within 5 bp of the junction whenever possible.
4. Review off-target burden:
   - Exclude guides with predicted off-target sites containing 0-1 mismatches elsewhere in coding exons.
   - Flag guides with multiple 2-mismatch sites in expressed loci for secondary review.
5. For dual-guide deletions:
   - Place the two cuts 50 bp to 500 bp apart for routine PCR-resolvable deletions.
   - Keep both guides in regions with unique primer design space outside the deletion interval.
6. For ssODN donors:
   - Use 60-90 bp homology arms on each side for small edits and short tags that fit ssODN length constraints.
   - Include PAM-disrupting or guide-disrupting silent changes when the donor sequence preserves coding potential.
7. For plasmid or PCR donors:
   - Use 300-800 bp homology arms per side for many mammalian knockin workflows.
   - Sequence-verify the full donor junction region before use.
8. For coding-region donors:
   - Recode the donor region overlapping the guide so the repaired allele is not re-cut.
   - Preserve amino acid sequence unless the project requires a functional substitution.
9. [CRITICAL] Freeze the final guide list and donor sequence in a written design sheet that includes genome build, transcript ID, cut position, primer plan, and expected edited amplicon size.
10. [DO NOT] Use a donor that restores the intact PAM and protospacer unless the workflow also includes a blocking mutation plan.

#### Exit Criteria (must ALL be true to proceed):
- Candidate guides and final selected guides are documented
- Off-target review is completed
- Donor sequence and blocking-mutation plan are defined when HDR is used
- Genotyping primer plan is drafted

---

### Module 3: REAGENT_PREPARATION_AND_QC

**Preconditions:** Guides, Cas9, donor templates, primers, and delivery consumables are on hand. Storage history and lot information are available for each critical reagent.
**Pause point:** YES - aliquoted reagents can remain at -20°C or -80°C according to vendor storage instructions. Avoid more than 3 freeze-thaw cycles for guide RNA and more than 5 freeze-thaw cycles for Cas9 protein unless the vendor states a tighter limit.

#### Steps:

1. Confirm sgRNA or crRNA:tracrRNA identity and concentration:
   - Synthetic sgRNA working stocks: 20-100 µM.
   - crRNA and tracrRNA working stocks: 20-100 µM each.
   - For crRNA:tracrRNA workflows, record whether the material is stored as separate RNAs or as a pre-annealed duplex aliquot.
   - Pre-annealed duplex aliquots can be stored at -80°C; keep duplex freeze-thaw count at 3 cycles or fewer.
2. For RNA guide handling:
   - Use RNase-free tubes and barrier tips.
   - Keep working aliquots on ice during setup and return unused material to -80°C within 30 min.
3. Confirm Cas9 format:
   - Cas9 protein: maintain on ice during setup.
   - Cas9 plasmid: confirm concentration and plasmid-DNA A260/A280 at or above 1.8.
   - Cas9 mRNA: use RNase-free handling, keep on ice, and confirm mRNA A260/A280 at or above 2.0 if spectrophotometric purity data are used.
4. For donor templates:
   - ssODN working stocks: 50-200 µM.
   - Plasmid donors: verify sequence across both junctions and the full insert.
   - PCR donors: confirm the single expected band on agarose gel and purify before use.
5. Prepare genotyping primers:
   - Design primers 150-300 bp outside the expected cut or insertion region when possible.
   - Target 300-800 bp amplicons for routine Sanger-based indel review.
6. Prepare selection reagents if used:
   - Puromycin kill-curve starting range: 0.5-5 µg/mL; define the final working concentration by a kill curve in the exact cell line before use.
   - Blasticidin kill-curve starting range: 2-10 µg/mL; define the final working concentration by a kill curve in the exact cell line before use.
   - These ranges are starting points only; every cell line requires its own kill curve before selection begins.
7. [CRITICAL] Record reagent lot, concentration, freeze-thaw count, and working aliquot date for Cas9, guides, and donors in the same run sheet.
8. [BEGINNER TRAP] Do not assume an archived donor plasmid still matches the current guide plan. Reconfirm the donor sequence around the cut-site overlap before the run.

#### Exit Criteria (must ALL be true to proceed):
- Guide, Cas9, and donor identity are confirmed
- Concentrations and freeze-thaw counts are recorded
- Genotyping primers are available
- Selection reagent plan is defined when enrichment will be used

---

### Module 4: RNP_ASSEMBLY_OR_PLASMID_SETUP

**Preconditions:** Reagent QC is complete. The final guide, Cas9, and donor combinations are selected. Cell count targets and delivery vessel map are prepared.
**Pause point:** YES - assembled RNP can rest on ice for 15-30 min before delivery if the supplier SOP permits that hold window. Do not hold assembled RNP at 20-25°C longer than 30 min before electroporation or lipid addition.

#### Steps:

1. For synthetic sgRNA plus Cas9 protein RNP:
   - Combine sgRNA and Cas9 at a molar ratio of 1.2:1 to 2:1 sgRNA:Cas9.
   - Calculate molar input from the actual sgRNA and Cas9 working-stock concentrations, then add nuclease-free water or supplier-recommended buffer to reach the target reaction volume.
   - Incubate the sgRNA-Cas9 mixture at 20-25°C for 10-20 min to allow full RNP formation before proceeding.
2. For crRNA:tracrRNA workflows:
   - Anneal crRNA and tracrRNA 1:1 at 95°C for 5 min, remove the tube from the heat block, and allow it to cool naturally to 20-25°C for at least 5 min before Cas9 addition. Do not place the annealed duplex on ice before Cas9 addition.
   - Add Cas9 after duplex formation and incubate at 20-25°C for 10-20 min.
3. For plasmid editing workflows:
   - Example 24-well plasmid setup: 0.5-1.5 µg Cas9-sgRNA plasmid in 50 µL serum-free medium.
   - If cotransfecting donor plasmid, keep total DNA mass constant across comparison groups by balancing with carrier plasmid.
4. For RNP plus ssODN donor:
   - Add donor after RNP assembly.
   - Example electroporation reaction: RNP in 20 µL + ssODN donor 0.5-1 µL from a 100 µM stock.
5. For RNP plus plasmid donor:
   - Keep donor plasmid physically separate from RNP assembly until the final reaction mix is prepared.
   - Avoid prolonged RNP incubation with high DNA mass before delivery.
6. Label every reaction with guide ID, donor ID, Cas9 batch, and cell destination.
7. [CRITICAL] Use a shared master mix for replicate reactions whenever the design is identical across replicates.
8. [DO NOT] Assemble multiple guide conditions in unlabeled tubes. Guide-swap errors are common when several targets are prepared in one session.

#### Exit Criteria (must ALL be true to proceed):
- RNP or plasmid reaction composition is recorded
- Assembly time and temperature are recorded
- Donor addition order is recorded when donors are used
- Tube labels and destination map are complete

---

### Module 5: CELL_PREPARATION_AND_DELIVERY

**Preconditions:** Cells are healthy, authenticated, and free of mycoplasma. Delivery instrument or lipid reagent is ready. Recovery medium is pre-warmed.
**Pause point:** NO for electroporation after cells enter electroporation buffer. YES for plasmid or RNP lipid delivery after cells are plated and before complexes are added.

#### Steps:

1. Confirm cell health before editing:
   - Adherent cultures should be 60-80% confluent on the day of lipid delivery.
   - Electroporation workflows should start with viability at or above 90%.
2. Prepare cell numbers:
   - 24-well lipid delivery: 5 × 10^4 to 1.5 × 10^5 cells in 500 µL per well.
   - 6-well lipid delivery: 2 × 10^5 to 5 × 10^5 cells in 2 mL per well.
   - Electroporation: 1 × 10^5 to 2 × 10^6 cells per reaction, matched to the kit format.
3. For adherent-cell harvest before electroporation:
   - Wash once with PBS.
   - Detach cells with the pre-tested dissociation reagent recorded in the run plan, such as 0.25% trypsin or Accutase.
   - Quench into complete medium and centrifuge at 300 ×g, 20-25°C, 5 min.
4. Wash cells for electroporation if the kit requires low-serum or serum-free input:
   - Resuspend in PBS or kit buffer.
   - Centrifuge at 300 ×g, 20-25°C, 5 min.
   - Resuspend in electroporation buffer at the kit-defined density.
5. Electroporation workflow:
   - Combine cells with editing mix immediately before transfer to the cuvette or strip.
   - Avoid visible bubbles.
   - Pulse with the selected program and transfer to pre-warmed medium within 5 min.
6. Lipid delivery workflow:
   - Add complexes into antibiotic-free medium.
   - Example 24-well addition: 50-100 µL complexes into 500 µL medium.
   - Example 6-well addition: 200-250 µL complexes into 2 mL medium.
   - For Cas9 RNP lipid delivery, pre-plate cells to the target density, assemble RNP first, then mix the RNP with the lipid reagent in serum-free medium using the supplier-specified ratio and incubate at 20-25°C for 10-15 min before addition to cells.
   - For plasmid lipid delivery, optimize DNA mass and lipid input separately from RNP-lipid conditions because plasmid and RNP complexes do not use the same complexing behavior.
7. For sensitive primary cells after electroporation:
   - If the supplier kit includes a dedicated recovery medium, allow recovery at 37°C for 10-15 min in the cuvette or strip before transfer.
   - Then transfer to the pre-warmed culture vessel.
8. [CRITICAL] Keep total cell number, final reaction volume, and delivery timing consistent across directly compared conditions.
9. [BEGINNER TRAP] Do not use antibiotics during the first 16-24 h after lipid delivery unless the exact cell line and reagent combination has validated survival data.

#### Exit Criteria (must ALL be true to proceed):
- Cell health and density match the chosen delivery method
- Delivery settings or complex volumes are documented
- Recovery medium is ready before delivery starts
- Compared conditions use matched cell numbers and final volumes

---

### Module 6: POST_EDIT_RECOVERY_AND_ENRICHMENT

**Preconditions:** Delivery is complete. Cells have been returned to the incubator or recovery vessel. The enrichment plan is defined.
**Pause point:** YES - recovery and bulk screening windows span 24-120 h, with the exact window defined by the selected assay. Do not start drug selection before confirming that the recovery interval matches the delivery method and cell class.

#### Steps:

1. Immediate recovery:
   - Return cells to 37°C, 5% CO₂ immediately after delivery.
   - Avoid medium exchange during the first 6 h after electroporation unless the supplier SOP specifies a different recovery step and timing.
2. For lipid-delivered editing reagents:
   - Replace medium at 4-6 h for toxicity-prone lines.
   - Replace medium at 12-24 h for fast-growing, lipid-tolerant immortalized cell lines such as HEK293T or HeLa when viability remains at or above 90%.
3. First assessment window:
   - Viability at 16-24 h.
   - Editing screen at 48-96 h for bulk indel analysis.
   - HDR screen at 72-120 h when the readout requires repaired allele accumulation.
4. If enrichment is used:
   - Puromycin selection commonly begins 24-48 h after plasmid delivery.
   - Fluorescence-based sorting commonly begins 24-72 h after reporter expression appears.
5. For selection setup:
   - Use the kill-curve-defined concentration.
   - Refresh drug-containing medium every 48-72 h until non-transfected control wells fall below 10% survival by microscopy or viability stain.
6. Document morphology and recovery:
   - Record attachment, clumping, debris load, and growth rate at 24 h and 48 h.
7. [CRITICAL] Separate delivery toxicity from editing failure by comparing untreated, delivery-only, and targeting conditions in the same run.
8. [DO NOT] Freeze the bulk population for long-term banking before the first edit-frequency screen unless a backup frozen aliquot is collected after the screen window is already secured.

#### Exit Criteria (must ALL be true to proceed):
- Recovery timing is documented
- Viability assessment window is defined
- Selection or enrichment plan is documented when used
- Bulk screening harvest time is scheduled

---

### Module 7: BULK_EDITING_ANALYSIS_AND_CLONAL_ISOLATION

**Preconditions:** Cells have recovered long enough for the chosen assay. Primers, extraction reagents, and clone-isolation supplies are ready.
**Pause point:** YES - bulk DNA can be stored at 4°C for 24 h before PCR or at -20°C for longer storage. Single-cell clone plates can pause during expansion, with media exchange every 48-72 h.

#### Steps:

1. Harvest bulk cells for DNA extraction:
   - 24-well plate DNA harvest: aspirate medium, wash with PBS, and lyse or pellet according to the extraction kit.
   - If pelleting suspension cells, centrifuge at 500 ×g, 20-25°C, 5 min before lysis; this higher g-force helps pellet spherical suspension cells more reliably than the 300 ×g spin used for pre-electroporation handling of harvested adherent cells in Module 5.
2. Amplify the target region:
   - Use primers positioned outside the expected cut or donor-integration junction.
   - Keep routine amplicons in the 300-800 bp window when the workflow uses Sanger deconvolution.
3. First-pass bulk analysis options:
   - Sanger deconvolution for indel frequency.
   - Restriction digest when the edit creates or removes a site.
   - Amplicon sequencing for final percentage and allele-spectrum analysis.
   - Sanger deconvolution acceptance threshold: ICE R² at or above 0.95 before relying on the estimated edit percentage.
   - TIDE acceptance threshold: p below 0.05; if decomposition error exceeds 5%, repeat the sequencing run or move to amplicon sequencing.
4. For protein-linked knockout confirmation:
   - Harvest protein at 72-120 h or later if the target has a long half-life.
5. For clone isolation:
   - Single-cell sort into 96-well plates or perform limiting dilution at 0.5 cell per 100 µL.
   - Use 150-200 µL medium per 96-well clone well.
6. Clone expansion:
   - Score wells for single-colony origin.
   - Split expanding clones into replicate plates for cryobanking and genotyping.
7. For knockin clones:
   - Run both 5' junction and 3' junction PCR.
   - Include a wild-type spanning amplicon to detect mixed or random-integration backgrounds.
8. [CRITICAL] Keep bulk-population interpretation separate from clone-level interpretation. A bulk edit rate of 60% does not predict the zygosity distribution of expanded clones.
9. [BEGINNER TRAP] Do not call a clone homozygous from one small PCR band alone when a large deletion, allele dropout, or donor concatemer can hide the second allele.

#### Exit Criteria (must ALL be true to proceed):
- Bulk edit assay is completed or scheduled
- Clone isolation route is documented when clone work is planned
- Genotyping strategy includes junction or wild-type controls when needed
- Sample identity map is preserved from harvest through analysis

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: design
CONDITION: Bulk editing frequency is below 10% across multiple repeats while cell viability remains at or above 85%
DIAGNOSIS: Guide selection or cut-site placement is weak for the chosen locus
CONFIDENCE: high
LIKELY_CAUSES:
  - The guide sequence has low intrinsic activity
  - The cut site is too far from the required edit position
  - Target chromatin access is poor in the chosen cell line
DISTINGUISH:
  - High viability with low editing points to guide performance more strongly than delivery toxicity
  - A second guide at the same locus that edits efficiently indicates that delivery and cell health were not the limiting factors
  - A guide that cuts well in one cell line but not another supports a chromatin-access explanation
IMMEDIATE_FIX:
  - Test 2-3 alternate guides targeting the same exon or junction
  - Move the guide closer to the intended HDR edit if precise repair is the goal
  - Confirm target expression and locus accessibility data for the chosen cell line
PREVENTION: Design and rank 3-6 candidate guides per locus before starting the first delivery run

---

### RULE DX-002
STAGE: delivery
CONDITION: Viability at 24 h falls below 50% after Cas9 delivery
DIAGNOSIS: Delivery conditions are too harsh for the cell class
CONFIDENCE: high
LIKELY_CAUSES:
  - Electroporation pulse energy is too high
  - Lipid or polymer reagent dose is too high
  - Cell density or buffer hold time before delivery is outside the tolerated window
DISTINGUISH:
  - A delivery-only control with matching death confirms that toxicity is delivery-driven rather than edit-driven
  - Immediate post-pulse cell rupture or debris points to electroporation stress rather than guide design
  - Strong toxicity after high reagent volume in lipid delivery, with low death in untreated controls, supports reagent overload
IMMEDIATE_FIX:
  - Move to the next lower-energy electroporation program or lower reagent volume
  - Reduce time in electroporation buffer to less than 15 min
  - Lower total DNA, Cas9, or RNP mass per reaction
PREVENTION: Run a delivery-only optimization matrix in the target cell type before the first full editing campaign

---

### RULE DX-003
STAGE: hdr
CONDITION: Indel formation is detectable but precise knockin or sequence replacement remains below 2%
DIAGNOSIS: HDR donor design or donor delivery is limiting repair outcome
CONFIDENCE: high
LIKELY_CAUSES:
  - The cut site is too far from the desired edit
  - The donor lacks a PAM-blocking or guide-blocking change
  - Donor amount or donor format is poorly matched to the cell type
DISTINGUISH:
  - Detectable indels with near-zero HDR indicate that Cas9 cutting occurred but precise repair did not
  - Re-cutting signatures in sequencing near the repaired allele support a missing blocking-mutation problem
  - A donor redesign that restores HDR without changing electroporation settings points to donor architecture rather than delivery
IMMEDIATE_FIX:
  - Redesign the donor to place the edit within 10 bp of the cut
  - Add PAM-disrupting or protospacer-disrupting silent recoding
  - Compare ssODN versus plasmid donor if the current donor format is underperforming
PREVENTION: For precise edits, lock donor architecture and blocking mutations at the design-review stage before reagent ordering

---

### RULE DX-004
STAGE: genotyping
CONDITION: A clone appears wild type by one PCR assay, but protein loss or phenotype suggests editing occurred
DIAGNOSIS: PCR design misses a large deletion, insertion, or allele dropout event
CONFIDENCE: medium
LIKELY_CAUSES:
  - Primer-binding sites were lost
  - One allele amplified preferentially
  - A large rearrangement falls outside the first assay window
DISTINGUISH:
  - Discordance between protein loss and a wild-type PCR band points to genotyping incompleteness rather than a true wild-type state
  - A second primer set outside the first amplicon that changes the call supports allele dropout or structural change
  - Junction-specific PCR that detects an edited allele confirms the first assay was under-informative
IMMEDIATE_FIX:
  - Redesign primers 150-300 bp farther from the cut site
  - Add a long-range PCR or junction PCR panel
  - Sequence independent amplicons from the same clone
PREVENTION: Use at least two primer strategies for clone calling when the workflow includes large indels, dual guides, or donor insertion

---

### RULE DX-005
STAGE: clone_isolation
CONDITION: Very few single-cell clones survive expansion after sorting or limiting dilution
DIAGNOSIS: Clone isolation density or recovery support is too weak
CONFIDENCE: medium
LIKELY_CAUSES:
  - Single-cell wells lack conditioned medium or survival support
  - Sorting stress is too high
  - Cells were isolated too soon after harsh delivery
DISTINGUISH:
  - Bulk culture recovery with poor clone outgrowth points to the isolation stage rather than the edit stage
  - Better survival in conditioned medium or feeder-supported wells confirms a recovery-support limitation
  - Poor expansion from both edited and control sorted cells indicates sorting or single-cell culture stress
IMMEDIATE_FIX:
  - Delay single-cell isolation until bulk cells show stable growth
  - Use 50-75% conditioned medium collected from healthy log-phase cultures of the same cell line, filter it through a 0.22 µm membrane, and apply it during the first 4-7 d after sorting; if the cell line does not tolerate that fraction, reduce the conditioned-medium fraction to 25-50% or use a commercial single-cell survival supplement
  - Lower sorter pressure or use a wider nozzle when cell size permits
PREVENTION: Pilot a clone-survival workflow with untreated cells before committing a high-value editing campaign to clone isolation

---

### RULE DX-006
STAGE: off_target_risk
CONDITION: Edited clones show unexpected growth, morphology, or pathway phenotypes that do not track with the intended genotype class
DIAGNOSIS: Off-target editing or clone-selection bias may be confounding interpretation
CONFIDENCE: medium
LIKELY_CAUSES:
  - The guide has high-priority off-target sites
  - Only one edited clone was carried forward
  - Single-cell bottleneck selected a rare background variant
DISTINGUISH:
  - Phenotypes reproduced across multiple independent guides support on-target biology more strongly than one clone from one guide
  - Divergent phenotypes among clones with the same intended edit point to clone-specific background effects
  - Rescue by cDNA re-expression supports on-target causality
IMMEDIATE_FIX:
  - Carry at least 2 independent guides or multiple independent clones into phenotyping
  - Sequence top predicted off-target loci in lead clones
  - Add complementation or rescue experiments
PREVENTION: Use more than one guide and more than one independent edited clone when the project advances to mechanism claims

---

### RULE DX-007
STAGE: reagent_handling
CONDITION: Editing performance drops sharply with a new guide or Cas9 batch after previously successful runs
DIAGNOSIS: Reagent identity, degradation, or setup error is likely
CONFIDENCE: medium
LIKELY_CAUSES:
  - Guide RNA degraded during handling
  - Cas9 protein lost activity from storage abuse
  - The wrong guide was assembled into the reaction
DISTINGUISH:
  - A positive-control guide that also fails implicates Cas9 or delivery rather than one new guide
  - A single failed target with an otherwise successful positive control points to guide identity or guide quality
  - Repeating the setup from fresh aliquots that restores editing confirms a reagent-preparation problem
IMMEDIATE_FIX:
  - Rebuild the reaction from fresh aliquots
  - Verify guide IDs and tube labels against the run sheet
  - Test a positive-control editing target in parallel
PREVENTION: Aliquot guides and Cas9 into single-session volumes and require two-point identity checks during setup

---

### RULE DX-008
STAGE: bulk_analysis
CONDITION: TIDE, ICE, or Sanger deconvolution gives unstable or contradictory edit percentages between replicate PCR reactions
DIAGNOSIS: Amplicon quality or mixed-template complexity is undermining deconvolution
CONFIDENCE: medium
LIKELY_CAUSES:
  - PCR background products are present
  - The amplicon is too long or low quality for clean Sanger traces
  - The edit spectrum is too complex for the chosen analysis route
DISTINGUISH:
  - Sharp single PCR bands with clean traces support deconvolution reliability more than smeared or multi-band amplicons
  - Reproducible disagreement between Sanger deconvolution and amplicon sequencing points to the analysis method rather than the edit itself
  - Improved consistency after shortening the amplicon supports an amplicon-design limitation
IMMEDIATE_FIX:
  - Redesign primers for a 300-500 bp product
  - Gel-purify the expected band before sequencing if non-target products are visible
  - Move to amplicon sequencing for complex edit spectra
PREVENTION: Use short, single-band amplicons for Sanger-based editing estimates and reserve deep sequencing for mixed or high-value samples

---

### RULE DX-009
STAGE: knockout_validation
CONDITION: DNA editing is high, but protein reduction remains weak at the planned harvest time
DIAGNOSIS: Protein turnover or isoform architecture is masking the knockout readout
CONFIDENCE: medium
LIKELY_CAUSES:
  - The harvest window is too early for protein depletion
  - The targeted exon is skipped in one or more active isoforms
  - In-frame alleles remain abundant
DISTINGUISH:
  - High indel frequency with retained protein at 48 h but loss by 96-120 h supports a turnover-timing explanation
  - RNA splice analysis showing exon skipping supports isoform escape rather than failed cutting
  - Amplicon sequencing enriched for in-frame alleles supports residual protein from edited but functional alleles
IMMEDIATE_FIX:
  - Extend protein harvest to 96-120 h or longer if the target is stable
  - Sequence alleles to quantify in-frame versus frameshift outcomes
  - Redesign guides to a more constitutive exon if isoform escape is likely
PREVENTION: Match the knockout validation window to target half-life and transcript architecture before starting the run

---

### RULE DX-010
STAGE: knockin_validation
CONDITION: Junction PCR is positive, but the intended protein localization or size is wrong
DIAGNOSIS: Partial donor integration, mixed alleles, or frame disruption is likely
CONFIDENCE: medium
LIKELY_CAUSES:
  - Only one junction integrated correctly
  - The donor inserted with a frame error
  - Random integration produced a misleading PCR signal
DISTINGUISH:
  - Positive 5' junction with negative 3' junction supports partial integration
  - Correct DNA junctions with wrong protein size support a frame or splice problem
  - A wild-type spanning assay that still amplifies in the same clone suggests mixed alleles or heterozygosity rather than full replacement
IMMEDIATE_FIX:
  - Run 5' junction, 3' junction, and wild-type spanning PCR together
  - Sequence the full edited coding region
  - Recheck donor frame, linker sequence, and recoding map
PREVENTION: Use a three-assay genotype panel for every knockin clone before advancing it to downstream experiments

---

### RULE DX-011
STAGE: selection
CONDITION: Antibiotic selection fails to enrich edited or transfected cells
DIAGNOSIS: Selection timing or kill-curve calibration is poor
CONFIDENCE: medium
LIKELY_CAUSES:
  - Drug concentration is too low
  - Selection begins before marker expression is established
  - Control cells are partially resistant
DISTINGUISH:
  - Survival of untreated control cells during drug exposure confirms under-dosed selection
  - Strong marker expression with weak enrichment supports kill-curve miscalibration rather than failed delivery
  - Death of both marker-positive and marker-negative cells after very early selection points to mistimed selection onset
IMMEDIATE_FIX:
  - Re-run the kill curve in the same passage range as the editing experiment
  - Start selection 24-48 h after plasmid delivery; use earlier timing only after a documented validation run in the same system
  - Track marker expression before drug addition
PREVENTION: Complete a cell-line-specific kill curve and selection-timing pilot before relying on drug enrichment

---

### RULE DX-012
STAGE: mixed_population
CONDITION: Bulk editing rates look strong, but downstream phenotype varies widely between repeats
DIAGNOSIS: Mixed-population composition is unstable across replicates
CONFIDENCE: medium
LIKELY_CAUSES:
  - Edit-spectrum composition differs from run to run
  - Cell recovery after delivery changes the surviving subpopulation
  - Phenotype depends on zygosity or exact indel class rather than edit rate alone
DISTINGUISH:
  - Similar total indel percentages with different allele spectra point to composition drift rather than raw efficiency drift
  - Stable phenotype only after clone isolation supports population heterogeneity as the limiting factor
  - Repeat-to-repeat shifts in viability together with phenotype shifts support recovery-selection bias
IMMEDIATE_FIX:
  - Add amplicon sequencing to inspect allele composition
  - Normalize the harvest window and recovery conditions across runs
  - Move the project to clonal analysis if the phenotype requires genotype resolution
PREVENTION: Do not over-interpret pooled bulk populations when phenotype depends on allele class, zygosity, or clone-specific adaptation

---

### RULE DX-013
STAGE: plasmid_delivery
CONDITION: Reporter-plasmid control shows transfection-positive cells below 10% while cell viability remains above 85%
DIAGNOSIS: Plasmid delivery efficiency is limiting the workflow rather than guide activity
CONFIDENCE: high
LIKELY_CAUSES:
  - Lipid-to-DNA ratio is outside the effective range for the cell line
  - Cell density at the time of delivery is too high or too low
  - Plasmid quality, endotoxin burden, or supercoiled fraction is poor
DISTINGUISH:
  - Low reporter-plasmid positivity with high viability points to delivery inefficiency more strongly than reagent toxicity
  - Strong plasmid delivery in a reporter control with weak editing in the editing plasmid supports a guide or locus problem rather than a delivery problem
  - Improved positivity after adjusting density or lipid-to-DNA ratio confirms that delivery optimization, not guide redesign, is the immediate need
IMMEDIATE_FIX:
  - Re-optimize lipid-to-DNA ratio in the target cell line
  - Check plasmid A260/A280, endotoxin status, and supercoiled integrity
  - Adjust plating density to the supplier-recommended window for that vessel format
PREVENTION: Run a reporter-plasmid transfection optimization before using plasmid-based CRISPR delivery as the primary editing route

---

## 5. RISK RULES

### Risk Matrix (RM-001 to RM-024) and Critical Findings (CF-001 to CF-003)

### RISK RM-001
STAGE: project_design
ITEM: Targeting a non-constitutive exon for knockout
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Target exon is shared by the transcript isoforms relevant to the phenotype
MITIGATION: Choose an early constitutive exon and review transcript maps before guide ordering

---

### RISK RM-002
STAGE: guide_design
ITEM: Guide cut site is too far from the intended HDR edit
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Distance from cut to desired edit is documented
MITIGATION: Keep the cut within 10 bp of the intended edit whenever possible

---

### RISK RM-003
STAGE: guide_design
ITEM: High-priority coding off-target sites remain unresolved
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Off-target review is completed before final guide selection
MITIGATION: Exclude guides with 0-1 mismatch coding off-target sites and flag dense 2-mismatch coding sites for secondary review

---

### RISK RM-004
STAGE: donor_design
ITEM: Donor lacks PAM-blocking or protospacer-blocking recoding
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Blocking mutation plan is recorded in the donor sequence sheet
MITIGATION: Add silent PAM-disrupting or guide-disrupting changes to the donor when coding context permits

---

### RISK RM-005
STAGE: reagent_handling
ITEM: Guide RNA degradation during setup
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Guide freeze-thaw count and RNase-free handling are documented
MITIGATION: Use RNase-free consumables, keep guides on ice during setup, and discard heavily thawed aliquots

---

### RISK RM-006
STAGE: reagent_handling
ITEM: Cas9 activity loss from storage abuse
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Cas9 lot, storage temperature, and thaw history are recorded
MITIGATION: Aliquot Cas9 into single-session volumes and keep it on ice during setup

---

### RISK RM-007
STAGE: rnp_assembly
ITEM: Incorrect sgRNA:Cas9 ratio in RNP assembly
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Molar ratio is calculated in the run sheet
MITIGATION: Assemble RNP at 1.2:1 to 2:1 sgRNA:Cas9 and use the same ratio across compared conditions

---

### RISK RM-008
STAGE: labeling
ITEM: Guide-condition swap due to poor tube labeling
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Each tube includes guide ID, donor ID, and destination well or cuvette
MITIGATION: Label before pipetting and require a second identity check during multi-guide setup

---

### RISK RM-009
STAGE: cell_health
ITEM: Mycoplasma-positive or unhealthy cells used for editing
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Mycoplasma test within the past 30 days is negative and cell viability is at or above 90%
MITIGATION: Test active lines before editing campaigns and postpone delivery when health metrics are poor

---

### RISK RM-010
STAGE: electroporation
ITEM: Cells held too long in electroporation buffer before pulsing
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Buffer-hold time is recorded and remains below 15 min
MITIGATION: Prepare cells last, assemble the final reaction quickly, and pulse immediately after loading

---

### RISK RM-011
STAGE: electroporation
ITEM: Bubble carryover causes arcing or uneven pulse delivery
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: No visible bubbles are present in the cuvette or strip
MITIGATION: Load slowly, inspect the chamber before pulsing, and rebuild the reaction if bubbles remain

---

### RISK RM-012
STAGE: electroporation
ITEM: Pulse program is too harsh for the target cell type
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Viability is measured within 24 h and compared with a delivery-only control
MITIGATION: Use a cell-line-validated program and step down to a lower-energy program when toxicity is excessive

---

### RISK RM-013
STAGE: lipid_delivery
ITEM: Antibiotics remain in medium during early lipid-based editing
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Medium composition for the first 24 h is logged
MITIGATION: Use antibiotic-free medium during complex exposure and early recovery unless the same cell line and reagent combination has written survival-validation data under antibiotic-containing conditions

---

### RISK RM-014
STAGE: recovery
ITEM: Medium replacement is delayed in toxicity-prone lipid workflows
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Medium-change time is recorded
MITIGATION: Replace medium at 4-6 h for toxicity-prone lines and 12-24 h for fast-growing, lipid-tolerant immortalized cell lines with high viability

---

### RISK RM-015
STAGE: screening
ITEM: Bulk editing is screened too early after delivery
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Harvest time matches the planned assay window
MITIGATION: Run first-pass bulk indel analysis at 48-96 h and HDR analysis at 72-120 h

---

### RISK RM-016
STAGE: assay_design
ITEM: Protein validation is performed before target turnover allows depletion
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Target half-life and protein harvest window are documented
MITIGATION: Extend protein harvest to 96-120 h or longer for stable proteins

---

### RISK RM-017
STAGE: enrichment
ITEM: Drug selection starts before marker expression is established
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Selection start time is recorded relative to delivery
MITIGATION: Start selection 24-48 h after plasmid delivery; use earlier timing only after a documented validation run in the same system

---

### RISK RM-018
STAGE: enrichment
ITEM: Kill curve is outdated for the current cell passage state
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Kill-curve date and passage range are documented
MITIGATION: Re-run the kill curve whenever medium, serum, passage behavior, or antibiotic lot changes materially

---

### RISK RM-019
STAGE: bulk_analysis
ITEM: Amplicon is too long or mixed for clean Sanger deconvolution
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Amplicon length and single-band status are confirmed before sequencing
MITIGATION: Keep Sanger deconvolution amplicons in the 300-800 bp range and require a single dominant PCR band

---

### RISK RM-020
STAGE: clone_genotyping
ITEM: Homozygous call made from one small PCR assay
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: More than one primer strategy is used for clone calling
MITIGATION: Use at least two independent primer sets and add long-range or junction PCR when the locus architecture is complex

---

### RISK RM-021
STAGE: clone_isolation
ITEM: Single-cell clones are isolated before bulk cells recover from delivery stress
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Bulk culture growth has stabilized before single-cell isolation begins
MITIGATION: Delay clone isolation until edited bulk cells show stable expansion for at least 48 h

---

### RISK RM-022
STAGE: interpretation
ITEM: One edited clone is treated as definitive biological proof
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: More than one clone or more than one guide is carried into phenotype work
MITIGATION: Validate findings in independent clones or with an independent guide; for mechanistic claims, add cDNA rescue or endogenous-allele complementation as required supporting evidence, while descriptive phenotype projects can defer rescue work to the publication-validation stage

---

### RISK RM-023
STAGE: knockin_analysis
ITEM: Partial donor integration is missed because only one junction PCR is run
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Both junction assays and a wild-type spanning assay are planned
MITIGATION: Run 5' junction, 3' junction, and wild-type spanning PCR for every knockin clone

---

### RISK RM-024
STAGE: documentation
ITEM: Reagent lots, pulse settings, and harvest windows are not recorded
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: The run sheet contains guide lot, Cas9 lot, donor lot, delivery settings, cell count, and harvest timing
MITIGATION: Use a written editing worksheet for every run and complete it before result interpretation

---

---

#### Critical Findings (CF-001 to CF-003)

### RISK CF-001
STAGE: controls
ITEM: Editing claim made without untreated, delivery-only, or non-targeting control alignment
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Control set is present in the same run and readout window
MITIGATION: (1) Repeat the run with matched controls. (2) Separate delivery toxicity from editing outcome before redesigning the guide. (3) Do not interpret phenotype shifts without a control framework that matches the delivery route.

---

### RISK CF-002
STAGE: clone_genotyping
ITEM: Clone advanced as homozygous without multi-assay confirmation
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Homozygous calls include at least two DNA assays and sequence confirmation
MITIGATION: (1) Re-genotype with a second primer set. (2) Add long-range or junction PCR if the locus allows large deletions or insertions. (3) Sequence both assays before advancing the clone.

---

### RISK CF-003
STAGE: interpretation
ITEM: Mechanism claim made from one guide or one clone without orthogonal support
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Independent guide, independent clone, or rescue evidence is present
MITIGATION: (1) Confirm the phenotype with an independent guide or clone. (2) Add rescue or complementation if the claim is mechanistic. (3) Treat single-guide single-clone data as provisional until corroborated.

---

## 6. PARAMETER CONSTRAINTS

### Guide And Donor Design

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Candidate guides reviewed per locus | 2 | 3-6 | 10 | <2: design space is too narrow for robust selection |
| Cut distance to precise HDR edit | 0 bp | 0-10 bp | 20 bp | >20 bp: HDR frequency often drops sharply |
| ssODN homology arm length | 40 bp | 60-90 bp | 120 bp | <40 bp: repair support may weaken; >120 bp each side can exceed synthesis constraints |
| Plasmid or PCR donor arm length | 150 bp | 300-800 bp | no absolute upper limit | <150 bp: junction efficiency may be low for many loci; >1000 bp per arm: cloning complexity and synthesis cost increase |

### RNP Or Plasmid Setup

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| sgRNA:Cas9 molar ratio in RNP | 1.0:1 | 1.2:1 to 2.0:1 | 3.0:1 | >3.0:1 adds RNA excess without clear gain in many systems |
| RNP assembly incubation at 20-25°C | 5 min | 10-20 min | 30 min | >30 min: activity drift or setup delay risk increases |
| ssODN donor per electroporation reaction | 10 pmol | 20-100 pmol | 200 pmol | >200 pmol: toxicity can rise in sensitive lines |
| Plasmid DNA per 24-well editing transfection | 0.25 µg | 0.5-1.0 µg | 1.5 µg | >1.5 µg: toxicity and mixed-delivery artifacts rise |

### Cell Preparation And Delivery

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Adherent confluence at lipid delivery | 50% | 60-80% | 85% | >85%: uptake and growth recovery often decline |
| Electroporation cell input per reaction | 1 × 10^5 | 2 × 10^5 to 1 × 10^6 | 2 × 10^6 | Outside kit range: viability and editing can collapse |
| Cell hold in electroporation buffer before pulse | 0 min | 1-10 min | 15 min | >15 min: viability loss rises |
| Transfer after electroporation | immediate | within 5 min | 10 min | >10 min: buffer stress can reduce recovery |
| Lipid:RNP ratio for Cas9 RNP-lipid delivery, expressed as lipid-reagent volume to RNP protein mass equivalent | 1:1 starting ratio | 2:1-5:1 optimization window | 10:1 | Outside this range: toxicity can rise or delivery efficiency can fall; confirm performance with fluorescent Cas9 or a reporter control |
| Cas9 RNP-lipid complex incubation at 20-25°C | 5 min | 10-15 min | 20 min | >20 min: complex behavior can drift and toxicity can rise |
| Cas9 RNP-lipid complex volume per 24-well format | 25 µL | 50-100 µL | 150 µL | >150 µL: osmotic and medium-composition shifts can reduce recovery |

### Recovery And Screening

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Viability check after delivery | 12 h | 16-24 h | 36 h | >36 h: early delivery toxicity signal can be missed |
| First bulk indel screen | 24 h | 48-96 h | 120 h | <24 h: edited allele burden may be under-measured |
| First HDR screen | 48 h | 72-120 h | 168 h | <48 h: repaired allele accumulation may be under-measured |
| Drug selection start after plasmid delivery | 24 h | 24-48 h | 72 h | <24 h: marker expression may be incomplete; delay selection and recheck marker expression before adding drug; >72 h: background carryover can rise; add drug and discard delayed wells |

### Genotyping And Cloning

| Parameter | Value / Range | Notes |
|-----------|--------------|-------|
| Routine Sanger deconvolution amplicon size | 300-800 bp | Shorter clean amplicons support more stable trace analysis |
| Limiting-dilution seeding density | 0.3-0.8 cell per 100 µL | 0.5 cell per 100 µL is a common starting point for single-cell isolation |
| Clone well medium volume in 96-well plates | 150-200 µL | Exchange medium every 48-72 h during outgrowth |
| Clone panel size for moderate-difficulty knockout | 24-48 clones | Precise knockin campaigns often require more clones |
| Clone panel size for precise knockin | at least 48 clones | Carry at least 48 clones into genotyping for many precise-knockin campaigns |

---

## 7. QC GATES

### QC Gate 1: Before Guide Ordering

PASS criteria (ALL must be true):
  - Editing goal and locus strategy are defined
  - Target exon or junction is chosen with transcript review completed
  - Candidate guides and final selected guides are documented
  - Validation readout and success metric are written

ACTION if FAIL: If the target exon is uncertain, pause and review transcript usage in the target cell model. If the success metric is missing, define the assay and threshold before ordering reagents. If off-target review is incomplete, do not finalize guide selection.
WARNING trigger: One documentation field remains incomplete, but target identity, guide identity, and assay plan are already verified. Complete the missing record within 48 h or escalate the gate to FAIL.

---

### QC Gate 2: Before Delivery Setup

PASS criteria (ALL must be true):
  - Guide, Cas9, and donor identities are confirmed
  - Concentrations and freeze-thaw counts are recorded
  - Genotyping primers are ready
  - Cells are healthy and mycoplasma-negative

ACTION if FAIL: If guide identity or donor identity is uncertain, stop and reverify against the design sheet. If cells are unhealthy or untested, postpone delivery. If primers are not ready, do not start a run that cannot be screened on time.
WARNING trigger: One non-identity record, such as a lot note or thaw-date entry, is missing while reagent identity and cell health remain verified. Complete the missing record within 48 h or escalate the gate to FAIL.

---

### QC Gate 3: After RNP Assembly Or Plasmid Mix Setup

PASS criteria (ALL must be true):
  - Reaction composition is recorded
  - Assembly time and temperature are within the defined window
  - For crRNA:tracrRNA workflows, duplex annealing was completed and the annealing temperature record was captured before Cas9 addition
  - Tubes are labeled with guide and destination IDs
  - Replicates use matched reaction composition

ACTION if FAIL: If the mix order or tube identity is uncertain, discard the setup and rebuild from the written worksheet. If assembly time drifted across conditions, remake the reactions with synchronized timing.
WARNING trigger: One timing or worksheet field is missing, but tube identity, reaction composition, and annealing completion remain confirmed. Complete the missing record within 48 h or escalate the gate to FAIL.

---

### QC Gate 4: After Delivery And Early Recovery

PASS criteria (ALL must be true):
  - Delivery settings or complex volumes are recorded
  - Recovery medium was ready before delivery
  - Viability check at 16-24 h is scheduled or completed
  - Control groups remain identifiable and viable enough for comparison

ACTION if FAIL: If settings were not captured, the run cannot serve as an optimization anchor. If recovery timing was delayed or controls are missing, treat the run as limited-value pilot data and repeat before drawing conclusions.
WARNING trigger: The run remains interpretable, but one recovery note or one control annotation is incomplete while identity and viability tracking remain intact. Complete the missing record within 48 h or escalate the gate to FAIL.

---

### QC Gate 5: Before Final Clone Or Bulk Interpretation

PASS criteria (ALL must be true):
  - Bulk assay quality is acceptable for the chosen analysis route
  - Clone identity map is preserved
  - Multi-assay genotype confirmation is in place for clone calls
  - Phenotype claims are supported by more than one line of evidence when the project is mechanistic

ACTION if FAIL: If Sanger traces are poor, shorten the amplicon or move to amplicon sequencing. If clone identity is uncertain, do not advance the clone. If a mechanism claim relies on one guide or one clone, collect independent supporting evidence first.
WARNING trigger: One confirmatory record or one secondary annotation remains incomplete, but the core genotype call and sample identity are intact. Complete the missing record within 48 h or escalate the gate to FAIL.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified CRISPR-Cas9 issue and root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in the diagnosis based on controls and assay evidence |
| recommended_actions | list[string] | Ordered recovery, redesign, or validation actions |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass or fail status for each QC gate |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters linked to diagnostic rules |
| protocol_section_reference | string | Section of SOP-CRISPR-CAS9-001 relevant to the issue |
| editing_status | enum: efficient / low_editing / toxic / mixed / indeterminate | Summary of the editing outcome |
| genotype_resolution_status | enum: bulk_only / partial_clone_call / confirmed_clone_call / uncertain | Strength of genotype resolution |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | User needs plating density planning, post-electroporation recovery support, or single-cell outgrowth help |
| transfection_v1 | User needs plasmid or lipid-delivery optimization before switching to editing-specific troubleshooting |
| western_blot_v1 | User needs protein-loss confirmation after knockout or tag verification after knockin |
| immunofluorescence_v1 | User needs tag localization or protein-expression imaging after editing |
| flow_cytometry_v1 | User needs reporter enrichment, surface-marker editing readout, or clone sorting support |
| rt_qpcr_v1 | User needs transcript-level confirmation of knockout or repair outcome |
| amplicon_sequencing_v1 | User needs deep edit-spectrum or HDR-frequency quantification beyond Sanger deconvolution |
| single_cell_cloning_v1 | User needs clone isolation, outgrowth, and banking workflows after bulk editing success |
