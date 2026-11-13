import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import os, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "sim_FULL_rg1.00")
OUT = os.path.join(ROOT, "NUE_replicate_results.xlsx")
# both files are written by 05_summary.Rmd
resp_rows = list(csv.DictReader(open(os.path.join(D, "replicate_response_long.csv"))))
inb_rows = list(csv.DictReader(open(os.path.join(D, "replicate_dF.csv"))))      # dF as a fraction

SCEN = ["GS_NTM", "GS_NTM_NUE35", "GS_NTM_NUE75", "GS_NTM_NUE35_MUN", "GS_NTM_NUE75_CH4", "GS_NTM_NUE35_OCS_dF1"]
BREEDS = ["HOL", "RDC", "JER"]
TRAITS = ["NUE", "MUN", "CH4", "MY", "PY", "SF"]   # 11 Nov 2026: SF replaces DMI (05 writes SF)
EXTRA = ["NTM", "EUR", "dF"]          # per replicate x breed, from replicate_dF.csv
FMT = {"NTM": "0.0", "EUR": "0.0", "dF": "0.00%"}
UNIT = {"NTM": "NTM index units", "EUR": "EUR per cow-year", "dF": "per generation"}
REPS = range(10)   # 11 Nov 2026: 10 replicates per main scenario
COMPARISONS = [("GS_NTM_NUE35", "GS_NTM"), ("GS_NTM_NUE75", "GS_NTM"), ("GS_NTM_NUE35_MUN", "GS_NTM_NUE35"),
               ("GS_NTM_NUE75_CH4", "GS_NTM_NUE75"), ("GS_NTM_NUE35_OCS_dF1", "GS_NTM_NUE35")]

F = "Arial"
H = Font(name=F, bold=True, color="FFFFFF"); HFILL = PatternFill("solid", start_color="1F4E78")
BLUE = Font(name=F, color="0000FF"); BLACK = Font(name=F, color="000000"); GREEN = Font(name=F, color="008000")
BOLD = Font(name=F, bold=True); TITLE = Font(name=F, bold=True, size=13)
NOTE = Font(name=F, italic=True, size=9, color="595959")
thin = Side(style="thin", color="BFBFBF"); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
NUM = "0.00;-0.00;0.00"; CEN = Alignment(horizontal="center")

def header(ws, r, cols):
    for j, c in enumerate(cols, 1):
        x = ws.cell(row=r, column=j, value=c); x.font, x.fill, x.border = H, HFILL, BOX
        x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
def put(ws, r, c, v, font=BLACK, fmt=None, center=False):
    x = ws.cell(row=r, column=c, value=v); x.font = font; x.border = BOX
    if fmt: x.number_format = fmt
    if center: x.alignment = CEN
    return x
def widths(ws, w):
    for j, v in enumerate(w, 1): ws.column_dimensions[get_column_letter(j)].width = v

wb = Workbook()

# ---------- Replicate data: response (inputs) + inbreeding rate (inputs) ----------
ws = wb.active; ws.title = "Replicate data"
ws["A1"] = "Simulated results per replicate (inputs)"; ws["A1"].font = TITLE
ws["A2"] = ("Rows = trait responses (gen 20 minus gen 10 mean genetic value, founder genetic SD units) and the rate of "
            "inbreeding per generation ('dF %', from genomic F). Blue = values from the simulation files in column I.")
ws["A2"].font = NOTE
header(ws, 4, ["Scenario", "Replicate", "Breed", "Trait", "Gen 10 mean G", "Gen 20 mean G", "Value", "Unit", "Source (sim_FULL_rg1.00/)"])
r = 5
for d in resp_rows:
    for j, v in enumerate([d["scenario"], int(d["replicate"]), d["breed"], d["trait"]], 1): put(ws, r, j, v, BLUE)
    put(ws, r, 5, float(d["start"]), BLUE, "0.000"); put(ws, r, 6, float(d["end"]), BLUE, "0.000")
    put(ws, r, 7, f"=F{r}-E{r}", BLACK, "0.000"); put(ws, r, 8, "genetic SD"); put(ws, r, 9, d["source"], BLUE)
    r += 1
for d in inb_rows:
    rep = int(d["replicate"])
    for k in EXTRA:
        src = d["source"] if k == "dF" else "computed in 05_summary.Rmd from gs_trend + gs_sdA0 + params/index_weights.csv"
        for j, v in enumerate([d["scenario"], rep, d["breed"], k], 1): put(ws, r, j, v, BLUE)
        put(ws, r, 5, None); put(ws, r, 6, None)
        put(ws, r, 7, float(d[k]), BLUE, FMT[k]); put(ws, r, 8, UNIT[k]); put(ws, r, 9, src, BLUE)
        r += 1
last = r - 1
ws.freeze_panes = "A5"; widths(ws, [16, 10, 8, 8, 13, 13, 11, 14, 40])
RD = "'Replicate data'"
def rng(col): return f"{RD}!${col}$5:${col}${last}"

# ---------- Paired differences ----------
wp = wb.create_sheet("Paired differences")
wp["A1"] = "Paired differences between scenarios within each replicate (same random seed)"; wp["A1"].font = TITLE
wp["A2"] = "All values are formulas pulling from 'Replicate data'."; wp["A2"].font = NOTE
header(wp, 4, ["Comparison", "Scenario A", "Scenario B", "Replicate", "Breed", "Trait", "A", "B", "A - B", "(A - B)^2"])
pr = 5
for a, b in COMPARISONS:
    for rep in REPS:
        for breed in BREEDS:
            for trait in TRAITS + EXTRA:
                for j, v in enumerate([f"{a} - {b}", a, b, rep, breed, trait], 1): put(wp, pr, j, v, BLUE)
                fmt = FMT.get(trait, NUM)
                for j, col in [(7, "B"), (8, "C")]:
                    put(wp, pr, j, f'=SUMIFS({rng("G")},{rng("A")},${col}{pr},{rng("B")},$D{pr},{rng("C")},$E{pr},{rng("D")},$F{pr})', GREEN, fmt)
                put(wp, pr, 9, f"=G{pr}-H{pr}", BLACK, fmt); put(wp, pr, 10, f"=I{pr}^2", BLACK, "0.000000")
                pr += 1
plast = pr - 1
wp.freeze_panes = "A5"; widths(wp, [32, 16, 16, 10, 8, 8, 10, 10, 10, 11])
PD = "'Paired differences'"
def prng(col): return f"{PD}!${col}$5:${col}${plast}"

# ---------- Summary ----------
s = wb.create_sheet("Summary", 0)
s["A1"] = "NUE breeding simulation: replicate results (10 replicates per scenario)"; s["A1"].font = TITLE
s["A2"] = ("Source: 04_breeding_program.Rmd outputs, FULL scale (25,614 cows), no-GxE dataset, 10k SNP array, SNPBLUP evaluation. GS_NTM = genomic selection on the "
           "NTM index (May 2026 weights); GS_NTM_NUE35 / GS_NTM_NUE75 = NTM plus NUE weight 0.35 / 0.75; GS_NTM_NUE35_MUN = NUE 0.35 plus MUN -0.35; GS_NTM_NUE75_CH4 = NUE 0.75 plus CH4 -0.5; GS_NTM_NUE35_OCS_dF1 = NTM + NUE 0.35 with optimum contribution selection at dF = 1%/generation.")
s["A2"].font = NOTE
s["A4"] = "Table 1. Response over 10 selection generations (founder genetic SD units), NTM value and rate of inbreeding: mean and SD over replicates"
s["A4"].font = BOLD
header(s, 5, ["Trait", "Breed", "Scenario", "n replicates", "Mean", "SD"])
r = 6
for trait in TRAITS + EXTRA:
    fmt = FMT.get(trait, NUM)
    for breed in BREEDS:
        for sc in SCEN:
            for j, v in enumerate([trait, breed, sc], 1): put(s, r, j, v, BLUE)
            crit = f'{rng("A")},$C{r},{rng("D")},$A{r},{rng("C")},$B{r}'
            put(s, r, 4, f"=COUNTIFS({crit})", GREEN, "0", True)
            put(s, r, 5, f"=AVERAGEIFS({rng('G')},{crit})", GREEN, fmt, True)
            sq = f"SUMPRODUCT(({rng('A')}=$C{r})*({rng('D')}=$A{r})*({rng('C')}=$B{r})*({rng('G')})^2)"
            put(s, r, 6, f'=IF(D{r}>1,SQRT(MAX(0,({sq}-D{r}*E{r}^2)/(D{r}-1))),"n/a")', BLACK, fmt, True)
            r += 1
r += 1
s.cell(row=r, column=1, value="Table 2. Paired differences between scenarios (A - B, same seed within replicate)").font = BOLD
r += 1
header(s, r, ["Comparison", "Trait", "Breed", "n pairs", "Mean difference", "SD of difference", "Same sign in every replicate?"])
r += 1
for a, b in COMPARISONS:
    for trait in TRAITS + EXTRA:
        fmt = FMT.get(trait, NUM)
        for breed in BREEDS:
            for j, v in enumerate([f"{a} - {b}", trait, breed], 1): put(s, r, j, v, BLUE)
            crit = f'{prng("A")},$A{r},{prng("F")},$B{r},{prng("E")},$C{r}'
            put(s, r, 4, f"=COUNTIFS({crit})", GREEN, "0", True)
            put(s, r, 5, f"=AVERAGEIFS({prng('I')},{crit})", GREEN, fmt, True)
            put(s, r, 6, f'=IF(D{r}>1,SQRT(MAX(0,(SUMIFS({prng("J")},{crit})-D{r}*E{r}^2)/(D{r}-1))),"n/a")', GREEN, fmt, True)
            put(s, r, 7, f'=IF(OR(COUNTIFS({crit},{prng("I")},">0")=D{r},COUNTIFS({crit},{prng("I")},"<0")=D{r}),"Yes","No")', BLACK, None, True)
            r += 1
r += 1
for n in [
    "NUE: higher is better. MUN: lower is better (less N lost as urea). CH4: lower is better. MY/PY: 305-d milk/protein yield. SF: Saved Feed index, higher is better (less feed at equal yield). NTM/EUR: value of the simulated part of NTM (May 2026 weights; EUR per NTM unit HOL 9.9, RDC 9.2, JER 8.0, Fikse & Kargo 2020); excludes non-simulated sub-indices. dF: rate of inbreeding per generation (FAO guideline at most 1%).",
    "Each replicate has its own coalescent founder population and burn-in (seed 20261031 + replicate), so between-population variation is included; the coalescent demography is the same for all replicates. Within a replicate all scenarios share founders, burn-in and seed (paired).",
    "The paired t-tests (p-values) are in 05_summary.html; with 10 replicates they indicate consistency across seeds, not a formal claim about real populations.",
    "SD = sample standard deviation, sqrt((sum of x^2 - n*mean^2)/(n-1)).",
    "Colour key: blue = inputs from simulation files; green = formulas pulling from another sheet; black = formulas within this sheet.",
]:
    s.cell(row=r, column=1, value=n).font = NOTE; r += 1
s.freeze_panes = "A6"; widths(s, [34, 9, 18, 13, 16, 16, 26])

# ---------- Next steps ----------
wn = wb.create_sheet("Next steps")
wn["A1"] = "Open items"; wn["A1"].font = TITLE
header(wn, 3, ["#", "Item", "Status", "Owner"])
for i, it in enumerate([
    (1, "Jersey economic values for milk and protein (NTM 2018 report) to replace the Holstein milk:protein ratio used for Jersey", "Open", "NAV / Emmanuel"),
    (2, "Decide the NUE weight on top of NTM. The NUE gain is in Table 2; the NTM cost was mostly not detectable in 10 replicates (see the SD of the NTM paired difference in Table 2), so price it from selection-index theory (05_summary.html, file 00)", "Open", "Breeding organisation"),
    (6, "If a simulated NTM cost is required: the number of replicates needed for 80% power is computed per breed in 05_summary.html, item 2", "Proposed", "Cluster run"),
    (3, "Make G compatible with A22 (adjusted G or metafounders) before comparing bulls across breeds; current ssGBLUP EBVs are valid within breed only", "Proposed", "Pipeline (file 02)"),
    (4, "Independent founder populations per replicate", "Done (11 Nov 2026)", "Pipeline"),
    (5, "Full-size genotyped run (all 25,614 cows) for G-based models and GxE estimation", "Proposed", "Cluster run"),
], 4):
    for j, v in enumerate(it, 1):
        c = wn.cell(row=i, column=j, value=v); c.font = Font(name=F); c.border = BOX
        c.alignment = Alignment(wrap_text=True, vertical="top")
widths(wn, [5, 90, 12, 13])


# ---------- Genomic prediction (file 02 cross-validation) ----------
wg = wb.create_sheet("Genomic prediction")
wg["A1"] = "Cross-validated accuracy of EBVs (file 02): one run per dataset, 3 folds + forward"; wg["A1"].font = TITLE
wg["A2"] = ("acc_within_breed = cor(EBV, true BV) within breed, n-weighted (selection is within breed). acc_pooled = across breeds, "
            "affected by breed-level EBV offsets. slope = b(true BV on EBV), pooled. h2_REML_fit = h2 fitted by the model's REML (NA for Bayes). "
            "Differences below about 0.05 are within fold-to-fold noise.")
wg["A2"].font = NOTE
header(wg, 4, ["Dataset", "Trait", "Scheme", "Model", "acc_within_breed", "acc_pooled", "slope", "h2_REML_fit", "Source"])
g = 5
for ds in ["sim_FULL_rg1.00", "sim_FULL_rg0.90"]:
    for tr in ["NUE", "MUN", "DMI", "CH4"]:
        p = os.path.join(ROOT, ds, f"cv_results_{tr}.csv")
        if not os.path.exists(p): continue
        for d in csv.DictReader(open(p)):
            if d["model"] == "GBLUP_snp" or "acc_within_breed" not in d: continue
            for j, v in enumerate([ds, tr, d["scheme"], d["model"]], 1): put(wg, g, j, v, BLUE)
            for j, k in [(5, "acc_within_breed"), (6, "acc_TBV"), (7, "slope"), (8, "h2_REML_fit")]:
                put(wg, g, j, float(d[k]) if d.get(k) not in (None, "", "NA") else None, BLUE, "0.000")
            put(wg, g, 9, f"{ds}/cv_results_{tr}.csv", BLUE); g += 1
glast = g - 1
def grng(col): return f"'Genomic prediction'!${col}$5:${col}${glast}"
g += 1
wg.cell(row=g, column=1, value="Summary: mean within-breed accuracy (k-fold = mean of the 3 folds)").font = BOLD; g += 1
header(wg, g, ["Dataset", "Trait", "Model", "k-fold", "forward"]); g += 1
for ds in ["sim_FULL_rg1.00", "sim_FULL_rg0.90"]:
    for tr in ["NUE", "MUN", "DMI", "CH4"]:
        if not os.path.exists(os.path.join(ROOT, ds, f"cv_results_{tr}.csv")): continue
        for m in ["ABLUP", "GBLUP", "ssGBLUP", "wssGBLUP", "rrBLUP", "BayesA", "BayesB"]:
            for j, v in enumerate([ds, tr, m], 1): put(wg, g, j, v, BLUE)
            base = f'$A{g},{grng("B")},$B{g},{grng("D")},$C{g}'
            put(wg, g, 4, f'=IFERROR(AVERAGEIFS({grng("E")},{grng("A")},{base},{grng("C")},"fold*"),"n/a")', BLACK, "0.000", True)
            put(wg, g, 5, f'=IFERROR(AVERAGEIFS({grng("E")},{grng("A")},{base},{grng("C")},"forward"),"n/a")', BLACK, "0.000", True)
            g += 1
wg.freeze_panes = "A5"; widths(wg, [17, 7, 9, 10, 16, 12, 9, 12, 36])

wb.save(OUT); print(OUT, "input rows:", last - 4, "paired rows:", plast - 4)
