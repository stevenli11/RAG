---
skill_id: crispr_knockout_v1
skill_name: CRISPR Knockout Complete Workflow Skill
version: 1.0
method_family: genome_engineering
tags: [crispr, knockout, cas9, sgrna, gene_editing, nhej, clonal_isolation, transfection, nucleofection, lentiviral_delivery, validation, t7e1, amplicon_sequencing, western_blot, flow_cytometry, cell_pool, single_cell_clone]
applies_to: [mammalian_cell_lines, pooled_knockout, clonal_knockout, plasmid_delivery, rnp_delivery, lentiviral_cas9_systems]
does_not_apply_to: [base_editing, prime_editing, knockin_hdr, large_genomic_rearrangements, germline_editing, in_vivo_gene_editing, embryos, plants, microbial_crispr_adaptation]
risk_level: high
bsl_level: "BSL-2 (lentiviral delivery only); otherwise BSL-1 with institutional molecular biology containment per biosafety office guidance"
last_updated: 2026-03-18
source_protocol: SOP-CRISPRKO-001
---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I knock out a gene with CRISPR," "which sgRNA should I pick," "my editing efficiency is low," "how do I make a clonal knockout line," "how do I validate a knockout," "my CRISPR cells keep dying," "should I use plasmid or RNP," "how do I enrich edited cells," "how do I screen clones," "why do I still see protein after editing," "how do I avoid off-targets," or any question about designing, executing, enriching, cloning, and validating a CRISPR-Cas9 gene knockout in mammalian cells. This skill covers the complete knockout workflow: target selection and sgRNA design, delivery strategy selection (plasmid, RNP, or lentiviral), cell preparation, editing execution, enrichment and recovery, pooled versus clonal workflows, single-cell cloning, genotypic and phenotypic validation, and structured diagnostic rules for low editing, poor viability, false-positive clones, mosaicism, and residual protein signal. This skill is organized into 7 workflow modules covering the complete editing trajectory from guide design to validated clone. This skill does NOT cover: precise HDR knock-in workflows, base editing, prime editing, CRISPRi/a, in vivo delivery, embryo editing, or pooled screening library design at scale. Redirect those queries to the matching skill listed in Section 9.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| gene_target | string | Official gene symbol or transcript target intended for knockout |
| cell_line_name | string | Specific cell line or primary cell type being edited |
| species | enum: human / mouse / rat / other | Determines genome build, transcript annotation, and reagent compatibility |
| workflow_goal | enum: pooled_knockout / clonal_knockout / pilot_feasibility / validation_only / troubleshooting | Primary objective of the edit campaign |
| delivery_method | enum: plasmid / rnp / lentiviral / unknown | Intended or attempted CRISPR delivery format |
| validation_priority | enum: genotype_first / protein_first / phenotype_first | Primary success readout driving the workflow |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| transcript_isoform | string | Specific transcript or exon model being targeted |
| target_exon | string | Exon number or coding region selected for sgRNA placement |
| sgRNA_sequence | string | 20 nt guide sequence used for targeting |
| pam_type | enum: NGG / alternative / unknown | PAM requirement for the nuclease used |
| cas_nuclease | enum: spcas9 / hifi_cas9 / spcas9_hf1 / espcas9 / other | Nuclease variant used |
| delivery_reagent | string | Lipid reagent, nucleofection program, or viral system used |
| editing_efficiency_percent | float (0-100) | Measured editing rate from ICE/TIDE, NGS, or mismatch assay |
| viability_percent_24h | float (0-100) | Cell viability 24 h after delivery |
| viability_percent_72h | float (0-100) | Cell viability 72 h after delivery |
| selection_marker | string | Antibiotic or fluorescent marker used for enrichment |
| selection_start_time_h | float | Hours post-delivery when enrichment or antibiotic selection began |
| protein_half_life_category | enum: short / medium / long / unknown | Helps explain delayed protein knockout phenotype |
| days_post_editing | int | Days elapsed since CRISPR delivery |
| clone_count_screened | int | Number of clones screened for clonal workflows |
| genotype_result | string | Summary of genotyping result (e.g., mixed indels, homozygous frameshift, WT) |
| protein_result | string | Summary of western blot / flow / IF result |
| off_target_concern | enum: low / medium / high | Concern level based on guide quality or phenotype ambiguity |
| essential_gene_status | enum: yes / no / unknown | Whether the target is expected to impair growth or survival when lost |
| copy_number_status | enum: normal / amplified / deleted / unknown | Important for cancer lines with multiple alleles |
| ploidy_status | enum: diploid / aneuploid / unknown | Affects clonal knockout expectations |

---

## 3. WORKFLOW MODULES

### Module 1: TARGET_DEFINITION_AND_SGRNA_DESIGN

**Preconditions:** The target gene identity is confirmed using the correct species and transcript annotation. The user has defined whether the desired outcome is a pooled loss-of-function population or a validated clonal knockout line.
**Pause point:** YES — do not order reagents or begin wet lab work until target exon choice and guide ranking are finalized.

#### Steps:

1. [CRITICAL] Confirm the exact gene symbol, species, and transcript model before guide design. Genes with multiple isoforms frequently have non-shared exons; targeting the wrong exon produces an apparent "edit" without a functional knockout.
2. Select an early constitutive coding exon shared by the major functional isoforms whenever possible. Avoid exons that are alternatively spliced out of the dominant protein-coding transcript.
3. [CRITICAL] Prefer guides that cut within the first 30-50% of the coding sequence and ensure the resulting frameshift is expected to generate a premature termination codon at least 50-55 nt upstream of the last exon-exon junction, where NMD is most reliably triggered. For single-exon genes or genes with very large terminal exons, NMD may not occur regardless of cut position; confirm isoform architecture before selecting the guide. For single-exon targets, NMD cannot be relied upon; instead target a sequence encoding a functionally critical domain, catalytic residue, conserved motif, or essential binding interface, or use a dual-guide large-deletion strategy to remove a substantial portion of the coding sequence. Plan for more stringent protein-level validation to detect residual truncated protein activity.
4. Screen 3-4 candidate sgRNAs instead of relying on a single guide. Rank by on-target activity, low predicted off-target burden, and exon relevance.
5. [DO NOT] Choose a guide solely because it has the highest score if it targets an exon absent from the biologically relevant isoform.
6. Check for SNPs, known polymorphisms, or cell-line-specific mutations in the guide binding site if the line is heavily engineered or cancer-derived. A mismatch in the seed region can reduce editing dramatically.
7. [CRITICAL] If the cell line has copy-number amplification or is known to be aneuploid, plan for more extensive clone screening. A "biallelic" edit assumption is unsafe in many cancer lines.
8. Prefer at least two independent sgRNAs for biological conclusions. A phenotype observed with only one guide is not enough evidence of on-target gene loss.

#### Exit Criteria (must ALL be true to proceed):
- Target exon is shared by the relevant protein-coding isoforms
- At least 2 high-priority sgRNAs are selected
- Off-target review is documented
- A validation strategy is selected before editing begins

---

### Module 2: DELIVERY_STRATEGY_SELECTION

**Preconditions:** Candidate sgRNAs are defined. The user has basic information on the target cell line's transfectability and growth behavior.
**Pause point:** YES — delivery method determines timing, controls, enrichment strategy, and biosafety requirements.

#### Steps:

1. [DECISION POINT] Choose delivery format:
   - RNP: preferred for many difficult or sensitive lines; fastest editing window; lowest persistent Cas9 exposure; often best for minimizing off-target risk.
   - Plasmid: simplest setup for easy-to-transfect lines; slower expression kinetics; prolonged Cas9 expression can increase off-target activity.
   - Lentiviral: useful for hard-to-transfect adherent or suspension lines and for stable Cas9/sgRNA systems; requires BSL-2 practices and viral controls.
2. Use RNP for pilot feasibility in challenging cells unless strong local data support plasmid delivery.
3. Use plasmid only if the cell line routinely tolerates the chosen lipid/electroporation workflow and short-term toxicity remains within the project's viability limits.
4. [CRITICAL] If the target gene is likely essential, avoid aggressive early selection that can eliminate edited cells before they recover. Essential-gene projects require conservative enrichment timing and time-course analysis rather than aggressive selection.
5. Match the enrichment strategy to delivery:
   - Fluorescent plasmid: sort positive cells 48-72 h post-transfection.
   - Antibiotic plasmid/lentivirus: begin selection only after expression is established.
   - RNP: no built-in marker unless co-delivered; consider surrogate reporters or direct pooled genotyping.
6. [DO NOT] Move into single-cell cloning before confirming that the pooled population contains meaningful editing. Cloning a mostly wild-type pool wastes weeks.

#### Exit Criteria (must ALL be true to proceed):
- Delivery method matches cell-line tolerance and project goal
- Enrichment plan is defined or intentionally omitted
- Controls are specified: non-targeting, mock, and positive-control edit where possible
- Biosafety level matches the selected delivery method: BSL-2 for lentiviral, BSL-1 with institutional molecular biology containment for plasmid or RNP

---

### Module 3: CELL_PREPARATION_AND_EDITING_EXECUTION

**Preconditions:** Cells are healthy, low-passage where possible, mycoplasma-negative, and in log-phase growth. Reagents are prepared and verified.
**Pause point:** NO — once RNP is assembled or cells are committed to transfection/nucleofection, complete the workflow without delays.

#### Steps:

1. [CRITICAL] Start with a healthy culture: viability >=90%, no visible contamination, and no recent overgrowth stress. CRISPR does not rescue unhealthy cells; it amplifies workflow noise.
2. Plate or prepare cells so they are in the recommended physiological state at delivery:
   - Adherent lipid transfection: 70-90% confluence at the time of reagent addition.
   - Electroporation/nucleofection: single-cell suspension from actively growing cultures; transfer cells to pre-equilibrated recovery medium within 15 min of the nucleofection pulse.
   - Lentiviral transduction: cells should be proliferative and not overcrowded at infection.
3. Assemble the CRISPR components exactly as required for the chosen chemistry. For RNP, mix sgRNA and Cas9 at a 2:1-4:1 molar ratio and incubate at 25°C for 10-20 min immediately before use. Do not assemble on ice or leave assembled RNP at 37°C for >30 min.
4. Include the minimum control set:
   - Mock delivery control
   - Non-targeting guide control
   - Positive editing control if the platform is unvalidated in this cell line
5. [CRITICAL] Record the exact cell number, reagent amounts, nucleofection program or lipid ratio, and timing. Low-editing troubleshooting is impossible without this metadata.
6. After delivery, return cells to pre-equilibrated recovery medium immediately. For electroporation workflows, minimize centrifugation and pipetting stress.
7. [BEGINNER TRAP] Do not interpret morphology or protein loss at 24 h as knockout success. DNA cleavage occurs early; phenotypic consequences often lag by several days.
8. [DO NOT] Freeze or expand the edited pool before confirming recovery by viability and growth metrics and documenting detectable editing.

#### Exit Criteria (must ALL be true to proceed):
- Delivery completed with documented conditions
- Recovery initiated immediately after editing
- Controls were carried through the same run
- Cells remain viable enough for downstream enrichment or monitoring

---

### Module 4: ENRICHMENT_AND_POOL_RECOVERY

**Preconditions:** Cells have undergone editing and have had an initial recovery period matched to the delivery method.
**Pause point:** YES — timing of selection or sorting has major effects on both viability and apparent editing efficiency.

#### Steps:

1. Allow an initial recovery window before applying stress:
   - Many plasmid workflows: fluorescence-based sort at 48-72 h post-transfection; antibiotic selection start at 24-72 h depending on resistance marker expression window and kill-curve data
   - RNP workflows: assess recovery first; enrich only if a co-marker exists
   - Lentiviral systems: begin antibiotic selection only after transgene expression is established
2. [CRITICAL] Determine whether the target is essential or growth-limiting. If yes or unknown, use conservative enrichment and interpret depletion as potentially biological, not technical failure.
3. For antibiotic selection, first establish a kill curve in the unedited parental line. Never guess the dose.
4. For FACS enrichment, set the positive gate to exclude cells in the lower 20% of fluorescence signal and all viability-dye-positive events; do not extend the gate to include dim or dying cells to avoid a false sense of successful delivery.
5. Expand the enriched pool for initial validation before launching clonal work. This is the first decision point where the project should either proceed or be redesigned.
6. [CRITICAL] Preserve a backup aliquot of the edited pool once recovery is confirmed by viability and growth metrics. Clonal workflows can fail even when the pool is strong.
7. [DO NOT] Conclude that selection failure means editing failure. Selection marker expression, transduction efficiency, and editing activity are related but not identical.

#### Exit Criteria (must ALL be true to proceed):
- Enrichment timing matches the platform
- Pool recovery is documented at 48-96 h
- A backup of the edited pool is banked if the workflow continues
- Initial editing readout is planned or completed

---

### Module 5: INITIAL_EDITING_ASSESSMENT

**Preconditions:** The edited pool has recovered and contains >=1 x 10^5 viable cells for DNA extraction, or >=5 x 10^4 cells per condition for protein or phenotypic analysis.
**Pause point:** YES — do not start clone isolation until the pool shows editing at >=30% by ICE/TIDE or amplicon sequencing (see Section 6 Editing Readout table).

#### Steps:

1. Measure editing in the bulk population using a fit-for-purpose assay:
   - Sanger + ICE/TIDE: fast screening for pooled indels
   - Amplicon NGS: preferred when precision or low-frequency edits matter
   - T7E1/mismatch assays: only coarse screening; cannot detect homozygous edits because they require heteroduplex formation between WT and mutant alleles, and can produce a false-negative result when pooled editing is near 100%; cannot serve as sole final validation
2. [CRITICAL] Align the assay to the cut site. Poor primer placement or sequencing through low-quality amplicons can make a good edit look bad.
3. For protein-based validation, wait long enough for protein turnover. Stable proteins may persist for 3-14 days after efficient gene disruption depending on protein half-life; consult the Section 6 validation parameter table for washout intervals.
4. [DECISION POINT] Pool interpretation:
   - Editing >=70% with expected viability: proceed confidently toward pool-based phenotyping or clone isolation.
   - Editing 30-70%: usable for some pooled assays; optimize before cloning if single-cell work is planned.
   - Editing <30%: redesign or re-optimize before investing in clone screening.
5. Compare the targeting guide against non-targeting and mock controls at the same time point. Without this, toxicity and phenotype interpretation are weak.
6. [DO NOT] Treat reduced protein as proof of a true null genotype. Partial editing, in-frame indels, or antibody artifacts can all mimic a knockout.

#### Exit Criteria (must ALL be true to proceed):
- A pooled editing measurement exists
- The measurement is interpretable and linked to the target cut site
- Decision made: proceed, optimize, or redesign
- Validation timing accounts for protein persistence where relevant

---

### Module 6: SINGLE_CELL_CLONING_AND_EXPANSION

**Preconditions:** The pool shows editing at >=30% by ICE/TIDE or amplicon sequencing and the cells are robust enough to survive single-cell isolation.
**Pause point:** NO — once cells are single-cell sorted or diluted, continue through early monitoring without long gaps.

#### Steps:

1. Choose a clonal isolation method matched to the line:
   - Single-cell FACS into conditioned medium
   - Limiting dilution only if validated locally for clonality
   - Colony picking for lines that form discrete colonies
2. [CRITICAL] Use conditioned medium, feeder support, or enhanced recovery conditions if the cell line is known to clone poorly. To prepare conditioned medium: collect spent medium from a healthy log-phase culture of the same cell line, filter through a 0.22 µm membrane to remove debris, and mix 1:1 with fresh complete medium. Use within 24 h of preparation. Many knockout projects fail at the clone-expansion stage rather than the edit stage.
3. Record plate map, clone IDs, isolation date, and source pool. Traceability errors are a common hidden cause of "mysterious" validation failures.
4. Expand clones in phases:
   - Early survival monitoring
   - [VISUAL CHECK] Check each well at 24 h and again at 72 h by microscopy: single-cell origin wells should show one clearly separated cell at 24 h, and a small cluster of 2-4 cells at 72 h; flag wells with multiple founding cells for exclusion from clonal tracking
   - Split for parallel cryobackup and genotyping
   - Expand only confirmed candidates
5. [CRITICAL] Cryopreserve each promising clone as soon as there is enough material. Do not wait until final validation to create the first backup.
6. Expect extra complexity in aneuploid or amplified loci. A clone may show mixed alleles for longer, and more clones may be needed to find a complete functional knockout.
7. [DO NOT] Advance a clone to expensive functional studies before confirming clonality and genotype. Morphological uniformity is not proof of genotype purity.

#### Exit Criteria (must ALL be true to proceed):
- Clone identity and plate map are documented
- Early backup stocks exist for viable candidate clones
- At least 24 clones are available for screening for diploid targets, or at least 48 for aneuploid or amplified loci
- The screening workflow is ready before clones overgrow

---

### Module 7: GENOTYPIC_AND_FUNCTIONAL_VALIDATION

**Preconditions:** Candidate pools or clones are available with enough biomass for DNA and phenotype assays.
**Pause point:** YES — validation must be multi-layered before the knockout is considered confirmed.

#### Steps:

1. Perform locus-level genotyping around the cut site for every candidate clone advanced past preliminary screening.
2. [CRITICAL] Sequence both alleles to the extent possible and resolve mixed traces. A clone with an indel call but unresolved mixed sequence is not yet a confirmed knockout.
3. Classify edit outcomes:
   - Frameshift on all functional alleles: strong knockout candidate
   - In-frame indel: requires caution; often not a true loss of function
   - Mixed/WT plus edited alleles: not a full knockout clone
4. Pair genotyping with at least one orthogonal functional readout:
   - Western blot for protein absence
   - Flow cytometry for surface proteins
   - IF for localization loss
   - RT-qPCR when nonsense-mediated decay is expected
   - Pathway or growth phenotype when biologically justified
5. [CRITICAL] Account for protein half-life. If genotype is convincing but protein remains, extend the washout interval before rejecting the clone.
6. Validate with a second independent sgRNA or rescue experiment before making strong causal biological claims.
7. For rescue validation: re-express a codon-modified cDNA of the target gene that is resistant to sgRNA re-cutting, with at least 3-4 silent mutations in the PAM-proximal seed region. Confirm that the rescue construct restores the wild-type phenotype in at least one confirmed knockout clone. Include an empty-vector control in the same confirmed knockout clone to confirm that phenotype rescue requires the target coding sequence and is not caused by the delivery procedure itself.
8. [DECISION POINT] If off_target_concern is high or biological results are ambiguous: (1) run Cas-OFFinder or equivalent computational prediction for the guide; (2) sequence the top 5-10 predicted off-target sites by amplicon Sanger or NGS in each confirmed clone; (3) if off-target edits are found in clones used for biology, repeat with a higher-specificity nuclease variant, for example HiFi Cas9 (IDT), SpCas9-HF1, or eSpCas9, or redesign the guide to a lower predicted off-target burden.
9. [DO NOT] Call a clone "knockout confirmed" based on only one assay layer.

#### Exit Criteria (must ALL be true to proceed):
- Genotype is resolved at the target locus
- At least one orthogonal validation assay supports loss of function
- Residual WT alleles are excluded or explicitly documented
- Clone status is labeled as confirmed, partial, or rejected

---

## 4. DIAGNOSTIC RULES

### RULE DX-001

**IF:** Editing efficiency in the pool is <30%
**THEN LIKELY CAUSE:** Poor sgRNA choice, guide-target mismatch, weak delivery, or incorrect assay timing
**CHECK:**
- Confirm guide sequence and PAM orientation
- Confirm the target site exists in the actual cell line / transcript
- Review delivery conditions and positive-control edit performance
- Verify genotyping primers flank the cut site correctly
**ACTION:**
- Switch to a higher-ranked guide or test 2-3 guides in parallel
- Re-optimize delivery conditions using a positive-control target
- Repeat measurement at a later time point if collected too early

---

### RULE DX-002

**IF:** Viability at 24 h post-delivery is <70%
**THEN LIKELY CAUSE:** Delivery toxicity, excessive reagent load, harsh electroporation, or poor starting culture health
**NOTE:** The >=85% threshold in Section 6 applies to culture health before editing; post-delivery 24 h viability below 70% indicates excessive delivery toxicity.
**CHECK:**
- Review starting cell viability and confluence
- Compare mock-treated cells to targeted cells
- Check reagent ratio or nucleofection program
**ACTION:**
- Reduce reagent burden or cell handling stress
- Use healthier log-phase cells
- Consider switching to RNP delivery to reduce plasmid-associated toxicity; if nucleofection is the cause, test a lower cell-density program or reduce the plasmid dose

---

### RULE DX-003

**IF:** Delivery marker is strong but editing remains low
**THEN LIKELY CAUSE:** Marker expression without effective cutting, poor guide design, or inactive Cas9 complex formation
**CHECK:**
- Determine whether marker and editing cargo are physically linked
- Confirm Cas9 and sgRNA assembly / expression
- Review guide sequence quality and target-site integrity
**ACTION:**
- Replace the guide first
- Validate cutting with a known positive-control locus
- Use RNP or re-cloned expression constructs

---

### RULE DX-004

**IF:** Genotyping suggests editing but protein remains near wild-type
**THEN LIKELY CAUSE:** In-frame indel, incomplete allelic knockout, long protein half-life, antibody artifact, or a frameshift in the final or penultimate exon where NMD is not triggered and a truncated protein is still expressed from the edited allele
**CHECK:**
- Inspect exact indel sequence
- Confirm all alleles were resolved
- Review protein turnover timing and antibody epitope location
**ACTION:**
- Extend the post-edit interval
- Check the position of the frameshift relative to the last exon junction; if NMD evasion is likely, reposition the guide to an earlier constitutive exon
- Re-sequence clones with ambiguous traces
- Use an orthogonal antibody or functional assay

---

### RULE DX-005

**IF:** Clones repeatedly screen as mixed WT/edited
**THEN LIKELY CAUSE:** Aneuploid locus, incomplete clonality, or editing mosaicism in the source pool
**CHECK:**
- Review cell line ploidy and copy-number status
- Confirm the clone truly originated from one cell
- Examine whether clone isolation occurred before edits were fixed
**ACTION:**
- Screen more clones
- Use stricter single-cell deposition and earlier pooled validation
- Consider re-editing a high-quality partially edited clone only if scientifically justified

---

### RULE DX-006

**IF:** Selection eliminates nearly all cells
**THEN LIKELY CAUSE:** Selection started too early, dose too high, or target gene loss impairs survival
**CHECK:**
- Compare with the parental kill curve
- Review the time from delivery to selection start
- Evaluate whether the gene is essential
**ACTION:**
- Delay or soften selection
- Use fluorescent enrichment instead of antibiotic pressure
- Interpret depletion cautiously for essential-gene targets

---

### RULE DX-007

**IF:** The pool validates well but single-cell clones fail to expand
**THEN LIKELY CAUSE:** Clone fragility, poor recovery conditions, or target-dependent growth defect
**CHECK:**
- Compare clone survival to parental single-cell cloning performance
- Assess whether conditioned medium or feeder support was used
- Review whether the target gene supports proliferation
**ACTION:**
- Improve clonal recovery conditions
- Bank the pool and consider pooled phenotyping if biologically justified
- Increase clone number rather than over-interpreting a few failures

---

### RULE DX-008

**IF:** One sgRNA produces the phenotype but a second sgRNA does not
**THEN LIKELY CAUSE:** Off-target effect or guide-specific toxicity
**CHECK:**
- Compare on-target editing rates for both guides
- Review predicted off-target burden
- Assess whether rescue re-expression restores phenotype
**ACTION:**
- Do not claim on-target biology yet
- Add a rescue experiment or third independent guide
- Prioritize orthogonal validation before publication-grade conclusions

---

### RULE DX-009

**IF:** No clear indels are detected, but phenotype appears altered
**THEN LIKELY CAUSE:** Assay artifact, transient delivery stress, selection bias, or non-CRISPR biological noise
**CHECK:**
- Repeat genotyping with a better amplicon and later time point
- Compare against mock and non-targeting controls
- Examine cell health and growth rate changes unrelated to the target
**ACTION:**
- Re-measure genotype before pursuing phenotype interpretation
- Reset expectations and repeat the pilot with stronger controls

---

### RULE DX-010

**IF:** Multiple confirmed edited clones show variable phenotype strength
**THEN LIKELY CAUSE:** Clonal background effects, residual protein turnover differences, or incomplete functional knockout in some clones
**CHECK:**
- Verify each clone's exact indel architecture
- Compare protein depletion levels and passage number
- Evaluate whether the assay is sensitive to clonal adaptation
**ACTION:**
- Use multiple independent clones
- Include pooled validation and rescue where possible
- Avoid over-relying on a single "best-looking" clone

---

### RULE DX-011

**IF:** Editing efficiency is low in one cell line but the same guide works in permissive control cells
**THEN LIKELY CAUSE:** Cell-line-specific SNP or mutation in the guide seed region (positions 1-12 proximal to PAM), or copy-number amplification preventing full allelic editing
**CHECK:**
- Sequence the target locus in the actual cell line
- Identify SNPs or structural variants overlapping the guide
- Compare allele count against expected copy number
**ACTION:**
- Redesign the guide to avoid the polymorphic site
- Select a guide targeting an unaffected allele region
- Screen more clones if copy-number amplification is confirmed

---

### RULE DX-012

**IF:** Fewer than 10% of wells show colony formation after limiting dilution cloning
**THEN LIKELY CAUSE:** Conditioned medium fraction too low, incorrect seeding density, unsuitable plate format, or the cell line requires feeder support for single-cell survival
**CHECK:**
- Review conditioned medium preparation: confirm 50% spent medium from a healthy log-phase culture filtered through 0.22 µm
- Confirm seeding density was calculated for 0.5 cells per well in 200 µL
- Check whether the 96-well plate surface is tissue-culture treated
- Compare clone formation rate against parental cells in the same conditions
**ACTION:**
- Increase conditioned medium to 70% of the final well volume
- Add 10 µM ROCK inhibitor (Y-27632) for the first 48-72 h; replace with inhibitor-free conditioned medium at 72 h or at first medium change. Do not maintain ROCK inhibitor beyond 72 h, particularly for iPSC-derived lines
- Switch to FACS single-cell deposition as the more reliable alternative
- Verify cell counting accuracy before repeating

---

### RULE DX-013

**IF:** Viability at 24 h is >=70% but declines progressively between day 2 and day 5 without antibiotic selection
**THEN LIKELY CAUSE:** Prolonged Cas9 expression from plasmid cargo generating cumulative DSB-associated toxicity, particularly in slow-cycling or chromosomally fragile cell lines
**CHECK:**
- Compare the rate of viability decline between targeting and non-targeting plasmid control wells
- Review whether Cas9 expression from the plasmid is constitutive or contains any self-limiting element
- Note whether the guide targets a genomic region near a fragile site or repetitive element
**ACTION:**
- Switch to RNP delivery to eliminate prolonged nuclease expression
- Reduce plasmid dose if switching format is not immediately feasible
- Move the initial pool readout earlier to 48 h to capture editing before cell loss compounds the population

---

### RULE DX-014

**IF:** Dual-guide strategy was used to create a large deletion, but PCR shows a strong wild-type band alongside or instead of the expected deletion band
**THEN LIKELY CAUSE:** Wild-type or in-deletion-heterozygous allele is preferentially amplified; large deletion alleles are outcompeted by the shorter WT amplicon under routine PCR conditions
**CHECK:**
- Confirm the deletion product size; amplicons >500 bp different from WT are routinely under-represented in competitive PCR
- Run deletion-specific and WT-specific primers in separate reactions, not as a single multiplex
- Sequence the expected deletion junction using a deletion-flanking primer pair with a product size <400 bp
**ACTION:**
- Design allele-specific primer pairs: one pair spanning the deletion junction, positive for deletion, and one pair spanning the deleted region, positive for WT
- Run deletion confirmation by junction PCR and WT confirmation by internal PCR separately before interpreting clone genotype
- Do not conclude WT persistence from a single competitive multiplex PCR

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-015)

### RISK RM-001
STAGE: design
ITEM: Targeting a non-constitutive exon
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm the selected exon is present in the biologically relevant transcript isoforms
MITIGATION: Choose an early shared coding exon; verify transcript models before ordering guides

---

### RISK RM-002
STAGE: design
ITEM: Over-reliance on a single sgRNA
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Determine whether at least two independent guides are planned for biological confirmation
MITIGATION: Design multiple guides and require concordant results for strong conclusions

---

### RISK RM-003
STAGE: delivery
ITEM: Using unhealthy cells at the time of editing
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Starting viability >=90%, no contamination, log-phase growth
MITIGATION: Delay editing until culture health is restored; do not optimize CRISPR on stressed cultures

---

### RISK RM-004
STAGE: delivery
ITEM: Missing positive and negative controls
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Mock, non-targeting, and positive-control edit included in pilot
MITIGATION: Treat controls as mandatory for any new platform or cell line

---

### RISK RM-005
STAGE: enrichment
ITEM: Starting antibiotic selection without a kill curve
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Kill curve data exists in the parental line
MITIGATION: Run kill curve first; otherwise selection data are uninterpretable

---

### RISK RM-006
STAGE: enrichment
ITEM: Misinterpreting depletion of an essential-gene edit as technical failure
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Target essentiality reviewed before selection or long recovery comparisons
MITIGATION: Use time-course sampling and cautious enrichment for essential targets

---

### RISK RM-007
STAGE: cloning
ITEM: Beginning clonal screening from a weakly edited pool
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Pool editing efficiency documented before cloning
MITIGATION: Require pooled validation before single-cell isolation

---

### RISK RM-008
STAGE: cloning
ITEM: Loss of candidate clones due to missing early cryobackups
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm backup stocks are created before final validation is complete
MITIGATION: Freeze promising clones at the earliest safe split

---

### RISK RM-009
STAGE: validation
ITEM: Calling in-frame indels a knockout
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Exact indel classification performed for each candidate
MITIGATION: Require frameshift or function-disrupting evidence on all relevant alleles

---

### RISK RM-010
STAGE: validation
ITEM: Declaring success based on protein assay alone
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Locus-level genotype exists alongside protein or phenotype data
MITIGATION: Require multi-layer validation before final clone designation

---

### RISK RM-011
STAGE: interpretation
ITEM: Off-target phenotype mistaken for on-target biology
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Independent guides or rescue support the conclusion
MITIGATION: Use orthogonal confirmation before mechanistic claims

---

### RISK RM-012
STAGE: interpretation
ITEM: Copy-number amplified locus assumed to be diploid
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Cell line karyotype / copy-number context reviewed
MITIGATION: Plan to screen more clones and interpret allelic status cautiously

---

### RISK RM-013
STAGE: biosafety
ITEM: Lentiviral CRISPR handled outside BSL-2 containment
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: BSL-2 practices and institutional approvals are in place
MITIGATION: Follow lentiviral_transduction_v1 biosafety requirements: conduct all open viral manipulations in a certified BSC, decontaminate liquid waste with 10% bleach for >=10 min before disposal, and confirm institutional BSL-2 approval and personnel training before use

---

### RISK RM-014
STAGE: records
ITEM: Incomplete tracking of guide, pool, and clone identity
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Plate maps, clone IDs, and reagent batch records are complete
MITIGATION: Assign each guide, pool, and clone a unique alphanumeric ID at creation, for example GUIDE-001, POOL-001-P3, or CLONE-A04, and record all IDs in a linked lab notebook or electronic tracking file from day 1; never refer to samples by position alone

---

### RISK RM-015
STAGE: publication
ITEM: Claiming gene-function causality from one clone
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: More than one independent clone or orthogonal validation exists
MITIGATION: Use multiple clones, independent guides, and rescue whenever feasible

---

### Critical Findings (CF-001 to CF-003)

#### RISK CF-001
STAGE: validation
ITEM: Project labeled "knockout confirmed" without resolved genotype and orthogonal validation
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm there is both locus-level sequence evidence and at least one functional or protein-level confirmation
MITIGATION: Do not release the line as validated until both layers are complete

---

#### RISK CF-002
STAGE: interpretation
ITEM: Strong phenotype from a single guide with no rescue or second-guide support
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Review whether the phenotype is reproduced by independent targeting strategies
MITIGATION: Pause downstream conclusions; add a second guide and rescue design before proceeding

---

#### RISK CF-003
STAGE: cloning
ITEM: Hard-to-clone or essential-gene project forced into a clone-only decision gate
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Determine whether pooled evidence already answers the biological question more safely
MITIGATION: Use pooled validation when scientifically justified and treat clone failure as potentially biological, not purely technical

---

## 6. PARAMETER CONSTRAINTS

### Guide Design

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Number of candidate sgRNAs screened | 2 | 3-4 | 6 | If only 1 guide is available, treat conclusions as provisional |
| Position within coding sequence | first 10% | first 30-50% | first 70% | If targeting very late exons, expect higher risk of partial protein function |
| Independent guides for biological confirmation | 2 | 2-3 | — | Fewer than 2: treat biological conclusions as provisional; more than 3 independent guides is rarely needed unless results are discordant across guides |

### Cell State at Editing

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Starting viability | 85% | >=90% | 100% | <85%: postpone editing; troubleshoot culture first |
| Adherent confluence at lipid delivery | 60% | 70-90% | 90% | <60%: poor plasmid uptake expected; re-plate and allow attachment for 16-24 h before delivery; >90%: over-confluence may reduce delivery and alter cell physiology |
| Days since last passage | 1 | 2-3 | 5 | If heavily overgrown or freshly stressed, reset culture before editing |

### RNP Assembly

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| sgRNA:Cas9 molar ratio | 1:1 | 2:1-4:1 | 8:1 | >8:1: excess sgRNA can reduce editing consistency; re-titrate |
| Assembly incubation temperature | 20°C | 25°C | 37°C | Do not assemble on ice; complex formation is inefficient below 20°C. 37°C is an emergency ceiling only - at 37°C, assembly must be completed in <=10 min to avoid sgRNA degradation; prefer 25°C for all routine use |
| Assembly incubation time | 5 min | 10-20 min | 30 min | <5 min: incomplete complex formation; at 25°C, 30 min is acceptable though not needed; at 37°C, do not exceed 10 min due to sgRNA degradation risk |

### Editing Readout

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Time to initial pooled genotype readout | 48 h | 72-120 h | 168 h | <48 h: edited fraction may be under-reported; >168 h: clonal outgrowth and selection effects may distort the initial edit estimate |
| Pooled editing for clone launch | 30% | >=70% | — | <30%: redesign guide or re-optimize delivery before cloning |
| Clones screened for routine diploid targets | 12 | 24-48 | 96 | <12: screening power is weak; >96: consider whether locus complexity or cloning strategy should be revised |

### Validation

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Validation layers per confirmed clone | 2 | 3 | 4 | <2: do not call the clone confirmed; add genotype or orthogonal function/protein data |
| Independent confirmed clones for strong biology claims | 1 | 2-3 | 5 | 1 clone only: treat causality as provisional until an additional clone, guide, or rescue result is available |
| Days allowed for long-lived protein washout | 3 | 7-14 | 21 | <3 days: protein persistence may confound interpretation; >21 days: re-check genotype and culture drift before waiting longer |

---

## 7. QC GATES

### QC Gate 1: Before Reagent Ordering

PASS criteria (ALL must be true):
  - Target gene, species, and relevant transcript are confirmed
  - At least 2 candidate sgRNAs have been selected
  - Target exon is shared across the intended functional isoforms
  - Validation strategy is defined in advance

ACTION if FAIL: Revisit transcript selection and guide ranking before ordering reagents or cloning constructs. See Section 6 Guide Design parameter table for minimum and optimal sgRNA counts.

---

### QC Gate 2: Before Editing Run

PASS criteria (ALL must be true):
  - Cells are healthy and mycoplasma-negative: viability >=85% and in log-phase growth (see Section 6 Cell State parameter table)
  - Delivery platform and controls are finalized
  - Reagent identities and amounts are documented
  - Enrichment strategy and backup plan are defined

ACTION if FAIL: Delay the run. Do not spend CRISPR reagents on a poorly prepared edit day.

---

### QC Gate 3: After Pool Recovery

PASS criteria (ALL must be true):
  - Viability at 48-96 h after delivery is >=70% for routinely cultured immortalized lines or >=60% for primary or fragile cells
  - Cells have resumed active growth or proliferation compared to mock-treated control
  - A pooled editing readout is scheduled at 72-120 h post-delivery or has been completed
  - A backup aliquot of the edited pool is banked if the project continues

ACTION if FAIL: Optimize delivery or guide design before proceeding to cloning or phenotype work.

---

### QC Gate 4: Before Single-Cell Cloning

PASS criteria (ALL must be true):
  - Bulk editing efficiency justifies cloning
  - Recovery conditions for single-cell growth are ready
  - Clone tracking schema and plate maps are prepared
  - At least 24 clones are planned for routine diploid targets, or at least 48 for aneuploid or amplified loci (see Section 6 parameter table)

ACTION if FAIL: Keep the project at the pooled stage until editing strength or clone support improves.

---

### QC Gate 5: Clone Confirmation

PASS criteria (ALL must be true):
  - Candidate clone genotype is resolved at the target locus
  - All functional alleles are classified
  - An orthogonal assay supports loss of function
  - Backup vials exist for confirmed candidates

ACTION if FAIL: Mark the clone as provisional or rejected; do not label it as a confirmed knockout.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified bottleneck, root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in the interpretation based on available evidence |
| recommended_actions | list[string] | Ordered next actions; redesign or mitigation first |
| risk_flags | list[{risk_id, severity, message}] | Active warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass/fail status for each QC gate |
| guide_status | enum: pass / redesign / high_off_target_risk | Overall assessment of sgRNA quality |
| pool_status | enum: strong / borderline / weak / failed | Suitability of the edited pool for the next stage |
| clone_status | enum: confirmed / provisional / partial / rejected | Final designation for each screened clone |
| validation_gaps | list[string] | Missing evidence required before claiming knockout success |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | User needs routine mammalian cell maintenance, thawing, passaging, or recovery support before or after editing |
| transfection_v1 | User specifically needs non-viral nucleic acid delivery optimization outside the knockout decision framework |
| lentiviral_transduction_v1 | User needs viral packaging, titering, or transduction workflow support |
| flow_cytometry_v1 | User needs FACS enrichment, single-cell sorting, or protein-level validation by flow |
| western_blot_v1 | User needs protein-level knockout confirmation by immunoblot |
| rt_qpcr_v1 | User needs transcript-level validation or nonsense-mediated decay assessment |
| amplicon_sequencing_v1 | User needs high-resolution indel quantification by NGS |
| knockin_hdr_v1 | User requests precise insertion or HDR-mediated editing - REDIRECT immediately; this skill does not apply |
| base_editing_v1 | User requests nucleotide conversion without DSBs - REDIRECT immediately; this skill does not apply |

---
