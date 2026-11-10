"""W11 figure: each part of the Abstract comes from another part of the manuscript."""
from common import scene, save

W = "w11"

ABS = [("배경", "1문장"), ("gap", "1문장"), ("접근", "1~2문장"), ("핵심 결과", "2~3문장, 수치와 함께"), ("결론", "1문장")]


def abstract_sources():
    h, gap, y0 = 16, 4, 13
    s = scene(h=y0 + 5 * h + 4 * gap + 14, alt="Abstract의 다섯 부분과 각 부분을 가져오는 곳")
    s.text(4, 4, 80, 7, "원고", bold=True, name_pt=12)
    s.text(150, 4, 86, 7, "Abstract", bold=True, name_pt=12)
    rows = [y0 + i * (h + gap) for i in range(5)]
    right = [s.box(150, y, 86, h, n, sub=sub, style="primary" if n == "핵심 결과" else "soft", name_pt=11.5)
             for y, (n, sub) in zip(rows, ABS)]
    intro = s.box(4, rows[0], 72, 2 * h + gap, "Introduction", sub="첫 문단, gap 문장, 마지막 문단")
    meth = s.box(4, rows[2], 72, h, "Methods", sub="종, 모델, n")
    res = s.box(4, rows[3], 72, h, "Results", sub="결론 문장과 수치")
    disc = s.box(4, rows[4], 72, h, "Discussion", sub="마지막 문장")
    s.link(intro, right[0], sides="right>left")
    s.link(intro, right[1], sides="right>left")
    s.link(meth, right[2], sides="right>left")
    s.link(res, right[3], sides="right>left")
    s.link(disc, right[4], sides="right>left")
    s.text(4, rows[4] + h + 3, 232, 7, "Abstract에만 있는 결과나 주장은 없어야 한다. 접근은 Introduction 마지막 문단에서도 가져온다.",
           name_pt=10, color="muted")
    return save(s, W, "abstract_sources")


if __name__ == "__main__":
    abstract_sources()
