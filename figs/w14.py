"""W14 figure: answer each reviewer comment in four parts."""
from common import scene, save

W = "w14"

ROWS = [
    ("의견 인용", "R1C3", "R1C3: Serum creatinine is shown only as group means. Please show individual values and "
     "explain how blood was collected.", "soft"),
    ("감사", "짧게 한 문장", "We thank the reviewer for this suggestion.", "soft"),
    ("한 일", "실제로 한 것만", "We now show serum creatinine for each mouse (Fig. 1c). We also state in the Methods how and "
     "when blood was collected.", "primary"),
    ("바뀐 위치", "쪽, 줄, Figure", "Changes: Methods, page 6, lines 120–124; Fig. 1c and its legend, page 22, lines 455–457.", "soft"),
]


def response_parts():
    heights = [22, 16, 22, 22]
    gap = 4
    s = scene(h=4 + sum(heights) + 3 * gap + 16, alt="리뷰어 의견 하나에 답하는 네 부분")
    y = 4
    for (name, sub, text, style), h in zip(ROWS, heights):
        s.box(4, y, 52, h, name, sub=sub, style=style, name_pt=12.5)
        s.box(62, y, 174, h, text, align="left", valign="middle", name_pt=11, bold=False)
        y += h + gap
    s.text(4, y + 1, 232, 7, "가상의 의견과 답변. 하지 않은 분석이나 약속은 쓰지 않는다.", name_pt=10, color="muted")
    return save(s, W, "response_parts")


if __name__ == "__main__":
    response_parts()
