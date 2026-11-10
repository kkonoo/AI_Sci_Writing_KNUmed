"""W8 figure: a review comment has a location, a problem and a reason (and a suggestion if any)."""
from common import scene, save

W = "w08"

PARTS = [
    ("위치", "Lines 14–16 (qPCR):", "primary"),
    ("문제", "The reference gene used for normalization is not given.", "mid"),
    ("이유", "Without it, a reader cannot repeat the ΔΔCt calculation.", "mid"),
    ("제안 (있으면)", "Please name the gene.", "soft"),
]


def comment_parts():
    s = scene(h=64, alt="리뷰 코멘트의 네 부분: 위치, 문제, 이유, 제안")
    x0, inner, gap = 4, 232, 4
    widths = [42, 66, 66, 46]
    scale = (inner - gap * 3) / sum(widths)
    x = x0
    for (label, text, style), w in zip(PARTS, widths):
        w *= scale
        s.pill(x, 4, w, 10, label, style=style, name_pt=11.5)
        s.box(x, 18, w, 28, text, align="left", valign="middle", name_pt=11, bold=False)
        x += w + gap
    s.text(x0, 50, inner, 8, "위치가 없으면 저자가 어디를 고칠지 모르고, 이유가 없으면 반영할지 판단할 수 없다.",
           name_pt=10.5, color="muted")
    return save(s, W, "comment_parts")


if __name__ == "__main__":
    comment_parts()
