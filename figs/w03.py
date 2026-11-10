"""W3 figure: one sentence with three ideas becomes three sentences."""
from common import scene, save

W = "w03"

BEFORE = ("Compound X treatment-associated fibrotic area reduction was accompanied by decreased "
          "Col1a1 and Acta2 expression, suggesting Smad3 pathway-mediated antifibrotic activity.")
AFTER = [
    "Compound X reduced the fibrotic area in UUO kidneys.",
    "It also lowered the expression of Col1a1 and Acta2.",
    "These changes suggest that Smad3 signaling mediates the antifibrotic effect of compound X.",
]


def split_sentence():
    s = scene(h=91, alt="생각 세 개를 담은 한 문장을 세 문장으로 나눈다")
    s.text(4, 4, 90, 7, "전: 한 문장에 생각 세 개", bold=True, name_pt=11)
    before = s.box(4, 13, 90, 65, BEFORE, style="soft", align="left", valign="middle", name_pt=11, bold=False)
    s.text(124, 4, 112, 7, "후: 한 문장에 생각 하나", bold=True, name_pt=11)
    bh, gap = 19, 4
    boxes, circles = [], []
    for i, t in enumerate(AFTER):
        y = 13 + i * (bh + gap)
        circles.append(s.circle(129, y + bh / 2, 4.8, str(i + 1), style="mid", name_pt=10))
        boxes.append(s.box(136, y, 100, bh, t, align="left", valign="middle", name_pt=10.5, bold=False))
    s.link(before, circles[1], sides="right>left", label="문장을 나눈다")
    s.text(4, 80, 232, 7, "가상의 예시. 뜻과 주장은 그대로 두고 문장만 나눈다.", name_pt=9.5, color="muted")
    return save(s, W, "split_sentence")


if __name__ == "__main__":
    split_sentence()
