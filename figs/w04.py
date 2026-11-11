"""W4 figure: the example storyboard, one question and one conclusion sentence per figure.

Korean: assets/img/w04/storyboard.svg, English: storyboard.en.svg.
"""
from common import scene, save

W = "w04"

CONCLUSIONS = [
    "Mice given compound X or vehicle have similar body weight and serum creatinine after UUO.",
    "Compound X reduces interstitial fibrosis in the obstructed kidney.",
    "Compound X lowers Col1a1 and Acta2 expression after UUO.",
    "Compound X lowers Smad3 phosphorylation in the obstructed kidney.",
]

TEXT = {
    "ko": dict(
        alt="가상의 예시 연구의 Figure 순서 카드 네 장",
        questions=["compound X가 전신 상태를 바꾸는가?", "섬유화가 줄었는가?", "섬유화 유전자의 발현도 줄었는가?",
                   "TGF-β/Smad3 신호도 달라졌는가?"],
        note="결론 문장만 차례로 이어 읽으면 Abstract의 결과 부분처럼 읽혀야 한다. 가상의 예시.",
    ),
    "en": dict(
        alt="Figure order cards for the fictional example study",
        questions=["Does compound X change general health?", "Is fibrosis reduced?",
                   "Is the expression of fibrosis genes lower too?", "Does TGF-β/Smad3 signaling change too?"],
        note="Read in order, the conclusion sentences alone should read like the results part of an Abstract. Fictional example.",
    ),
}


def storyboard(lang="ko"):
    t = TEXT[lang]
    en = lang == "en"
    qh = 19 if en else 15
    s = scene(h=90 if en else 82, alt=t["alt"], budget=12)
    x0, inner, gap = 4, 232, 5
    n = len(CONCLUSIONS)
    w = (inner - (n - 1) * gap) / n
    prev = None
    for i, (q, concl) in enumerate(zip(t["questions"], CONCLUSIONS)):
        x = x0 + i * (w + gap)
        c = s.circle(x + w / 2, 10, 5.2, f"{i + 1}", style="primary" if i == 0 else "mid", name_pt=9.5)
        if prev is not None:
            s.link(prev, c, sides="right>left", kind="dots")
        prev = c
        s.box(x, 19, w, qh, q, style="soft", name_pt=10.5 if en else 11.5)
        s.box(x, 22 + qh, w, 30, concl, align="left", valign="top", name_pt=11, bold=False)
    s.text(x0, 56 + qh, inner, 11 if en else 7, t["note"], name_pt=10, color="muted")
    return save(s, W, "storyboard" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    storyboard("ko")
    storyboard("en")
