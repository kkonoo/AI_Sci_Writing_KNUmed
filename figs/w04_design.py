"""W4 figures: study designs of the two fictional example studies used across the course.

Korean: assets/img/w04/design_wet.svg, design_dry.svg. English: design_wet.en.svg, design_dry.en.svg.
"""
from common import scene, save

W = "w04"

WET = {
    "ko": dict(
        alt="가상의 예시 연구 설계: 마우스 UUO 모델과 compound X",
        heads=["동물과 군", "처치", "수확", "측정"],
        mice=("수컷 C57BL/6J", "8주령"),
        day0=("Day 0", "왼쪽 UUO 수술 또는 sham 수술"),
        dose=("Day 0–6", "UUO 군: compound X 10 mg/kg 또는 vehicle, 경구, 하루 한 번"),
        day7=("Day 7", "신장 채취"),
        figs=[("Fig. 1", "체중, 혈청 크레아티닌"), ("Fig. 2", "Masson's trichrome, 섬유화 면적"),
              ("Fig. 3", "qPCR: Col1a1, Acta2, Fn1"), ("Fig. 4", "웨스턴 블롯: p-Smad3/Smad3")],
    ),
    "en": dict(
        alt="Fictional example study design: mouse UUO model and compound X",
        heads=["Animals and groups", "Treatment", "Harvest", "Measurements"],
        mice=("Male C57BL/6J", "8 weeks old"),
        day0=("Day 0", "Left UUO or sham surgery"),
        dose=("Day 0–6", "UUO groups: compound X 10 mg/kg or vehicle, oral, once a day"),
        day7=("Day 7", "Kidneys harvested"),
        figs=[("Fig. 1", "Body weight, serum creatinine"), ("Fig. 2", "Masson's trichrome, fibrotic area"),
              ("Fig. 3", "qPCR: Col1a1, Acta2, Fn1"), ("Fig. 4", "Western blot: p-Smad3/Smad3")],
    ),
}

DRY = {
    "ko": dict(
        alt="가상의 예시 연구 설계: 사람 신장 생검 단일세포 RNA 시퀀싱 재분석",
        heads=["데이터", "분석", "비교", "검증"],
        data=("공개된 사람 신장 생검", "단일세포 RNA 시퀀싱"), people=("섬유화 환자 8명", "대조군 6명"),
        qc=("QC, 세포 유형 주석", "Fig. 1, Fig. 2 (UMAP)"), sub=("섬유아세포 아형 나누기", "MF2를 찾음"),
        ratio=("환자별 MF2 비율", "섬유아세포 중 비율, Wilcoxon (Fig. 3)"),
        markers=("MF2 표지 유전자", "Fig. 4"), spatial=("공간 전사체로 위치 확인", "Fig. 4"),
    ),
    "en": dict(
        alt="Fictional example study design: reanalysis of single-cell RNA sequencing of human kidney biopsies",
        heads=["Data", "Analysis", "Comparison", "Validation"],
        data=("Public human kidney biopsies", "Single-cell RNA sequencing"), people=("8 patients with fibrosis", "6 controls"),
        qc=("QC, cell type annotation", "Fig. 1, Fig. 2 (UMAP)"), sub=("Fibroblast subtypes", "MF2 identified"),
        ratio=("MF2 proportion per patient", "Share of fibroblasts, Wilcoxon (Fig. 3)"),
        markers=("MF2 marker genes", "Fig. 4"), spatial=("Location by spatial transcriptomics", "Fig. 4"),
    ),
}


def _columns(s, heads, y0, h, gap=8):
    n = len(heads)
    w = (232 - (n - 1) * gap) / n
    bands = []
    for i, head in enumerate(heads):
        x = 4 + i * (w + gap)
        s.text(x, y0, w, 7, head, bold=True, name_pt=11.5)
        bands.append((s.band(x, y0 + 8, w, h, "", style="faint"), x, w))
    for (a, _, _), (b, _, _) in zip(bands, bands[1:]):
        s.link(a, b, sides="right>left")
    return bands


def suffix(lang):
    return "" if lang == "ko" else ".en"


def wet(lang="ko"):
    t = WET[lang]
    s = scene(h=110, budget=12, alt=t["alt"])
    bands = _columns(s, t["heads"], 4, 94)
    row = [15 + i * 21 for i in range(4)]
    (_, x, w) = bands[0]
    s.box(x + 3, row[0] + 1.75, w - 6, 15, t["mice"][0], sub=t["mice"][1], name_pt=11.5)
    for i, (g, st) in enumerate([("sham", "plain"), ("UUO + vehicle", "plain"), ("UUO + compound X", "primary")]):
        s.box(x + 3, row[i + 1] + 1.75, w - 6, 15, g, sub="n = 6", style=st, name_pt=11)
    (_, x, w) = bands[1]
    s.box(x + 3, row[0], w - 6, 24, t["day0"][0], sub=t["day0"][1], name_pt=11.5)
    s.box(x + 3, row[1] + 9, w - 6, 34, t["dose"][0], sub=t["dose"][1], name_pt=11.5)
    (_, x, w) = bands[2]
    s.box(x + 3, row[0], w - 6, 24, t["day7"][0], sub=t["day7"][1], name_pt=11.5)
    (_, x, w) = bands[3]
    for i, (f, sub) in enumerate(t["figs"]):
        s.box(x + 3, row[i], w - 6, 18.5, f, sub=sub, align="left", name_pt=10.5, sub_pt=9.5)
    return save(s, W, "design_wet" + suffix(lang))


def dry(lang="ko"):
    t = DRY[lang]
    s = scene(h=78, budget=10, alt=t["alt"])
    bands = _columns(s, t["heads"], 4, 62)
    pt = 11 if lang == "ko" else 10.5
    (_, x, w) = bands[0]
    s.box(x + 3, 15, w - 6, 26, t["data"][0], sub=t["data"][1], name_pt=pt)
    s.box(x + 3, 46, w - 6, 20, t["people"][0], sub=t["people"][1], name_pt=pt)
    (_, x, w) = bands[1]
    qh = 22 if lang == "ko" else 26
    s.box(x + 3, 15, w - 6, qh, t["qc"][0], sub=t["qc"][1], name_pt=pt)
    s.box(x + 3, 20 + qh, w - 6, 46 - qh, t["sub"][0], sub=t["sub"][1], name_pt=pt)
    (_, x, w) = bands[2]
    s.box(x + 3, 15, w - 6, 30, t["ratio"][0], sub=t["ratio"][1], style="primary", name_pt=pt)
    (_, x, w) = bands[3]
    s.box(x + 3, 15, w - 6, 22, t["markers"][0], sub=t["markers"][1], name_pt=pt)
    s.box(x + 3, 42, w - 6, 24, t["spatial"][0], sub=t["spatial"][1], name_pt=pt)
    return save(s, W, "design_dry" + suffix(lang))


if __name__ == "__main__":
    for lang in ("ko", "en"):
        wet(lang)
        dry(lang)
