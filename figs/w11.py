"""W11 figure: each part of the Abstract comes from another part of the manuscript.

Korean: assets/img/w11/abstract_sources.svg, English: abstract_sources.en.svg.
"""
from common import scene, save

W = "w11"

TEXT = {
    "ko": dict(
        alt="Abstract의 다섯 부분과 각 부분을 가져오는 곳",
        manuscript="원고",
        abs=[("배경", "1문장"), ("gap", "1문장"), ("접근", "1~2문장"), ("핵심 결과", "2~3문장, 수치와 함께"), ("결론", "1문장")],
        intro="첫 문단, gap 문장, 마지막 문단", meth="종, 모델, n", res="결론 문장과 수치", disc="마지막 문장",
        note="Abstract에만 있는 결과나 주장은 없어야 한다. 접근은 Introduction 마지막 문단에서도 가져온다.",
    ),
    "en": dict(
        alt="The five parts of the Abstract and where each part comes from",
        manuscript="Manuscript",
        abs=[("Background", "1 sentence"), ("Gap", "1 sentence"), ("Approach", "1–2 sentences"),
             ("Key results", "2–3 sentences, with numbers"), ("Conclusion", "1 sentence")],
        intro="First paragraph, gap sentence, last paragraph", meth="Species, model, n",
        res="Conclusion sentences and numbers", disc="Last sentence",
        note="No result or claim should appear only in the Abstract. The approach also comes from the last paragraph of the Introduction.",
    ),
}
KEY = 3  # key results


def abstract_sources(lang="ko"):
    t = TEXT[lang]
    en = lang == "en"
    h, gap, y0 = 16, 4, 13
    s = scene(h=y0 + 5 * h + 4 * gap + (18 if en else 14), alt=t["alt"])
    s.text(4, 4, 80, 7, t["manuscript"], bold=True, name_pt=12)
    s.text(150, 4, 86, 7, "Abstract", bold=True, name_pt=12)
    rows = [y0 + i * (h + gap) for i in range(5)]
    right = [s.box(150, y, 86, h, n, sub=sub, style="primary" if i == KEY else "soft", name_pt=11.5)
             for i, (y, (n, sub)) in enumerate(zip(rows, t["abs"]))]
    lw = 88 if en else 72
    intro = s.box(4, rows[0], lw, 2 * h + gap, "Introduction", sub=t["intro"])
    meth = s.box(4, rows[2], lw, h, "Methods", sub=t["meth"])
    res = s.box(4, rows[3], lw, h, "Results", sub=t["res"])
    disc = s.box(4, rows[4], lw, h, "Discussion", sub=t["disc"])
    s.link(intro, right[0], sides="right>left")
    s.link(intro, right[1], sides="right>left")
    s.link(meth, right[2], sides="right>left")
    s.link(res, right[3], sides="right>left")
    s.link(disc, right[4], sides="right>left")
    s.text(4, rows[4] + h + 3, 232, 11 if en else 7, t["note"], name_pt=10, color="muted")
    return save(s, W, "abstract_sources" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    abstract_sources("ko")
    abstract_sources("en")
