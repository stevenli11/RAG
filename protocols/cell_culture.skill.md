---
skill_id: cell_culture_v1
skill_name: Mammalian Cell Culture Complete Workflow Skill
version: 1.0
method_family: cell_biology
tags: [cell_culture, passaging, subculture, cryopreservation, thawing, mycoplasma, contamination, adherent, suspension, aseptic_technique, trypsinization, cell_counting, viability, media_preparation, sterile_workflow]
applies_to: [adherent_cells, suspension_cells, primary_cells, immortalized_cell_lines, stem_cells_general]
does_not_apply_to: [3d_organoid_culture, microcarrier_bioreactor, insect_cells, bacterial_culture, iPSC_reprogramming, GMP_manufacturing, xenograft_in_vivo]
risk_level: medium
bsl_level: "BSL-2 (BSL-1 for non-human, non-pathogenic lines only)"
last_updated: 2026-03-14
source_protocol: SOP-CELLCULTURE-001
---

---

## 1. CONTEXT

This skill is invoked when a user asks questions including but not limited to: "how do I passage my cells," "my cells are dying," "my cells look weird under the microscope," "how do I thaw cells from liquid nitrogen," "my cell culture is contaminated," "how do I freeze down cells," "how do I count cells," "what is the correct split ratio," "how do I prepare complete medium," "my cells aren't growing," "how do I test for mycoplasma," "my cells look detached," "how do I maintain HEK293 / HeLa / A549 / MCF7 / Jurkat," or any question about routine mammalian cell culture maintenance, passaging, cryopreservation, thawing, cell counting, viability assessment, media preparation, and contamination troubleshooting. This skill covers the complete routine cell culture workflow: biosafety cabinet (BSC) setup and aseptic technique, media and reagent preparation, thawing cells from cryopreserved stocks, routine subculture of adherent and suspension cells (including trypsinization, cell dissociation, and split ratios), cell counting and viability assessment (hemocytometer, automated counter, trypan blue exclusion), cryopreservation (freezing down cells), mycoplasma testing, and structured diagnostic rules for all major failure modes including contamination (bacterial, fungal, mycoplasma), poor growth, abnormal morphology, and viability loss. This skill does NOT cover: 3D organoid culture (use SOP-ORGANOID-001), iPSC reprogramming or differentiation protocols (use SOP-IPSC-001), microcarrier or bioreactor-based culture (use SOP-BIOREACTOR-001), insect cell culture (Sf9/Hi5 for baculovirus; use SOP-INSECT-001), GMP-grade manufacturing (use SOP-GMP-001), or bacterial/yeast culture. Redirect those queries to the appropriate skill.

---

## 2. INPUTS

### 2.1 Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| cell_type | enum: adherent / suspension | Growth modality of the cell line |
| cell_line_name | string | Specific cell line (e.g., HeLa, HEK293T, A549, Jurkat, K562, MCF7, U2OS, NIH/3T3) |
| species | enum: human / mouse / rat / other | Species of origin — determines BSL level and medium formulation |
| workflow_goal | enum: routine_passage / thaw_from_frozen / cryopreservation / cell_counting / media_preparation / mycoplasma_testing / troubleshooting | Primary task the user is performing |
| passage_number | int or "unknown" | Current passage number — critical for interpreting growth behavior and experimental suitability |

### 2.2 Optional Diagnostic Inputs (provide when troubleshooting)

| Input | Type | Description |
|-------|------|-------------|
| confluence_percent | int (0–100) | Estimated confluence at the time of observation |
| days_since_passage | int | Number of days since the last split |
| split_ratio | string (e.g., "1:10") | Split ratio used at last passage |
| doubling_time_observed | float (hours) | Observed doubling time — compare against expected for the cell line |
| viability_percent | float (0–100) | Trypan blue exclusion viability at last count |
| cell_morphology | string | Description of observed morphology (e.g., "rounded," "vacuolated," "granular," "floating debris") |
| medium_color | enum: bright_red / orange_red / yellow / pink / purple | pH indicator color of phenol-red-containing medium |
| medium_change_frequency | string | How often medium is changed (e.g., "every 2 days," "every 3 days") |
| mycoplasma_status | enum: positive / negative / untested / unknown | Most recent mycoplasma test result |
| mycoplasma_test_date | date or "never" | Date of last mycoplasma test |
| contamination_description | string | Visible contamination characteristics (e.g., "cloudy medium," "floating threads," "black dots," "pH shift") |
| incubator_co2_percent | float | CO₂ setting (should be 5.0% for most culture) |
| incubator_temperature | float (°C) | Incubator temperature (should be 37.0°C) |
| serum_lot_number | string | FBS lot number — for lot-to-lot variation diagnosis |
| trypsin_exposure_time | float (min) | Duration of trypsinization at last passage |
| freezing_method | enum: controlled_rate / isopropanol_container / direct_minus80 | Cryopreservation method used |

---

## 3. WORKFLOW MODULES

### Module 1: BSC_SETUP_AND_ASEPTIC_TECHNIQUE

**Preconditions:** BSC has been certified within the past 12 months (certification sticker visible). BSC UV light has been off for at least 15 min before use (UV damages media components and plasticware). Lab coat, closed-toe shoes, and safety glasses are worn. 70% ethanol spray bottle is available.
**Pause point:** NO — BSC setup is performed immediately before each culture session. Do not set up and walk away.

#### Steps:

**BSC PREPARATION:**
1. [CRITICAL] Turn on BSC blower at least 15 min before starting work. This establishes laminar airflow and purges particulates from the work zone. Do not begin work immediately after turning on the blower.
2. [CRITICAL] Turn off the UV lamp before opening the sash. UV exposure causes severe skin and eye damage and degrades media, plasticware, and reagents.
3. Raise sash to the operating height marked on the cabinet (typically 8–10 inches). The sash height is calibrated to the airflow — operating at a different height compromises containment.
4. Wipe the entire interior work surface of the BSC with 70% ethanol using lint-free wipes. Wipe in a back-to-front, side-to-side pattern. Allow the surface to air-dry completely (approximately 2 min).
5. [CRITICAL] Wipe every item entering the BSC with 70% ethanol before placing it inside. This includes: media bottles, pipette boxes, tube racks, flasks, centrifuge tubes, and waste containers. The only exceptions are sterile items removed from sealed packaging inside the BSC.
6. [BEGINNER TRAP] Placing items at the front edge of the BSC disrupts the protective air curtain. All items must be placed at least 4 inches (10 cm) back from the front grille. Working directly over the front grille is the single most common cause of contamination from improper technique.
7. [DO NOT] Block the front or rear grilles of the BSC with items. Blocked grilles disrupt laminar airflow and eliminate containment protection.
8. Place a waste container (small beaker with ~50 mL 10% bleach) inside the BSC for aspiration waste.
9. Place serological pipettes, pipette aid, and tube racks in the BSC. Organize items so that clean items are on one side and waste on the other to prevent cross-contamination.

**ASEPTIC TECHNIQUE PRINCIPLES (enforce throughout all modules):**
10. [CRITICAL] Never pass bare hands or arms over open vessels. Work with arms parallel to the airflow (front-to-back), not across it.
11. [CRITICAL] Never leave flasks, tubes, or bottles open longer than the time required for the current pipetting step. Cap or flame immediately after each operation.
12. [CRITICAL] Change gloves with 70% ethanol spray between handling different cell lines. Cross-contamination between cell lines is undetectable without STR authentication.
13. [BEGINNER TRAP] Talking, sneezing, or coughing near open vessels introduces oral flora. If this occurs with a vessel open, discard the contents.
14. [DO NOT] Use a cell phone or touch your face while gloved inside the BSC. Recontaminate gloves with 70% ethanol immediately if this occurs.
15. [CRITICAL] Work with only ONE cell line at a time inside the BSC. Complete all operations for one line, remove all materials, decontaminate the BSC surface with 70% ethanol, then begin the next cell line. Working with two cell lines simultaneously is the primary cause of cross-contamination.

#### Exit Criteria (must ALL be true to proceed):
- BSC blower has been running ≥15 min
- UV lamp is off
- All interior surfaces wiped with 70% ethanol and dry
- All items entering BSC were surface-decontaminated
- No items blocking front or rear grilles
- Only one cell line's materials are present in the BSC

---

### Module 2: MEDIA_AND_REAGENT_PREPARATION

**Preconditions:** Base medium, serum, and supplements are available. Media storage conditions have been verified. BSC is set up per Module 1.
**Pause point:** YES — complete medium can be stored at 4°C for up to 4 weeks (label with preparation date and expiry). Warm only the volume needed for the current session — do not repeatedly warm and cool the entire bottle.

#### Steps:

**BASE MEDIUM SELECTION:**
1. [DECISION POINT] Select base medium:
   - DMEM (Dulbecco's Modified Eagle Medium): default for most adherent lines (HEK293, HeLa, A549, U2OS, NIH/3T3, MCF7). High glucose (4.5 g/L) with L-glutamine and sodium pyruvate unless the cell line datasheet specifies otherwise.
   - RPMI 1640: default for most suspension and hematopoietic lines (Jurkat, K562, THP-1, Raji, U937, HL-60) and some adherent lines (e.g., HCT116). Contains no calcium — do not substitute for DMEM without verification.
   - MEM (Minimum Essential Medium): for primary fibroblasts, some epithelial lines (Vero, BHK-21). Lower amino acid concentration than DMEM.
   - F-12K or Ham's F-12: for CHO cells, some lung epithelial lines.
   - DMEM/F-12 (1:1 mix): for stem cells, neural lines, some epithelial lines.
   - Specialty media (e.g., McCoy's 5A for HCT116 per some protocols, Leibovitz L-15 for CO₂-free incubation): use only when specified by cell line datasheet.
   - [CRITICAL] Always verify the correct base medium for a specific cell line before preparing. The ATCC or cell bank datasheet is the authoritative source. Using the wrong base medium causes gradual phenotypic drift or acute growth arrest.

**SERUM SUPPLEMENTATION:**
2. [DECISION POINT] Select serum:
   - Fetal Bovine Serum (FBS): standard supplement for most lines. Use heat-inactivated FBS (56°C for 30 min) if required by the cell line protocol (e.g., for complement-sensitive assays). Otherwise, use non-heat-inactivated FBS.
   - Standard FBS concentration: 10% (v/v). Range: 5–20% depending on cell line. Reduced serum (0.5–2%) for serum starvation assays.
   - [BEGINNER TRAP] FBS has significant lot-to-lot variation. When switching lots, perform a parallel growth comparison (old lot vs. new lot) for at least 3 passages before switching entirely. Growth rate, morphology, and transfection efficiency can all change with a new lot.
   - [CRITICAL] Record the FBS lot number in the lab notebook for every experiment. If results change unexpectedly, the first thing to check is whether the FBS lot changed.
3. [DECISION POINT] L-glutamine supplementation:
   - If base medium contains GlutaMAX (L-alanyl-L-glutamine dipeptide): no additional glutamine is needed. GlutaMAX is stable in solution and does not produce ammonia.
   - If base medium contains L-glutamine: L-glutamine degrades in solution (half-life ~2–3 weeks at 37°C, ~6 months at 4°C). For long-term stored media, supplement with fresh L-glutamine (2 mM final) or switch to GlutaMAX.
   - [BEGINNER TRAP] Ammonia accumulation from glutamine degradation inhibits cell growth and is not visible. If cells gradually slow down over weeks in stored medium, replace with fresh medium supplemented with L-glutamine.

**COMPLETE MEDIUM PREPARATION:**
4. Calculate volumes for the desired final volume. Example for 500 mL complete DMEM + 10% FBS + 1% Pen/Strep:

| Component | Volume | Final concentration |
|-----------|--------|-------------------|
| DMEM base medium (with L-glutamine, high glucose) | 445 mL | — |
| FBS (heat-inactivated or standard, per cell line requirement) | 50 mL | 10% |
| Penicillin-Streptomycin (100×, 10,000 U/mL Pen + 10,000 µg/mL Strep) | 5 mL | 1× (100 U/mL Pen, 100 µg/mL Strep) |
| **Total** | **500 mL** | |

5. [DECISION POINT] Antibiotics:
   - Use Pen/Strep (1×) for routine maintenance of established cell lines.
   - [DO NOT] use antibiotics as a substitute for good aseptic technique. Antibiotics mask low-level contamination and promote antibiotic-resistant organisms.
   - [CRITICAL] Omit antibiotics from media used for transfection, transduction, or any experiment where membrane integrity is compromised. Antibiotics enter permeabilized cells and are cytotoxic.
   - For primary cells or precious samples: add Gentamicin (50 µg/mL) or Normocin (100 µg/mL) for broad-spectrum protection during initial establishment.

6. Add all supplements to the base medium bottle inside the BSC using serological pipettes. Swirl the bottle 10× to mix. Do not shake vigorously (creates foam that denatures serum proteins).
7. Label bottle with: complete medium name, supplements and concentrations, FBS lot number, preparation date, expiry date (4 weeks from preparation), preparer initials.
8. [PAUSE POINT] Store at 4°C in the dark. Stable for 4 weeks. Discard after 4 weeks.

**PRE-WARMING REAGENTS FOR USE:**
9. [CRITICAL] Pre-warm the following to 37°C in a water bath or bead bath for 15–30 min before use: complete medium, trypsin-EDTA (or other dissociation reagent), PBS (Ca²⁺/Mg²⁺-free).
10. [DO NOT] Pre-warm the entire stock bottle. Aliquot only the volume needed for this session into a separate sterile tube or bottle. Repeated warming and cooling of the stock promotes reagent degradation and microbial growth.
11. [BEGINNER TRAP] Using cold medium on cells causes thermal shock, reduces post-passage viability by 5–15%, and delays cell attachment for adherent lines. Always use pre-warmed medium.
12. [VISUAL CHECK] Before use, inspect pre-warmed medium for: clarity (no turbidity), color (orange-red for pH 7.2–7.4 with phenol red), and absence of floating particles. If turbid, discard — contamination is likely.

#### Exit Criteria (must ALL be true to proceed):
- Correct base medium selected per cell line datasheet
- FBS lot number recorded
- All supplements added at correct concentrations
- Bottle labeled with date, contents, and expiry
- Aliquots pre-warmed to 37°C before use
- Medium is clear, correct color, and free of particulates

---

### Module 3: THAWING_CELLS_FROM_CRYOPRESERVED_STOCK

**Preconditions:** Cryovial is in liquid nitrogen storage or −150°C freezer. Complete medium is pre-warmed to 37°C. BSC is set up per Module 1. A culture vessel (flask or plate) is pre-labeled and has pre-warmed medium added.
**Pause point:** NO — once the cryovial is removed from liquid nitrogen, proceed without interruption. DMSO in the freezing medium is cytotoxic at 37°C; every minute of delay at room temperature reduces viability.

#### Steps:

**PRE-THAW PREPARATION:**
1. Pre-warm 10 mL complete medium to 37°C in a 15 mL conical tube (for washing out DMSO).
2. Pre-fill a culture vessel with the appropriate volume of pre-warmed complete medium:
   - T-25 flask: 5 mL
   - T-75 flask: 12–15 mL
   - T-175 flask: 25–30 mL
   - 10 cm dish: 10 mL
   - 6-well plate: 2 mL per well
3. Place the prepared vessel in the 37°C / 5% CO₂ incubator to equilibrate while thawing the vial.
4. Label the vessel with: cell line name, passage number (passage at freezing + 1), date, operator initials.

**THAWING:**
5. [CRITICAL] Retrieve the cryovial from liquid nitrogen using cryogloves and face shield. If stored in the liquid phase, the vial may have liquid nitrogen trapped inside — hold the vial at arm's length for 10 sec to allow pressure equalization before warming.
6. [CRITICAL] Transport the cryovial on dry ice (not at room temperature). Do not allow the vial to begin thawing during transport.
7. Thaw the cryovial rapidly in a 37°C water bath. Hold the vial by the cap (above the waterline to prevent contamination of the cap threads). Swirl continuously.
8. [CRITICAL] Remove the vial from the water bath when a small ice crystal (~20% of volume) remains — approximately 60–90 sec. Do NOT allow the vial to fully warm to 37°C. DMSO at 37°C is cytotoxic within minutes.
9. [VISUAL CHECK] The cell suspension should be mostly liquid with a small visible ice chip. If the vial is fully thawed and warm to the touch, proceed immediately — do not pause.
10. Wipe the outside of the cryovial thoroughly with 70% ethanol. Transfer to the BSC.

**DMSO REMOVAL:**
11. [DECISION POINT] Select DMSO removal method:
    - Method A (Dilution/centrifugation — recommended for most cell lines): Transfer the thawed cell suspension (~1 mL) dropwise into the pre-warmed 10 mL conical tube. Add the cells to the medium drop by drop over 30 sec while swirling. Centrifuge at 200 × g for 5 min at room temperature. Aspirate supernatant carefully, leaving the pellet undisturbed. Resuspend the pellet in 1 mL fresh pre-warmed complete medium by pipetting up and down 5 times with a 1 mL pipette (do not vortex). Transfer to the pre-prepared culture vessel.
    - Method B (Direct plating — acceptable for hardy immortalized lines such as HEK293T, HeLa, NIH/3T3): Transfer the thawed cell suspension directly into the pre-prepared culture vessel containing pre-warmed medium. The DMSO is diluted by the culture medium volume. Change medium after 12–24 h to remove residual DMSO.
    - Method C (For sensitive primary cells or stem cells): Use Method A but add medium at 1 mL/min with constant gentle swirling (osmotic shock protection). Consider adding 10 µM Y-27632 (ROCK inhibitor) to the plating medium for the first 24 h to enhance survival.
12. [BEGINNER TRAP] Pipetting thawed cells vigorously through a small bore creates shear stress that lyses fragile cells. Use a 1 mL pipette tip (wide bore) or cut the end of a standard tip. Pipette slowly — 5 gentle up-and-down strokes maximum.
13. [DO NOT] Vortex thawed cells at any point. Vortexing causes >30% viability loss in most cell lines and >60% in primary cells.

**POST-THAW CULTURE:**
14. Place the vessel in the 37°C / 5% CO₂ incubator. Do not disturb for at least 6 h to allow cell attachment (adherent lines).
15. [CRITICAL] Change medium at 12–24 h post-thaw. This removes: (a) residual DMSO, (b) dead cell debris, (c) cryoprotectant breakdown products. For direct-plated cells (Method B), the 12–24 h medium change is mandatory.
16. [VISUAL CHECK] At 24 h post-thaw: observe cells under an inverted phase-contrast microscope at 10× magnification.
    - Adherent cells: ≥50% of cells should be attached and spread (flat, phase-dark). Floating round phase-bright cells are dead or dying.
    - Suspension cells: viability ≥60% by trypan blue exclusion at 24 h is acceptable. <40%: thaw a new vial.
17. [DECISION POINT] Post-thaw recovery assessment at 48–72 h:
    - Viability ≥80% and cells proliferating: proceed to routine culture (Module 4 or 5).
    - Viability 50–80% and cells proliferating slowly: continue with daily medium changes for an additional 48 h. Do not passage until cells have recovered.
    - Viability <50% at 48 h with no visible proliferation: thaw a new vial from a different lot if available. Do not invest time in recovering a culture with <50% viability at 48 h.
18. [CRITICAL] Do not use thawed cells for experiments until at least passage 2 after thawing (i.e., the cells must have been passaged at least twice after thawing). Cells recovering from cryopreservation exhibit altered gene expression, growth kinetics, and stress responses.

#### Exit Criteria (must ALL be true to proceed):
- Cryovial was thawed in ≤90 sec in 37°C water bath
- DMSO was removed or diluted within 5 min of thawing
- Medium was changed at 12–24 h post-thaw
- Viability ≥50% at 24 h (adherent: ≥50% attachment; suspension: ≥60% trypan blue viability)
- Cells observed under microscope at 24 h and 48 h; morphology recorded
- Passage number recorded as (passage at freezing + 1)

---

### Module 4: ROUTINE_SUBCULTURE_ADHERENT_CELLS

**Preconditions:** Cells are at 70–90% confluence (cell-line-dependent; see split ratio table). Medium, PBS, and trypsin-EDTA are pre-warmed to 37°C. BSC is set up per Module 1. A new culture vessel is pre-labeled.
**Pause point:** NO — once trypsin is added, the procedure must be completed without interruption to prevent over-trypsinization.

#### Steps:

**PRE-PASSAGE ASSESSMENT:**
1. [VISUAL CHECK] Observe the culture under the microscope at 10× before starting:
   - Confirm confluence is in the appropriate range for passage (typically 70–90%). Exact confluence for passage depends on cell line — see Parameter Constraints Section 6.
   - Confirm cell morphology is normal for the cell line: adherent cells are flat, spread, and phase-dark with visible nuclei. Note any abnormalities (rounding, vacuolation, granularity, floating cells).
   - [CRITICAL] Check medium color. Orange-red = normal pH (~7.2–7.4). Yellow = acidic (overgrown, metabolic waste accumulation, or CO₂ loss). Purple/pink = alkaline (CO₂ excess or medium degradation). Yellow medium + high confluence = passage immediately. Yellow medium + low confluence = potential contamination — investigate before passaging.
2. [DECISION POINT] Passage timing:
   - 70–80% confluence: ideal for most lines. Passage now.
   - 80–90% confluence: acceptable for fast-growing lines (HEK293T, HeLa). Passage immediately.
   - >95% confluence (contact-inhibited lines like NIH/3T3): cells have entered growth arrest. Passage immediately; may require 24–48 h recovery before normal growth resumes.
   - >95% confluence (non-contact-inhibited lines like HeLa, HEK293T): cells are piling up and undergoing selection pressure. Passage immediately; note that overgrown cells may exhibit altered phenotype.
   - [DO NOT] Allow cells to reach 100% confluence routinely. Post-confluent culture causes: senescence (primary cells), phenotypic drift (immortalized lines), contact inhibition artifacts, and altered response to experimental treatments.

**TRYPSINIZATION:**
3. Aspirate all culture medium from the flask. Tilt the flask to collect medium at the bottom corner; aspirate with a Pasteur pipette connected to vacuum. Do not touch the cell monolayer with the pipette tip.
4. [CRITICAL] Wash the monolayer with Ca²⁺/Mg²⁺-free PBS to remove residual serum. Serum contains trypsin inhibitors that prevent cell dissociation.
   - T-25: 3 mL PBS
   - T-75: 5 mL PBS
   - T-175: 10 mL PBS
   - 10 cm dish: 5 mL PBS
5. Aspirate the PBS wash completely. Residual PBS dilutes trypsin and reduces dissociation efficiency.
6. Add trypsin-EDTA (0.05% trypsin, 0.02% EDTA in Ca²⁺/Mg²⁺-free HBSS or PBS):
   - T-25: 0.5–1 mL
   - T-75: 1–2 mL
   - T-175: 3–4 mL
   - 10 cm dish: 1–2 mL
7. [CRITICAL] Tilt the flask to distribute trypsin evenly over the entire monolayer. Ensure all cells are covered by a thin film. Excess trypsin does not accelerate dissociation but does increase enzyme damage.
8. Incubate at 37°C in the incubator (not at room temperature). Incubation time depends on cell line:

| Cell line category | Trypsin time at 37°C | Notes |
|-------------------|---------------------|-------|
| Easily detached (HEK293T, HEK293) | 1–2 min | HEK293T detaches with PBS wash alone in some labs |
| Standard adherent (HeLa, A549, MCF7, U2OS) | 3–5 min | Check at 3 min |
| Tightly adherent (primary fibroblasts, MDCK, Caco-2) | 5–8 min | May require 0.25% trypsin or Accutase |
| Very tightly adherent (primary hepatocytes, some epithelial lines) | 8–15 min with 0.25% trypsin | Consider collagenase + dispase |

9. [VISUAL CHECK] After the minimum incubation time, observe under the microscope. Cells that are ready to detach appear rounded up (phase-bright, spherical) but may still be loosely attached.
10. [CRITICAL] Tap the side of the flask firmly with the palm 3–5 times to dislodge rounded cells. Check under the microscope — ≥90% of cells should be floating.
11. [BEGINNER TRAP] Do not extend trypsinization beyond the recommended time to detach the last 5–10% of cells. Over-trypsinization (>10 min for standard lines) causes: surface receptor cleavage, membrane damage, reduced viability, and delayed re-attachment. Accept 90% detachment and move on.
12. [DO NOT] Scrape cells with a cell scraper as a substitute for trypsinization during routine passage. Scraping produces uneven single-cell suspensions with clumps and variable viability. Cell scrapers are acceptable only for specific applications (e.g., protein lysate collection).

**TRYPSIN NEUTRALIZATION AND COLLECTION:**
13. Add at least 2× the trypsin volume of complete medium (containing serum) to neutralize trypsin:
    - T-25: add 2–3 mL complete medium
    - T-75: add 4–6 mL complete medium
    - T-175: add 8–10 mL complete medium
14. Pipette the cell suspension up and down 5–10 times against the flask floor to break up clumps and create a single-cell suspension. Use a 10 mL serological pipette.
15. [VISUAL CHECK] Hold the pipette up to the light — the suspension should appear homogeneous with no visible clumps. If clumps are present, pipette an additional 10 times. If clumps persist, pass through a 70 µm cell strainer.
16. Transfer the entire cell suspension to a 15 mL conical tube.

**CENTRIFUGATION AND RESUSPENSION:**
17. Centrifuge at 200 × g for 5 min at room temperature.
18. [DO NOT] Centrifuge at >300 × g for routine passage. Excessive centrifugal force compacts the pellet, damages cell membranes, and reduces viability.
19. [VISUAL CHECK] After centrifugation, a loose white/off-white pellet should be visible at the bottom of the tube. The supernatant should be clear (tinted by medium color).
20. Aspirate the supernatant carefully without disturbing the pellet. Leave ~100 µL above the pellet.
21. Resuspend the pellet in fresh pre-warmed complete medium. Volume depends on the planned split ratio and whether cell counting is needed:
    - For routine passage without counting: resuspend in 1 mL per planned flask (e.g., 3 mL if splitting into 3 flasks).
    - For counted passage: resuspend in a known volume (e.g., 5 mL) to allow accurate cell counting.
22. Pipette up and down 10 times with a 1 mL or 5 mL pipette to create a single-cell suspension. Avoid introducing bubbles.

**SEEDING:**
23. [DECISION POINT] Determine seeding density:
    - Use standard split ratios if cell counting is not required:

| Cell line | Standard split ratio | Passage frequency | Notes |
|-----------|---------------------|-------------------|-------|
| HEK293T | 1:8 to 1:15 | Every 2–3 days | Very fast doubling (~20 h); detaches easily |
| HeLa | 1:6 to 1:10 | Every 2–3 days | Doubling ~24 h |
| A549 | 1:4 to 1:8 | Every 3–4 days | Doubling ~22 h |
| MCF7 | 1:3 to 1:6 | Every 3–4 days | Doubling ~30 h; requires estrogen |
| U2OS | 1:4 to 1:8 | Every 3–4 days | Doubling ~26 h |
| NIH/3T3 | 1:10 to 1:20 | Every 2–3 days | Contact-inhibited; do not let exceed 70% confluence |
| Jurkat (suspension) | See Module 5 | See Module 5 | — |
| Primary fibroblasts | 1:2 to 1:4 | Every 4–7 days | Slower growth; limited passages |

    - Use counted seeding density for experiments:

| Vessel | Typical seeding density | Medium volume |
|--------|----------------------|---------------|
| T-25 flask | 0.5–1.0 × 10⁶ | 5 mL |
| T-75 flask | 1.0–3.0 × 10⁶ | 12–15 mL |
| T-175 flask | 3.0–8.0 × 10⁶ | 25–30 mL |
| 6-well plate | 0.2–0.5 × 10⁶ per well | 2 mL per well |
| 12-well plate | 0.1–0.2 × 10⁶ per well | 1 mL per well |
| 24-well plate | 0.05–0.1 × 10⁶ per well | 0.5 mL per well |
| 96-well plate | 5,000–20,000 per well | 100–200 µL per well |
| 10 cm dish | 1.0–3.0 × 10⁶ | 10 mL |

24. Add the calculated volume of cell suspension to the pre-warmed medium in the new vessel.
25. [CRITICAL] Distribute cells evenly. For flasks: rock the flask gently front-to-back and side-to-side 5 times in a cross pattern. For plates: pipette the suspension into the center of the well; rock in a cross pattern 5 times on a flat surface.
26. [DO NOT] Swirl plates in a circular motion. Circular motion concentrates cells in the center of the well (the "donut effect"), producing uneven monolayers and unreliable results.
27. [BEGINNER TRAP] Placing a plate directly into the incubator without distributing cells evenly is the most common cause of edge effects and heterogeneous monolayers.
28. Place the vessel in the 37°C / 5% CO₂ incubator.
29. [CRITICAL] Record in the lab notebook: cell line name, passage number (increment by 1), date, split ratio or seeding density, medium lot, operator initials.

#### Exit Criteria (must ALL be true to proceed):
- Cells were at 70–90% confluence before passage
- Trypsinization time did not exceed the maximum for the cell line
- Trypsin was neutralized with ≥2× volume serum-containing medium
- Cell suspension was a single-cell suspension (no visible clumps)
- Cells were seeded at the correct density
- Cells were distributed evenly in the vessel (no swirling)
- Passage number was recorded
- Vessel was labeled and placed in 37°C / 5% CO₂ incubator

---

### Module 5: ROUTINE_SUBCULTURE_SUSPENSION_CELLS

**Preconditions:** Suspension culture is at the appropriate density for passage (cell-line-dependent; see below). Pre-warmed complete medium is available. BSC is set up per Module 1.
**Pause point:** NO — cells in suspension are sensitive to temperature changes. Complete the procedure within 30 min.

#### Steps:

**PRE-PASSAGE ASSESSMENT:**
1. [VISUAL CHECK] Before the BSC, gently swirl the flask to resuspend settled cells. Observe under the microscope:
   - Cells should be single cells or very small clusters (2–4 cells).
   - Large clumps (>10 cells) indicate: over-confluent culture, poor medium quality, or cell stress.
   - Many phase-bright, shrunken cells: excessive dead cells — check viability.
2. [DECISION POINT] Passage timing based on cell density:

| Cell line | Optimal density range | Max density | Seed at | Passage frequency |
|-----------|---------------------|-------------|---------|-------------------|
| Jurkat | 0.5–2.0 × 10⁶/mL | 3.0 × 10⁶/mL | 0.2–0.5 × 10⁶/mL | Every 2–3 days |
| K562 | 0.5–2.0 × 10⁶/mL | 3.0 × 10⁶/mL | 0.2–0.5 × 10⁶/mL | Every 2–3 days |
| THP-1 | 0.5–1.5 × 10⁶/mL | 2.0 × 10⁶/mL | 0.2–0.4 × 10⁶/mL | Every 3–4 days |
| HL-60 | 0.5–1.5 × 10⁶/mL | 2.0 × 10⁶/mL | 0.2–0.4 × 10⁶/mL | Every 2–3 days |
| Raji | 0.5–2.0 × 10⁶/mL | 2.5 × 10⁶/mL | 0.3–0.5 × 10⁶/mL | Every 2–3 days |

3. [DO NOT] Allow suspension cells to exceed their maximum density. Over-confluent suspension cultures: deplete nutrients rapidly, accumulate ammonia and lactate, experience pH drop (yellow medium), and undergo apoptosis. Unlike adherent cells, there is no visual "confluence" cue — you must count cells.

**SUBCULTURE PROCEDURE:**
4. Gently resuspend the culture by swirling the flask 5 times or pipetting up and down 3 times with a serological pipette.
5. Transfer a known volume of culture to a 15 mL conical tube (e.g., 1 mL for cell counting, plus the volume needed for reseeding).
6. [DECISION POINT] Subculture method:
   - Method A (Simple dilution — for healthy, fast-growing cultures): Discard or archive a fraction of the culture and add fresh medium to reduce density to the target seeding density. No centrifugation needed.
   - Method B (Centrifugation — when medium change is required, e.g., metabolite accumulation, medium conditioning): Transfer the desired volume to a conical tube. Centrifuge at 200 × g for 5 min at room temperature. Aspirate spent medium. Resuspend pellet in fresh pre-warmed complete medium at the target seeding density.
7. For Method A: Remove the required volume of culture from the flask. Add an equal or greater volume of fresh pre-warmed complete medium to reach the target seeding density.
8. [CRITICAL] For both methods: Calculate the exact volume of cell suspension and fresh medium needed to achieve the target seeding density. Do not estimate.
9. Mix the new culture by gently swirling the flask 5 times. Place in the 37°C / 5% CO₂ incubator.
10. Record: cell line, passage number, date, seeding density, medium lot, operator initials.

**MEDIUM CHANGE WITHOUT PASSAGE (for slow-growing suspension cultures):**
11. If density is still below the passage threshold but medium is >48 h old: centrifuge the culture at 200 × g for 5 min, aspirate 50% of the spent medium, and replace with 50% fresh pre-warmed medium. Gently resuspend. This extends nutrient availability without diluting cell density.

#### Exit Criteria (must ALL be true to proceed):
- Cell density was measured before passage
- Cells were seeded at the correct density (within the optimal range for the cell line)
- Medium is fresh and pre-warmed
- Passage number recorded
- Vessel labeled and placed in incubator

---

### Module 6: CELL_COUNTING_AND_VIABILITY

**Preconditions:** Single-cell suspension is available. Trypan blue (0.4%) is available. Hemocytometer or automated counter is available and clean. BSC is set up for the counting step (or counting is performed at the bench if using an automated counter).
**Pause point:** NO — count cells immediately after trypsinization and resuspension. Cell viability decreases over time at room temperature.

#### Steps:

**TRYPAN BLUE EXCLUSION:**
1. [CRITICAL] Ensure the cell suspension is a single-cell suspension (no clumps). Clumps cause undercounting.
2. Mix the cell suspension by pipetting 5 times immediately before removing the counting aliquot. Cells settle within 30 sec.
3. Combine in a microcentrifuge tube: 10 µL cell suspension + 10 µL trypan blue (0.4%) = 1:2 dilution. Mix by pipetting 5 times.
4. [CRITICAL] Count within 3 min of adding trypan blue. Trypan blue is cytotoxic — exposure >5 min causes viable cells to stain positive (false-dead), artificially lowering the viability measurement.
5. [DO NOT] Store trypan-blue-stained cells and count later. This produces unreliable viability measurements.

**HEMOCYTOMETER COUNTING:**
6. [CRITICAL] Clean the hemocytometer and coverslip with 70% ethanol. Dry with a lint-free wipe. Place the coverslip on the hemocytometer — it should adhere by surface tension (Newton's rings visible at the edges confirm proper seating).
7. Load 10 µL of the trypan-blue-stained cell mixture into the hemocytometer chamber by placing the pipette tip at the edge of the coverslip and allowing capillary action to fill the chamber.
8. [DO NOT] Overfill or underfill the chamber. Overfilling raises the fluid level and overestimates cell density. Underfilling leaves the grid partially dry and underestimates.
9. [VISUAL CHECK] Under the microscope at 10×: live cells appear phase-bright (clear cytoplasm) and exclude trypan blue. Dead cells appear dark blue (trypan blue has entered through compromised membranes).
10. Count cells in 4 corner squares (each 1 mm × 1 mm, containing 16 smaller squares).
11. Count cells touching the top and left borders of each square. Do NOT count cells touching the bottom or right borders. This avoids double-counting cells on shared boundaries.
12. [BEGINNER TRAP] Inconsistent counting rules between operators is the primary source of hemocytometer variability. Always count top-and-left-border cells; never count bottom-and-right.

**CALCULATION:**
13. Viable cells/mL = (total viable cells counted in 4 squares ÷ 4) × dilution factor × 10⁴

    Example: 120 viable cells counted in 4 squares, 1:2 dilution with trypan blue:
    Viable cells/mL = (120 ÷ 4) × 2 × 10⁴ = 60 × 10⁴ = 6.0 × 10⁵ cells/mL

14. Viability (%) = (viable cells counted ÷ total cells counted) × 100
15. Total viable cells = viable cells/mL × total volume of cell suspension (mL)

**AUTOMATED CELL COUNTER (e.g., Countess, TC20, Vi-CELL):**
16. If using an automated counter: Follow the same trypan blue staining procedure (Steps 1–5).
17. Load 10 µL of stained suspension into the counting chamber slide (disposable).
18. Insert into counter and run. Record: viable cells/mL, total cells/mL, viability %, and cell size distribution.
19. [BEGINNER TRAP] Automated counters can miscount clumps as single large cells or miss small cells. Always validate a new counter against manual hemocytometer counts for your cell line (run both methods on the same sample for 5 passages).

**ACCEPTANCE CRITERIA:**
20. Healthy routine culture viability should be ≥90% for immortalized lines, ≥85% for primary cells.
21. Viability 80–90%: acceptable but investigate if persistent across passages.
22. Viability 70–80%: concerning — troubleshoot trypsinization time, medium quality, and passage frequency.
23. Viability <70%: critical — do not use for experiments. Identify and fix the cause before proceeding (see Diagnostic Rules DX-008, DX-009).

#### Exit Criteria (must ALL be true to proceed):
- Cell suspension was single-cell (no visible clumps)
- Trypan blue exposure time was <3 min
- ≥100 cells counted per hemocytometer count (or automated counter count accepted)
- Viability ≥90% for immortalized lines (≥85% for primary cells)
- Cell density, viability, and total cell count recorded

---

### Module 7: CRYOPRESERVATION

**Preconditions:** Cells are in log-phase growth (60–80% confluence for adherent; optimal density range for suspension). Cell viability is ≥90%. Freezing medium is prepared. Mr. Frosty or equivalent controlled-rate freezing container is available. Cryovials and labels are prepared.
**Pause point:** YES — cryovials stored in liquid nitrogen are stable indefinitely. However, the procedure itself has no pause points between adding freezing medium and placing cells at −80°C.

#### Steps:

**FREEZING MEDIUM PREPARATION:**
1. [DECISION POINT] Select freezing medium:
   - Standard freezing medium: 90% FBS + 10% DMSO (v/v). Prepare fresh on the day of freezing.
   - Serum-free freezing medium (e.g., CryoStor CS10, Bambanker): use for cells that will be used in serum-free applications or for GMP-adjacent work. Follow manufacturer's instructions.
   - [DO NOT] Use culture medium (DMEM/RPMI + 10% FBS) as the freezing medium base. FBS provides cryoprotective proteins; culture medium alone does not provide sufficient protection. The 90% FBS formulation is not the same as complete culture medium.
2. [CRITICAL] Prepare freezing medium immediately before use. DMSO at room temperature is cytotoxic to cells; minimize the time cells are in contact with DMSO at temperatures above 4°C.
3. Filter-sterilize the freezing medium through a 0.22 µm syringe filter into a sterile tube. Keep on ice.

**CELL HARVESTING:**
4. Harvest cells as per Module 4 (adherent) or Module 5 (suspension). Create a single-cell suspension.
5. Count cells per Module 6. Record viable cell count and viability. Viability must be ≥90% before proceeding with cryopreservation.
6. [DO NOT] Freeze cells with viability <90%. Low-viability stocks produce even lower-viability thaws (typically 10–20% further loss). A vial frozen at 80% viability may thaw at 55–65% — often below recovery threshold.
7. Centrifuge the cell suspension at 200 × g for 5 min at room temperature. Aspirate supernatant completely.

**FREEZING:**
8. Resuspend the cell pellet in cold freezing medium (on ice) at a density of 1–5 × 10⁶ viable cells per mL.
   - Optimal: 1–2 × 10⁶/mL for most cell lines (1 mL per cryovial).
   - For primary cells or rare cells: 2–5 × 10⁶/mL.
9. [CRITICAL] Work quickly from this point. Once cells are in DMSO-containing freezing medium, DMSO cytotoxicity begins immediately at room temperature. Complete steps 9–13 within 10 min.
10. Aliquot 1 mL of cell suspension per cryovial. Label each vial with: cell line name, passage number, viable cell count per vial, freezing date, FBS lot number, operator initials.
11. [CRITICAL] Use a controlled-rate freezing method:
    - Mr. Frosty (isopropanol-filled freezing container): provides −1°C/min cooling rate. Place cryovials inside the Mr. Frosty container. [CRITICAL] Verify the isopropanol in the Mr. Frosty is at the fill line and is not >5 uses old. Replace isopropanol every 5 uses.
    - CoolCell: alcohol-free controlled-rate container. Follow manufacturer's instructions.
    - Programmable controlled-rate freezer: set −1°C/min from room temperature to −80°C.
12. [CRITICAL] Place the freezing container immediately in a −80°C freezer. Do not store at room temperature, 4°C, or −20°C before −80°C.
13. [DO NOT] Place individual cryovials directly in the −80°C freezer without a controlled-rate container. Direct placement produces uncontrolled cooling (−5 to −10°C/min), causing intracellular ice crystal formation and massive cell death. Viability on thaw drops to 10–30%.

**TRANSFER TO LIQUID NITROGEN:**
14. [CRITICAL] After 12–24 h at −80°C, transfer cryovials to liquid nitrogen storage (−196°C liquid phase or −150°C vapor phase). Cells stored at −80°C lose viability progressively — shelf life at −80°C is approximately 3–6 months. For long-term storage (>6 months), liquid nitrogen is mandatory.
15. Record in the cryostorage database: cell line, passage number, number of vials, viable cell count per vial, location (rack/box/position), date frozen, operator.

#### Exit Criteria (must ALL be true to proceed):
- Cells were in log-phase growth (60–80% confluence or optimal density)
- Viability was ≥90% before freezing
- Freezing medium was 90% FBS + 10% DMSO (or validated serum-free alternative)
- Cell density was 1–5 × 10⁶ viable cells/mL
- Controlled-rate freezing (−1°C/min) was used
- Vials were at −80°C within 10 min of adding freezing medium
- Vials were transferred to liquid nitrogen within 24 h
- Cryostorage database updated

---

### Module 8: MYCOPLASMA_TESTING

**Preconditions:** Cells have been in culture for at least 1 week without antibiotics (antibiotics suppress mycoplasma growth and produce false-negative results). Culture supernatant or cell pellet is available for testing.
**Pause point:** YES — collected supernatant can be stored at −20°C for up to 2 weeks before testing. However, fresh samples produce the most reliable results.

#### Steps:

**TESTING SCHEDULE:**
1. [CRITICAL] Test every cell line for mycoplasma: (a) upon receipt or thaw from any source, (b) every 4 weeks during routine culture, (c) before using cells for any experiment that will generate data for publication, (d) if unexplained growth changes, morphological changes, or experimental variability occur.
2. [DO NOT] Assume that cells from a "trusted" source (collaborator, cell bank, commercial vendor) are mycoplasma-free. Testing upon receipt is mandatory regardless of source.

**SAMPLE COLLECTION:**
3. Collect 1 mL of culture supernatant from cells that have been growing for 48–72 h (to allow mycoplasma DNA accumulation in the supernatant). Transfer to a sterile microcentrifuge tube.
4. [CRITICAL] Culture the cells WITHOUT antibiotics for at least 1 passage (ideally 1 week) before testing. Antibiotics suppress mycoplasma growth below detection limits.
5. Centrifuge supernatant at 200 × g for 5 min to pellet cells and debris. Transfer 500 µL of clear supernatant to a new tube for testing.

**PCR-BASED DETECTION (recommended method):**
6. [DECISION POINT] Select detection method:
   - PCR/qPCR (recommended): Most sensitive (detects as few as 10 CFU/mL). Use a commercial kit (e.g., Lonza MycoAlert PLUS, Sartorius Microsart ATMP Mycoplasma, Minerva Biolabs Venor GeM). Process per kit instructions.
   - MycoAlert luminescent assay (rapid screening): Detects mycoplasmal enzymes. Fast (20 min) but less sensitive than PCR. Useful for routine screening. Follow manufacturer's protocol.
   - DAPI/Hoechst staining (visual method): Stain cells and examine for extracellular fluorescent puncta (mycoplasma on cell surface). Low sensitivity — detects only heavy contamination.
7. For PCR: Extract DNA from 200 µL supernatant per kit instructions. Run PCR with mycoplasma-specific primers (targeting 16S rRNA gene). Include positive control (kit-provided) and negative control (sterile water or medium).
8. [VISUAL CHECK] Gel electrophoresis of PCR product: positive control shows a band at the expected size (varies by kit, typically 250–500 bp). Negative control shows no band. Test samples: any visible band at the correct size = POSITIVE.

**INTERPRETATION AND ACTION:**
9. [DECISION POINT] Mycoplasma test result:
   - NEGATIVE: Record result and date. Proceed with culture and experiments. Retest in 4 weeks.
   - POSITIVE: STOP all experiments with this cell line immediately. See DX-005.
   - INDETERMINATE: Retest with a fresh sample in 48 h. If indeterminate again, treat as positive.
10. [CRITICAL] A confirmed mycoplasma-positive culture must be: (a) quarantined immediately (move to a dedicated hood and incubator or dispose), (b) reported to the lab manager, (c) all cell lines sharing the same incubator must be tested.

#### Exit Criteria (must ALL be true to proceed):
- Testing was performed on cells cultured without antibiotics for ≥1 passage
- PCR or validated assay was used with positive and negative controls
- Result recorded with date and test method
- If positive: quarantine and reporting actions initiated
- If negative: documented and scheduled for retesting in 4 weeks

---

## 4. DIAGNOSTIC RULES

### RULE DX-001
STAGE: routine_culture
CONDITION: Medium turns yellow within 24 h of medium change, cells appear normal, confluence is <60%
DIAGNOSIS: Bacterial contamination (early stage) — rapid pH drop from bacterial metabolic acid production
CONFIDENCE: high
LIKELY_CAUSES:
  - Bacterial contamination introduced during last passage or medium change (break in aseptic technique)
  - Contaminated medium or reagent (shared bottle, contaminated water bath)
  - Contaminated CO₂ incubator water tray (reservoir of environmental bacteria)
DISTINGUISH:
  - Observe under microscope at 40×: bacteria appear as small, rapidly moving dots (motile bacteria) or clusters of tiny dark particles in the medium between cells. They are much smaller than mammalian cells (~1 µm vs. 10–30 µm)
  - Is the contamination in one flask or in all flasks from the same medium batch? If all flasks: medium or supplement is contaminated
  - Does the contamination recur after treatment with antibiotics? Antibiotic-resistant strain or persistent source
  - Was the incubator water tray cleaned recently? Stagnant water trays are a reservoir for environmental bacteria
IMMEDIATE_FIX:
  - Discard the contaminated flask immediately — do NOT open it inside the BSC. Bleach the flask (add 10% bleach to the medium, wait 20 min) before disposal
  - If the cell line is irreplaceable and no frozen stock exists: add 10× Pen/Strep (1,000 U/mL penicillin + 1,000 µg/mL streptomycin) + Gentamicin (50 µg/mL) for 48 h, then passage into antibiotic-free medium and observe. Success rate: <30% — usually contamination returns
  - Check all other cultures from the same session; quarantine suspect cultures
PREVENTION: Strict aseptic technique (Module 1); do not share medium bottles between operators; clean incubator water tray monthly with 10% bleach; do not pre-warm medium in a water bath without wiping bottles with 70% ethanol before placing in BSC; add copper sulfate to incubator water tray to inhibit microbial growth

---

### RULE DX-002
STAGE: routine_culture
CONDITION: Visible turbidity in medium; floating fibrous strands, cotton-like balls, or fuzzy colonies on the medium surface or flask walls; medium may or may not be yellow
DIAGNOSIS: Fungal contamination (yeast or mold)
CONFIDENCE: high
LIKELY_CAUSES:
  - Airborne fungal spores entered culture during BSC work (sash too high, items blocking airflow, or BSC HEPA filter compromised)
  - Contaminated reagent (especially FBS — fungal spores survive in serum)
  - Environmental source: lab with high fungal spore load (proximity to construction, old building, poor air handling)
  - Incubator contamination from a previously contaminated culture
DISTINGUISH:
  - Yeast: medium becomes turbid (cloudy) with small round cells visible at 40× (5–10 µm, oval, sometimes budding). pH drops slowly. Medium may become slightly yellow
  - Mold: visible filamentous growth (hyphae) floating on the surface or attached to flask walls. Easily visible to the naked eye as cottony or fuzzy masses. Can be white, green, black, or orange
  - Check whether contamination correlates with a specific reagent lot, operator, or incubator
IMMEDIATE_FIX:
  - Discard the contaminated culture. Fungal contamination cannot be reliably cleared with antifungals in routine practice
  - Bleach the flask before disposal (10% bleach, 20 min)
  - Decontaminate the incubator shelf where the flask was located (70% ethanol wipe)
  - If fungal contamination is recurrent: decontaminate the entire incubator (remove shelves, wipe with 10% bleach, then 70% ethanol, dry completely before returning to service)
PREVENTION: Maintain BSC certification; do not work with sash above the operating mark; clean incubator monthly; do not store open containers in the incubator; keep lab doors closed during BSC work; consider Fungizone (Amphotericin B, 2.5 µg/mL) for primary cell cultures during initial establishment

---

### RULE DX-003
STAGE: routine_culture
CONDITION: Medium remains clear (no turbidity), but cells exhibit one or more of: reduced growth rate (>50% slower than expected), abnormal morphology (granular cytoplasm, vacuolation, altered cell size distribution), altered gene expression or experimental results without explanation, DAPI staining shows extracellular punctate fluorescence around cells
DIAGNOSIS: Mycoplasma contamination
CONFIDENCE: medium (must confirm with PCR test)
LIKELY_CAUSES:
  - Mycoplasma contamination from another cell line in the same lab (most common source: cross-contamination during passage)
  - Contaminated serum lot (mycoplasma can survive in commercially processed FBS)
  - Contamination from operator oral/nasal flora (Mycoplasma orale, M. salivarium) — talking or mouth-pipetting near open cultures
  - Contaminated laboratory reagents (trypsin, media supplements)
DISTINGUISH:
  - Mycoplasma is NOT visible under standard light microscopy — it is too small (0.1–0.3 µm)
  - Medium remains clear and pH is normal — mycoplasma does not produce visible turbidity
  - Mycoplasma causes subtle changes: slowed growth, altered morphology, cytogenetic abnormalities, altered surface markers, and reduced transfection efficiency
  - The ONLY reliable detection methods are: PCR-based testing (gold standard), MycoAlert enzymatic assay (screening), or DAPI/Hoechst staining (low sensitivity)
  - [CRITICAL] If experimental results suddenly become irreproducible and no protocol changes have been made, mycoplasma contamination should be the first hypothesis to investigate
IMMEDIATE_FIX:
  - Perform PCR-based mycoplasma test immediately (Module 8)
  - If POSITIVE: quarantine the culture. Options: (1) Discard and thaw a clean frozen stock (preferred). (2) Treat with Plasmocin (InvivoGen, 25 µg/mL treatment dose) for 2 weeks, then retest. Success rate for Plasmocin treatment: ~85% for M. hyorhinis, ~60% for M. orale. (3) BM-Cyclin treatment (Roche) as alternative
  - Test ALL cell lines in the same incubator and lab
  - If no clean frozen stock exists: treat with Plasmocin for 2 weeks, retest, passage for 2 more weeks without Plasmocin, then retest again to confirm clearance
PREVENTION: Mandatory mycoplasma testing every 4 weeks for all cell lines; test upon receipt from any source; work with one cell line at a time; never mouth-pipette; do not talk or lean over open vessels; add Plasmocin prophylactic (2.5 µg/mL) to long-term cultures if mycoplasma is a recurring problem in the lab

---

### RULE DX-004
STAGE: routine_culture
CONDITION: Adherent cells are floating or detaching in large sheets; remaining attached cells appear rounded; medium may be normal color or slightly yellow
DIAGNOSIS: Cell death or detachment — multiple possible causes
CONFIDENCE: low (requires systematic investigation)
LIKELY_CAUSES:
  - Over-trypsinization at last passage — surface adhesion molecules were cleaved; cells cannot re-attach
  - Cytotoxic contaminant in medium (endotoxin in water supply, detergent residue on glassware, cytotoxic substance in serum)
  - Mycoplasma contamination (late stage — causes detachment in some cell lines)
  - Incubator malfunction: temperature >38°C or CO₂ >6% (check incubator log)
  - Serum lot change — new lot may lack attachment factors
  - Flask surface not tissue-culture treated (untreated polystyrene does not support adhesion)
DISTINGUISH:
  - Were cells trypsinized within the past 24 h? If yes, and cells are floating: over-trypsinization is the most likely cause. Check trypsin exposure time
  - Is the problem in ONE flask or ALL flasks? One flask = handling error. All flasks = medium, incubator, or systemic issue
  - Check incubator temperature and CO₂ independently (use a calibrated thermometer and Fyrite CO₂ analyzer, not the incubator display)
  - Does the problem occur with fresh medium from a new bottle? If yes: incubator or flask surface issue. If no: medium/reagent issue
  - Check flask label — is it tissue-culture (TC) treated? Non-TC-treated surfaces prevent adhesion
IMMEDIATE_FIX:
  - If over-trypsinization: collect floating cells, centrifuge at 200 × g for 5 min, reseed into a new TC-treated flask with fresh medium. If viability >70%, recovery is possible
  - If medium/reagent issue: change to fresh medium from a different lot; observe for 24 h
  - If incubator issue: move cultures to a backup incubator and service the primary unit
  - If new FBS lot: switch back to the previous lot if available; order new lots and test before switching
PREVENTION: Monitor trypsinization time strictly per cell line; check incubator temperature and CO₂ weekly with independent instruments; qualify new FBS lots before switching; use only TC-treated culture vessels; do not reuse flasks

---

### RULE DX-005
STAGE: mycoplasma_testing
CONDITION: Mycoplasma PCR test returns POSITIVE for one or more cell lines
DIAGNOSIS: Active mycoplasma contamination — requires immediate quarantine and remediation
CONFIDENCE: high (when confirmed by PCR with positive and negative controls)
LIKELY_CAUSES:
  - See DX-003 for contamination routes
DISTINGUISH:
  - Confirm result with a second independent test method or repeat PCR from a fresh sample (false-positive rate for PCR is <2% with proper controls)
  - Identify the mycoplasma species (some kits provide species-level identification) — M. hyorhinis (most common in cell culture), M. orale (human oral flora), M. arginini (bovine), A. laidlawii (environmental)
IMMEDIATE_FIX:
  - QUARANTINE: Move the contaminated culture to a separate hood and incubator, or discard immediately
  - ALERT: Notify the lab manager and all personnel sharing the incubator
  - TEST: Screen ALL cell lines in the lab within 48 h
  - OPTION 1 (preferred): Discard contaminated culture. Thaw a clean frozen stock that was known mycoplasma-negative at the time of freezing. Test the thawed stock at passage 2
  - OPTION 2 (if no clean stock exists): Treat with Plasmocin Treatment (InvivoGen) at 25 µg/mL for 14 days (two 7-day courses). Passage cells normally during treatment. After 14 days, culture for an additional 14 days WITHOUT Plasmocin. Then retest by PCR. If negative: freeze down a clean stock. If still positive: repeat treatment once more or discard
  - DECONTAMINATE: Clean the incubator, water bath, and all shared equipment with 70% ethanol. Change incubator water tray water and add copper sulfate
PREVENTION: See DX-003 prevention measures; consider Plasmocin prophylactic (2.5 µg/mL) as a lab-wide standard; establish a culture quarantine protocol; enforce one-cell-line-at-a-time policy

---

### RULE DX-006
STAGE: routine_culture / thawing
CONDITION: Cells fail to proliferate after thawing — viability is acceptable (>50%) but no visible growth after 5 days
DIAGNOSIS: Post-thaw growth failure — cells are viable but arrested
CONFIDENCE: medium
LIKELY_CAUSES:
  - Extended storage at −80°C without transfer to liquid nitrogen — slow viability loss over months causes surviving cells to be stressed and growth-arrested
  - Cryopreservation at too high a passage number — cells were already senescent or phenotypically drifted before freezing
  - DMSO was not removed within 24 h post-thaw — residual DMSO inhibits proliferation at concentrations >0.5%
  - Incorrect medium: base medium or serum concentration does not match the cell line requirements
  - Seeding density too low: <50,000 cells/mL for most lines — cells require paracrine signals from neighbors to proliferate
DISTINGUISH:
  - How long were the cells stored at −80°C? If >6 months: extended −80°C storage is the likely cause
  - What was the passage number at freezing? If passage >30 for primary cells or passage >50 for immortalized lines: age-related arrest is possible
  - Was the 12–24 h medium change performed? If not: DMSO may be inhibiting growth
  - Was the seeding density adequate? If <50,000 cells/mL: re-seed at higher density
IMMEDIATE_FIX:
  - Change medium with fresh pre-warmed complete medium
  - If seeding density was low: centrifuge cells at 200 × g for 5 min, resuspend in smaller volume, and re-seed at higher density (≥1 × 10⁵ cells/mL)
  - Add conditioned medium (50% fresh + 50% filtered spent medium from healthy growing culture of the same line) to provide growth factors
  - If all else fails: thaw a new vial from a different freezing lot
PREVENTION: Transfer vials to liquid nitrogen within 24 h of −80°C placement; freeze cells at low passage numbers; change medium at 12–24 h post-thaw; seed at ≥1 × 10⁵ cells/mL for most lines

---

### RULE DX-007
STAGE: routine_culture
CONDITION: Cells are growing but morphology has changed: cells appear larger, flatter, more vacuolated, or have increased granularity; doubling time has increased; cells may stain positive for SA-β-galactosidase
DIAGNOSIS: Cellular senescence (primary cells) or phenotypic drift (immortalized lines)
CONFIDENCE: medium
LIKELY_CAUSES:
  - Primary cells: Hayflick limit reached — cells have exhausted their replicative capacity. This is inevitable and passage-number-dependent
  - Immortalized lines at very high passage: accumulation of genetic alterations causing drift in phenotype, gene expression, and drug sensitivity
  - Repeated over-confluent culture: contact inhibition stress accelerates senescence markers
  - Oxidative stress: standard culture conditions (20% O₂) cause oxidative damage over time (primary cells are more sensitive)
  - Mycoplasma contamination can mimic senescence phenotype — rule out first
DISTINGUISH:
  - What is the current passage number? Primary fibroblasts: senescence typically at passage 15–30 (depending on donor age). Primary epithelial: passage 5–15. Immortalized lines: phenotypic drift becomes significant above passage 20–30
  - SA-β-galactosidase staining: positive staining at pH 6.0 is a hallmark of senescence in primary cells
  - Test for mycoplasma first — mycoplasma can cause morphological changes resembling senescence
  - Compare doubling time against expected for the cell line at low passage — a 2× increase in doubling time is a strong indicator of senescence or drift
IMMEDIATE_FIX:
  - For primary cells: thaw a low-passage frozen stock. There is no reversal of replicative senescence
  - For immortalized lines: thaw an early-passage stock (preferably passage <15). Compare growth and morphology
  - Reduce confluence threshold for passage: passage at 60–70% instead of 80–90% to reduce contact inhibition stress
  - Consider hypoxic culture (3–5% O₂) for oxidative-stress-sensitive primary cells
PREVENTION: Freeze multiple vials at the earliest possible passage; always record and monitor passage number; establish a maximum passage number policy (e.g., primary cells: use within 10 passages of thaw; immortalized lines: use within 20 passages of thaw); passage before cells reach high confluence

---

### RULE DX-008
STAGE: cell_counting
CONDITION: Viability consistently <80% at routine passage even with optimized trypsinization time and fresh medium
DIAGNOSIS: Chronic low viability — systemic culture health problem
CONFIDENCE: medium
LIKELY_CAUSES:
  - Mycoplasma contamination (test first — this is the most common occult cause)
  - Over-trypsinization: trypsin time has been gradually extended beyond the acceptable range
  - Medium quality: expired or degraded serum (left at room temperature or repeated warm/cool cycles), degraded glutamine, or expired base medium
  - Incubator conditions: temperature drift (>38°C), CO₂ drift (check with Fyrite), or humidity loss (dry incubator causes evaporation and osmotic stress)
  - Passage frequency too low: cells are routinely over-confluent before passage
DISTINGUISH:
  - Test for mycoplasma immediately — this is the most common and most underdiagnosed cause
  - Check all medium components: preparation date, storage conditions, FBS lot, expiry dates
  - Verify incubator conditions with independent instruments (not the incubator display)
  - Review passage records: has confluence at passage been >90% for the past 5 passages?
  - Try a different FBS lot: side-by-side comparison for 2 passages
IMMEDIATE_FIX:
  - Test for mycoplasma
  - Prepare fresh medium from new reagents
  - Verify incubator temperature and CO₂ with calibrated instruments
  - Reduce trypsinization time by 30%
  - Passage more frequently (at 70% confluence instead of 90%)
PREVENTION: Mycoplasma testing every 4 weeks; fresh medium every 4 weeks (discard old batches); incubator calibration monthly; strict trypsinization timing; passage at 70–80% confluence

---

### RULE DX-009
STAGE: cryopreservation / thawing
CONDITION: Viability after thawing is consistently <40% despite using controlled-rate freezing
DIAGNOSIS: Cryopreservation or thawing protocol failure
CONFIDENCE: medium
LIKELY_CAUSES:
  - DMSO concentration incorrect (too low: insufficient cryoprotection; too high: cytotoxicity)
  - Cells were not in log-phase growth at the time of freezing (confluent or stressed cells survive poorly)
  - Controlled-rate freezing failed: Mr. Frosty isopropanol was depleted or at wrong level; container was not at room temperature before use
  - Thawing was too slow: cells remained in the partially frozen state for >2 min, allowing ice recrystallization
  - Extended storage at −80°C (>6 months) without transfer to liquid nitrogen
  - Viability before freezing was <90%
DISTINGUISH:
  - Check the freezing medium DMSO concentration: was it 10%? Higher = more cytotoxic; lower = less cryoprotection
  - What was the viability before freezing? If <90%, the starting material was suboptimal
  - How long was the Mr. Frosty at −80°C before this vial was added? If a warm Mr. Frosty was placed with vials, cooling rate was correct. If vials were added to a cold Mr. Frosty already at −80°C: cooling rate was too fast (Mr. Frosty must equilibrate from room temperature)
  - How long were the vials stored at −80°C? >6 months: viability loss expected
  - How quickly were the cells thawed? >2 min in the water bath: too slow
IMMEDIATE_FIX:
  - Thaw a different vial from the same lot more carefully (rapid thaw in 60–90 sec, stop with ice crystal remaining)
  - If all vials from this lot yield low viability: thaw from a different lot or source
  - If no other lots exist: plate the low-viability thaw at high density (all cells in a T-25) with conditioned medium + ROCK inhibitor (10 µM Y-27632 for the first 24 h) and attempt recovery
PREVENTION: Freeze only healthy, log-phase cells with viability ≥90%; use 10% DMSO in 90% FBS; start Mr. Frosty from room temperature every time; transfer to liquid nitrogen within 24 h; validate the Mr. Frosty cooling rate annually

---

### RULE DX-010
STAGE: routine_culture
CONDITION: Same cell line performs differently between operators — different growth rates, morphology, or experimental results
DIAGNOSIS: Inter-operator variability — technique-dependent inconsistency
CONFIDENCE: medium
LIKELY_CAUSES:
  - Different trypsinization times between operators (most common)
  - Different split ratios or confluence at passage
  - Different medium warming practices (one operator uses cold medium)
  - Different passage intervals (one operator feeds every 2 days, another every 4 days)
  - Cross-contamination: one operator's "HeLa" may actually be a different cell line
DISTINGUISH:
  - Compare passage logs: passage number, confluence at passage, split ratio, trypsinization time, medium change frequency
  - Have both operators count cells at the same passage with the same counting method — is there a systematic offset?
  - Perform STR authentication on cell stocks from each operator to confirm cell line identity
IMMEDIATE_FIX:
  - Standardize passage protocol: write a cell-line-specific passage SOP that specifies exact confluence threshold, split ratio, trypsinization time, and medium change schedule
  - Both operators should use the same frozen stock and passage in parallel for 3 passages; compare results
  - STR authenticate to rule out cross-contamination
PREVENTION: Written cell-line-specific passage SOPs; standardized passage schedule; regular STR authentication; common frozen stock for all operators

---

### RULE DX-011
STAGE: routine_culture
CONDITION: Incubator CO₂ alarm or cells growing slowly across all cell lines in the same incubator
DIAGNOSIS: Incubator malfunction — CO₂ or temperature out of specification
CONFIDENCE: medium
LIKELY_CAUSES:
  - CO₂ tank empty or valve partially closed — culture medium becomes alkaline (pink/purple color with phenol red)
  - CO₂ sensor drift — displayed value does not match actual CO₂ concentration
  - Temperature controller failure — actual temperature may be >38°C (causes heat stress) or <36°C (slowed growth)
  - Humidity loss — water tray is empty; medium evaporates, increasing osmolarity and causing cell stress
  - Door opened too frequently — CO₂ and temperature recovery is slow in older incubators
DISTINGUISH:
  - Check medium color: purple/pink = alkaline (CO₂ too low); yellow = acidic (CO₂ too high or contamination)
  - Measure CO₂ with an independent Fyrite analyzer — compare to the incubator display
  - Place a calibrated thermometer inside for 2 h — compare to the incubator display
  - Check the water tray: is there water? Is the humidity reading on the incubator above 90%?
  - Check the CO₂ tank gauge: is the tank empty or nearly empty?
IMMEDIATE_FIX:
  - If CO₂ tank is empty: replace immediately. Cultures can tolerate 1–2 h without CO₂ at 37°C if doors remain closed
  - If temperature is out of range: move all cultures to a backup incubator immediately
  - If humidity is low: refill the water tray with sterile deionized water. Add copper sulfate (1% w/v) to inhibit microbial growth
  - Recalibrate CO₂ and temperature sensors per manufacturer's instructions
PREVENTION: Weekly independent CO₂ and temperature checks; maintain a backup incubator; check CO₂ tank level daily; refill water tray weekly; schedule annual incubator service and calibration

---

### RULE DX-012
STAGE: routine_culture
CONDITION: Black or dark spots visible on the flask surface that do not wash off; cells may still be growing around them
DIAGNOSIS: Mold contamination (adherent mold spores) or precipitated media components
CONFIDENCE: medium
LIKELY_CAUSES:
  - Mold spores that have settled on the flask surface and germinated
  - Precipitated calcium phosphate (from medium overheating or pH shift) — these are crystalline, non-biological
  - Precipitated serum proteins (from freeze-thaw cycling of FBS)
DISTINGUISH:
  - Observe at 40×: mold shows filamentous branching hyphae; precipitates are amorphous crystalline structures without biological morphology
  - Do the spots grow over 48 h? Mold grows; precipitates do not
  - Remove the medium and wash with warm PBS — precipitates may partially dissolve; mold does not
  - Aspirate a spot with a pipette and place on a slide: Gram stain or KOH mount reveals fungal hyphae
IMMEDIATE_FIX:
  - If mold: discard the culture. Bleach and dispose. See DX-002
  - If precipitate: medium can be replaced with fresh medium. If precipitates are minor, they do not affect cell growth. If extensive: prepare fresh medium and verify reagent quality
PREVENTION: Do not overheat medium (>40°C); do not repeatedly warm and cool FBS; filter-sterilize complete medium if precipitation occurs; clean incubator to reduce mold spore load

---

## 5. RISK RULES

### Risk Matrix Entries (RM-001 to RM-025)

#### RISK RM-001
STAGE: aseptic_technique
ITEM: Cross-contamination between cell lines
PROBABILITY: high (without strict one-line-at-a-time policy)
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm only one cell line's materials are in the BSC at a time. Verify cell line identity by STR authentication annually
MITIGATION: Work with one cell line at a time in the BSC; decontaminate BSC surface between cell lines; use separate medium bottles per cell line where possible; perform STR authentication upon receipt and annually; spray gloves with 70% ethanol between handling different cell lines

---

#### RISK RM-002
STAGE: aseptic_technique
ITEM: Contamination from improper BSC use (items blocking airflow, sash too high)
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Verify sash is at the operating mark. Confirm front and rear grilles are unobstructed. All items are ≥4 inches from the front grille
MITIGATION: BSC certification annually; mark operating sash height on the cabinet; do not overload the BSC work surface; keep items away from grilles; never work with sash above the marked position

---

#### RISK RM-003
STAGE: media_preparation
ITEM: FBS lot-to-lot variation affecting cell growth and experimental results
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Record FBS lot number for every experiment. Perform side-by-side lot comparison before switching
MITIGATION: Reserve and lot-test FBS before committing; buy large quantities of a single lot; perform 3-passage growth comparison (old vs. new lot) before switching; always record lot number in lab notebook and publication methods

---

#### RISK RM-004
STAGE: media_preparation
ITEM: L-glutamine degradation in stored medium producing ammonia
PROBABILITY: high (for medium stored >2 weeks at 37°C or >6 weeks at 4°C)
IMPACT: medium
SCORE: HIGH
CHECK: Note medium preparation date. If >4 weeks old, check pH and consider supplementing with fresh glutamine or discarding
MITIGATION: Use GlutaMAX (stable dipeptide) instead of L-glutamine; prepare only the amount of medium needed for 4 weeks; store at 4°C; do not pre-warm the entire bottle

---

#### RISK RM-005
STAGE: trypsinization
ITEM: Over-trypsinization causing cell damage and reduced viability
PROBABILITY: high (for operators without cell-line-specific timing)
IMPACT: medium
SCORE: HIGH
CHECK: Confirm trypsin exposure time does not exceed the maximum for the cell line (see Module 4, Step 8). Monitor cells under microscope during trypsinization
MITIGATION: Set a timer for every trypsinization; check cells under the microscope at the minimum time; tap flask to dislodge rounded cells rather than extending incubation; use 0.05% trypsin (not 0.25%) for routine passage of standard lines

---

#### RISK RM-006
STAGE: trypsinization
ITEM: Under-trypsinization producing clumps and inaccurate cell counts
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Visually confirm single-cell suspension before counting or seeding. Clumps are visible to the naked eye when tilting the tube
MITIGATION: Pipette up and down 10× after trypsin neutralization; check under microscope for single cells; if clumps persist, pass through a 70 µm cell strainer

---

#### RISK RM-007
STAGE: routine_culture
ITEM: Overgrowth — cells exceed 95% confluence regularly
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Observe confluence before every medium change. If cells are >90% confluence on two consecutive observations, increase passage frequency or split ratio
MITIGATION: Establish a written passage schedule per cell line; passage at 70–80% confluence; never allow contact-inhibited lines (NIH/3T3, MDCK) to exceed 70% confluence; keep a passage log visible in the lab

---

#### RISK RM-008
STAGE: cryopreservation
ITEM: DMSO cytotoxicity during freezing procedure
PROBABILITY: high (if procedure takes >15 min after adding DMSO)
IMPACT: high
SCORE: CRITICAL
CHECK: Time from adding DMSO-containing freezing medium to placement at −80°C must be <10 min
MITIGATION: Prepare all materials (cryovials, labels, Mr. Frosty) before harvesting cells; add freezing medium and aliquot rapidly; place in −80°C immediately; do not leave cells in DMSO at room temperature

---

#### RISK RM-009
STAGE: cryopreservation
ITEM: Uncontrolled cooling rate (no Mr. Frosty or equivalent)
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Confirm controlled-rate freezing container is being used. Verify Mr. Frosty isopropanol level is at the fill line
MITIGATION: Always use a controlled-rate freezing device (Mr. Frosty, CoolCell, or programmable freezer); never place cryovials directly into −80°C; replace Mr. Frosty isopropanol every 5 uses; start Mr. Frosty from room temperature

---

#### RISK RM-010
STAGE: cryopreservation
ITEM: Extended storage at −80°C without transfer to liquid nitrogen
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Verify all cryovials >24 h old at −80°C have been transferred to liquid nitrogen. Audit cryostorage database monthly
MITIGATION: Transfer to liquid nitrogen within 24 h of −80°C placement; set a calendar reminder; do not use −80°C as long-term storage — viability drops below useful levels within 3–6 months

---

#### RISK RM-011
STAGE: thawing
ITEM: Slow thawing causing ice recrystallization and cell death
PROBABILITY: medium
IMPACT: high
SCORE: HIGH
CHECK: Thawing should be complete (with small ice crystal remaining) within 60–90 sec in a 37°C water bath
MITIGATION: Use a 37°C water bath (not room temperature or dry incubator for thawing); swirl continuously; remove when small ice chip remains; do not allow full warming to 37°C

---

#### RISK RM-012
STAGE: thawing
ITEM: DMSO toxicity post-thaw — failure to remove DMSO within appropriate time
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Confirm DMSO was removed by centrifugation/wash or diluted by plating within 5 min of thawing. Confirm medium change at 12–24 h post-thaw
MITIGATION: Dilute or centrifuge within 5 min of thawing; change medium at 12–24 h for all methods; for sensitive cells, wash by centrifugation (Method A in Module 3)

---

#### RISK RM-013
STAGE: routine_culture
ITEM: Mycoplasma contamination undetected without routine testing
PROBABILITY: high (30–80% of untested lab cultures are contaminated per published surveys)
IMPACT: high
SCORE: CRITICAL
CHECK: Verify mycoplasma testing records exist for every cell line in the lab. Testing interval must be ≤4 weeks
MITIGATION: Mandatory monthly mycoplasma testing; test upon receipt of any cell line; test before using cells for experiments generating publication data; maintain testing log visible in the lab; require mycoplasma testing as a condition for manuscript submission

---

#### RISK RM-014
STAGE: routine_culture
ITEM: Phenotypic drift at high passage numbers
PROBABILITY: high (for primary cells >passage 15; immortalized lines >passage 30)
IMPACT: high
SCORE: HIGH
CHECK: Record passage number at every split. Compare current passage to the maximum acceptable passage for the cell line. Compare current doubling time to reference doubling time at low passage
MITIGATION: Establish maximum passage number policy; thaw a fresh stock when approaching the limit; freeze multiple vials at early passages; record passage number in all publications

---

#### RISK RM-015
STAGE: routine_culture
ITEM: Cell line misidentification / cross-contamination
PROBABILITY: high (15–20% of cell lines in repositories are misidentified per ICLAC)
IMPACT: high
SCORE: CRITICAL
CHECK: STR authentication report on file for every cell line. Authentication performed upon receipt and annually
MITIGATION: STR authenticate upon receipt from any source; re-authenticate annually and before publication; check the ICLAC Register of Misidentified Cell Lines; never work with two cell lines simultaneously in the BSC; use separate medium bottles per cell line where practical

---

#### RISK RM-016
STAGE: incubator_maintenance
ITEM: Incubator contamination from water tray
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Inspect water tray weekly for turbidity, biofilm, or discoloration. Confirm copper sulfate is present
MITIGATION: Clean water tray monthly (10% bleach, rinse, refill with sterile deionized water); add copper sulfate (1% w/v) to inhibit microbial growth; autoclave water tray quarterly; do not use tap water

---

#### RISK RM-017
STAGE: media_preparation
ITEM: Antibiotics masking contamination
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Antibiotics should be considered a safety net, not a replacement for aseptic technique. If contamination occurs in antibiotic-containing medium, the organism is resistant
MITIGATION: Periodically passage cells without antibiotics for at least 1 passage to unmask latent contamination; always omit antibiotics for mycoplasma testing; do not rely on antibiotics to compensate for poor technique

---

#### RISK RM-018
STAGE: routine_culture
ITEM: Uneven cell distribution in multi-well plates
PROBABILITY: high (without proper plate agitation technique)
IMPACT: medium
SCORE: HIGH
CHECK: After seeding, observe at least 4 representative wells under microscope to confirm even distribution before placing in incubator
MITIGATION: Rock plates in a cross pattern (front-back, left-right) 5× each direction — do NOT swirl circularly; allow plates to settle on a flat surface for 5 min before moving to incubator; do not stack plates immediately after seeding

---

#### RISK RM-019
STAGE: routine_culture
ITEM: Osmotic stress from medium evaporation in outer wells of multi-well plates (edge effect)
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Compare cell growth/morphology in edge wells vs. inner wells. If systematic differences exist: edge effect is present
MITIGATION: Fill outer wells with sterile PBS or water (sacrificial wells); maintain incubator humidity >90%; do not leave plates outside the incubator longer than necessary; use humidified incubators with water trays

---

#### RISK RM-020
STAGE: safety
ITEM: Liquid nitrogen handling — cryogenic burns and asphyxiation
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: Cryogloves, face shield, and closed-toe shoes worn when handling liquid nitrogen. Storage area has adequate ventilation and O₂ monitoring
MITIGATION: Always wear cryogloves, face shield, and long sleeves when handling liquid nitrogen or cryovials from liquid-phase storage; ensure storage room has O₂ monitoring and alarm; never seal a container of liquid nitrogen (pressure buildup); never transport liquid nitrogen in a passenger elevator

---

#### RISK RM-021
STAGE: thawing
ITEM: Cryovial explosion from trapped liquid nitrogen
PROBABILITY: low
IMPACT: high
SCORE: HIGH
CHECK: If vials were stored in the liquid phase of liquid nitrogen, hold at arm's length for 10 sec after removal to allow pressure equalization
MITIGATION: Use internally threaded cryovials (less prone to leakage than externally threaded); transition to vapor-phase storage where possible; wear face shield when retrieving vials from liquid-phase storage; hold vial at arm's length after removal

---

#### RISK RM-022
STAGE: media_preparation
ITEM: Medium overheating during pre-warming (>40°C) denaturing growth factors
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Pre-warm medium to 37°C only — do not exceed 40°C. Use a water bath or bead bath with a calibrated thermometer
MITIGATION: Set water bath to 37°C and verify with a thermometer; remove medium as soon as it reaches temperature; do not leave medium in the water bath for >30 min; pre-warm only the volume needed for the session

---

#### RISK RM-023
STAGE: routine_culture
ITEM: CO₂ disruption from frequent incubator door opening
PROBABILITY: medium
IMPACT: medium
SCORE: MEDIUM
CHECK: Minimize door-open time. Group tasks so all cultures needing attention are handled in one session
MITIGATION: Organize work to minimize door-open events; open the incubator only when necessary; close the door within 15 sec per opening; if multiple flasks need attention, remove all at once; consider a dedicated "feeding" incubator separate from a "resting" incubator for sensitive experiments

---

#### RISK RM-024
STAGE: cell_counting
ITEM: Inaccurate cell counts from clumps or operator error
PROBABILITY: high
IMPACT: medium
SCORE: HIGH
CHECK: Confirm single-cell suspension before counting. Count ≥100 cells for statistical reliability. Validate automated counters against hemocytometer
MITIGATION: Pipette to single-cell suspension before counting; count ≥100 cells per count; use consistent counting rules (top-and-left border); validate automated counters at setup; re-count if adjacent squares differ by >15%

---

#### RISK RM-025
STAGE: safety
ITEM: Biohazardous waste handling — human-derived cell lines
PROBABILITY: low (probability of exposure)
IMPACT: high
SCORE: HIGH
CHECK: All human-derived cell lines must be handled at BSL-2 unless risk assessment allows BSL-1. All liquid waste must be decontaminated with 10% bleach for 20 min before drain disposal
MITIGATION: Treat all human-derived cell lines as potential biohazards (BSL-2); decontaminate all liquid waste with 10% bleach (20 min contact time); autoclave all solid waste; use sharps containers for glass pipettes and broken glass; complete institutional biosafety training before handling human-derived materials

---

### Critical Findings (CF-001 to CF-004)

#### RISK CF-001
STAGE: routine_culture
ITEM: Mycoplasma contamination in a lab without routine testing
PROBABILITY: high (published surveys report 15–35% prevalence in academic labs without testing)
IMPACT: high
SCORE: CRITICAL
CHECK: Verify mycoplasma testing records exist and are current for every cell line in active culture
MITIGATION: (1) Implement mandatory monthly mycoplasma testing for all cell lines in the lab. (2) Test every new cell line upon receipt regardless of source. (3) Test before any experiment generating publication data. (4) Maintain a visible testing log in the culture room. (5) If any line tests positive, test ALL lines in the lab within 48 h. (6) Consider Plasmocin prophylactic (2.5 µg/mL) as a lab-wide standard.

---

#### RISK CF-002
STAGE: routine_culture
ITEM: Cell line misidentification going undetected
PROBABILITY: high (ICLAC has documented >500 misidentified cell lines; HeLa cross-contamination is the most common)
IMPACT: high
SCORE: CRITICAL
CHECK: STR authentication records on file and current for every cell line. Cross-reference against ICLAC Register of Misidentified Cell Lines
MITIGATION: (1) STR authenticate every cell line upon receipt. (2) Re-authenticate annually and before manuscript submission. (3) Check cell line name against the ICLAC Register of Misidentified Cell Lines before starting any new project. (4) Major journals now require STR authentication data — include in all publications. (5) Never share cell lines without STR documentation.

---

#### RISK CF-003
STAGE: cryopreservation
ITEM: Entire cell line inventory lost due to equipment failure (−80°C freezer malfunction or liquid nitrogen dewar exhaustion)
PROBABILITY: low
IMPACT: high
SCORE: CRITICAL
CHECK: Confirm that frozen stocks are stored in at least TWO independent locations (different freezers, different rooms, or off-site backup)
MITIGATION: (1) Store cryovials in at least two independent locations. (2) Connect −80°C freezer to a temperature alarm system. (3) Monitor liquid nitrogen dewar level weekly and maintain a fill schedule. (4) Deposit critical cell lines with a cell bank (ATCC, ECACC, JCRB, or institutional biorepository). (5) Maintain a cryostorage inventory database with location, passage number, and date for every vial.

---

#### RISK CF-004
STAGE: routine_culture
ITEM: Antibiotics used as primary contamination prevention, masking chronic low-level contamination
PROBABILITY: high
IMPACT: high
SCORE: CRITICAL
CHECK: Assess lab antibiotic usage policy. If all cultures are maintained with antibiotics at all times, low-level contamination may be masked
MITIGATION: (1) Periodically passage cells without antibiotics for at least 1 passage (ideally 1 week) to unmask latent contamination. (2) All mycoplasma testing must be performed on antibiotic-free cultures. (3) Do not use antibiotics as a replacement for aseptic technique. (4) Investigate and resolve the root cause of any contamination event rather than relying on antibiotics to suppress it. (5) Omit antibiotics for transfection, transduction, and membrane-integrity-compromising experiments.

---

## 6. PARAMETER CONSTRAINTS

### Incubator Conditions

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Temperature | 36.5°C | 37.0°C | 37.5°C | <36.5°C: slowed growth; >37.5°C: heat stress and apoptosis; >38°C: acute cell death — move cultures immediately |
| CO₂ | 4.5% | 5.0% | 5.5% | <4.5%: alkaline medium (pink/purple); >5.5%: acidic medium (yellow); check with Fyrite analyzer |
| Humidity | 85% | 95% | 100% | <85%: medium evaporation causing osmotic stress; edge wells affected first; refill water tray |

### Trypsinization

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Trypsin concentration (routine passage) | 0.025% | 0.05% | 0.25% | Use 0.05% for most lines; 0.25% for tightly adherent only |
| Trypsin exposure time (standard lines) | 1 min | 3–5 min | 8 min | >8 min: over-trypsinization likely; surface receptors cleaved |
| Trypsin exposure time (tightly adherent) | 3 min | 5–8 min | 15 min | >15 min: use alternative dissociation (Accutase, TrypLE) |
| Neutralization volume | 2× trypsin volume | 3× trypsin volume | 5× trypsin volume | <2×: incomplete neutralization; residual trypsin damages cells during centrifugation |

### Centrifugation

| Parameter | Minimum | Optimal | Maximum | Action if Out of Range |
|-----------|---------|---------|---------|----------------------|
| Speed (routine pelleting) | 150 × g | 200 × g | 300 × g | >300 × g: cell damage and compacted pellet; <150 × g: incomplete pelleting |
| Duration | 3 min | 5 min | 7 min | >7 min at >300 × g: excessive for mammalian cells |
| Temperature | RT | RT | 25°C | Do not centrifuge at 4°C for routine passage (cold shock) |

### Cryopreservation

| Parameter | Value / Range | Notes |
|-----------|--------------|-------|
| DMSO concentration | 10% (v/v) | 5–10% range acceptable; 10% is standard |
| Freezing medium base | 90% FBS (or serum-free cryopreservation medium) | Do not use culture medium as the base |
| Cell density | 1–5 × 10⁶ viable cells/mL | Optimal 1–2 × 10⁶/mL for most lines |
| Viability before freezing | ≥90% | Do not freeze cells with viability <90% |
| Cooling rate | −1°C/min | Achieved by Mr. Frosty, CoolCell, or programmable freezer |
| Time from DMSO addition to −80°C | <10 min | DMSO is cytotoxic at room temperature |
| Maximum storage at −80°C | 24 h (before LN₂ transfer) | >6 months at −80°C: significant viability loss |

### Cell Counting

| Parameter | Minimum | Optimal | Notes |
|-----------|---------|---------|-------|
| Cells counted per measurement | 100 | 200 | <100 cells: coefficient of variation >20%; unreliable |
| Trypan blue exposure time | — | <3 min | >5 min: viable cells begin staining (false-dead) |
| Acceptable viability (immortalized) | 80% (investigate) | ≥90% | <80%: troubleshoot before proceeding |
| Acceptable viability (primary) | 75% (investigate) | ≥85% | <75%: troubleshoot before proceeding |

---

## 7. QC GATES

### QC Gate 1: After Thawing

PASS criteria (ALL must be true):
  - Cryovial was thawed rapidly (60–90 sec in 37°C water bath)
  - DMSO was removed or diluted within 5 min
  - Cells were plated and placed in 37°C / 5% CO₂ incubator
  - Medium was changed at 12–24 h post-thaw
  - At 24 h: adherent cells show ≥50% attachment; suspension cells show ≥60% viability
  - At 48 h: evidence of cell proliferation (increasing cell number or colony expansion)

ACTION if FAIL: If viability <50% at 24 h with no recovery at 48 h: thaw a new vial from a different lot. If medium change was missed at 12–24 h: change immediately and observe for 24 h. If no frozen backup exists: attempt recovery with conditioned medium and ROCK inhibitor (see DX-006).

---

### QC Gate 2: Before Routine Passage

PASS criteria (ALL must be true):
  - Cell confluence is within the acceptable range for the cell line (70–90% for most lines)
  - Cell morphology is normal (flat, spread, phase-dark for adherent; round, single cells for suspension)
  - Medium color is orange-red (pH 7.2–7.4)
  - No visible contamination (turbidity, floating particles, surface growth)
  - Passage number is recorded and within the acceptable range for the cell line

ACTION if FAIL: If confluence >95%: passage immediately but note overgrowth in the record. If morphology is abnormal: check for contamination (DX-001 to DX-003) and senescence (DX-007). If medium is yellow at low confluence: suspect contamination — examine at 40× before passaging. If passage number exceeds maximum: thaw a low-passage stock.

---

### QC Gate 3: After Passage

PASS criteria (ALL must be true):
  - Trypsinization time did not exceed the maximum for the cell line
  - Cell suspension was a single-cell suspension (no visible clumps)
  - Cell viability ≥90% (immortalized) or ≥85% (primary)
  - Cells were seeded at the correct density or split ratio
  - Cells distributed evenly in the vessel (no circular swirling)
  - Passage number incremented and recorded
  - Vessel labeled with cell line, passage number, date, and initials

ACTION if FAIL: If viability is low (<85%): investigate trypsinization time and medium quality (see DX-008). If clumps are present: pass through a 70 µm cell strainer before seeding. If seeding density was incorrect: adjust at the next passage; do not add or remove cells from a vessel already placed in the incubator.

---

### QC Gate 4: Before Cryopreservation

PASS criteria (ALL must be true):
  - Cells are in log-phase growth (60–80% confluence or optimal density range)
  - Cell viability ≥90%
  - Cells have been tested for mycoplasma within the past 30 days and result is negative
  - Freezing medium is freshly prepared (same day)
  - Controlled-rate freezing container is available and at room temperature
  - Cryovials are labeled with: cell line, passage number, cell count, date, FBS lot, initials

ACTION if FAIL: If viability <90%: troubleshoot culture health before freezing (see DX-008). If mycoplasma status is positive or untested: test before freezing — do not freeze potentially contaminated stocks. If Mr. Frosty is not at room temperature: wait until it reaches room temperature before proceeding.

---

### QC Gate 5: Monthly Quality Audit

PASS criteria (ALL must be true):
  - Mycoplasma testing completed for all cell lines in active culture within the past 30 days
  - Incubator temperature and CO₂ verified with independent instruments within the past 7 days
  - Passage number recorded for all cell lines; no lines exceed the maximum allowable passage
  - Cryostorage inventory is up to date
  - All frozen stocks >24 h old at −80°C have been transferred to liquid nitrogen
  - BSC certification is current (within the past 12 months)

ACTION if FAIL: Mycoplasma testing overdue: test all lines immediately. Incubator out of specification: calibrate or service. Passage number exceeded: thaw a low-passage stock. Cryostorage audit reveals vials at −80°C >24 h: transfer to liquid nitrogen (with awareness that viability may be reduced if >1 month at −80°C).

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
| protocol_section_reference | string | Section of SOP-CELLCULTURE-001 relevant to the issue |
| passage_number_status | enum: acceptable / approaching_limit / exceeded | Status relative to the maximum passage number for the cell line |
| mycoplasma_testing_status | enum: current / overdue / never_tested | Status of mycoplasma testing for the cell line |

---

## 9. RELATED SKILLS

| Skill ID | Trigger Condition |
|----------|------------------|
| rt_qpcr_v1 | Gene expression analysis of cultured cells is needed — provides RNA extraction through qPCR workflow |
| flow_cytometry_v1 | Cell viability by multi-color dye exclusion, cell cycle analysis, surface marker phenotyping, or sorting is needed |
| western_blot_v1 | Protein-level analysis from cell lysates is needed |
| transfection_v1 | User needs to introduce plasmid DNA, siRNA, or CRISPR components into cultured cells |
| lentiviral_transduction_v1 | Stable gene expression or knockdown via lentiviral delivery is required |
| elisa_v1 | Quantification of secreted proteins in conditioned medium or cell lysates is needed |
| immunofluorescence_v1 | Protein localization or expression at the single-cell level by fluorescence microscopy is needed |
| organoid_culture_v1 | User needs 3D culture, organoid establishment, or Matrigel-based culture — REDIRECT immediately; this skill does not apply |
| ipsc_culture_v1 | User needs iPSC maintenance, reprogramming, or differentiation — REDIRECT immediately; this skill does not apply |
