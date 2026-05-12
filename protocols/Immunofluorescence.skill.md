---
skill_id: immunofluorescence_v1
skill_name: Immunofluorescence Complete Workflow Skill
version: 1.0
method_family: microscopy
tags: [immunofluorescence, fluorescence_microscopy, fixation, permeabilization, blocking, primary_antibody, secondary_antibody, cytospin, coverslips, chamber_slides, mounting, image_acquisition, background_reduction]
applies_to: [adherent_cells, suspension_cells_cytospin, cryosection, paraffin_section, glass_coverslips, chamber_slides]
does_not_apply_to: [flow_cytometry_only, live_cell_super_resolution, electron_microscopy, tissue_clearing]
risk_level: medium
bsl_level: "BSL-2 for human-derived material unless institutional assessment permits lower containment"
last_updated: 2026-03-15
source_protocol: SOP-IF-001
---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I stain cells for immunofluorescence," "my IF signal is weak," "why is my background high," "how do I fix cells on coverslips," "what permeabilization should I use," "how long should I block," "my secondary antibody is nonspecific," "how do I mount slides," "how do I image DAPI and Alexa Fluor dyes," "my cells washed off during staining," "how do I stain suspension cells by cytospin," "how do I store stained slides," or any question about fixed-cell immunofluorescence workflow design, execution, QC, and troubleshooting. This skill covers the complete fixed-sample immunofluorescence workflow: workspace and reagent setup, coverslip or chamber-slide preparation, fixation selection, permeabilization and blocking, primary antibody incubation, secondary antibody and counterstain incubation, mounting, imaging, control design, and structured diagnostic rules for major failure modes including low signal, high background, spectral bleed-through, photobleaching, cell loss, fixation artifacts, and antibody mismatch. This skill does NOT cover: live-cell imaging with genetically encoded fluorescent proteins, tissue clearing, electron microscopy, flow cytometry staining panels, spatial omics workflows, or ultrastructure-preserving fixation for transmission EM. Redirect those queries to the matching skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| sample_type | enum: adherent_cells / suspension_cells_cytospin / cryosection / paraffin_section | Physical sample format that determines adhesion, fixation, and wash handling |
| target_protein | string | Protein or epitope of interest |
| host_species_primary | enum: rabbit / mouse / goat / rat / chicken / human / other | Host species of the primary antibody |
| fluorophore_channels | list[string] | Requested imaging channels (for example DAPI, FITC, Alexa Fluor 488, Alexa Fluor 594, Alexa Fluor 647) |
| workflow_goal | enum: localization / colocalization / expression_comparison / morphology / organelle_marker / troubleshooting | Primary analytical purpose |
| sample_substrate | enum: glass_coverslip / chamber_slide / glass_slide / cytospin_slide | Surface supporting the sample during staining and imaging |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| cell_density_percent | int (0-100) | Surface coverage at fixation time for adherent samples |
| fixation_method | enum: 4pct_pfa / methanol / acetone / paraformaldehyde_glutaraldehyde_mix / unknown | Fixative used |
| antigen_retrieval_method | enum: none / citrate_pH6 / tris_edta_pH9 / enzyme_retrieval / unknown | Retrieval chemistry for paraffin sections |
| antigen_retrieval_time | string | Time and temperature used for HIER or enzyme retrieval |
| fixation_time | string | Time at the stated fixation temperature |
| permeabilization_reagent | enum: triton_x100 / saponin / tween20 / none / unknown | Reagent used for membrane permeabilization |
| blocking_buffer | string | Blocking formulation, including protein and detergent concentrations |
| primary_antibody_dilution | string | Primary dilution, for example 1:100 or 2 µg/mL |
| primary_incubation | string | Incubation temperature and duration for the primary antibody |
| secondary_antibody_dilution | string | Secondary dilution, for example 1:500 |
| wash_count | int | Number of wash cycles between steps |
| wash_volume | string | Volume per wash in µL or mL |
| mounting_medium | string | Antifade medium used |
| microscope_type | enum: widefield / confocal / spinning_disk / epifluorescence / unknown | Imaging platform |
| exposure_ms | dict | Exposure time per channel in ms |
| laser_percent | dict | Laser power per channel if confocal or spinning-disk was used |
| negative_control_status | enum: included / omitted / unknown | Whether no-primary or isotype controls were processed |
| signal_problem | enum: low_signal / high_background / no_signal / bleed_through / photobleaching / morphology_loss / cell_loss | Main observed failure mode |

---

## 3. WORKFLOW MODULES

### Module 1: WORKSPACE_AND_REAGENT_SETUP

**Preconditions:** Samples are labeled with sample ID, date, and target. PBS, fixation reagents, blocking buffer, wash buffer, antibodies, and mounting medium are available. Light-protective storage box or aluminum foil is available for fluorophore-conjugated reagents. If handling human-derived material, containment and PPE match institutional biosafety requirements.
**Pause point:** YES - antibody master mixes can be prepared, labeled, and held on ice for up to 30 min before application. Do not hold diluted antibodies longer than 4 h before use.

#### Steps:

1. Clean the bench with 70% ethanol and place absorbent pads under the staining area.
2. Prepare PBS, PBS + 0.05% Tween-20, or TBS-based wash buffer according to the antibody datasheet. For one 12 mm coverslip in a 24-well plate, use 300 µL per wash. For one well of an 8-well chamber slide, use 200 µL per wash. For one glass microscope slide in a humidified chamber, use 80-120 µL reagent under a Parafilm cover.
3. Pre-label tubes for fixative, blocking buffer, primary antibody mix, secondary antibody mix, and counterstain.
4. [CRITICAL] Protect all fluorophore-conjugated antibodies, phalloidin conjugates, and nuclear dyes from light immediately after thawing or dilution.
5. Thaw aliquots on ice. Mix by inversion 10 times or by pipetting 5 times with a wide-bore tip if viscous protein blockers are used.
6. Prepare a humidified incubation chamber using a sealed box lined with water-moistened paper towels. Add 10 mL sterile water to maintain chamber humidity during antibody incubations of 1 h to overnight.
7. [CRITICAL] Verify species compatibility before starting:
   - Primary host species must differ from the sample species if endogenous immunoglobulin background is a concern.
   - Secondary antibody must recognize the primary host species and match the intended fluorophore channel.
   - Multiple primary antibodies from the same host require directly labeled primaries, sequential staining validation, or subclass-specific secondaries.
8. Prepare fixative fresh when needed:
   - 4% paraformaldehyde in PBS: prepare and aliquot inside a chemical fume hood, then bring the working aliquot to 4°C or 20-25°C according to the validated fixation plan before use.
   - Methanol: pre-chill to -20°C for 30 min before use.
   - Acetone: pre-chill to -20°C for 30 min before use.
9. [CRITICAL] Handle paraformaldehyde, methanol, and acetone in a chemical fume hood. Formaldehyde is a carcinogenic aldehyde, and methanol plus acetone are flammable toxic solvents; keep all three away from ignition sources and cap containers immediately after dispensing.
10. [DO NOT] Use expired mounting medium, antibody aliquots with repeated freeze-thaw cycles above 3 cycles, or wash buffer with visible precipitate.

#### Exit Criteria (must ALL be true to proceed):
- Reagents are labeled and organized by step
- Light-sensitive reagents are protected from light
- Wash volumes are matched to substrate format
- Primary and secondary species compatibility has been verified
- Fixative is at the required temperature for the selected protocol

---

### Module 2: SUBSTRATE_PREPARATION_AND_SAMPLE_ATTACHMENT

**Preconditions:** Cells or sections are available. If staining adherent cultured cells, the culture is healthy and at the planned density. Coating reagent is available if the sample type requires attachment enhancement.
**Pause point:** YES - coated coverslips can be stored at 20-25°C in a dust-free box for 7 days. Seeded adherent cells can be fixed after 18-24 h of attachment. Cytospin slides can be air-dried for 10 min and fixed immediately.

#### Steps:

1. For 12 mm glass coverslips, place one sterile coverslip per well of a 24-well plate using sterile forceps.
2. Select substrate coating if required:
   - Poly-L-lysine for suspension cells or weakly adherent lines: add 300 µL of 0.01% solution per 12 mm coverslip, incubate at 20-25°C for 20 min, aspirate, rinse once with 500 µL sterile water, air-dry for 30 min.
   - Collagen I for fibroblast-like or primary epithelial cells: add 300 µL of 50 µg/mL solution, incubate at 37°C for 1 h, aspirate, rinse once with 500 µL PBS.
   - Laminin for neuronal or epithelial polarity studies: add 300 µL of 10 µg/mL solution, incubate at 37°C for 2 h, aspirate immediately before seeding.
3. Seed adherent cells at a density that will reach 50-70% coverage at fixation:
   - 24-well plate with 12 mm coverslip: 3 × 10^4 to 8 × 10^4 cells in 500 µL medium per well for rapidly dividing immortalized lines such as HEK293T or HeLa.
   - 8-well chamber slide: 1 × 10^4 to 3 × 10^4 cells in 250 µL medium per well.
4. For suspension cells by cytospin:
   - Prepare 1 × 10^5 cells in 100 µL PBS with 1% BSA per slide spot.
   - Load sample into cytospin funnels and centrifuge at 400-800 rpm (targeting 20-80 ×g), 20-25°C, 5 min. Verify the exact rpm-to-×g conversion and acceptable range for the instrument model and cell type before routine use.
   - Air-dry the slide for 10 min before fixation.
5. [CRITICAL] For colocalization studies, avoid overconfluence. Fix adherent cells at 50-70% coverage so single-cell outlines remain resolvable.
6. [BEGINNER TRAP] Do not allow coverslips to dry after cells have attached and before fixation. Drying for even 1-2 min causes edge artifacts and membrane collapse.
7. Inspect the sample under phase contrast or brightfield before fixation:
   - Cells should show expected morphology.
   - No obvious contamination or widespread detachment.
   - Cell density should support single-cell segmentation if quantitative imaging is planned.

#### Exit Criteria (must ALL be true to proceed):
- Substrate coating matches sample attachment needs
- Cell density at fixation target is defined
- Cytospin parameters were recorded if suspension cells were used
- Samples show intact morphology before fixation
- No drying event occurred before fixation

---

### Module 3: FIXATION

**Preconditions:** The selected fixation chemistry matches the target epitope and cellular structure. Wash buffer is ready. Samples have reached the target density or section preparation is complete.
**Pause point:** YES - fixed samples can be held in PBS at 4°C for 24 h before permeabilization if sealed and protected from evaporation. Methanol-fixed slides can be held at -20°C for 7 days in a sealed slide box with desiccant.

#### Steps:

1. Remove culture medium completely without touching the cell layer.
2. Rinse once using a temperature matched to the fixation chemistry:
   - For 4% paraformaldehyde fixation: rinse once with PBS at 20-25°C. Use 500 µL per 24-well coverslip, 200 µL per chamber-slide well, or 40 mL in a Coplin jar for glass slide sections for 2 min.
   - For methanol or acetone fixation: rinse once with ice-cold PBS to pre-equilibrate the sample temperature before applying the chilled solvent. Use 500 µL per 24-well coverslip, 200 µL per chamber-slide well, or 40 mL in a Coplin jar for glass slide sections for 2 min.
3. Select fixation method:
   - 4% paraformaldehyde in PBS: add 300 µL per 24-well coverslip or 200 µL per chamber-slide well; incubate at 4°C for 15 min as the default starting condition for morphology-preserving IF. No active rocking is required at 4°C; ensure the fixative covers the sample surface evenly by tilting the plate once immediately after addition. A 20-25°C for 10 min fixation may be used only when that condition has been validated for the specific target and sample.
   - Ice-cold methanol: add 300 µL per coverslip or immerse slide in 40 mL methanol; incubate at -20°C for 10 min. Use for beta-tubulin, gamma-tubulin, centrin, and phospho-epitopes where aldehyde crosslinking masks the epitope. Do not use for lipid droplets, ER membrane components, or targets that require intact lipid bilayers, because methanol dissolves membrane lipids.
   - Ice-cold acetone: immerse slide in 40 mL acetone; incubate at -20°C for 5 min. Use only when the antibody datasheet supports acetone fixation. After fixation, allow solvent to evaporate for 30 s, then rehydrate in PBS for 2 × 5 min before blocking. No aldehyde quench is required because acetone does not generate free aldehydes.
4. For paraffin sections, complete deparaffinization and antigen retrieval before blocking:
   - Bake slides at 60°C for 30 min on a slide warmer to improve section adhesion and soften excess paraffin before deparaffinization. Extend to 1 h for thick sections or reduce to 20 min for Superfrost Plus-mounted sections.
   - Deparaffinize in fresh xylene, 2 changes, 5 min each.
   - Rehydrate through ethanol series: 100% for 2 min twice, 95% for 2 min, 70% for 2 min, then rinse in distilled water for 2 min.
   - Perform HIER in either 10 mM citrate buffer pH 6.0 or Tris-EDTA buffer pH 9.0, 95-99°C, 15-20 min, according to the validated target requirement.
   - Cool slides in retrieval buffer at 20-25°C for 20 min, then rinse in PBS before proceeding.
5. [CRITICAL] Record the exact fixation chemistry, temperature, and time. These variables are a major source of signal loss or epitope masking.
6. For paraformaldehyde-fixed samples, quench residual aldehydes:
   - Add 300 µL of 50-100 mM NH4Cl in PBS per coverslip or 200 µL per chamber-slide well.
   - Incubate at 20-25°C for 10-15 min.
   - Alternatively, use 0.1 M glycine in PBS for 10 min when glycine quenching is preferred for the validated workflow.
7. Wash fixed samples 3 times with PBS:
   - 500 µL per wash in 24-well plates.
   - 200 µL per wash in 8-well chamber slides.
   - 40 mL per wash for Coplin jars.
   - Incubate 3 min per wash at 20-25°C.
8. [DO NOT] Exceed paraformaldehyde fixation for 20 min unless a validated antigen retrieval plan is in place. Longer aldehyde exposure can reduce antibody access.
9. [VISUAL CHECK] After fixation or retrieval, the cell layer or section should remain attached with preserved boundaries and minimal floating debris.

#### Exit Criteria (must ALL be true to proceed):
- Fixation chemistry, temperature, and duration were recorded
- Residual aldehydes were quenched when paraformaldehyde was used
- Samples remained attached through post-fixation washes
- No obvious fixation precipitate is present on the sample

---

### Module 4: PERMEABILIZATION_AND_BLOCKING

**Preconditions:** Fixed samples are washed and intact. The target localization is known or estimated so membrane permeabilization strength can be chosen.
**Pause point:** YES - blocked samples can be held at 4°C for 12 h in blocking buffer if sealed and protected from evaporation. Do not leave blocked samples at 20-25°C for more than 2 h before primary incubation.

#### Steps:

1. Select permeabilization strength based on the target:
   - Triton X-100 0.1% in PBS: 300 µL per coverslip or 200 µL per chamber-slide well; incubate at 20-25°C for 10 min. Use for soluble cytoplasmic and nuclear proteins. Avoid for membrane-integrated proteins or loosely anchored cytoskeletal proteins that may be extracted at 0.1%.
   - Saponin 0.05% in PBS: 300 µL per coverslip or 200 µL per chamber-slide well; incubate at 20-25°C for 10 min. Use when plasma membrane preservation matters.
   - Tween-20 0.05-0.1% in PBS: 300 µL per coverslip or 200 µL per chamber-slide well; incubate at 20-25°C for 5-10 min. Use when a milder membrane access condition is needed for nuclear antigens or when Triton X-100 causes extraction artifacts.
   - No permeabilization: for extracellular epitopes or surface proteins only.
2. Wash 3 times with PBS, 3 min each, using the same wash volumes as Module 3.
3. If background remains elevated after 3 PBS-only washes, switch subsequent washes to PBS + 0.05% Tween-20, or use detergent-containing wash buffer when the antibody datasheet recommends detergent wash.
4. Prepare blocking buffer:
   - 3% BSA in PBS for rabbit or mouse primaries that do not require serum-based blocking.
   - 5% normal donkey serum + 1% BSA in PBS when donkey secondaries will be used.
5. Apply blocking buffer:
   - 300 µL per coverslip in 24-well plate.
   - 200 µL per chamber-slide well.
   - 100 µL under Parafilm for slide sections in a humidified chamber.
6. Incubate at 20-25°C for 30-60 min; use 30 min for routine adherent cells and 45-60 min for cryosections, paraffin sections, or samples prone to high background.
7. [CRITICAL] If endogenous Fc receptor background is expected, add Fc block according to the sample type:
   - Human or mouse immune cells on slides: 5 µg/mL Fc receptor blocking reagent in blocking buffer, 20-25°C, 15 min before primary antibody.
8. [BEGINNER TRAP] Do not use serum from the same species as the primary antibody host in the blocking buffer if species-specific background is already problematic. Match the serum to the secondary antibody host instead.
9. Remove blocking buffer immediately before primary antibody addition. Do not wash unless the antibody datasheet instructs otherwise.

#### Exit Criteria (must ALL be true to proceed):
- Permeabilization strength matches target localization
- Blocking formulation matches the secondary antibody strategy
- Blocking duration and temperature were recorded
- Fc block was applied and recorded when the sample contains cells with Fc receptors (macrophages, dendritic cells, B cells, NK cells)
- Samples remain fully covered with liquid at all times

---

### Module 5: PRIMARY_ANTIBODY_INCUBATION

**Preconditions:** Blocking is complete. Validated primary antibody concentration range is available from datasheet, publication, or pilot titration. Humidified chamber is prepared for long incubations.
**Pause point:** YES - primary incubation can be performed at 4°C overnight for 12-18 h when increased sensitivity is needed. Do not exceed 20 h at 4°C without validation.

#### Steps:

1. Prepare the primary antibody in blocking buffer:
   - For antibodies supplied in buffer without carrier protein: start at 1-5 µg/mL.
   - For antibodies supplied with BSA or glycerol as stabilizer: 1:200 to 1:500 is a reasonable starting range only when the stock concentration is 0.8-1.2 mg/mL.
   - For stock concentrations outside 0.8-1.2 mg/mL, calculate the target µg/mL and adjust the dilution ratio accordingly. Confirm the starting condition with the datasheet and run a 3-point titration on first use.
2. Example setup for one 12 mm coverslip:
   - 100 µL primary antibody mix placed on Parafilm in a humidified chamber, invert coverslip cell-side down.
   - Alternative in-well method: 200 µL per chamber-slide well or 200-300 µL per coverslip in the plate.
3. Include controls in the same run:
   - No-primary control using blocking buffer only.
   - Known positive sample for the target when available.
   - Known negative sample or knockout control when available.
4. Incubate using one validated option:
   - 20-25°C for 1 h for abundant targets with validated room-temperature staining.
   - 4°C for 12-18 h for low-abundance targets or when higher signal-to-background is required.
5. [CRITICAL] For multiplex staining, check host species and fluorophore plan before loading:
   - Rabbit primary + donkey anti-rabbit Alexa Fluor 488.
   - Mouse primary + donkey anti-mouse Alexa Fluor 594.
   - Chicken primary + donkey anti-chicken Alexa Fluor 647.
6. [DO NOT] Allow the antibody droplet to shrink from evaporation. Refill chamber humidity if incubation exceeds 4 h.
7. Wash 3 times after primary incubation:
   - 500 µL per wash for coverslips in 24-well plates.
   - 200 µL per wash for chamber-slide wells.
   - 40 mL per wash for slide jars.
   - Incubate 5 min per wash at 20-25°C with slow orbital rocking if available.
8. [VISUAL CHECK] After the third wash, the sample should remain attached with no visible precipitated antibody crystals.

#### Exit Criteria (must ALL be true to proceed):
- Primary dilution or concentration was recorded
- Primary incubation temperature and duration were recorded
- At least one negative control was included
- Wash count and wash duration after primary incubation were completed
- Samples remained hydrated and attached during incubation

---

### Module 6: SECONDARY_ANTIBODY_AND_COUNTERSTAIN

**Preconditions:** Primary antibody incubation and washes are complete. Secondary antibodies are cross-adsorbed for the planned species combination. Counterstains are compatible with selected channels.
**Pause point:** YES - after secondary incubation and washes, samples can be held in PBS at 4°C for up to 12 h in the dark before mounting. Nuclear dyes can be added either during the secondary step or in a separate 5 min step.

#### Steps:

1. Prepare secondary antibody in blocking buffer:
   - Dilution range: 1:300 (most concentrated, use only when signal is below interpretable threshold after optimization at 1:500) to 1:1000 (most dilute, use when background needs reduction).
   - Default starting dilution for cross-adsorbed secondaries in initial optimization: 1:500.
2. Add optional counterstains in the same incubation when compatible:
   - DAPI: 300 nM final concentration.
   - Hoechst 33342: 1 µg/mL.
   - Phalloidin conjugate: 1:100 to 1:200, only if actin staining is required.
3. Apply 100 µL per coverslip in a humidified chamber, 200 µL per chamber-slide well, or 100 µL under Parafilm on sections.
4. Incubate at 20-25°C for 45 min in the dark.
5. Wash 3 times with PBS or PBS + 0.05% Tween-20:
   - 500 µL per wash for coverslips.
   - 200 µL per wash for chamber-slide wells.
   - 40 mL per wash for slide jars.
   - Incubate 5 min per wash at 20-25°C in the dark.
6. If nuclear stain was not included with the secondary, add DAPI or Hoechst in PBS for 5 min at 20-25°C, then wash 2 times with PBS for 3 min each.
7. [CRITICAL] Use one fluorophore per channel with clear spectral spacing:
   - DAPI with Alexa Fluor 488 and Alexa Fluor 594 is a well-separated 3-color set suitable for widefield and confocal systems with DAPI, FITC/GFP, and TRITC/mCherry filter sets or laser lines.
   - Add Alexa Fluor 647 for a 4-color set when the microscope supports far-red detection.
8. [DO NOT] Pair FITC and Alexa Fluor 488 in the same experiment. Their spectra overlap too strongly for clean separation on widefield systems with conventional FITC/GFP filter sets.
9. [BEGINNER TRAP] Secondary antibody incubation longer than 90 min at 20-25°C often raises background without increasing usable signal.

#### Exit Criteria (must ALL be true to proceed):
- Secondary antibody species and fluorophore match the primary plan
- Counterstain concentration and incubation time were recorded
- Post-secondary washes were completed in the dark
- Channel plan supports optical separation

---

### Module 7: MOUNTING_AND_COVERSLIP_HANDLING

**Preconditions:** Final washes are complete and samples are free of unbound fluorophore. Mounting medium and labeled slides are ready.
**Pause point:** YES - mounted slides can cure horizontally in the dark at 20-25°C for 30 min before imaging. For hard-setting media, full cure may require 12-24 h at 20-25°C.

#### Steps:

1. Label each glass slide with sample ID, target, date, and fluorophore set.
2. Select the mounting medium according to imaging and storage needs:
   - Hard-setting antifade medium: use for archival storage, shipment, or re-imaging over multiple days.
   - Glycerol-based antifade medium: use for same-day to 72 h imaging when a non-hardening mount is preferred.
   - For oil-immersion objectives (60× or 100×, NA ≥1.3): use a hard-setting medium with refractive index 1.47-1.52.
   - For water-immersion objectives: a glycerol-based or aqueous medium with refractive index 1.33-1.45 is preferred.
   - Check the objective barrel marking for the recommended immersion and mounting-medium range.
3. Remove the final wash with a substrate-specific method:
   - Coverslips in wells: aspirate from the wall, leave a thin liquid film, then lift the coverslip with forceps immediately before mounting.
   - Chamber slides: aspirate from the chamber edge without touching the sample, then proceed directly to mounting medium application.
   - Glass slide sections: drain the slide vertically on lint-free tissue for 2-3 s without allowing the section to dry.
4. Mount coverslips:
   - Place 8-12 µL antifade mounting medium on the slide for one 12 mm coverslip.
   - Lift the coverslip with fine forceps and lower cell-side down onto the mounting medium at an angle to reduce bubble formation.
5. For chamber slides with removable gaskets:
   - Remove chamber walls according to manufacturer instructions.
   - Add 10-20 µL mounting medium per well footprint.
   - Apply a coverslip slowly from one edge to the other.
6. Remove excess medium at the slide edges with a lint-free wipe. Do not press on the coverslip center.
7. Seal the coverslip edge with clear nail polish if the slide will be stored longer than 24 h.
8. Cure mounted slides flat in the dark:
   - 20-25°C for 30 min before immediate imaging.
   - 20-25°C for 12-24 h for full hard-set curing when required.
9. Store finished slides at 4°C in a light-protective slide box with desiccant.

#### Exit Criteria (must ALL be true to proceed):
- Slides are labeled and mounted without visible bubbles over the region of interest
- Mounting medium volume matches coverslip size
- Coverslip edges are sealed if storage will exceed 24 h
- Slides are protected from light during curing and storage

---

### Module 8: IMAGE_ACQUISITION_AND_DATA_QC

**Preconditions:** Slides are mounted and cured enough for imaging. Microscope alignment, objective cleanliness, and filter or laser setup have been checked. Acquisition settings can be recorded per channel.
**Pause point:** YES - mounted slides stored at 4°C in the dark can be imaged for 1-2 weeks with antifade media validated for the fluorophore set, but signal loss should be expected for unstable fluorophores after 7 days.

#### Steps:

1. Turn on the microscope in the correct sequence and allow illumination to stabilize:
   - LED or lamp-based widefield: warm for 10 min.
   - Laser-based confocal: warm for 20 min.
2. Clean the objective lens with lens paper and objective-safe solvent if residue is visible.
3. Focus using transmitted light or the dimmest fluorescence channel first to reduce bleaching.
4. Set acquisition parameters using the negative control and a representative positive sample:
   - Widefield exposure: begin at 20-200 ms for DAPI and 100-500 ms for Alexa Fluor channels.
   - Confocal laser power: begin at 0.5-5% with gain adjusted to avoid saturated pixels.
5. [CRITICAL] Keep acquisition settings identical across samples that will be quantitatively compared within one experiment.
6. Capture single-channel images first when bleed-through is suspected. Use sequential scanning for confocal multiplex experiments with overlapping spectra.
7. Record metadata for every image set:
   - Objective magnification and NA.
   - Exposure ms or laser percent.
   - Detector gain or camera gain.
   - Pixel size and z-step if z-stacks are collected.
8. Acquire at least 5 random fields per condition for descriptive studies or at least 10 random fields per condition for quantitative intensity comparisons.
9. [DO NOT] Adjust exposure until the brightest structures saturate. Keep signal below saturation so intensity differences remain interpretable.
10. Save raw images in the microscope native format or as OME-TIFF before any contrast adjustment or annotation.

#### Exit Criteria (must ALL be true to proceed):
- Negative control and positive sample informed acquisition settings
- Identical settings were used for comparable samples
- Raw image files and metadata were saved
- No channel shows extensive saturation in the main region of interest

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: fixation
CONDITION: Target signal is absent or markedly reduced after 4% paraformaldehyde fixation, but the same antibody has worked in other experiments
DIAGNOSIS: Epitope masking by aldehyde fixation
CONFIDENCE: medium
LIKELY_CAUSES:
  - Paraformaldehyde crosslinking masked the target epitope
  - Fixation time exceeded 15-20 min at 20-25°C
  - Aldehyde quenching step was omitted
DISTINGUISH:
  - Compare with a methanol-fixed pilot slide if the datasheet supports solvent fixation
  - Check whether morphology is preserved but signal is lost; that pattern supports masking rather than sample loss
  - Verify whether known positive control tissue or cells stained in the same run
IMMEDIATE_FIX:
  - Repeat with 4% paraformaldehyde at 4°C for 15 min and add a 50-100 mM NH4Cl quench for 10-15 min
  - Alternatively, use 0.1 M glycine in PBS for 10 min as the quench reagent if that option is validated for the assay
  - If validated for the antibody, test methanol fixation at -20°C for 10 min
  - Increase primary incubation to 4°C for 12-18 h after fixation conditions are corrected
PREVENTION: Validate fixation chemistry for each target; record fixation time precisely; use a positive control in each new staining setup

---

### RULE DX-002
STAGE: permeabilization
CONDITION: Membrane-associated structures look fragmented or washed out after Triton X-100 treatment
DIAGNOSIS: Over-permeabilization causing extraction of target-associated structures
CONFIDENCE: high
LIKELY_CAUSES:
  - Triton X-100 concentration was too high for the target
  - Permeabilization time exceeded 10 min at 20-25°C
  - Target is membrane-proximal and was solubilized
DISTINGUISH:
  - Cytosolic markers may remain visible while membrane patterns disappear
  - A saponin-based repeat often preserves membrane-associated epitopes better
  - Cell outlines may appear intact even though specific membranes have lost signal
IMMEDIATE_FIX:
  - Reduce Triton X-100 to 0.05-0.1% for 5 min at 20-25°C
  - Test saponin 0.05% for 10 min at 20-25°C
  - For surface epitopes, omit permeabilization entirely
PREVENTION: Match permeabilization strength to target localization; pilot-test one strong and one mild condition for new antibodies

---

### RULE DX-003
STAGE: secondary_antibody
CONDITION: Strong diffuse fluorescence appears in all samples including the no-primary control
DIAGNOSIS: Secondary antibody-driven nonspecific background
CONFIDENCE: high
LIKELY_CAUSES:
  - Secondary antibody concentration is too high
  - Cross-adsorption is inadequate for the sample species
  - Blocking formulation is mismatched to the secondary strategy
DISTINGUISH:
  - Signal in the no-primary control indicates the primary antibody is not required for the observed pattern
  - Background often appears on nuclei, extracellular matrix, or sample edges when the secondary is the driver
  - Lowering secondary concentration by 2-fold often reduces the signal markedly if this diagnosis is correct
IMMEDIATE_FIX:
  - Reduce the secondary dilution from 1:500 to 1:1000
  - Use highly cross-adsorbed secondary antibodies
  - Block with 5% serum from the secondary host species plus 1% BSA for 30 min at 20-25°C
PREVENTION: Always run a no-primary control for new secondaries; titrate secondary antibodies before multiplex experiments

---

### RULE DX-004
STAGE: primary_antibody
CONDITION: No visible signal is present in experimental samples, but DAPI staining and morphology look intact
DIAGNOSIS: Primary antibody concentration or incubation conditions are inadequate
CONFIDENCE: medium
LIKELY_CAUSES:
  - Primary antibody is too dilute
  - Primary incubation time is too short for a low-abundance target
  - Antibody was degraded by repeated freeze-thaw cycles
DISTINGUISH:
  - Intact DAPI with preserved cells argues against cell loss
  - Positive control failure alongside experimental failure supports reagent or incubation issues
  - If a different lot of the same antibody works, reagent degradation is likely
IMMEDIATE_FIX:
  - Increase primary concentration 2-fold within the datasheet range
  - Shift incubation from 20-25°C for 1 h to 4°C for 12-18 h
  - Use a fresh antibody aliquot with no more than 3 prior freeze-thaw cycles
PREVENTION: Aliquot primaries into single-experiment volumes; document dilution and storage history

---

### RULE DX-005
STAGE: secondary_antibody
CONDITION: Signal appears in the wrong channel or in more than one fluorophore channel for the same structure
DIAGNOSIS: Spectral bleed-through or channel crosstalk
CONFIDENCE: high
LIKELY_CAUSES:
  - Fluorophore spectra overlap too closely
  - Exposure or gain is high enough to spread bright signal into adjacent channels
  - Simultaneous scanning was used on a confocal system with overlapping fluorophores
DISTINGUISH:
  - Single-labeled controls reveal whether one fluorophore is visible in another channel
  - Bleed-through follows bright structures rather than all structures
  - Sequential scanning reduces the artifact if crosstalk is the cause
IMMEDIATE_FIX:
  - Re-image with sequential scanning
  - Reduce exposure ms or laser percent for the brightest channel
  - Replace overlapping fluorophores with a wider-spaced set such as DAPI, Alexa Fluor 488, Alexa Fluor 594, and Alexa Fluor 647
PREVENTION: Build the channel plan before staining; include single-labeled controls for multiplex assays

---

### RULE DX-006
STAGE: mounting_and_imaging
CONDITION: Fluorescence fades rapidly during acquisition, especially after the first field
DIAGNOSIS: Photobleaching during image acquisition
CONFIDENCE: high
LIKELY_CAUSES:
  - Exposure ms or laser percent is too high
  - Slides remained uncovered from light-protective storage for too long
  - Antifade mounting medium is missing or expired
DISTINGUISH:
  - The first image field is brighter than later fields from the same slide
  - Repeated imaging of one area causes progressive intensity loss
  - DAPI often persists better than green or red channels when bleaching is the cause
IMMEDIATE_FIX:
  - Reduce exposure by 25-50% or reduce laser percent to the lowest level that preserves usable signal
  - Use antifade mounting medium and image within 24-72 h after mounting
  - Focus in transmitted light or a dimmer channel before opening the target channel shutter
PREVENTION: Protect slides from light at every post-secondary step; capture the least stable fluorophores first

---

### RULE DX-007
STAGE: washing
CONDITION: Cells or sections detach during washes, leaving patchy empty regions
DIAGNOSIS: Sample loss from inadequate attachment or overly forceful liquid handling
CONFIDENCE: high
LIKELY_CAUSES:
  - Coverslips were not coated for weakly adherent samples
  - Pipette stream hit the sample directly during aspiration or dispensing
  - Fixation was incomplete before repeated washes
DISTINGUISH:
  - Empty areas often begin at the edge where liquid was dispensed
  - DAPI signal disappears together with the target signal in detached regions
  - Cytospin samples are especially vulnerable if fixation is delayed
IMMEDIATE_FIX:
  - Use poly-L-lysine coating for weakly adherent or cytospin samples
  - Dispense and aspirate against the well wall rather than onto the sample
  - Verify fixation time and repeat with 4% paraformaldehyde at 4°C for 15 min, or use 20-25°C for 10 min only when that condition has already been validated for the target
PREVENTION: Match coating to sample type; keep all washes slow and wall-directed; avoid drying between steps

---

### RULE DX-008
STAGE: blocking
CONDITION: Punctate or diffuse background is high across the cytoplasm and around nuclei even though the target is visible
DIAGNOSIS: Blocking and wash stringency are inadequate
CONFIDENCE: medium
LIKELY_CAUSES:
  - Blocking protein concentration is too low
  - Wash count or wash duration is too low
  - Detergent is absent even though the antibody pair benefits from mild wash stringency
DISTINGUISH:
  - The signal-to-background ratio improves when wash count rises from 3 to 5
  - No-primary control may stay dark while experimental slides still show diffuse haze, pointing to incomplete removal of bound primary-secondary complexes
  - Background that clusters around nuclei often responds to longer blocking or detergent-containing washes
IMMEDIATE_FIX:
  - Increase blocking to 5% serum plus 1% BSA for 30-60 min at 20-25°C
  - Increase washes to 5 cycles, 5 min each, with PBS + 0.05% Tween-20
  - Reduce both primary and secondary concentrations by 2-fold in a pilot titration
PREVENTION: Optimize one variable at a time; record wash duration rather than wash count alone

---

### RULE DX-009
STAGE: fixation
CONDITION: Cell morphology is shrunken, rounded, or collapsed after fixation
DIAGNOSIS: Fixation artifact from osmotic or solvent stress
CONFIDENCE: medium
LIKELY_CAUSES:
  - Methanol or acetone fixation is too harsh for the sample
  - PBS rinse temperature and fixative temperature were mismatched
  - Samples were partially dried before fixation
DISTINGUISH:
  - Cytoskeletal collapse with preserved slide attachment often points to fixation chemistry rather than wash loss
  - Edge-dominant collapse suggests drying before fixative coverage
  - Repeating with paraformaldehyde often restores morphology if solvent fixation caused the defect
IMMEDIATE_FIX:
  - Repeat using 4% paraformaldehyde at 4°C for 15 min as the first recovery condition
  - Pre-rinse with PBS at the same temperature as the fixative plan
  - Move samples from medium to fixative without any uncovered interval
PREVENTION: Keep the sample continuously covered; choose solvent fixation only when the antibody has been validated for it

---

### RULE DX-010
STAGE: imaging
CONDITION: Bright puncta or crystals appear on the slide that do not match cellular structures
DIAGNOSIS: Precipitated antibody or dried reagent artifact
CONFIDENCE: high
LIKELY_CAUSES:
  - Antibody solution precipitated during incubation
  - Reagent droplet partially dried in the humidified chamber
  - Mounting medium crystallized from old or contaminated stock
DISTINGUISH:
  - Artifacts often sit above the focal plane of the cells
  - The same puncta may be visible in more than one fluorescence channel
  - Freshly prepared filtered antibody mix removes the pattern if precipitation is the cause
IMMEDIATE_FIX:
  - Centrifuge antibody mix at 10,000 ×g, 4°C, 5 min before application
  - Filter the blocking buffer or antibody diluent through a 0.22 µm filter if precipitate is recurrent
  - Maintain chamber humidity and replace old mounting medium
PREVENTION: Spin antibody mixes before use when cloudiness is visible; do not allow small droplets to evaporate during long incubations

---

### RULE DX-011
STAGE: control_design
CONDITION: Experimental slides show a convincing pattern, but there is no matched negative control or positive control in the run
DIAGNOSIS: Interpretability failure due to missing controls
CONFIDENCE: high
LIKELY_CAUSES:
  - No-primary control was omitted
  - Positive control sample was not included
  - New antibody lot was used without validation controls
DISTINGUISH:
  - Strong-looking signal can still be nonspecific when controls are absent
  - A no-primary control separates primary-driven signal from secondary-driven background
  - A positive control determines whether a true negative sample is biologically negative or technically failed
IMMEDIATE_FIX:
  - Repeat the experiment with a no-primary control and one validated positive control
  - Add knockout or knockdown negative material if available for specificity confirmation
  - Do not interpret localization claims until controls have been reviewed
PREVENTION: Make controls part of the plate map or slide map before starting each staining run

---

### RULE DX-012
STAGE: multiplex_design
CONDITION: Two primary antibodies from the same host species are used with conventional secondary antibodies, producing overlapping or misleading localization
DIAGNOSIS: Host-species collision in multiplex staining
CONFIDENCE: high
LIKELY_CAUSES:
  - Both primaries are rabbit or both are mouse
  - Conventional secondary antibodies bind both primaries
  - Sequential loading was attempted without validated subclass isolation
DISTINGUISH:
  - Both targets appear in both planned channels
  - Single-stain controls for each primary alone reveal cross-labeling
  - Using directly labeled primaries or subclass-specific secondaries resolves the issue if host collision is the cause
IMMEDIATE_FIX:
  - Replace one primary with a different host species version if available
  - Use directly conjugated primary antibodies for one target
  - Use subclass-specific secondaries only when the antibody subclasses are verified and cross-reactivity testing is performed
PREVENTION: Plan host species at the assay-design stage; avoid same-host multiplex designs unless a validated workaround is available

---

### RULE DX-013
STAGE: fixation / imaging
CONDITION: Signal appears in unstained regions or in the no-primary control, often strongest in the green channel, and persists after lowering secondary concentration
DIAGNOSIS: Sample autofluorescence or residual aldehyde autofluorescence
CONFIDENCE: medium
LIKELY_CAUSES:
  - Residual aldehydes remain after paraformaldehyde fixation
  - Endogenous autofluorescent material such as lipofuscin, flavins, collagen, elastin, or dense mitochondrial content is present
  - Exposure settings are too high for the background level of the sample
DISTINGUISH:
  - Autofluorescence remains visible in a no-primary and no-secondary control
  - Signal often appears across multiple channels with similar morphology rather than matching a single target pattern
  - Paraffin sections and highly fixed samples show this pattern more often than lightly fixed cultured cells
IMMEDIATE_FIX:
  - Increase aldehyde quenching to 100 mM NH4Cl for 10-15 min or use 0.1 M glycine for 10 min
  - Add a validated autofluorescence-quenching step such as 0.1% Sudan Black B in 70% ethanol for 5-10 min when the sample type tolerates it
  - Reduce exposure ms or laser percent and image single-channel controls before interpreting target localization
PREVENTION: Include no-primary controls in every run; optimize aldehyde quenching after paraformaldehyde fixation; select fluorophores in red or far-red channels when green-channel autofluorescence is high

---

### RULE DX-014
STAGE: fixation / antigen_retrieval
CONDITION: Paraffin sections show weak or absent staining despite an intact section and a validated antibody
DIAGNOSIS: Antigen retrieval mismatch or incomplete deparaffinization
CONFIDENCE: medium
LIKELY_CAUSES:
  - HIER buffer pH does not match the target requirement
  - Retrieval temperature or time is too low
  - Paraffin was not fully removed before retrieval
DISTINGUISH:
  - A section edge may stain while the center stays weak when deparaffinization is incomplete
  - Switching from citrate pH 6.0 to Tris-EDTA pH 9.0, or the reverse, often changes signal when retrieval mismatch is the main problem
  - Positive control paraffin tissue processed in parallel helps separate antibody failure from retrieval failure
IMMEDIATE_FIX:
  - Repeat deparaffinization with two fresh xylene changes for 5 min each and full ethanol rehydration
  - Compare HIER in 10 mM citrate pH 6.0 versus Tris-EDTA pH 9.0 at 95-99°C for 15-20 min
  - Extend cooling in retrieval buffer to 20 min before PBS transfer to reduce section lifting
PREVENTION: Record retrieval buffer, pH, temperature, and duration for every paraffin run; keep a target-specific retrieval log tied to antibody lot and tissue type

---

## 5. RISK RULES

### Risk Matrix (RM-001 to RM-023) and Critical Findings (CF-001 to CF-003)

#### RISK RM-001
STAGE: fixation
ITEM: Paraformaldehyde exposure during preparation or use
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Fixative prepared and handled in a fume hood or ventilated area; gloves and eye protection worn
MITIGATION: Prepare 4% paraformaldehyde in a chemical hood; treat formaldehyde-containing solutions as carcinogenic chemical hazards; wear nitrile gloves and safety glasses; cap containers immediately after dispensing; collect waste in labeled aldehyde waste bottles

---

#### RISK RM-002
STAGE: substrate_preparation
ITEM: Coverslip breakage causing cuts or sample loss
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Coverslips handled with fine forceps over a padded bench liner; cracked coverslips discarded before use
MITIGATION: Use forceps with aligned tips; handle one coverslip at a time; discard chipped or cracked glass immediately into a sharps container

---

#### RISK RM-003
STAGE: sample_attachment
ITEM: Overconfluent cultures preventing single-cell analysis
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Cell density at fixation is 50-70% for morphology or colocalization studies
MITIGATION: Seed pilot wells 24 h before the main experiment; adjust seeding to 3 × 10^4, 5 × 10^4, or 8 × 10^4 cells per 12 mm coverslip based on growth rate

---

#### RISK RM-004
STAGE: fixation
ITEM: Under-fixation causing antigen redistribution or wash loss
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Fixation time and temperature recorded for every run
MITIGATION: Use 4% paraformaldehyde at 4°C for 15 min as the first test point for fixed-cell assays; reserve 20-25°C for 10 min only for target-validated workflows; verify attachment after the first wash

---

#### RISK RM-005
STAGE: fixation
ITEM: Over-fixation masking epitopes
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Paraformaldehyde exposure does not exceed 20 min unless validated
MITIGATION: Start with 4°C for 15 min for morphology-preserving fixation; if optimization is needed, compare 4°C for 10 min, 4°C for 15 min, and 20-25°C for 10 min only when the target tolerates warmer fixation

---

#### RISK RM-006
STAGE: permeabilization
ITEM: Detergent extraction of membrane or cytoskeletal targets
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Permeabilization reagent matches target localization
MITIGATION: Use saponin 0.05% for membrane-proximal targets; reserve Triton X-100 0.1% for intracellular targets that tolerate stronger extraction

---

#### RISK RM-007
STAGE: blocking
ITEM: High background from mismatched blocking serum
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Blocking serum species matches the secondary antibody host strategy
MITIGATION: Use 5% normal donkey serum with donkey secondaries or 5% normal goat serum with goat secondaries; add 1% BSA when diffuse background persists

---

#### RISK RM-008
STAGE: primary_antibody
ITEM: Primary antibody titration not optimized
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: At least three pilot dilutions tested for a new antibody lot
MITIGATION: Run 1:100, 1:250, and 1:500 in parallel for the first evaluation; keep secondary dilution and acquisition settings constant during titration

---

#### RISK RM-009
STAGE: secondary_antibody
ITEM: Species mismatch between primary and secondary antibodies
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Secondary label explicitly states recognition of the primary host species
MITIGATION: Verify host pairing before dilution; keep a written channel map next to the staining station; label all antibody tubes with host species and fluorophore

---

#### RISK RM-010
STAGE: multiplex_design
ITEM: Same-host primaries causing cross-labeling
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Host species table reviewed before assay setup
MITIGATION: Select different-host primaries whenever possible; if not possible, use directly labeled primaries or validated subclass-specific approaches

---

#### RISK RM-011
STAGE: washing
ITEM: Cell loss from forceful aspiration or dispensing
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Liquid is added and removed from the well wall, not directly onto the sample
MITIGATION: Angle the pipette tip against the wall; leave a thin liquid film during aspiration if the sample detaches easily; use coating for weakly adherent cells

---

#### RISK RM-012
STAGE: secondary_antibody
ITEM: Fluorophore photobleaching during staining
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: All post-secondary steps are performed in low light or with light protection
MITIGATION: Cover plates with foil; keep slides in a dark box; shorten time between final wash and mounting to less than 30 min

---

#### RISK RM-013
STAGE: mounting
ITEM: Bubbles under coverslips obscuring fields of view
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Mounted slide inspected at low magnification before imaging
MITIGATION: Apply 8-12 µL mounting medium per 12 mm coverslip; lower the coverslip at an angle; remount immediately if a bubble crosses the region of interest

---

#### RISK RM-014
STAGE: imaging
ITEM: Saturated pixels causing invalid intensity comparisons
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Histogram or range indicator shows minimal or no saturation in the region of interest
MITIGATION: Reduce exposure ms or laser percent until the brightest structures fall below saturation; use the same settings across compared groups

---

#### RISK RM-015
STAGE: imaging
ITEM: Inconsistent acquisition settings between groups
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Exposure ms, gain, objective, and detector settings recorded identically for all comparison groups
MITIGATION: Set exposure using controls before imaging blinded samples; save configuration presets; do not re-balance individual samples when quantitative comparison is planned

---

#### RISK RM-016
STAGE: control_design
ITEM: Missing no-primary control
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: One sample per staining run receives blocking buffer instead of primary antibody
MITIGATION: Reserve at least one coverslip or one chamber-slide well for the no-primary control in every run; image it with the same settings as the stained samples

---

#### RISK RM-017
STAGE: control_design
ITEM: Missing positive control for a new antibody lot
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: A known positive sample is included whenever a new lot or new fixation condition is tested
MITIGATION: Maintain archived positive-control slides or frozen positive-control cells; run them in parallel with new lots and new fixation conditions

---

#### RISK RM-018
STAGE: storage
ITEM: Signal loss during long slide storage
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Imaging date relative to mounting date is logged
MITIGATION: Image within 7 days when feasible; store at 4°C in the dark with desiccant; seal coverslip edges if storage exceeds 24 h

---

#### RISK RM-019
STAGE: sample_handling
ITEM: Drying artifact between staining steps
PROBABILITY: high
IMPACT: high
SCORE: HIGH
CHECK: Samples remain covered by liquid at every step
MITIGATION: Prepare the next reagent before aspirating the current one; process one plate or one slide rack at a time; refill humidified chamber water if incubation exceeds 4 h

---

#### RISK RM-020
STAGE: data_management
ITEM: Loss of raw image metadata
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Raw native files or OME-TIFF exports are saved before adjustment
MITIGATION: Export raw data immediately after acquisition; store metadata with exposure, gain, objective, and pixel size in the same project folder; back up files to a second location within 24 h

---

#### RISK RM-021
STAGE: fixation
ITEM: Methanol or acetone vapor exposure and ignition risk
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Methanol and acetone are dispensed in a chemical fume hood away from hot plates, open flames, and spark sources
MITIGATION: Pre-chill methanol and acetone in sealed labeled containers; open them only inside a chemical fume hood; keep ignition sources out of the area; wear nitrile gloves and safety glasses; collect solvent waste in approved flammable-waste containers

---

#### RISK RM-022
STAGE: antigen_retrieval
ITEM: Paraffin-section antigen retrieval mismatch or overheating
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Retrieval buffer, pH, temperature, and duration are recorded for each paraffin run; section adhesion is checked after cooling
MITIGATION: Use citrate pH 6.0 or Tris-EDTA pH 9.0 according to target validation; keep HIER at 95-99°C for 15-20 min; cool sections in retrieval buffer for 20 min before PBS transfer; use positively charged slides to reduce section lifting

---

#### RISK RM-023
STAGE: reagent_handling
ITEM: Primary or secondary antibody degradation from repeated freeze-thaw cycles
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Antibody aliquot history is recorded; working aliquots do not exceed 3 freeze-thaw cycles
MITIGATION: Aliquot antibodies into single-run or short-series volumes on first thaw; store according to vendor temperature guidance; discard aliquots after 3 freeze-thaw cycles or when precipitate appears; keep staining logs linked to antibody lot and aliquot date

---

### Critical Findings (CF-001 to CF-003)

#### CF-001
STAGE: control_design
ITEM: Localization claim made without negative and positive controls
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm that a no-primary control and a validated positive control are present in the same experiment set
MITIGATION: (1) Repeat the staining run with both controls included. (2) Do not interpret localization or absence-of-expression claims until controls pass. (3) If specificity remains uncertain, add knockout, knockdown, or peptide-blocked confirmation.

---

#### CF-002
STAGE: imaging
ITEM: Quantitative comparison performed with different exposure or gain settings between groups
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Review acquisition metadata for every compared image
MITIGATION: (1) Re-image all groups with one matched setting set. (2) Use controls to establish the exposure before group imaging starts. (3) Exclude mismatched acquisitions from quantitative analysis.

---

#### CF-003
STAGE: multiplex_design
ITEM: Same-host multiplex staining interpreted as true colocalization without cross-reactivity controls
PROBABILITY: medium
IMPACT: high
SCORE: CRITICAL
CHECK: Verify host species, subclass, and control design for every multiplex antibody pair
MITIGATION: (1) Replace one primary with a different host species or a directly labeled primary. (2) Run single-stain controls for each primary alone. (3) Do not interpret overlapping patterns as biological colocalization until host-collision artifacts are excluded.

---

## 6. PARAMETER CONSTRAINTS

### Fixation

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| 4% paraformaldehyde fixation time at 4°C | 10 min | 15 min | 20 min | <10 min: under-fixation and wash loss risk; >20 min: epitope masking likely |
| 4% paraformaldehyde fixation time at 20-25°C | 5 min | 10 min | 15 min | Use only for target-validated workflows; >15 min: over-fixation risk increases |
| Methanol fixation time at -20°C | 5 min | 10 min | 15 min | >15 min: morphology distortion and extraction risk |
| Acetone fixation time at -20°C | 3 min | 5 min | 10 min | >10 min: excessive dehydration and sample distortion risk |
| NH4Cl quench concentration | 50 mM | 100 mM | 150 mM | <50 mM: quenching may be incomplete after aldehyde fixation; >150 mM: no added benefit and unnecessary reagent use |
| NH4Cl quench duration | 10 min | 10-15 min | 15 min | Omission raises autofluorescence and background risk |

### Permeabilization And Blocking

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Triton X-100 concentration | 0.05% | 0.1% | 0.2% | >0.2%: membrane extraction likely |
| Triton X-100 incubation | 3 min | 10 min | 15 min | >15 min: extraction artifact likely |
| Saponin concentration | 0.02% | 0.05% | 0.1% | <0.02%: weak permeabilization; >0.1%: morphology risk |
| Blocking time at 20-25°C | 20 min | 30 min | 60 min | <20 min: background risk; >60 min at 20-25°C: risk of BSA or serum degradation in aqueous buffer without measurable background reduction; proceed to primary incubation |

### Antibody Incubation

Note: For dilution ratios, a higher denominator means a more dilute antibody solution and a lower final antibody concentration.

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Primary incubation at 20-25°C | 45 min | 60 min | 120 min | <45 min: low signal risk; >120 min: evaporation and background risk |
| Primary incubation at 4°C | 12 h | 16 h | 20 h | >20 h: nonspecific binding can increase |
| Secondary dilution (higher denominator = more dilute) | 1:1000 | 1:500 | 1:300 | More concentrated than 1:300 raises background risk |
| Secondary incubation at 20-25°C | 30 min | 45 min | 90 min | >90 min: nonspecific background likely |

### Washes

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Wash count between antibody steps | 3 | 3-5 | 5 | <3: unbound antibody carryover likely |
| Wash duration per cycle | 3 min | 5 min | 10 min | <3 min: weak removal of unbound reagent |
| Wash volume per 12 mm coverslip in 24-well plate | 300 µL | 500 µL | 700 µL | <300 µL: incomplete coverage; >700 µL: splash and sample disturbance risk |
| Wash volume per 8-well chamber-slide well | 150 µL | 200 µL | 300 µL | <150 µL: incomplete coverage; >300 µL: overflow risk |

### Mounting And Imaging

| Parameter | Value / Range | Notes |
|-----------|--------------|-------|
| Mounting medium per 12 mm coverslip | 8-12 µL | Too little traps air; too much spreads under edges |
| Widefield DAPI exposure | 20-200 ms | Begin low and increase only until nuclei are clearly resolved |
| Widefield Alexa Fluor 488 or FITC exposure | 50-500 ms | Keep brightest pixels below saturation |
| Confocal laser percent | 0.5-5% | Use the lowest value that maintains interpretable signal |
| Random fields per condition | 5-10 | Use at least 10 for intensity comparison studies |

---

## 7. QC GATES

### QC Gate 1: Before Fixation

PASS criteria (ALL must be true):
  - Sample density is within the planned range for analysis
  - Cells or sections show intact morphology before fixation
  - The substrate or coating matches sample attachment needs
  - Fixative temperature and fixation chemistry have been selected and prepared

ACTION if FAIL: If cells are overconfluent, reseed and fix a new plate at lower density. If weakly adherent samples lack coating, restart with poly-L-lysine or another validated coating. If morphology is already poor before fixation, correct the culture or sample-prep issue before staining.

---

### QC Gate 2: After Fixation And Permeabilization

PASS criteria (ALL must be true):
  - Fixation time, temperature, and chemistry were recorded
  - Samples remained attached through fixation washes
  - Permeabilization strength matches the target localization
  - No drying event occurred

ACTION if FAIL: If cells detached, repeat with a coated substrate and wall-directed washes. If morphology collapsed, test paraformaldehyde instead of methanol or acetone. If fixation variables were not recorded, the run cannot support optimization decisions and should be repeated with full documentation.

---

### QC Gate 3: After Primary And Secondary Incubation

PASS criteria (ALL must be true):
  - Primary and secondary host-species pairing is correct
  - Negative control is included
  - Wash count and wash duration meet the minimum requirement
  - Samples were protected from light after secondary application

ACTION if FAIL: If the negative control is missing, do not interpret specificity. If wash count is below 3, repeat the staining run with full washes. If secondary pairing is incorrect, the run should be repeated with the proper secondary antibody.

---

### QC Gate 4: Before Quantitative Imaging

PASS criteria (ALL must be true):
  - Positive and negative controls have been reviewed
  - Acquisition settings are locked for all comparable groups
  - Saturated pixels are absent or rare outside non-analytic regions
  - Raw file saving is enabled

ACTION if FAIL: If acquisition settings differ between groups, re-image before analysis. If controls fail, troubleshoot specificity before collecting more data. If raw saving is disabled, enable it and reacquire.

---

### QC Gate 5: Slide Storage And Reanalysis

PASS criteria (ALL must be true):
  - Mounted slides are labeled with sample ID and date
  - Coverslip edges are sealed if storage exceeds 24 h
  - Slides are stored at 4°C in the dark
  - Imaging date relative to mounting date is documented

ACTION if FAIL: If slide labeling is incomplete, relabel immediately from the sample map before identity is lost. If slides were left in light or at 20-25°C for multiple days, expect fluorophore loss and confirm with a control slide before reanalysis.

---

## 8. OUTPUTS

### 8.1 Primary Outputs

| Output | Type | Description |
|--------|------|-------------|
| diagnosis | string | Identified staining or imaging issue and root cause, or "QC PASS - proceed" |
| confidence | enum: high / medium / low | Confidence in the diagnosis based on controls and available metadata |
| recommended_actions | list[string] | Ordered action list; immediate corrective action first, then optimization or prevention |
| risk_flags | list[{risk_id, severity, message}] | Active risk warnings from Sections 4 and 5 |

### 8.2 Secondary Outputs

| Output | Type | Description |
|--------|------|-------------|
| qc_gate_status | dict {gate_id: pass / fail / warning} | Pass or fail status for each of the 5 QC gates |
| parameter_violations | list[{param, observed, valid_range, dx_rule}] | Out-of-range parameters with linked diagnostic rule |
| protocol_section_reference | string | Section of SOP-IF-001 relevant to the issue |
| control_status | enum: complete / incomplete / failed | Whether the required controls were present and interpretable |
| imaging_comparability_status | enum: matched / mismatched / unknown | Whether acquisition settings support cross-sample comparison |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| cell_culture_v1 | User needs seeding density planning, coverslip plating, contamination troubleshooting, or upstream culture optimization before staining |
| western_blot_v1 | Protein abundance validation is needed for the same target before or after IF |
| flow_cytometry_v1 | User needs population-level marker expression rather than single-cell spatial localization |
| rt_qpcr_v1 | Transcript-level validation is needed for the stained target or treatment condition |
| confocal_imaging_v1 | User needs advanced z-stacks, deconvolution, or optical section planning beyond baseline IF acquisition |
| image_analysis_v1 | User needs segmentation, colocalization quantification, or batch image measurement |
| ihc_v1 | User is working with chromogenic tissue staining rather than fluorescent detection |
| live_cell_imaging_v1 | User needs dynamic imaging in living cells rather than fixed-sample staining |
