"""W3 figure: one sentence with three ideas becomes three sentences.

Korean: assets/img/w03/split_sentence.svg, English: split_sentence.en.svg.
"""
from common import scene, save

W = "w03"

BEFORE = ("Compound X treatment-associated fibrotic area reduction was accompanied by decreased "
          "Col1a1 and Acta2 expression, suggesting Smad3 pathway-mediated antifibrotic activity.")
AFTER = [
    "Compound X reduced the fibrotic area in UUO kidneys.",
    "It also lowered the expression of Col1a1 and Acta2.",
    "These changes suggest that Smad3 signaling mediates the antifibrotic effect of compound X.",
]

TEXT = {
    "ko": dict(alt="생각 세 개를 담은 한 문장을 세 문장으로 나눈다", before="전: 한 문장에 생각 세 개",
               after="후: 한 문장에 생각 하나", link="문장을 나눈다",
               note="가상의 예시. 뜻과 주장은 그대로 두고 문장만 나눈다."),
    "en": dict(alt="One sentence with three ideas becomes three sentences", before="Before: three ideas in one sentence",
               after="After: one idea per sentence", link="Split it",
               note="Fictional example. Only the sentences are split. The meaning and the claims stay the same."),
}


def split_sentence(lang="ko"):
    t = TEXT[lang]
    s = scene(h=91, alt=t["alt"])
    s.text(4, 4, 90, 7, t["before"], bold=True, name_pt=11)
    before = s.box(4, 13, 90, 65, BEFORE, style="soft", align="left", valign="middle", name_pt=11, bold=False)
    s.text(124, 4, 112, 7, t["after"], bold=True, name_pt=11)
    bh, gap = 19, 4
    circles = []
    for i, sentence in enumerate(AFTER):
        y = 13 + i * (bh + gap)
        circles.append(s.circle(129, y + bh / 2, 4.8, str(i + 1), style="mid", name_pt=10))
        s.box(136, y, 100, bh, sentence, align="left", valign="middle", name_pt=10.5, bold=False)
    s.link(before, circles[1], sides="right>left", label=t["link"])
    s.text(4, 80, 232, 7, t["note"], name_pt=9.5, color="muted")
    return save(s, W, "split_sentence" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    split_sentence("ko")
    split_sentence("en")
