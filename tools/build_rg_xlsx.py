"""Builds rg_evidence.xlsx: every trait pair, every candidate, every paper, and the filtering criteria.
Run: python3 tools/build_rg_xlsx.py  (then recalc with the xlsx skill's recalc.py)
Decisions follow the user's rules of 4 Nov 2026 (criteria sheet). PENDING = waiting for the user's answer."""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "rg_evidence.xlsx")
F = "Arial"
H = Font(name=F, bold=True, color="FFFFFF"); HFILL = PatternFill("solid", start_color="1F4E78")
BLUE = Font(name=F, color="0000FF"); BLACK = Font(name=F, color="000000"); BOLD = Font(name=F, bold=True)
TITLE = Font(name=F, bold=True, size=13); NOTE = Font(name=F, italic=True, size=9, color="595959")
FILL = {"PASS": PatternFill("solid", start_color="E2EFDA"), "FAIL": PatternFill("solid", start_color="FCE4D6"),
        "PENDING": PatternFill("solid", start_color="FFF2CC"), "IN MODEL": PatternFill("solid", start_color="DDEBF7"),
        "NO ESTIMATE": PatternFill("solid", start_color="EDEDED")}
thin = Side(style="thin", color="BFBFBF"); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
WRAP = Alignment(wrap_text=True, vertical="top")

def header(ws, r, cols):
    for j, c in enumerate(cols, 1):
        x = ws.cell(row=r, column=j, value=c); x.font, x.fill, x.border = H, HFILL, BOX
        x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
def widths(ws, w):
    for j, v in enumerate(w, 1): ws.column_dimensions[get_column_letter(j)].width = v

# ------------------------------------------------------------------ papers
# key: (citation, DOI or URL, population / country, Nordic?, access, contribution)
P = {
 "NAV2024": ("NAV routine genetic evaluation of dairy cattle, May 2024", "https://www.nordicebv.info (NAV documentation)", "HOL/RDC/JER, DK-SE-FI", "Yes", "used earlier (file 00)", "MY-PY 0.86 (in model)"),
 "Buitenhuis2023": ("Buitenhuis & Poulsen 2023. J Dairy Sci 106:5562-5569", "10.3168/jds.2022-22798", "Danish HOL/JER/Red, 422,305 cows", "Yes (Danish)", "uploaded PDF", "MY-MUN (in model); MU-protein % only"),
 "Tavernier2024": ("Tavernier et al. 2024. J Dairy Sci 107:2231-2240", "10.3168/jds.2023-24117", "Irish grazing Holstein-Friesian, 1,291 cows", "No (Ireland)", "uploaded PDF", "MY/PY/MUN-NUE (in model); NUE-N intake"),
 "Schneider2025": ("Schneider et al. 2025. J Dairy Sci 108:12519-12530", "10.3168/jds.2025-26853", "Danish Holstein, 4,019 cows", "Yes (Danish)", "uploaded PDF", "MY/PY-CH4 (in model)"),
 "Cavani2022": ("Cavani et al. 2022. J Dairy Sci 105:7564-7574", "10.3168/jds.2022-22066", "US Holstein, 1,328 cows", "No (USA)", "abstract (DOAJ)", "DMI-FR 0.69 (in model); FR-milk energy 0.21"),
 "Liinamo2012": ("Liinamo, Mantysaari & Mantysaari 2012. J Dairy Sci 95:6788-6794", "10.3168/jds.2012-5342", "Nordic Red heifers, Finland, 291 cows", "Yes (Finnish)", "uploaded PDF", "ECM-DMI 0.62 (0.32), Table 2"),
 "Lidauer2023": ("Lidauer et al. 2023. Animal 17:100917", "10.1016/j.animal.2023.100917", "Nordic Red, Finland, 654 primiparous cows", "Yes (Finnish)", "uploaded PDF", "DMI-ECM 0.64 (0.35), Table 3"),
 "Holtsmark2008": ("Holtsmark, Heringstad, Madsen & Odegard 2008. J Dairy Sci 91:4006-4012", "10.3168/jds.2007-0816", "Norwegian Red, 836,452 1st-lactation daughters", "Yes (Norwegian)", "abstract (Nofima, QxMD)", "culling with PY -0.41, SCS 0.20, ICF 0.15"),
 "Zetouni2018": ("Zetouni, Kargo, Norberg & Lassen 2018. J Dairy Sci 101:2273-2280", "10.3168/jds.2017-13402", "Danish Holstein, 1,397 CH4 cows", "Yes (Danish)", "uploaded PDF", "CH4 with ICF 0.17 (0.13), udder health 0.06 (0.19), Table 5"),
 "Bakke2024": ("Bakke & Heringstad 2024. Interbull Bulletin 60:78-85", "https://journal.interbull.org/index.php/ib/article/view/1934", "Norwegian Red, 2,074 cows", "Yes (Norwegian)", "uploaded PDF", "DMI-CH4 0.65 (0.10), Table 3; EBV-index correlations, Table 4"),
 "Chipondoro2024": ("Chipondoro 2024. MSc thesis, SLU", "https://stud.epsilon.slu.se/19720/", "Swedish Red, 194 cows, one herd", "Yes (Swedish)", "uploaded PDF", "CH4-DMI 0.48 (0.64) parity 1"),
 "Rzewuska2013": ("Rzewuska & Strabel 2013. J Appl Genet 54:473-482", "10.1007/s13353-013-0159-8", "Polish Holstein-Friesian, 50 herds", "No (Poland)", "uploaded PDF", "MU with MY 0.24, PY 0.19 (0.10), SCS -0.14 (0.11), Table 3"),
 "Rzewuska2015": ("Rzewuska & Strabel 2015. Anim Sci Pap Rep 33:243-256", "no DOI printed (Anim. Sci. Pap. Rep. 33(3))", "Polish Holstein-Friesian, 148,700 cows", "No (Poland)", "uploaded PDF", "MU-ICF -0.06 to 0.14 by DIM, Fig. 2 (no mean)"),
 "Kheirabadi2016": ("Kheirabadi & Razmkabir 2016. J Anim Sci Technol 58:38", "10.1186/s40781-016-0121-5", "Iranian Holstein, 146,765 cows", "No (Iran)", "PMC full text", "SCS-PY 0.11 (0.04)"),
 "Chen2021": ("Chen et al. 2021. J Dairy Sci 104:4413-4423", "10.3168/jds.2020-18849", "Walloon (Belgian) Holstein, 504 bulls", "No (Belgium)", "uploaded PDF", "approximate rg (Blanchard): PNUE and MY with udder health, longevity, fertility, Table 4"),
 "Poppe2020": ("Poppe, Veerkamp, van Pelt & Mulder 2020. J Dairy Sci 103:1667-1684", "10.3168/jds.2019-17290", "Dutch Holstein AMS, 198,754 cows", "No (Netherlands)", "WUR thesis chapter (edepot)", "LnVar MACE correlations with MY, DMI, UH, FER, LON, Table 2.6"),
 "Manzanilla2022": ("Manzanilla-Pech et al. 2022. Front Genet 13:885932", "10.3389/fgene.2022.885932", "Danish Holstein, Tjele, 511-955 cows", "Yes (Danish)", "PMC full text", "CH4 conc. with RFI, ECM, MBW - no pair in our 11 traits"),
 "Stephansen2025": ("Stephansen et al. 2025. JDS Commun 7:198-203", "10.3168/jdsc.2025-0898", "Danish Holstein, 5,104 cows", "Yes (Danish)", "PMC full text", "gRFI/BW/gFS index correlations - no DMI pair"),
 "Stephansen2023": ("Stephansen et al. 2023. J Dairy Sci 106:9078-9094", "10.3168/jds.2023-23330", "7 countries, 7,379 cows", "Partly", "abstract (WUR)", "gRFI across parities; DMI between continents - no pair in our traits"),
 "Lidauer2019": ("Lidauer et al. 2019. Interbull Bulletin (Cincinnati)", "https://www.nordicebv.info (Interbull_Bulletin_Lidauer_etal_Cincinnati2019.pdf)", "Nordic HOL/RDC/JER", "Yes", "uploaded PDF", "MBW index vs longevity 0.18/0.20 - MBW, not DMI"),
 "NAVsavedfeed2025": ("NAV 2025. Economic weight of Saved feed in NTM", "NAV internal note (uploaded)", "Nordic HOL/RDC/JER genomic bull calves", "Yes", "uploaded PDF", "Saved Feed index vs NTM sub-indices, Table 4 (breed-specific)"),
 "Li2016": ("Li et al. 2016. J Dairy Sci 99:7232-7239", "10.3168/jds.2015-10669", "Nordic HOL/RDC/JER", "Yes", "uploaded PDF", "DMI across lactation periods only"),
 "Mehtio2020": ("Mehtio et al. 2020. Animal 14:1588-1597", "10.1017/S1751731120000439", "Finnish Nordic Red, 37,424 cows", "Yes (Finnish)", "PMC full text", "energy-status traits with ICF - no pair in our traits"),
 "Muuttoranta2015": ("Muuttoranta et al. 2015. Interbull Bulletin 49", "https://journal.interbull.org/index.php/ib/article/view/1617", "Swedish HOL / RDC", "Yes", "uploaded PDF", "fertility traits among themselves only"),
 "Muuttoranta2021": ("Muuttoranta et al. 2021. Interbull Bulletin", "uploaded PDF (Genetic parameters for female fertility in Nordic dairy cattle)", "Nordic HOL/RDC", "Yes", "uploaded PDF", "fertility traits among themselves only"),
 "Hoglund2014": ("Hoglund, Sahana, Guldbrandtsen & Lund 2014. BMC Genet 15:8", "10.1186/1471-2156-15-8", "Nordic HOL/RDC/JER", "Yes", "uploaded PDF", "GWAS validation - no genetic correlations"),
 "Sahana2013": ("Sahana, Guldbrandtsen, Thomsen & Lund 2013. Anim Genet 44:620-626", "10.1111/age.12053", "Nordic Holstein", "Yes", "uploaded PDF", "QTL; only CM-SCS from literature - not a pair in our traits"),
 "Hu2023": ("Hu et al. 2023. Animal 17:100851", "10.1016/j.animal.2023.100851", "Chinese Holstein", "No (China)", "uploaded PDF", "longevity-cow fertility in supplement (not included)"),
 "Hu2021": ("Hu et al. 2021. Front Genet 12:695543 (review)", "10.3389/fgene.2021.695543", "review, many countries", "No", "uploaded PDF", "MY-longevity range -0.5 to +0.43 (various countries)"),
 "Chen2022": ("Chen et al. 2022. J Dairy Sci 105:7575-7587", "10.3168/jds.2021-21681", "Walloon Holstein", "No (Belgium)", "uploaded PDF", "NEI correlations only in a figure; NEI is not NUE"),
 "Kargo2014": ("Kargo et al. 2014. J Dairy Sci 97:7879-7888", "10.3168/jds.2013-7694", "Nordic", "Yes", "uploaded PDF", "economic values; no genetic correlations"),
 "Kamalanathan2023": ("Kamalanathan et al. 2023. Animals 13:1308", "10.3390/ani13081308", "Canadian Holstein, 330 cows", "No (Canada)", "PMC full text", "CH4 traits among themselves only"),
 "JAM2016": ("ASAS-ADSA Joint Annual Meeting 2016 abstracts (J Anim Sci 94 E-Suppl 5 / J Dairy Sci 99 E-Suppl 1), pp. 134-", "uploaded PDF (134.pdf)", "various", "No", "uploaded PDF", "nothing for our 11 traits"),
 "Negussie2013": ("Negussie, Stranden & Mantysaari 2013. J Dairy Sci 96:1237-1250", "10.3168/jds.2012-5720", "Finnish Nordic Red, 22,422 first-lactation cows", "Yes (Finnish)", "uploaded PDF (4 Nov)", "only fat:protein ratio (FPR) vs MY, DFI, DO, SCS, CM (Tables 2-4); no MY-ICF, MY-SCS or SCS-ICF; FPR is not a model trait"),
 "Buch2011": ("Buch, Sorensen, Lassen, Berg, Jakobsen, Johansson & Sorensen 2011. J Anim Breed Genet 128:174-182", "10.1111/j.1439-0388.2010.00904.x", "Swedish Red, first parity, ~624,000 cows", "Yes (Swedish)", "uploaded PDF (4 Nov)", "REML rg: PY-SCS 0.22 (0.017), PY-CFI 0.30 (0.025), SCS-CFI 0.15 (0.038), Table 4 (= PubMed 21554411)"),
 "Muuttoranta2019": ("Muuttoranta et al. 2019. J Dairy Sci 102:8184-8196", "10.3168/jds.2018-15858", "Swedish Holstein, Nordic Red", "Yes", "uploaded PDF (4 Nov)", "fertility traits across parities only; no pair with yield or udder health"),
 "Elgersma2018": ("Fluctuations in milk yield are heritable and can be used as a resilience indicator to breed healthy cows (Elgersma et al., J Dairy Sci 2018)", "10.3168/jds.2017-13270", "Dutch Holstein", "No (Netherlands)", "via Oloo et al. 2023 review table (JDS blocked)", "LnSD with udder health -0.36, longevity -0.30, calving interval -0.22; older than Poppe 2020 -> not used (recent over old)"),
 "Poppe2021": ("Genetic analysis of resilience indicators based on milk yield records in different lactations and at different lactation stages (Poppe et al., J Dairy Sci 2021)", "10.3168/jds.2020-19245", "Dutch Holstein", "No (Netherlands)", "ranges only, via Oloo et al. 2023 review (PDF not available)", "LnVar with MY 0.48-0.69, fertility -0.25 to -0.35, longevity -0.04 to -0.18, udder health -0.21 to -0.33 (ranges over lactations); not used: my decision 4 Nov 2026 to keep Poppe 2020"),
 "Oloo2023": ("Oloo et al. 2023. Front Anim Sci 4:1254877 (review)", "10.3389/fanim.2023.1254877", "review (sub-Saharan Africa; cites Dutch data)", "No", "full text", "tabulates Elgersma 2018 and Poppe 2020/2021 resilience correlations; no new estimates. Its LnVar-DMI -0.54 to -0.66 are Poppe's PARTIAL correlations (adjusted for yield), not the plain 0.24 used here"),
 "Kasna2025": ("Kasna, Zavadilova & Vareka 2025. Animals 15:667", "10.3390/ani15050667", "Czech Holstein, 3,080 cows", "No (Czechia)", "PMC full text", "resilience h2 0.02-0.13; correlations with other traits only as sire RBV correlations in figures (no values) - not usable"),
 "Nousiainen2004": ("Evaluation of milk urea nitrogen as a diagnostic of protein feeding (J Dairy Sci 2004; PubMed 14762082)", "10.3168/jds.S0022-0302(04)73178-1", "meta-analysis of feeding trials", "-", "abstract (search)", "phenotypic MUN-diet relation; no genetic correlations"),
 "Sewalem2006": ("Analysis of milk urea nitrogen and lactose and their effect on longevity in Canadian dairy cattle (J Dairy Sci 2006)", "10.3168/jds.S0022-0302(06)72537-1", "Canadian dairy cattle", "No (Canada)", "title only (JDS blocked)", "survival analysis of MUN on longevity, not a genetic correlation; non-European"),
 "Bobbo2016": ("Casein haplotype and milk quality in Italian Holstein (J Dairy Sci 2016)", "10.3168/jds.2015-10463", "Italian Holstein", "No", "title only", "casein haplotype effects; no pair in our traits"),
 "JAS_sky253": ("Effect of repeated trace mineral injections on beef heifer development and reproductive performance. J Anim Sci 96:3943", "10.1093/jas/sky253", "beef heifers", "No", "title (DOI redirect)", "not relevant"),
 "JAS_skaa220": ("Milk production, nitrogen utilization, and methane emissions of dairy cows grazing grass, forb, and legume-based pastures. J Anim Sci 98:skaa220", "10.1093/jas/skaa220", "grazing trial", "No", "title (PMC)", "nutrition trial, phenotypic; no genetic correlations"),
 "DOI_2021_21342": ("not identified", "10.3168/jds.2021-21342", "?", "?", "DOI did not resolve in search or fetch", "please check DOI or upload PDF"),
 "DOI_2023_00589": ("not identified", "10.3168/jds.2023-00589", "?", "?", "DOI did not resolve in search or fetch", "please check DOI or upload PDF"),
 "DOI_2023_00367": ("not identified", "10.3168/jds.2023-00367", "?", "?", "DOI did not resolve in search or fetch", "please check DOI or upload PDF"),
 "Negussie2017": ("Negussie et al. 2017. J Dairy Sci 100:2433-2453 (review, methane proxies)", "10.3168/jds.2016-12030", "review", "-", "uploaded PDF (4 Nov)", "no new pair; cites Olkin (1981) bounds for deriving unknown correlations from known ones - supports implied values"),
 "EggerDanner2015": ("Egger-Danner et al. 2015. Animal 9:191-207 (review, functional traits)", "10.1017/S1751731114002614", "review", "-", "uploaded PDF (4 Nov)", "CM-SCC 0.55-0.93 and other within-group correlations; no pair in our 11 traits"),
 "PM21554411": ("Same paper as Buch et al. 2011 (PubMed 21554411)", "10.1111/j.1439-0388.2010.00904.x", "Swedish Red", "Yes", "read as Buch2011", "see Buch2011"),
 "Konig2008": ("Konig et al. 2008 (cited in Rzewuska 2015)", "not read", "German Holstein", "No", "NOT READ (cited only)", "MUN-ICF 0.29 (as cited)"),
}

# ------------------------------------------------------------------ pairs
# t1, t2, candidate, SE, sign handling, source trait definition, paper keys (best first), tier, nordic, decision, reason
A = "B"; C = "C"
R = [
 ("MY","PY","0.86","","none","305-d yields","NAV2024","X","Yes","IN MODEL","NAV estimate already in model"),
 ("MY","DMI","0.64","0.35","none","ECM vs DMI (ECM proxy for MY)","Lidauer2023;Liinamo2012",A,"Yes","PASS","Nordic genetic correlation; rule 2 (recent over old) picks Lidauer 2023 over Liinamo 2012 (0.62, SE 0.32)"),
 ("PY","DMI","0.64","0.35","none","ECM vs DMI (no protein-yield estimate exists)","Lidauer2023;Liinamo2012",A,"Yes","PASS","same Nordic ECM estimate used for protein yield (proxy, flagged)"),
 ("MY","FR","0.21","","none","feeding rate vs milk energy","Cavani2022",A,"No","FAIL","decision 4 Nov: European estimates only (USA dropped)"),
 ("PY","FR","0.21","","none","feeding rate vs milk energy","Cavani2022",A,"No","FAIL","European estimates only (USA dropped)"),
 ("MY","SCS","+0.18","0.05","flipped (MY vs udder health index -0.18)","EBV-based approximate rg","Chen2021",C,"No","FAIL","rule 1: C-tier and not Nordic (Belgium)"),
 ("PY","SCS","0.22","0.017","none","lactation SCS vs 305-d PY, first parity (Iran 0.11 dropped)","Buch2011;Kheirabadi2016","A","Yes","PASS","Nordic REML estimate, same trait definitions (tier A)"),
 ("MY","ICF","+0.46","0.04","flipped (MY vs female fertility index -0.46)","EBV-based approximate rg","Chen2021",C,"No","FAIL","rule 1: C-tier and not Nordic"),
 ("PY","ICF","0.30","0.025","none","days calving to first insemination vs PY, first parity","Buch2011","A","Yes","PASS","Nordic REML estimate, same trait definitions (tier A)"),
 ("MY","LONG","-0.05","0.05","none","EBV-based approximate rg","Chen2021;Hu2021",C,"No","FAIL","rule 1: C-tier and not Nordic"),
 ("PY","LONG","+0.41","","flipped (culling vs PY -0.41)","1st-lactation culling vs 305-d PY","Holtsmark2008",A,"Yes","PASS","Nordic genetic correlation (Norwegian Red); culling used as inverse of longevity"),
 ("MY","LNVAR","0.64 (QR) / 0.62 (MA)","","none","MACE correlation","Poppe2020",C,"No","PASS","my exception for resilience (4 Nov); QR chosen over MA (00b_rg_update_check.html)"),
 ("PY","LNVAR","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("MY","MUN","-0.10","","none","cow-number-weighted Danish HOL/JER/Red","Buitenhuis2023;Rzewuska2013","X","Yes","IN MODEL","rule 2: Danish (-0.10) over Polish (+0.24)"),
 ("PY","MUN","0.11","","none","MU vs protein % (proxy for PY), Danish HOL 0.16 / RDC 0.10 / JER 0.04, CFIT cow-weighted like MY-MUN","Buitenhuis2023;Rzewuska2013",A,"Yes","PASS","decision 4 Nov: Danish protein % by breed; one matrix for all breeds, so weighted as MY-MUN (Polish PY 0.19 not used)"),
 ("MY","NUE","0.52","0.11","none","NUEtot","Tavernier2024;Chen2021","X","No","IN MODEL","rule 2: recent (Tavernier 2024) over old (Chen 2021, 0.47)"),
 ("PY","NUE","0.80","0.07","none","NUEtot","Tavernier2024;Chen2021","X","No","IN MODEL","rule 2: Tavernier 2024 over Chen 2021 (0.42)"),
 ("MY","CH4","0.33","0.09","none","CH4 concentration (sniffer)","Schneider2025","X","Yes","IN MODEL","Danish, same trait definition"),
 ("PY","CH4","0.46","0.09","none","CH4 concentration (sniffer)","Schneider2025","X","Yes","IN MODEL","Danish, same trait definition"),
 ("DMI","FR","0.69","","none","feeding rate per visit","Cavani2022","X","No","FAIL","European estimates only: removed from the model (USA)"),
 ("DMI","SCS","+0.10","","flipped (DMI EBV vs udder health index -0.10)","Spearman EBV-index correlation","Bakke2024",C,"Yes","PASS","rule 1: C-tier but Nordic (Norwegian Red)"),
 ("DMI","ICF","+0.26","","flipped (DMI EBV vs fertility index -0.26)","Spearman EBV-index correlation","Bakke2024",C,"Yes","PASS","rule 1: C-tier but Nordic (Norwegian Red)"),
 ("DMI","LONG","","","","","Lidauer2019","-","-","NO ESTIMATE","only MBW index-longevity (0.18 HOL, 0.20 RDC); MBW is not DMI"),
 ("DMI","LNVAR","0.24 (QR) / 0.26 (MA)","","none","MACE correlation","Poppe2020",C,"No","PASS","resilience exception; QR chosen"),
 ("DMI","MUN","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("DMI","NUE","0.08","0.23","none","NUEtot vs nitrogen intake (DMI x diet CP)","Tavernier2024",A,"No","PASS","European (Irish) genetic correlation kept"),
 ("DMI","CH4","0.65","0.10","none","CH4 production (g/d); model trait is concentration","Bakke2024;Chipondoro2024",A,"Yes","PASS","Nordic genetic correlation; Bakke (SE 0.10) over Chipondoro MSc (0.48, SE 0.64): same year, far smaller SE"),
 ("FR","SCS","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("FR","LNVAR","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("FR","ICF","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("FR","LONG","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("FR","MUN","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("FR","NUE","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("FR","CH4","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("SCS","LNVAR","+0.32 (QR) / +0.27 (MA)","","flipped (LnVar vs udder health index)","MACE correlation","Poppe2020",C,"No","PASS","resilience exception; QR chosen"),
 ("SCS","ICF","0.15","0.038","none","SCS vs days calving to first insemination, first parity","Buch2011","A","Yes","PASS","Nordic REML estimate, same trait definitions (tier A)"),
 ("SCS","LONG","-0.20","","flipped (culling vs SCS 0.20)","1st-lactation culling vs lactation mean SCS","Holtsmark2008",A,"Yes","PASS","Nordic genetic correlation (Norwegian Red)"),
 ("SCS","MUN","-0.14","0.11","none","test-day, lactation-1 mean","Rzewuska2013",A,"No","PASS","European (Polish); no Danish estimate to prefer"),
 ("SCS","NUE","+0.29","0.07","flipped (PNUE vs udder health -0.29)","EBV-based approximate rg","Chen2021",C,"No","FAIL","rule 1: C-tier and not Nordic"),
 ("SCS","CH4","0.06","0.19","none","udder health (mastitis 0-50 d) vs CH4 production","Zetouni2018;Bakke2024",A,"Yes","PASS","Danish genetic correlation preferred over Bakke 2024 EBV-index (+0.14) (question 4 on ranking)"),
 ("LNVAR","ICF","+0.40 (QR) / +0.35 (MA)","","flipped (LnVar vs fertility index)","MACE correlation","Poppe2020",C,"No","PASS","resilience exception; QR chosen"),
 ("LNVAR","LONG","-0.16 (QR) / -0.14 (MA)","","none","MACE correlation","Poppe2020",C,"No","PASS","resilience exception; QR chosen"),
 ("LNVAR","MUN","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("LNVAR","NUE","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("LNVAR","CH4","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("ICF","LONG","-0.15","","flipped (culling vs ICF 0.15)","1st-lactation culling vs ICF","Holtsmark2008",A,"Yes","PASS","Nordic genetic correlation (Norwegian Red)"),
 ("ICF","MUN","-0.06 to 0.14 (by DIM)","","none","daily rg, no single mean; Konig 2008 (cited) 0.29","Rzewuska2015;Konig2008",A,"No","FAIL","no single reported value (range over lactation only); Konig 2008 cited, not read"),
 ("ICF","NUE","+0.44","0.07","flipped (PNUE vs female fertility -0.44)","EBV-based approximate rg","Chen2021",C,"No","FAIL","rule 1: C-tier and not Nordic"),
 ("ICF","CH4","0.17","0.13","none","ICF vs CH4 production","Zetouni2018;Bakke2024",A,"Yes","PASS","Danish genetic correlation preferred over Bakke EBV-index (+0.22) (question 4)"),
 ("LONG","MUN","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("LONG","NUE","-0.33","0.08","none","EBV-based approximate rg","Chen2021",C,"No","FAIL","rule 1: C-tier and not Nordic"),
 ("LONG","CH4","","","","","Bakke2024","-","-","NO ESTIMATE","only CH4 EBV vs total merit (-0.07)"),
 ("MUN","NUE","-0.12","0.17","none","NUEtot vs MUN","Tavernier2024","X","No","IN MODEL","European (Irish) - kept"),
 ("MUN","CH4","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
 ("NUE","CH4","","","","","","-","-","NO ESTIMATE","no estimate in any source read"),
]
assert len(R) == 55

wb = Workbook()
# ---------- Summary ----------
s = wb.active; s.title = "Summary"
s["A1"] = "Genetic correlations for the 11-trait model: evidence and decisions (4 Nov 2026)"; s["A1"].font = TITLE
s["A2"] = "Counts are formulas on the 'Trait pairs' sheet. Decisions apply the criteria sheet; PENDING waits for a decision on the questions sheet."; s["A2"].font = NOTE
header(s, 4, ["Decision", "Number of pairs", "Meaning"])
meaning = {"IN MODEL": "already in the simulation matrix (kept)", "PASS": "new value, passes the criteria",
           "FAIL": "candidate exists but fails a criterion", "PENDING": "needs my decision",
           "NO ESTIMATE": "no published estimate found in any source read"}
last = 5 + len(R) - 1 + 1
for i, d in enumerate(meaning, 5):
    c = s.cell(row=i, column=1, value=d); c.font = BLUE; c.border = BOX; c.fill = FILL[d]
    x = s.cell(row=i, column=2, value=f"=COUNTIF('Trait pairs'!$L$5:$L${4+len(R)},A{i})"); x.font = BLACK; x.border = BOX
    y = s.cell(row=i, column=3, value=meaning[d]); y.font = BLACK; y.border = BOX
s.cell(row=10, column=1, value="Total").font = BOLD
s.cell(row=10, column=2, value="=SUM(B5:B9)").font = BOLD
s.cell(row=11, column=1, value="Check: 11 traits give 55 pairs").font = NOTE
s.cell(row=11, column=2, value='=IF(B10=55,"OK","ERROR")').font = BOLD
widths(s, [16, 16, 60])

# ---------- Trait pairs ----------
w = wb.create_sheet("Trait pairs")
w["A1"] = "All 55 trait pairs: candidate genetic correlation, source, DOI and decision"; w["A1"].font = TITLE
w["A2"] = ("Signs are in the model's direction: SCS, ICF, LNVAR high = worse; LONG high = better. 'flipped' = the source reports the "
           "correlation with an index where high is good (or with culling), so the sign was reversed. QR/MA = quantile regression / moving average.")
w["A2"].font = NOTE
cols = ["Trait 1", "Trait 2", "Candidate rg", "SE", "Sign handling", "Trait definition in source", "Source (best first)",
        "DOI / URL", "Population", "Evidence tier", "Nordic?", "Decision", "Reason", "Paper keys"]
header(w, 4, cols)
for i, (t1, t2, rg, se, sg, td, keys, tier, nord, dec, why) in enumerate(R, 5):
    ks = [k for k in keys.split(";") if k]
    src = "; ".join(P[k][0] for k in ks); doi = "; ".join(P[k][1] for k in ks); pop = "; ".join(P[k][2] for k in ks)
    vals = [t1, t2, rg, se, sg, td, src, doi, pop, tier, nord, dec, why]
    for j, v in enumerate(vals, 1):
        c = w.cell(row=i, column=j, value=v); c.font = BLUE if j <= 11 else BLACK; c.border = BOX; c.alignment = WRAP
    w.cell(row=i, column=12).fill = FILL[dec]
    k = w.cell(row=i, column=14, value=keys); k.font = BLUE; k.border = BOX
w.freeze_panes = "C5"; w.auto_filter.ref = f"A4:N{4+len(R)}"
widths(w, [7, 7, 16, 6, 24, 30, 40, 30, 30, 8, 9, 13, 50, 22])

# ---------- Papers ----------
p = wb.create_sheet("Papers")
p["A1"] = "Every paper read or requested for the genetic-correlation step"; p["A1"].font = TITLE
header(p, 3, ["Key", "Citation", "DOI / URL", "Population", "Nordic?", "How read", "What it contributed", "Pairs using it (formula)"])
for i, (k, v) in enumerate(P.items(), 4):
    for j, x in enumerate([k] + list(v), 1):
        c = p.cell(row=i, column=j, value=x); c.font = BLUE; c.border = BOX; c.alignment = WRAP
    f = p.cell(row=i, column=8, value=f'=COUNTIF(\'Trait pairs\'!$N$5:$N${4+len(R)},"*"&A{i}&"*")')
    f.font = BLACK; f.border = BOX
p.freeze_panes = "B4"; widths(p, [16, 46, 34, 30, 14, 24, 46, 12])
p.cell(row=5 + len(P), column=1, value="'Pairs using it' counts the pair rows whose 'Paper keys' column names this paper.").font = NOTE

# ---------- Criteria ----------
c = wb.create_sheet("Criteria")
c["A1"] = "Filtering criteria, in the order applied"; c["A1"].font = TITLE
header(c, 3, ["#", "Criterion", "Set by", "Effect"])
crit = [
 (1, "Value must be read in the paper itself (table or abstract), not taken from a citation in another paper.", "Author (project rule: no unverified values)", "Konig 2008 (cited by Rzewuska 2015) not used."),
 (2, "Evidence tier: A = REML/Bayes genetic correlation, same trait definition, Nordic (only Buch et al. 2011 qualifies); B = genetic correlation for a proxy trait or a non-Nordic population; C = approximate (EBV/index correlation or MACE, no or rough SE).", "Author", "Grades every candidate; no candidate reached tier A."),
 (3, "C-tier values are used only if estimated in a Nordic breed.", "Author (4 Nov, item 1)", "Bakke 2024 (Norwegian Red) passes; Chen 2021 (Belgium) and Poppe 2020 (Netherlands) fail: 11 values removed."),
 (4, "Where estimates conflict: Danish over Polish; recent over old.", "Author (4 Nov, item 2)", "MY-MUN keeps Danish -0.10; MY/PY-NUE keep Tavernier 2024; MY-DMI uses Lidauer 2023 over Liinamo 2012."),
 (5, "A genetic correlation outranks an EBV/index correlation for the same pair.", "Author", "SCS-CH4 and ICF-CH4 use Zetouni 2018 rather than Bakke 2024."),
 (6, "Among equal-tier estimates of the same year, the smaller SE wins.", "Author", "DMI-CH4 uses Bakke (SE 0.10) over Chipondoro (SE 0.64)."),
 (7, "Signs converted to the model's direction when the source uses an index where high = good, or culling (inverse of longevity).", "Author", "Marked 'flipped' in the Trait pairs sheet."),
 (8, "No value is invented: pairs with no published estimate stay at 0 and are listed as 'no estimate' until decided.", "Author (3 Nov: no assumed values)", "19 pairs."),
 (9, "Only European estimates are used for genuine (B-tier) genetic correlations; resilience (Poppe 2020, Dutch, C-tier) is a stated exception.", "Author (4 Nov, answers 1-2)", "USA and Iran values dropped, including DMI-FR from the model."),
 (10, "The final matrix must be positive definite; if not, it is bent (Hayes & Hill 1981) and every changed value is reported.", "Author (method already in file 00)", "Applied after my decisions."),
]
for i, row in enumerate(crit, 4):
    for j, x in enumerate(row, 1):
        z = c.cell(row=i, column=j, value=x); z.font = BLACK; z.border = BOX; z.alignment = WRAP
widths(c, [4, 70, 30, 60])

# ---------- Questions ----------
q = wb.create_sheet("Open questions")
q["A1"] = "Questions that block the final matrix"; q["A1"].font = TITLE
header(q, 3, ["#", "Question", "Pairs affected"])
qs = [
 (1, "ANSWERED 4 Nov: European estimates only (USA, Iran dropped; DMI-FR removed from the model).", "MY-FR, PY-FR, PY-SCS, DMI-FR"),
 (2, "ANSWERED 4 Nov: resilience exception; compared QR vs MA - differences <= 0.023 SD, bending equal; QR chosen (authors' recommendation).", "LNVAR pairs"),
 (3, "ANSWERED 4 Nov: Danish protein % by breed, cow-weighted to 0.11.", "PY-MUN"),
 (4, "OPEN: the assembled matrix is not valid (min eigenvalue -0.20) because unknown pairs fixed at 0 contradict published ones (e.g. PY-LNVAR must be >= ~0.16 given MY-PY 0.86 and MY-LNVAR 0.64). Ordinary bending moves MY-PY 0.86 -> 0.74; weighted bending keeps published values within 0.015 but gives unknown pairs implied values (LONG-NUE +0.30, PY-LNVAR +0.24, MY-LONG +0.23). Which?", "whole matrix"),
 (5, "OPEN: Saved Feed - raw DMI loses 1.1-1.9% NTM value vs production-corrected DMI (same trait, redistributed weights). Use corrected DMI?", "index weights"),
 (6, "PARTLY ANSWERED 4 Nov: Buch et al. 2011 fills PY-SCS, PY-ICF, SCS-ICF. 17 pairs still without an estimate (all 7 feeding-rate pairs; MUN, NUE, LNVAR, LONG, CH4 combinations).", "17 pairs"),
]
for i, row in enumerate(qs, 4):
    for j, x in enumerate(row, 1):
        z = q.cell(row=i, column=j, value=x); z.font = BLACK; z.border = BOX; z.alignment = WRAP
widths(q, [4, 90, 50])

wb.save(OUT); print(OUT)
