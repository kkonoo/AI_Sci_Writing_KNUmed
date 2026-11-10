"""W4 figure: the example storyboard, one question and one conclusion sentence per figure."""
from common import scene, save

W = "w04"

CARDS = [
    ("compound X가 전신 상태를 바꾸는가?",
     "Mice given compound X or vehicle have similar body weight and serum creatinine after UUO."),
    ("섬유화가 줄었는가?", "Compound X reduces interstitial fibrosis in the obstructed kidney."),
    ("섬유화 유전자의 발현도 줄었는가?", "Compound X lowers Col1a1 and Acta2 expression after UUO."),
    ("TGF-β/Smad3 신호도 달라졌는가?", "Compound X lowers Smad3 phosphorylation in the obstructed kidney."),
]


def storyboard():
    s = scene(h=82, alt="가상의 예시 연구의 Figure 순서 카드 네 장", budget=12)
    x0, inner, gap = 4, 232, 5
    n = len(CARDS)
    w = (inner - (n - 1) * gap) / n
    prev = None
    for i, (q, concl) in enumerate(CARDS):
        x = x0 + i * (w + gap)
        c = s.circle(x + w / 2, 10, 5.2, f"{i + 1}", style="primary" if i == 0 else "mid", name_pt=9.5)
        if prev is not None:
            s.link(prev, c, sides="right>left", kind="dots")
        prev = c
        s.box(x, 19, w, 15, q, style="soft", name_pt=11.5)
        s.box(x, 37, w, 30, concl, align="left", valign="top", name_pt=11, bold=False)
    s.text(x0, 71, inner, 7, "결론 문장만 차례로 이어 읽으면 Abstract의 결과 부분처럼 읽혀야 한다. 가상의 예시.",
           name_pt=10, color="muted")
    return save(s, W, "storyboard")


if __name__ == "__main__":
    storyboard()
