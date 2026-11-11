"""W14 figure: answer each reviewer comment in four parts.

Korean: assets/img/w14/response_parts.svg, English: response_parts.en.svg.
"""
from common import scene, save

W = "w14"

EXAMPLE = [
    "R1C3: Serum creatinine is shown only as group means. Please show individual values and "
    "explain how blood was collected.",
    "We thank the reviewer for this suggestion.",
    "We now show serum creatinine for each mouse (Fig. 1c). We also state in the Methods how and "
    "when blood was collected.",
    "Changes: Methods, page 6, lines 120–124; Fig. 1c and its legend, page 22, lines 455–457.",
]
STYLES = ["soft", "soft", "primary", "soft"]

TEXT = {
    "ko": dict(
        alt="리뷰어 의견 하나에 답하는 네 부분",
        parts=[("의견 인용", "R1C3"), ("감사", "짧게 한 문장"), ("한 일", "실제로 한 것만"), ("바뀐 위치", "쪽, 줄, Figure")],
        note="가상의 의견과 답변. 하지 않은 분석이나 약속은 쓰지 않는다.",
    ),
    "en": dict(
        alt="The four parts of a reply to one reviewer comment",
        parts=[("Quote the comment", "R1C3"), ("Thanks", "One short sentence"), ("What you did", "Only what you actually did"),
               ("Where it changed", "Page, line, figure")],
        note="Fictional comment and reply. Do not claim analyses you did not do, and do not make promises.",
    ),
}


def response_parts(lang="ko"):
    t = TEXT[lang]
    en = lang == "en"
    heights = [22, 16, 22, 22]
    gap = 4
    lw = 58 if en else 52
    s = scene(h=4 + sum(heights) + 3 * gap + 16, alt=t["alt"])
    y = 4
    for (name, sub), text, style, h in zip(t["parts"], EXAMPLE, STYLES, heights):
        s.box(4, y, lw, h, name, sub=sub, style=style, name_pt=12 if en else 12.5)
        s.box(lw + 10, y, 232 - lw - 6, h, text, align="left", valign="middle", name_pt=11, bold=False)
        y += h + gap
    s.text(4, y + 1, 232, 7, t["note"], name_pt=10, color="muted")
    return save(s, W, "response_parts" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    response_parts("ko")
    response_parts("en")
