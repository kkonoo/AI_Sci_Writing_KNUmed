"""W4 figures: study designs of the two fictional example studies used across the course."""
from common import scene, save

W = "w04"


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


def wet():
    s = scene(h=110, budget=12, alt="가상의 예시 연구 설계: 마우스 UUO 모델과 compound X")
    bands = _columns(s, ["동물과 군", "처치", "수확", "측정"], 4, 94)
    row = [15 + i * 21 for i in range(4)]
    (_, x, w) = bands[0]
    s.box(x + 3, row[0] + 1.75, w - 6, 15, "수컷 C57BL/6J", sub="8주령", name_pt=11.5)
    for i, (g, st) in enumerate([("sham", "plain"), ("UUO + vehicle", "plain"), ("UUO + compound X", "primary")]):
        s.box(x + 3, row[i + 1] + 1.75, w - 6, 15, g, sub="n = 6", style=st, name_pt=11)
    (_, x, w) = bands[1]
    s.box(x + 3, row[0], w - 6, 24, "Day 0", sub="왼쪽 UUO 수술 또는 sham 수술", name_pt=11.5)
    s.box(x + 3, row[1] + 9, w - 6, 34, "Day 0–6", sub="UUO 군: compound X 10 mg/kg 또는 vehicle, 경구, 하루 한 번", name_pt=11.5)
    (_, x, w) = bands[2]
    s.box(x + 3, row[0], w - 6, 24, "Day 7", sub="신장 채취", name_pt=11.5)
    (_, x, w) = bands[3]
    for i, (f, sub) in enumerate([("Fig. 1", "체중, 혈청 크레아티닌"), ("Fig. 2", "Masson's trichrome, 섬유화 면적"),
                                  ("Fig. 3", "qPCR: Col1a1, Acta2, Fn1"), ("Fig. 4", "웨스턴 블롯: p-Smad3/Smad3")]):
        s.box(x + 3, row[i], w - 6, 18.5, f, sub=sub, align="left", name_pt=10.5, sub_pt=9.5)
    return save(s, W, "design_wet")


def dry():
    s = scene(h=78, budget=10, alt="가상의 예시 연구 설계: 사람 신장 생검 단일세포 RNA 시퀀싱 재분석")
    bands = _columns(s, ["데이터", "분석", "비교", "검증"], 4, 62)
    (_, x, w) = bands[0]
    s.box(x + 3, 15, w - 6, 26, "공개된 사람 신장 생검", sub="단일세포 RNA 시퀀싱", name_pt=11)
    s.box(x + 3, 46, w - 6, 20, "섬유화 환자 8명", sub="대조군 6명", name_pt=11)
    (_, x, w) = bands[1]
    s.box(x + 3, 15, w - 6, 22, "QC, 세포 유형 주석", sub="Fig. 1, Fig. 2 (UMAP)", name_pt=11)
    s.box(x + 3, 42, w - 6, 24, "섬유아세포 아형 나누기", sub="MF2를 찾음", name_pt=11)
    (_, x, w) = bands[2]
    s.box(x + 3, 15, w - 6, 30, "환자별 MF2 비율", sub="섬유아세포 중 비율, Wilcoxon (Fig. 3)", style="primary", name_pt=11)
    (_, x, w) = bands[3]
    s.box(x + 3, 15, w - 6, 22, "MF2 표지 유전자", sub="Fig. 4", name_pt=11)
    s.box(x + 3, 42, w - 6, 24, "공간 전사체로 위치 확인", sub="Fig. 4", name_pt=11)
    return save(s, W, "design_dry")


if __name__ == "__main__":
    wet()
    dry()
