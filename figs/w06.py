"""W6 figure: a Results paragraph is purpose, what was done, result, interpretation.

Korean: assets/img/w06/paragraph_parts.svg, English: paragraph_parts.en.svg.
"""
from common import scene, save

W = "w06"

SENTENCES = [
    "To test whether compound X reduces fibrosis,",
    "we stained kidney sections with Masson's trichrome on day 7 after UUO (Fig. 2a).",
    "UUO increased the fibrotic area from 1.9% ± 0.6% in sham mice to 18.2% ± 4.0% in vehicle-treated mice "
    "(mean ± SD, n = 6 mice per group; P < 0.0001; Fig. 2b). Compound X lowered the fibrotic area to "
    "9.6% ± 3.1% (P = 0.0004 versus UUO + vehicle; one-way ANOVA with Tukey's test).",
    "Thus, compound X reduced interstitial fibrosis in the obstructed kidney.",
]
STYLES = ["soft", "soft", "primary", "soft"]

TEXT = {
    "ko": dict(
        alt="Results 단락의 네 부분과 예시 문장",
        parts=[("목적", "왜 이 실험을 했나"), ("한 일", "방법 이름과 조건만"), ("결과", "수치, n, 통계. 과거 시제"),
               ("해석", "데이터 범위 안에서 한 문장")],
        note="가상의 예시, Figure 2의 단락. 문헌과 비교하는 일은 Discussion(W10)에서 한다.",
    ),
    "en": dict(
        alt="The four parts of a Results paragraph, with example sentences",
        parts=[("Purpose", "Why this experiment"), ("What was done", "Method and conditions only"),
               ("Result", "Numbers, n, statistics. Past tense"), ("Interpretation", "One sentence within the data")],
        note="Fictional example, the paragraph for Figure 2. Comparison with the literature belongs in the Discussion (W10).",
    ),
}


def paragraph_parts(lang="ko"):
    t = TEXT[lang]
    heights = [16, 18, 36, 18]
    gap = 4
    en = lang == "en"
    lw = 68 if en else 56
    s = scene(h=4 + sum(heights) + gap * 3 + (22 if en else 18), alt=t["alt"])
    y = 4
    for (name, sub), sentence, style, h in zip(t["parts"], SENTENCES, STYLES, heights):
        s.box(4, y, lw, h, name, sub=sub, style=style, name_pt=12 if en else 12.5)
        s.box(lw + 10, y, 232 - lw - 6, h, sentence, align="left", valign="middle", name_pt=11, bold=False)
        y += h + gap
    s.text(4, y + 1, 232, 10 if en else 6, t["note"], name_pt=10, color="muted")
    return save(s, W, "paragraph_parts" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    paragraph_parts("ko")
    paragraph_parts("en")
