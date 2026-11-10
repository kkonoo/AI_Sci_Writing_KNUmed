"""W6 figure: a Results paragraph is purpose, what was done, result, interpretation."""
from common import scene, save

W = "w06"

ROWS = [
    ("목적", "왜 이 실험을 했나", "To test whether compound X reduces fibrosis,", "soft"),
    ("한 일", "방법 이름과 조건만", "we stained kidney sections with Masson's trichrome on day 7 after UUO (Fig. 2a).", "soft"),
    ("결과", "수치, n, 통계. 과거 시제",
     "UUO increased the fibrotic area from 1.9% ± 0.6% in sham mice to 18.2% ± 3.1% in vehicle-treated mice "
     "(mean ± SD, n = 6 mice per group; P < 0.0001; Fig. 2b). Compound X lowered the fibrotic area to "
     "9.6% ± 2.4% (P = 0.0004 versus UUO + vehicle; one-way ANOVA with Tukey's test).", "primary"),
    ("해석", "데이터 범위 안에서 한 문장", "Thus, compound X reduced interstitial fibrosis in the obstructed kidney.", "soft"),
]


def paragraph_parts():
    heights = [16, 18, 36, 18]
    gap = 4
    s = scene(h=4 + sum(heights) + gap * 3 + 18, alt="Results 단락의 네 부분과 예시 문장")
    y = 4
    for (name, sub, sentence, style), h in zip(ROWS, heights):
        s.box(4, y, 56, h, name, sub=sub, style=style, name_pt=12.5)
        s.box(66, y, 170, h, sentence, align="left", valign="middle", name_pt=11, bold=False)
        y += h + gap
    s.text(4, y + 1, 232, 6, "가상의 예시, Figure 2의 단락. 문헌과 비교하는 일은 Discussion(W10)에서 한다.", name_pt=10, color="muted")
    return save(s, W, "paragraph_parts")


if __name__ == "__main__":
    paragraph_parts()
