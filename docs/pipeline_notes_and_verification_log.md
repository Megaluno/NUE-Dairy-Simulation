# NUE genomic breeding pipeline (simulation) — Holstein / Red Dairy Cattle / Jersey × DNK / SWE / FIN / DEU

One pipeline, six R Markdown files run in order (plus one check file, 00b). Each file reads only the outputs of earlier files.

| File | Does | Reads | Writes |
|---|---|---|---|
| `00_genetic_parameters.Rmd` | Sourced h², r_g, population (CFIT 28,400 cows, Lassen & Borchersen slides), 40 single-breed herds, GxE scenarios; **NTM breeding goal** (May 2026 weights, Kargo et al. 2014 economic values) and expected NTM–NUE trade-off | — | `params/*.csv` incl. `index_weights.csv`, `ntm_nue_frontier.csv`, `params/RG_matrix.rds` |
| `00b_rg_update_check.Rmd` | Check of the update (does not change the pipeline): traits, h², population and herds, correlation pairs removed/added, Saved Feed source sensitivity (NAV 2026 vs Stephansen 2025), implied values, index-theory responses before vs now | `params/`, `archive_rg28/params/` | `params/update_check_index_theory.csv` |
| `01_founders_burnin.Rmd` | MaCS coalescent (AlphaSimR CATTLE history, 3-breed split), 10,005 SNP / 29 chr (50k in `hpc/`), 600 founders per breed, 11 correlated traits, breed × country × herd blocks, pedigree, 10-generation phenotypic burn-in | `params/` | `sim_<MODE>_rg<r>/burnin_state.rds`, `phenotypes.csv`, `pedigree.csv`, `trend_burnin.csv` |
| `02_genomic_prediction.Rmd` | Dosage matrix (0/1/2 → −1/0/1 → centred), VanRaden G, A⁻¹ (nadiv), H⁻¹; ABLUP-REML, GBLUP, ssGBLUP (pooled a + bG), ssGBLUP_MF (breed metafounders), weighted ssGBLUP, rrBLUP, BayesA, BayesB; forward + k-fold CV; pooled **and within-breed** accuracy; REML h² of every fit | `sim_*/` | `cv_results_<trait>.csv`, `ebv_forward_<trait>.csv`, `vc_gblup.csv`, `kernels.rds` |
| `03_multitrait_gxe.Rmd` | BGLR `Multitrait` with DIAG / UN / FA genetic and residual covariances; sommer GxE (main, CS, DIAG, US, FA) | `sim_*/`, `kernels.rds` | `mt_*.csv`, `gxe_models.csv` |
| `04_breeding_program.Rmd` | 8 programmes (PHENO, GS_NTM, GS_NTM_NUE35, GS_NTM_NUE75, GS_NTM_NUE35_MUN, GS_NTM_NUE75_CH4, GS_NTM_NUE35_MATE, GS_NTM_NUE35_OCS); SNP-BLUP or ssGBLUP (`eval_model`) × 10 generations; breed-specific NTM index weights; four-path breeder's equation; trends; index correlations; mate allocation (F < 6%); optimum contribution selection (`ocs_dF`) | `sim_*/burnin_state.rds`, `params/index_weights.csv` | `gs_*_<scenario>.csv`, `gs_sdA0.csv` |
| `04b_model_test.Rmd` | SNP-BLUP vs ssGBLUP inside the programme (2 replicates of GS_NTM_NUE35): response and run time; writes the winner | `sim_FULL_rg1.00*/gs_*` | `params/eval_model_choice.txt`, `params/eval_model_test.csv` |
| `05_summary.Rmd` | Collates all results into one report with the recommended breeding plan | all `sim_*/` result files | `05_summary.html` |

## Run

**Run actually done (this machine):** `queue_full_run.txt` (144 steps), 10k SNP, 10 replicates per main scenario, 5 per sensitivity set, SNPBLUP evaluation (verification log #22). The 50k / 20-replicate design below is the cluster version (`hpc/`).


The whole design is queued in `queue_design_20rep.txt` (159 steps; `./queue.sh queue_design_20rep.txt`, resumable,
each step leaves `logs/<step>.done`). In order:

1. `00` and `00b` (parameters, CH4 weight sweep, index definitions incl. GS_NTM_NUE35_MUN and GS_NTM_NUE35_CH4).
2. `01` burn-ins: rg 1.0 replicates 0 and 1, rg 0.9 replicate 0. Replicate r has its own founders
   (seed + r also changes the MaCS seed) and its own folder `sim_FULL_rg1.00_rep<r>`.
3. `02` on replicate 0 for NUE, MUN, SF, CH4 (+ NUE on rg 0.9): adds `ssGBLUP_MF` (breed metafounders)
   next to `ssGBLUP` (pooled a + bG) and writes `ssgblup_choice_<trait>.csv`.
4. `03`: multi-trait and GxE as separate steps (GxE REML cap raised to 100 iterations).
5. Model test: GS_NTM_NUE35 with SNP-BLUP and with ssGBLUP on replicates 0 and 1, then `04b_model_test.Rmd`
   writes the winner to `params/eval_model_choice.txt` (ssGBLUP only if higher NTM, NUE not lower, and
   evaluation time at most 2x SNP-BLUP). File 04 reads it (`eval_model = "auto"`).
6. `04` six main scenarios (GS_NTM, NUE35, NUE75, NUE35_MUN, NUE35_CH4, NUE35_OCS dF 1%) on replicates 0-19,
   PHENO and NUE35_MATE on replicate 0; burn-in r is run just before its scenarios.
7. `05_summary.Rmd` reads all replicate folders.

Results of the 28-correlation run are archived in `archive_rg28/` (sim folders, html, logs, queues).

Evidence for every genetic correlation (all 55 pairs, 36 papers with DOI, criteria, pass/fail reasons): `python3 tools/build_rg_xlsx.py` → `rg_evidence.xlsx`.

Spreadsheet of the replicate results and cross-validation (formulas, no typed numbers):
`python3 tools/build_xlsx.py` → `NUE_replicate_results.xlsx` (needs openpyxl; recalculate in Excel/LibreOffice on opening).

`run_mode = "TEST"` runs everything at 5% scale in minutes, for checking code.

## Software (as built in this workspace)

R 4.3.3, AlphaSimR 2.1.0, sommer 4.5.12, BGLR 1.1.4, rrBLUP 4.6.3, nadiv 2.18.0, OpenBLAS.
CRAN was blocked here, so packages were built from GitHub's CRAN mirror (`github.com/cran/<pkg>`).

## Every assumption that is NOT from a published source

| Where | Assumption | Why / what would replace it |
|---|---|---|
| 00 | Cows and farms per breed from CFIT slides (28,400 cows; 39 farms); only FIN-RDC, SWE-RDC, DEU-HOL known; the rest split equally over 4 countries (equal-split rule); rounding by largest remainder (cows within breed; farms scaled to 40) | Replace with real per-country counts when available |
| 00/01 | 40 single-breed herds (RDC 12, JER 12, HOL 16 after rounding); herd nested in breed, so file 02 drops the redundant breed term | CFIT farms are per breed; slide reports 39 farms / 42 herds |
| 00 | 25 of 45 trait-pair genetic correlations sourced; the other 20 take values implied by weighted bending (largest MY–LONG 0.29, PY–LNVAR 0.27, LONG–NUE 0.23, MY–ICF 0.21; see file 00) | Not estimates. Many sourced values are proxies or index correlations; evidence in `rg_evidence.xlsx` |
| 00 | All four NUE correlations (MY 0.52, PY 0.80, MUN −0.12, DMI 0.08) from one grazing Irish study (Tavernier et al. 2024), NUE h² from Chen et al. 2021 | Chen et al. imply PY–NUE < 0.47 in confinement Holstein |
| 00 | Correlation matrix made positive definite by weighted bending (Jorjani et al. 2003; weight 100 published, 1 unknown); largest change of a published value 0.015 | Ordinary bending would have moved MY–PY 0.86 → 0.74 |
| 00 | CH4 parameters (Danish Holstein) applied to Red and Jersey | Only Holstein estimates published (Schneider et al. 2025) |
| 00 | Between-country r_g = 1.0 (NAV) or 0.9 (sensitivity) | No DK-SE-FI-DE estimate found |
| 00 | ~~MUN h² from Belgian/Dutch data~~ | Resolved: Danish breed-specific values (Buitenhuis & Poulsen 2023) |
| 00 | Saved Feed (SF) replaces feeding rate; DMI dropped. SF h² = ReFI 0.23 (Lidauer et al. 2023, Nordic Red, all breeds); SF–PY/ICF/SCS/LONG = NAV 2026 Saved Feed index correlations (Yield index used for PY), CFIT-cow-weighted | NAV's SF is an index (0.40 ECM + 4.0 dBW − DMI) without a published h²; the formula could not be evaluated (no published kg variances of ECM, dBW) |
| 01 | Breed split times 30 / 50 generations | Not calibrated to a published between-breed F_ST |
| 01 | Herd-generation variance = 15% of base var(P) | Herd is fitted as a fixed block in every model |
| 01 | Residuals and herd effects independent across traits | No residual correlations sourced |
| 01 | 1 sire per 200 cows; 80% of cows used as dams | No public sire numbers found |
| 01 | Burn-in selects on MY + PY | Represents historical yield selection |
| 02 | G regularised 0.99 G + 0.01 I; blended 0.95 G* + 0.05 A₂₂ | Common choices |
| 02 | G **not** adjusted to A₂₂ (no metafounders) | Causes breed-level EBV offsets in ssGBLUP (log #14); EBVs valid for within-breed ranking only. Add G adjustment (Vitezica et al. 2011) or metafounders (Legarra et al. 2015) before across-breed comparison |
| 02 | G-based models on 1,500 genotyped + 1,500 non-genotyped cows (stratified breed × country); pedigree 3 generations back; 3 folds + forward | Workspace limits (2 cores, ~6 GB). On a cluster raise `n_geno_per_gen`, `n_nongeno`, `ped_depth`, `n_folds` |
| 03 | Herd-generation means removed before the 11-trait MCMC | Too many levels to sample |
| 03 | FA with 2 factors | Choice |
| 03 | Bayesian GxE priors: inverse-Wishart, df₀ = 6, prior mean r_g 0 and 0.95 | Prior-sensitivity design |
| 00/04 | NTM weights (May 2026) used for the 5 sub-indices with a simulated counterpart (64% of NTM weight for HOL/RDC, 72% for JER); other sub-indices not simulated | Absolute responses and EUR values too large; comparisons between indices less affected |
| 00/04 | One NTM sub-index SD = one genetic SD of the representing trait; Fertility = ICF only, Udder health = SCS only | Real sub-indices combine several traits |
| 00/04 | Yield = milk + protein (Kargo et al. 2014 Nordic economic values); fat not simulated; Jersey uses the Holstein milk:protein ratio | Jersey values are in the NTM 2018 report (not available) |
| 00/04 | NTM Saved Feed weight acts on SF directly | Production correction of DMI no longer needed |
| 00/04 | NUE weight 0.35 (= Saved Feed weight) and 0.75 on top of NTM | No published economic value for NUE |
| 04 | Elite-dam tier = top 15% | From the pipeline design figure ("top 10–20% per breed") |
| 04 | F limit 0.06 | From the pipeline design figure ("< 6%") |
| 04 | OCS: 300 bull candidates per breed; dam contributions fixed by the two-tier design; target ΔF 1% per generation | FAO guideline is ≤ 1%/generation |
| 04 | 5 replicates (seeds) for GS_NTM, GS_NTM_NUE35, GS_NTM_NUE75, GS_NTM_NUE35_OCS_dF1; 1 for PHENO and GS_NTM_NUE35_MATE | Replicates share one burn-in; between-founder-population variation not included |

Results with the 9-correlation matrix  are archived in `archive_rg9/`. The illustrative indices used earlier (GS_PROD, GS_NUE, GS_NUE_noMUN) and their results are in `archive_illustrative_index/`.

A queued run of every step is in `queue_main.txt` (scenarios of file 04: `queue_ntm.txt`) (`./queue.sh queue_main.txt`, resumable; each step leaves `logs/<step>.done`).

## Verification log (bugs found and fixed, checks passed)

| # | Found by | Problem | Fix | Check after fix |
|---|---|---|---|---|
| 1 | TEST run, file 01 | Herd effects drawn separately per breed, so a "mixed" herd had three different effects | One herd-generation effect per herd, shared by all breeds | All breeds present in every herd |
| 2 | Code review, file 01 | Bulls ranked on the current generation's dams instead of their own dams | Rank on previous generation's dam index | — |
| 3 | TEST, file 03 | GxE rule (BIC + point estimate) declared GxE on data simulated **without** GxE | LRT p < 0.05 **and** upper 95% limit of r_g < 0.80; r_g = 1 dataset always run as negative control | Control: no GxE declared for MY or NUE |
| 4 | FULL run, file 02 | Building H⁻¹ by block assignment into a sparse matrix took > 30 min | One sparse addition | Identical H⁻¹ (max difference 0); 7 s |
| 5 | FULL run, file 02 | A₂₂⁻¹ via sparse solve with sparse right-hand side | Sparse Cholesky, dense RHS | 10 s |
| 6 | FULL k-fold, file 02 | **sommer appends levels without records to the end of `u`**; EBVs were matched by position, scrambling ABLUP/GBLUP/ssGBLUP/wssGBLUP predictions in k-fold CV | Index EBVs by sommer's row names | cor(GBLUP, rrBLUP) = 1.000 on training and validation; matches BLUP identity G_vt G_tt⁻¹ û_t |
| 7 | FULL VC, file 02 | "True" h² reference included between-generation and between-breed genetic differences that the fixed effects absorb | Reference computed within breed × generation; ABLUP-REML added as diagnostic | see `vc_gblup.csv` |
| 8 | Runs killed (exit 137) | Out of memory: genotypes pulled for all ~77k cows before subsetting | Subset first; chunked genotype operations in file 04 | — |
| 9 | FULL run, file 04 | Expected response used only one female path, but sons come from the elite 15% of dams (observed gain > expected) | Four-path breeder's equation (Rendel & Robertson 1950) | Expected vs observed per generation: HOL 2.33 vs 2.29, RDC 2.10 vs 2.09 |
| 10 | TEST negative control, file 03 | Bayesian GxE posterior dominated by the inverse-Wishart prior (each cow in one country): false GxE with narrow intervals | Two opposite priors (mean r_g 0 and 0.95); GxE only if both agree, else "uninformative" | Control: MY "no important GxE", NUE "uninformative" |
| 11 | FULL run, file 03 | sommer correlated-country models (dense G⁻¹ ⊗ 4 countries) too slow for 2 cores | M1 vs M2 in sommer (30 REML iterations); M3–M5 switchable via `gxe_sommer_models` for a cluster | — |
| 12 | Code review, file 04 | Mate allocation keeps per-mating F < 6%, but population F still rises far above 6% | Reported explicitly; optimum contribution selection recommended as next step | — |
| 13 | Unit test, OCS solver | — | — | Contributions ≥ 0 summing to 1/2; coancestry target met; merit rises monotonically as the target loosens; unconstrained limit equals truncation on the top bull |
| 14 | FULL forward CV, file 02 | ssGBLUP NUE forward accuracy 0.002 (slope 0.01) though REML h² 0.11 was normal. Cause: breed-level EBV offsets (ssGBLUP ranked JER lowest; JER has the highest true mean) corrupt the correlation pooled over breeds. Breed is a fixed effect, so the between-breed part of the EBV is uninformative in every model | Added within-breed accuracy (`acc_within_breed`), fitted REML h² per model (`h2_REML_fit`), forward EBVs saved (`ebv_forward_<trait>.csv`); 05 ranks models within breed and reports within-breed dispersion | NUE forward ssGBLUP within-breed accuracy 0.235 (highest of all models); same seed reproduced the earlier pooled accuracies exactly |
| 15 | NTM documents, file 04 | The production index weighted milk yield +1; NTM's Yield sub-index gives milk volume a **negative** economic value (Nordic −0.030 €/kg HOL, −0.029 €/kg RDC; Kargo et al. 2014). The NUE index also differed from the production index in 8 weights, so no effect could be attributed to NUE | Indices rebuilt from NTM May 2026 weights (file 00); NUE indices differ from GS_NTM only in the NUE weight | Index weights in `params/index_weights.csv` match a hand calculation; TEST run: DMI and SCS fall, NUE rises with its weight |
| 16 | 5-replicate NTM runs, file 05 | The plan's item 2 headline ("an added NUE weight buys more at a small, priced cost") was written before the runs. Results: the NUE gain was significant in all 3 breeds at weight 0.75 and in 1 of 3 at 0.35, but no NTM difference was significant (paired SD 3–8 index units against a theoretical loss of 1–4 units) | Headline and verdict now computed inline from the paired tests; report gives theoretical loss, paired SD and replicates needed for 80% power; NTM price taken from selection-index theory | Workbook Summary values equal the report's paired table (spot-checked NUE, NTM, dF); recalc 0 errors |
| 17 | Correlation papers, file 00 | 46 of 55 pairs were 0 without a recorded decision. After adding 16 sourced pairs (sourcing rules) the matrix was far from positive definite (min eigenvalue −0.20): some zeros are mathematically impossible next to published values (PY–LNVAR ≥ ~0.16 given MY–PY 0.86, MY–LNVAR 0.64) | 28 sourced pairs (incl. Buch et al. 2011, added before the burn-ins); weighted bending; Saved Feed via production-corrected DMI; full re-run of files 00–05, old results archived | Published values moved ≤ 0.015; QR vs MA resilience differences ≤ 0.023 SD per unit i (00b); `rg_evidence.xlsx` recalculated, 0 errors |
| 18 | Report text after the 28-correlation re-run, files 03 and 05 | Hand-written sentences written for the old results no longer matched the new ones: multi-trait FA is now *less* accurate than DIAG for unrecorded NUE (old text: UN and FA both better); the REML likelihood-ratio test flagged GxE on the no-GxE control data for MY (p = 0.005; all four compound-symmetry fits hit the iteration cap); ssGBLUP breed means were in the right order this time (old text: breed offsets destroyed pooled accuracy); genomic-REML h² gaps moved from CH4/FR to ICF/yield | All these statements in 05 (and the stale ones in 03) are now computed inline from the result files, so they follow whatever the data show | 03 and 05 re-rendered |
| 19 | 10 further papers and CFIT numbers, files 00–02 | Feeding rate replaced by Saved Feed; DMI dropped; SF's own heritability is unpublished and the NAV formula could not be evaluated from published variances | SF entered with ReFI h² and NAV 2026 index correlations; CFIT population and 40 single-breed herds; file 02 fixed effects made full-rank for nested herds; 04 still uses mixed-herd `assign_blocks` (to update next) | TEST runs of 01 (40 herds, 1 breed each; SF realised h² ratio 0.77–0.87) and 02 (SF, all 7 models) passed; 00b documents every change |
| 20 | Decisions before the full run, files 01–05 | (a) an earlier text said no G–A22 adjustment was tested; wrong: `tune_G()` always rescaled G to A22 (Christensen et al. 2012), pooled over breeds. (b) 04 still had mixed-breed herds. (c) Replicates shared one founder population | (a) Metafounder ssGBLUP added (Γ from base allele frequencies, Legarra et al. 2015; custom (A^Γ)⁻¹) and compared with a rule fixed beforehand; (b) 04 uses the single-breed `assign_blocks` of 01; (c) 20 independent founder replicates; MUN and CH4 scenarios; ssGBLUP option and model test (04b); GxE REML cap 100 | TEST: (A^Γ)⁻¹A^Γ = I to 1.6e-12; G05 vs A^Γ22 block gaps ≤ 0.015 (pooled 0.04–0.12); NUE within-breed accuracy pooled 0.269 vs MF 0.267; 04 ran with both models (ssGBLUP EBV accuracy similar to SNP-BLUP); MaCS seed confirmed to come from R's RNG |
| 21 | Revision after a publishability review, files 00-05 and `hpc/` | Too many implied correlations (19 of 45); genome too small; NTM only ~64% simulated; conclusions resting on one NUE study | 11 traits (fat yield added; udder conformation, claw health, birth, calving, general health and youngstock survival added then dropped the same evening because their correlations are unpublished: 64-72% of NTM weight); 29 chr / 49,996 SNP (SNP-BLUP in n x n form, chunked genotypes); 38 of 55 pairs sourced (candidates and reasons in `params/rg_candidates_round3.csv`); NUE sensitivity (all NUE correlations x0, x0.5); Zhores job scripts (2 whole-node jobs, steps in parallel) | TEST chain 01-02-04 with 17 traits and 50k SNP passed (SNP-BLUP and ssGBLUP); weighted bending moves published values by <= 0.03 |
| 22 | Local run (10k SNP array; 10 main + 5 per sensitivity), files 01-05, `queue.sh`, `tools/build_xlsx.py` | The 50k design did not fit this machine (2 cores, about 6.1 GB per process): MaCS took about 80 min per founder set, and file 04 and ssGBLUP were killed for exceeding memory. In PHENO, the burn-in cows (about 1 GB) were never freed, because they were freed only inside the GS branch, so N_PHENO was killed (exit 137). Two container restarts (N_GS_NTM_NUE35_OCS_dF1_rep7; N_GS_NTM_SFh008_rep3) stopped a step before it wrote output. In 05, every `kable()` inside an `if` block except the last was not printed, which dropped 4 tables: replicate mean/SD, sensitivity sets, and the two EBV index-correlation and accuracy tables. The "±" sign printed as `<U+00B1>` (C locale), and the ssGBLUP line read "NTM NA ... Inf s" | 29 chr x 345 = 10,005 SNP, 600 founders per breed (the 50k version is kept in `hpc/`). The founder cache `founders/` (key = seed, size, chromosomes, segregating sites and a parameter hash) lets the sensitivity burn-ins reuse the main founders of the same replicate. File 04 and file 02 were changed for memory: Ws is never formed, past genomes are kept on disk, training cows are subset before merging, and data no longer needed is freed. The results are unchanged. PHENO now frees `st$kept_cows`. File 03 GxE: breed is dropped from the fixed effects because it is nested in herd x generation (single-breed herds). 04b: ssGBLUP could not run, so SNPBLUP was used for every replicate (rule in 04b). Replicates: 10 per main scenario (seed 20261031 + r, each with its own founders) and 5 per sensitivity set (NUEx0, NUEx05, SFh008); PHENO and NUE35_MATE once. `queue.sh` runs in 110-min windows and skips steps that already have a `.done` file, so lost steps reran from scratch. 05: `pk()` prints every table, "+/-" replaces "±", dF is shown with 4 decimals, and the ssGBLUP line says it could not be run. `build_xlsx.py`: 10 replicates, 6 scenarios, MUN and CH4 comparisons, SF instead of DMI | All 144 queued steps finished (`QUEUE COMPLETE` 06:14). The 2 lost steps reran OK. 05 re-rendered with all tables present, 10 replicates per main scenario and 5 per sensitivity set. `NUE_replicate_results.xlsx`: 7,562 formulas, 0 errors (LibreOffice recalculation) |
| 23 | Multiple-testing review, file 05 | The 120 paired tests of the replicate section were reported with uncorrected p-values only | File 05 now gives Table A (uncorrected), Table B (Benjamini-Hochberg and Bonferroni adjusted p, family = 120 tests; EUR repeats NTM), Table C (counts), Table D (headline results under each method), Table E (results that do not pass BH), and writes `paired_tests_multiple_testing.csv`. BH is the preferred reading | Significant at 5%: 57 uncorrected, 42 BH, 15 Bonferroni. NUE gain from the NUE weight passes BH in all breeds at both weights; CH4, MUN and dF effects pass; the NTM cost of OCS and of the MUN weight, and the HOL NTM difference at weight 0.35, do not pass BH |
| 24 | Wording review, all files | Process notes (dates, decision attributions) in comments and text | Removed; the title-page author line is kept | Wording only: no code logic, parameter value or result changed |

Software cross-check: sommer (Henderson) and rrBLUP (spectral REML) give identical variance components
(0.955 / 6.572) and BLUPs (cor = 1.00000) on the same 3,000 cows; G from this pipeline equals `rrBLUP::A.mat` to 2e-16.
